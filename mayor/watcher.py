#!/usr/bin/env python3
"""Mayor watcher: no AI, just polling.

Run it under the Monitor tool; every stdout line wakes the mayor.
  INCIDENT <kind> ... (game paused)   fire / disaster / gridlock / utility outage
  TURN_DONE <date> pop=.. money=..     a timed run finished and the game auto-paused
Also appends one row per poll to stats.csv (wall clock + city numbers) for the video overlay,
and incident marks to marks.csv (same file the recorder writes).
"""
import os
import csv
import json
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
_envf = HERE.parent / "mcp-server/.env"
ENV = dict(l.split("=", 1) for l in _envf.read_text().split() if "=" in l) if _envf.exists() else {}
ENV.setdefault("CS2MCP_TOKEN", os.environ.get("CS2MCP_TOKEN", ""))
BASE = "http://127.0.0.1:8642"
HDR = {"X-CS2MCP-Token": ENV.get("CS2MCP_TOKEN", ""), "X-Src": "watcher"}
POLL_S = 3
VEHICLES_EVERY = 4          # deadlock census every 4th poll (~12 s)
UTILITY_JUMP = 15           # new outage icons in one go before it counts as an incident

FIRE = re.compile(r"fire|burn|destroy|collaps|disaster|tornado|storm|flood|lightning|tsunami|meteor", re.I)  # traffic accidents are not incidents
AFTERMATH = re.compile(r"burned down|collapsed|destroyed", re.I)  # results, not ongoing danger
BLAZE_R, BLAZE_S = 300, 600
SESSION_WRAP_MIN, SESSION_END_MIN = 15, 20  # build-out session: 20 minutes
UTILITY = re.compile(r"no electricity|no water|sewage|not enough (electricity|water)|garbage", re.I)


def call(path, post=False, timeout=15):
    req = urllib.request.Request(BASE + path, headers=HDR, method="POST" if post else "GET",
                                 data=b"" if post else None)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def ensure_tunnel():
    """Optional: (re)open an SSH tunnel to the game PC if ensure-link.sh exists next to this file."""
    if (HERE / "ensure-link.sh").exists():
        subprocess.run([str(HERE / "ensure-link.sh")], check=False)


def say(line):
    print(line, flush=True)


def mark(text):
    with (HERE / "marks.csv").open("a") as f:
        f.write(f"{datetime.now().isoformat(timespec='seconds')},{text.replace(',', ';')}\n")


def pause():
    try:
        call("/sim/run?cancel=true", post=True)
    except Exception:
        pass
    call("/sim/control?paused=true", post=True)


VEGETATION = re.compile(r"tree|bush|shrub|flower|grass|hedge|car\d|truck|van\d|bus\d|trailer|motorbike|scooter", re.I)  # also burning vehicles: fire house handles them


def in_city(loc, owned, margin=150):
    """True if the point is inside (or within margin of) a tile the city owns; far-away wildfires and
    highway pile-ups elsewhere on the map are not the mayor's incidents."""
    if not owned:
        return True
    return any(b["minX"] - margin <= loc["x"] <= b["maxX"] + margin and b["minZ"] - margin <= loc["z"] <= b["maxZ"] + margin
               for b in owned)


