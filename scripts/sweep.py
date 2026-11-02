#!/usr/bin/env python3
"""Generate one ORFS config per design point and run the flow.

Examples:
  python3 scripts/sweep.py --period 4.0 --only bus_d8_r1 --dry   # show, do not run
  python3 scripts/sweep.py --period 4.0 --only bus_d8_r1         # one real run
  python3 scripts/sweep.py --period 4.0                          # all 24 points
A point is skipped if its 6_report.json already exists (use --force to redo it).
"""
import argparse, json, os, pathlib, shutil, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor

REPO = pathlib.Path(__file__).resolve().parent.parent
FLOW = pathlib.Path(os.environ.get("ORFS_FLOW", pathlib.Path.home() / "OpenROAD-flow-scripts" / "flow"))
PLATFORM = "sky130hd"
TOPS = {"core": "regfile", "bus": "mmio_top"}

DEPTHS = [8, 16, 32, 64]
READS = [1, 2, 4]
UTIL = 40          # same core utilisation for every run, so areas compare fairly


def points():
    # depth first, so if time runs out you still hold complete core/bus pairs for the small sizes
    for d in DEPTHS:
        for r in READS:
            for kind in ("core", "bus"):
                yield kind, d, r, 0


TAG = ""


def run_id(kind, d, r, b):
    return f"{kind}_d{d}_r{r}" + (f"_b{b}" if b else "") + TAG


def nickname(rid):
    return "rb_" + rid        # results land in results/sky130hd/rb_<id>/base/


def write_inputs(kind, d, r, b, period):
    rid = run_id(kind, d, r, b)
    rdir = REPO / "runs" / rid
    rdir.mkdir(parents=True, exist_ok=True)
    sdc = rdir / "constraint.sdc"
    sdc.write_text(
        f"set clk_name core_clock\n"
        f"set clk_port_name clk\n"
        f"set clk_period {period}\n"
        f"set clk_io_pct 0.2\n"
        f"set clk_port [get_ports $clk_port_name]\n"
        f"create_clock -name $clk_name -period $clk_period $clk_port\n"
        f"set non_clock_inputs [lsearch -inline -all -not -exact [all_inputs] $clk_port]\n"
        f"set_input_delay  [expr $clk_period * $clk_io_pct] -clock $clk_name $non_clock_inputs\n"
        f"set_output_delay [expr $clk_period * $clk_io_pct] -clock $clk_name [all_outputs]\n"
    )
    files = [str(REPO / "rtl" / "regfile.v")]
    if kind == "bus":
        files.append(str(REPO / "rtl" / "mmio_top.v"))
    cfg = rdir / "config.mk"
    cfg.write_text(
        f"export DESIGN_NICKNAME = {nickname(rid)}\n"
        f"export DESIGN_NAME     = {TOPS[kind]}\n"
        f"export PLATFORM        = {PLATFORM}\n"
        f"export VERILOG_FILES   = {' '.join(files)}\n"
        f"export VERILOG_DEFINES = -D P_DEPTH={d} -D P_NREAD={r} -D P_BYPASS={b}\n"
        f"export SDC_FILE        = {sdc}\n"
        f"export CORE_UTILIZATION = {UTIL}\n"
        f"export PLACE_DENSITY_LB_ADDON = 0.20\n"
        f"export TNS_END_PERCENT = 100\n"
    )
    (rdir / "meta.json").write_text(json.dumps(
        dict(id=rid, kind=kind, depth=d, nread=r, bypass=b, period_ns=period, util=UTIL, tag=TAG), indent=1))
    return rid, rdir, cfg


def done(rid):
    return (FLOW / "logs" / PLATFORM / nickname(rid) / "base" / "6_report.json").exists()


def run_one(args, kind, d, r, b):
    rid, rdir, cfg = write_inputs(kind, d, r, b, args.period)
    cmd = ["make", "-C", str(FLOW), f"DESIGN_CONFIG={cfg}"]
    if args.dry:
        print("DRY", rid, " ".join(cmd))
        return rid, "dry", 0.0
    if done(rid) and not args.force:
        print("SKIP", rid, "(already finished)")
        return rid, "skipped", 0.0
    if args.force:   # wipe the old results of this point first, otherwise make may reuse them
        subprocess.call(["make", "-C", str(FLOW), f"DESIGN_CONFIG={cfg}", "clean_all"],
                        stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    t0 = time.time()
    with open(rdir / "make.log", "w") as log:
        rc = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)
    dt = time.time() - t0
    status = "ok" if rc == 0 and done(rid) else f"FAILED rc={rc}"
    meta = json.loads((rdir / "meta.json").read_text())
    meta.update(runtime_s=round(dt, 1), status=status)
    (rdir / "meta.json").write_text(json.dumps(meta, indent=1))
    print(f"{status:12s} {rid:18s} {dt/60:6.1f} min", flush=True)
    return rid, status, dt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=float, required=True, help="target clock period in ns")
    ap.add_argument("--only", help="substring filter on the run id, e.g. bus_d8_r1")
    ap.add_argument("--bypass", type=int, default=0)
    ap.add_argument("--jobs", type=int, default=1)
    ap.add_argument("--tag", default="", help="suffix for probe runs, e.g. _p3 (kept out of sweep.csv)")
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--extra", nargs="*", default=[],
                    help="extra points as kind:depth:nread, e.g. bus:128:2 core:16:3")
    args = ap.parse_args()
    global TAG
    TAG = args.tag

    if not args.dry and not (shutil.which("openroad") and shutil.which("yosys")):
        sys.exit("openroad/yosys not on PATH. Run this through rf.")
    if not (FLOW / "Makefile").exists():
        sys.exit(f"ORFS flow dir not found: {FLOW}  (set ORFS_FLOW=/path/to/flow)")

    todo = [(k, d, r, args.bypass) for k, d, r, _ in points()]
    for e in args.extra:
        k, d, r = e.split(":")
        todo.append((k, int(d), int(r), args.bypass))
    if args.only:
        todo = [t for t in todo if args.only in run_id(*t)]
    print(f"{len(todo)} runs, period {args.period} ns, jobs {args.jobs}")
    with ThreadPoolExecutor(max_workers=args.jobs) as ex:
        results = list(ex.map(lambda t: run_one(args, *t), todo))
    bad = [r for r in results if r[1].startswith("FAILED")]
    print(f"finished. failures: {len(bad)}", [r[0] for r in bad])


if __name__ == "__main__":
    main()
