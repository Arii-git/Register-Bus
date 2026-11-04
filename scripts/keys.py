#!/usr/bin/env python3
"""Print metric keys (and values) of a finished run that contain a substring.
usage: python3 scripts/keys.py bus_d8_r1 power"""
import json, os, pathlib, sys
FLOW = pathlib.Path(os.environ.get("ORFS_FLOW", pathlib.Path.home() / "OpenROAD-flow-scripts" / "flow"))
rid, sub = sys.argv[1], sys.argv[2].lower()
logdir = FLOW / "logs" / "sky130hd" / ("rb_" + rid) / "base"
for f in sorted(logdir.glob("*.json")):
    d = json.loads(f.read_text())
    for k, v in d.items():
        if sub in k.lower():
            print(f"{f.name:22s} {k} = {v}")
