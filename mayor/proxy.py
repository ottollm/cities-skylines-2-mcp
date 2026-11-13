#!/usr/bin/env python3
"""Transparent logging proxy: 127.0.0.1:8642 (what the MCP server, watcher and helper call)
-> UPSTREAM (the bridge, or an SSH tunnel to it when the game runs on another PC).

Every request is forwarded unchanged (Host rewritten to the bridge's own port). Requests from the
mayor (anything without `X-Src`) are appended to events.jsonl so the camera operator knows where
the mayor is building or looking. Stdlib only.
"""
import os
import json
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPSTREAM = os.environ.get("CS2_UPSTREAM", "http://127.0.0.1:8643")
EVENTS = HERE / "events.jsonl"


def first_xz(data):
    """First {x, z} pair found anywhere in a JSON response (positions of what was built/changed)."""
    try:
        obj = json.loads(data)
    except Exception:
        return None
    stack = [obj]
    while stack:
        o = stack.pop(0)
        if isinstance(o, dict):
            if isinstance(o.get("x"), (int, float)) and isinstance(o.get("z"), (int, float)):
                return [o["x"], o["z"]]
            stack.extend(o.values())
        elif isinstance(o, list):
            stack.extend(o)
    return None


MAX_RUN_HOURS = 96  # build-out session: no extra cap (bridge max)


def cap_run(path):
    """Cap /sim/run?hours= at MAX_RUN_HOURS; the bridge's answer shows the hours actually run."""
    if not path.startswith("/sim/run?"):
        return path
    from urllib.parse import parse_qsl, urlencode
    base, _, q = path.partition("?")
    qs = parse_qsl(q, keep_blank_values=True)
    out = []
    for k, v in qs:
        if k == "hours":
            try:
                v = str(min(float(v), MAX_RUN_HOURS))
            except ValueError:
                pass
        out.append((k, v))
    return base + "?" + urlencode(out)


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _fwd(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else (b"" if self.command == "POST" else None)
        hdrs = {k: v for k, v in self.headers.items() if k.lower() in ("x-cs2mcp-token", "content-type")}
        hdrs["Host"] = "127.0.0.1:8642"
        mayor = not self.headers.get("X-Src")
        self.path = cap_run(self.path)
        req = urllib.request.Request(UPSTREAM + self.path, data=body, headers=hdrs, method=self.command)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                code, data, ctype = r.status, r.read(), r.headers.get("Content-Type", "application/json")
        except urllib.error.HTTPError as e:
            code, data, ctype = e.code, e.read(), e.headers.get("Content-Type", "application/json")
        except Exception as e:
            code, data, ctype = 502, json.dumps({"error": f"proxy: {e}"}).encode(), "application/json"
        if mayor:
            ev = {"t": time.time(), "m": self.command, "p": self.path}
            if self.path.startswith("/build/"):
                xz = first_xz(data)
                if xz:
                    ev["rxz"] = xz
            with EVENTS.open("a") as f:
                f.write(json.dumps(ev) + "\n")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    do_GET = _fwd
    do_POST = _fwd


if __name__ == "__main__":
    ThreadingHTTPServer.daemon_threads = True
    ThreadingHTTPServer(("127.0.0.1", 8642), H).serve_forever()
