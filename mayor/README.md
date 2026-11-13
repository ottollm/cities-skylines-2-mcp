# The mayor kit

How Claude Fable 5.2 ran **Fableton**: an empty meadow, a river and $1M → **90,761 residents**, played turn by turn through the bridge in this repo with no human moves in the game.

| | start | finish |
|---|---|---|
| residents | 0 | 90,761 |
| happiness | 50% | 80% (low point 58% at ~43k) |
| treasury | $1.0M | $1.98M (peak $25M before the final build-out) |
| play | | ~8 h over 10 one-hour sessions, 30 turns |

## Files

- **`MAYOR.md`**: the brief the model played with (goal, how a turn works, usage limits, incidents, diary format). The goal and pacing lines were tightened between sessions; this is the final version.
- **`diary.md`**: the model's own diary, unedited. One entry per turn (`Saw / Did / Why / Caption`), its notes to itself, session-end notes, and a few technical notes from the operator. The best read in the repo.
- **`stats.csv`**: population, treasury, happiness, health and notifications sampled every few seconds while the game ran.
- **`watcher.py`**: polls the bridge every few seconds; prints `TURN_DONE` when a timed run ends, pauses the game and prints `INCIDENT …` on fires, gridlock or utility outages, and `SESSION_WRAP_UP` / `SESSION_END_NOW` near the end of an hour. Run it under Claude Code's Monitor tool so these lines wake the model instead of it polling.
- **`report.py`**: one-call city report (overview, demand, budget, labor, services, zoning, traffic, problems) in a few hundred tokens.
- **`proxy.py`**: optional logging proxy in front of the bridge (`127.0.0.1:8642` → `CS2_UPSTREAM`); logs every mayor request to `events.jsonl` and caps `/sim/run` at a maximum number of in-game hours per call.

## The loop

1. Observe with `report.py` and the `cs2_*` data tools (numbers over screenshots).
2. Act: zoning, roads, services, taxes, budgets, policies, dev tree.
3. Append a diary entry.
4. Run time with `cs2_run_simulation`; wait for the watcher.
5. Incidents are separate mini-turns: fix the cause, one diary line, resume the run.

The scripts read the bridge token from `../mcp-server/.env` or the `CS2MCP_TOKEN` environment variable.