def main():
    ensure_tunnel()
    owned = []
    stats_path = HERE / "stats.csv"
    new_file = not stats_path.exists()
    stats = stats_path.open("a", newline="")
    w = csv.writer(stats)
    if new_file:
        w.writerow(["wall", "game", "population", "money", "happiness", "health", "traffic_flow", "notifications"])

    seen_fire = set()        # target entity ids already reported
    blazes = []              # (x, z, wall time) of blazes already reported
    seen_deadlock = set()
    last_utility = None
    was_running = None
    erroring = False
    n = 0
    say("WATCHER_UP")
    session_t0 = time.time()
    try:  # the session started when recording started (obs.py writes REC_START), not when this watcher (re)started
        recs = [l.split(",", 1)[0] for l in (HERE / "marks.csv").read_text().splitlines() if l.endswith(",REC_START")]
        if recs:
            t = datetime.fromisoformat(recs[-1]).timestamp()
            if time.time() - t < 3 * 3600:
                session_t0 = t
    except Exception:
        pass
    wrap_said = end_said = False
    while True:
        n += 1
        try:
            st = call("/state")
            if not st.get("cityLoaded"):
                time.sleep(POLL_S)
                continue
            sim = st["simulation"]
            running = not sim["paused"]
            ov = call("/city/overview")
            no = call("/city/notifications?limit=500")
            tr = call("/city/traffic") if n % VEHICLES_EVERY == 0 else None
            w.writerow([datetime.now().isoformat(timespec="seconds"), sim["gameDateTime"], ov["population"],
                        ov["money"], ov["averageHappiness"], ov["averageHealth"],
                        tr["cityTrafficFlowPercent"] if tr else "", no["total"]])
            stats.flush()

            incidents = []
            if n % 100 == 1 or not owned:  # refresh owned tile bounds now and then
                try:
                    owned[:] = [t["bounds"] for t in call("/city/tiles/list?owned=owned&features=false&limit=1000")["tiles"]]
                except Exception:
                    pass
            fires = [x for x in no["notifications"] if FIRE.search(x["type"]) and in_city(x["location"], owned)
                     and not AFTERMATH.search(x["type"])  # a burned-down shell is not something to react to
                     and not VEGETATION.search((x.get("target") or {}).get("prefab") or "")]  # burning trees: nothing the mayor can do
            fresh = [x for x in fires if (x["target"]["index"], x["type"]) not in seen_fire]
            for x in fresh:
                seen_fire.add((x["target"]["index"], x["type"]))
            # one blaze = one pause: fire spreading to the next house within BLAZE_R m of a blaze reported in
            # the last BLAZE_S seconds is the same incident, so it does not wake the mayor again
            now_t = time.time()
            blazes[:] = [b for b in blazes if now_t - b[2] < BLAZE_S]
            fresh = [x for x in fresh if not any(abs(x["location"]["x"] - bx) < BLAZE_R and abs(x["location"]["z"] - bz) < BLAZE_R
                                                 for bx, bz, _ in blazes)]
            for x in fresh:
                blazes.append((x["location"]["x"], x["location"]["z"], now_t))
            if fresh:
                kinds = sorted({x["type"] for x in fresh})
                loc = fresh[0]["location"]
                incidents.append(f"fire/disaster {len(fresh)}x {', '.join(kinds)} near x={loc['x']:.0f} z={loc['z']:.0f}")

            util = sum(c for t, c in no["countsByType"].items() if UTILITY.search(t))
            if last_utility is not None and util - last_utility >= UTILITY_JUMP and ov["population"] > 300:
                incidents.append(f"utility outage +{util - last_utility} icons (total {util})")
            last_utility = util

            if n % VEHICLES_EVERY == 0:
                vh = call("/city/vehicles", timeout=30)
                dl = vh.get("deadlocks", {})
                ids = {json.dumps(d, sort_keys=True)[:200] for d in dl.get("items", [])}
                if dl.get("count", 0) > 0 and not ids <= seen_deadlock:
                    seen_deadlock |= ids
                    incidents.append(f"gridlock {dl['count']} deadlock loop(s); see cs2_vehicles")

            if incidents and running:
                pause()
                for i in incidents:
                    mark("INCIDENT " + i)
                    say(f"INCIDENT {i} | {sim['gameDateTime']} | game paused")
                running = False
            elif incidents:
                for i in incidents:
                    mark("INCIDENT " + i)
                    say(f"INCIDENT {i} | {sim['gameDateTime']} | (game was already paused)")

            if was_running and not running and not incidents:
                say(f"TURN_DONE {sim['gameDateTime']} pop={ov['population']} money={ov['money']} "
                    f"happiness={ov['averageHappiness']}")
            was_running = running
            mins = (time.time() - session_t0) / 60
            if mins >= SESSION_WRAP_MIN and not wrap_said:
                wrap_said = True
                say(f"SESSION_WRAP_UP {mins:.0f} min: finish the current turn, no new big projects")
            if mins >= SESSION_END_MIN and not end_said:
                end_said = True
                say(f"SESSION_END_NOW {mins:.0f} min: when the current run ends, end the session (save, stop recording, diary note)")
            if erroring:
                say("WATCHER_RECOVERED")
                erroring = False
        except Exception as e:  # bridge down, game loading, tunnel dropped
            if not erroring:  # report once, not every retry
                say(f"WATCHER_ERROR {type(e).__name__}: {str(e)[:120]}")
                erroring = True
            ensure_tunnel()
            time.sleep(10)
        time.sleep(POLL_S)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
