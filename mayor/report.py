#!/usr/bin/env python3
"""One-call city report for the mayor: every key number in a few hundred tokens.

Reads the main data endpoints and flattens each JSON answer into short `key=value` lines
(numbers and short strings only, long lists cut to their first items). Read-only.
usage: python3 report.py            # full report
       python3 report.py traffic    # only sections whose name contains "traffic"
"""
import os
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
_envf = HERE.parent / "mcp-server/.env"
ENV = dict(l.split("=", 1) for l in _envf.read_text().split() if "=" in l) if _envf.exists() else {}
ENV.setdefault("CS2MCP_TOKEN", os.environ.get("CS2MCP_TOKEN", ""))
HDR = {"X-CS2MCP-Token": ENV.get("CS2MCP_TOKEN", "")}  # untagged: counts as the mayor's own read

SECTIONS = [
    ("state", "/state"),
    ("overview", "/city/overview"),
    ("demand", "/city/demand"),
    ("budget", "/city/budget"),
    ("labor", "/city/labor"),
    ("services", "/city/services"),
    ("zoning", "/city/zoning"),
    ("traffic", "/city/traffic?limit=5"),
    ("problems", "/city/notifications?limit=1"),
]
SKIP_KEYS = {"note", "notes", "stalenessWarning", "entity", "version", "index", "road", "owner"}
LIST_HEAD = 5


def get(path):
    req = urllib.request.Request("http://127.0.0.1:8642" + path, headers=HDR)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def fmt(v):
    if isinstance(v, float):
        return f"{v:.1f}" if abs(v) < 1000 else f"{v:,.0f}"
    if isinstance(v, int):
        return f"{v:,}" if abs(v) >= 10000 else str(v)
    return str(v)


def flat(obj, prefix, out, depth=0):
    if isinstance(obj, dict):
        scal = [f"{k}={fmt(v)}" for k, v in obj.items()
                if k not in SKIP_KEYS and isinstance(v, (int, float, bool)) or (isinstance(v, str) and len(v) <= 40 and k not in SKIP_KEYS)]
        if scal:
            out.append((prefix or "") + " " + " ".join(scal) if prefix else " ".join(scal))
        for k, v in obj.items():
            if k in SKIP_KEYS or not isinstance(v, (dict, list)) or depth > 3:
                continue
            flat(v, f"{prefix}.{k}" if prefix else k, out, depth + 1)
    elif isinstance(obj, list):
        if obj and all(isinstance(x, (int, float)) for x in obj):
            out.append(f"{prefix} [{', '.join(fmt(x) for x in obj[:12])}{', …' if len(obj) > 12 else ''}]")
            return
        for i, x in enumerate(obj[:LIST_HEAD]):
            flat(x, f"{prefix}[{i}]", out, depth + 1)
        if len(obj) > LIST_HEAD:
            out.append(f"{prefix} … +{len(obj) - LIST_HEAD} more")


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else ""
    for name, path in SECTIONS:
        if only and only not in name:
            continue
        try:
            d = get(path)
        except Exception as e:
            print(f"## {name}: unavailable ({type(e).__name__})")
            continue
        if name == "problems":  # only the counts, not every icon
            d = {"total": d.get("total"), "byType": d.get("countsByType", {})}
        lines = []
        flat(d, "", lines)
        print(f"## {name}")
        for l in lines[:40]:
            print("  " + l.strip())


if __name__ == "__main__":
    main()
