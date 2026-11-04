#!/usr/bin/env python3
"""Collect every finished run into results/sweep.csv.
usage: python3 scripts/parse.py          (grid runs only)
       python3 scripts/parse.py --all    (also the tagged probe runs)"""
import csv, json, os, pathlib, re, sys

REPO = pathlib.Path(__file__).resolve().parent.parent
FLOW = pathlib.Path(os.environ.get("ORFS_FLOW", pathlib.Path.home() / "OpenROAD-flow-scripts" / "flow"))
PLAT = "sky130hd"

KEY_AREA = "finish__design__instance__area"
KEY_WS = "finish__timing__setup__ws"
KEY_POWER = re.compile(r"^finish__power__total$")

FLOP = re.compile(r"__(dfxtp|dfrtp|dfstp|dfbbp|edfxtp|sdfxtp|dlxtp)")
MUX = re.compile(r"__mux[2-4]")


def load_metrics(rid):
    d = FLOW / "logs" / PLAT / ("rb_" + rid) / "base"
    f = d / "6_report.json"
    if not f.exists():
        return None
    return json.loads(f.read_text())

def synth_counts(rid):
    f = FLOW / "reports" / PLAT / ("rb_" + rid) / "base" / "synth_stat.txt"
    counts = {}
    if not f.exists():
        return counts
    for line in f.read_text().splitlines():
        m = re.search(r"(sky130_fd_sc_hd__\w+)", line)
        if not m:
            continue
        nums = re.findall(r"(?<![\w.])(\d+)(?![\w.])", line.replace(m.group(1), " "))
        if nums:
            counts[m.group(1)] = int(nums[0])      # first integer on the line = cell count
    return counts


def main():
    rows, problems = [], []
    for meta_f in sorted((REPO / "runs").glob("*/meta.json")):
        meta = json.loads(meta_f.read_text())
        rid = meta["id"]
        if meta.get("tag") and "--all" not in sys.argv:
            continue                      # probe runs (period search) stay out of the sweep table
        m = load_metrics(rid)
        if m is None:
            problems.append((rid, "no 6_report.json"))
            continue
        if KEY_AREA not in m or KEY_WS not in m:
            problems.append((rid, "area or slack key missing, run keys.py"))
            continue
        pw = next((k for k in m if KEY_POWER.match(k)), None)
        cells = synth_counts(rid)
        n_flop = sum(v for k, v in cells.items() if FLOP.search(k))
        n_mux = sum(v for k, v in cells.items() if MUX.search(k))
        T = float(meta["period_ns"])
        ws = float(m[KEY_WS])
        rows.append(dict(
            id=rid, kind=meta["kind"], depth=meta["depth"], nread=meta["nread"],
            bypass=meta["bypass"], period_target_ns=T,
            area_um2=float(m[KEY_AREA]), wns_ns=ws, period_est_ns=round(T - ws, 4),
            power_mw=(float(m[pw]) * 1e3 if pw else float("nan")),
            n_flops=n_flop, n_mux=n_mux, n_cells=sum(cells.values()),
            runtime_s=meta.get("runtime_s", ""),
        ))
    if not rows:
        sys.exit(f"no finished runs found. problems: {problems}")
    out = REPO / "results" / "sweep.csv"
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: (r["kind"], r["depth"], r["nread"])))
    print(f"wrote {out} with {len(rows)} rows; problems: {problems}")
    if any(r["n_flops"] == 0 for r in rows):
        print("WARNING: flop count is 0 for some rows, fix the regex in synth_counts() after reading synth_stat.txt")


if __name__ == "__main__":
    main()
