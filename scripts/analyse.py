#!/usr/bin/env python3
"""Plots, interface overhead, bandwidth metrics and the area cost model.
usage: python3 scripts/analyse.py
Reads results/sweep.csv, writes results/plots/*.png and results/summary.md
"""
import pathlib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

REPO = pathlib.Path(__file__).resolve().parent.parent
OUT = REPO / "results"
PLOTS = OUT / "plots"
PLOTS.mkdir(parents=True, exist_ok=True)
W = 16

all_df = pd.read_csv(OUT / "sweep.csv")
byp = all_df[all_df.bypass == 1].copy()      # stretch S1 rows, kept out of the main plots
df = all_df[all_df.bypass == 0].copy()
GRID_D, GRID_R = [8, 16, 32, 64], [1, 2, 4]
df["on_grid"] = df.depth.isin(GRID_D) & df.nread.isin(GRID_R)
df["bits"] = df.depth * W
# peak read bandwidth if every read port delivers one word per cycle at the estimated period
df["bw_gbps"] = df.nread * W / df.period_est_ns
df["bw_per_kum2"] = df.bw_gbps / (df.area_um2 / 1000.0)
df["pj_per_bit"] = df.power_mw / df.bw_gbps          # relative number, default switching activity

core = df[(df.kind == "core") & df.on_grid]
bus = df[(df.kind == "bus") & df.on_grid]
lines = []


def lineplot(ax, d, col, title, ylabel):
    for r, g in d.groupby("nread"):
        g = g.sort_values("depth")
        ax.plot(g.depth, g[col], marker="o", label=f"{r} read port(s)")
    ax.set_xscale("log", base=2)
    ax.set_xticks(GRID_D)
    ax.set_xticklabels(GRID_D)
    ax.set_xlabel("entries (16 bits each)")
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(alpha=0.3)
    ax.legend()


def two_panel(col, ylabel, fname):
    fig, axs = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    lineplot(axs[0], core, col, "core only (regfile)", ylabel)
    lineplot(axs[1], bus, col, "with bus interface (mmio_top)", ylabel)
    fig.tight_layout()
    fig.savefig(PLOTS / fname, dpi=160)
    plt.close(fig)


two_panel("area_um2", "cell area (um^2)", "1_area_vs_entries.png")
two_panel("period_est_ns", "target period minus WNS (ns)", "2_period_vs_entries.png")
two_panel("power_mw", "total power (mW, default activity)", "3_power_vs_entries.png")

# ---- interface overhead ----
m = core.merge(bus, on=["depth", "nread"], suffixes=("_core", "_bus"))
m["ovh_um2"] = m.area_um2_bus - m.area_um2_core
m["ovh_pct"] = 100 * m.ovh_um2 / m.area_um2_core
m["dperiod_ns"] = m.period_est_ns_bus - m.period_est_ns_core
fig, axs = plt.subplots(1, 2, figsize=(10, 4))
for r, g in m.groupby("nread"):
    g = g.sort_values("depth")
    axs[0].plot(g.depth, g.ovh_um2, marker="o", label=f"{r} read port(s)")
    axs[1].plot(g.depth, g.ovh_pct, marker="o", label=f"{r} read port(s)")
for ax, yl, t in zip(axs, ["extra area (um^2)", "extra area (% of core)"],
                     ["Bus interface cost, absolute", "Bus interface cost, relative"]):
    ax.set_xscale("log", base=2); ax.set_xticks(GRID_D); ax.set_xticklabels(GRID_D)
    ax.set_xlabel("entries"); ax.set_ylabel(yl); ax.set_title(t); ax.grid(alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(PLOTS / "4_interface_overhead.png", dpi=160); plt.close(fig)

# ---- bandwidth per area (the memory-movement view) ----
fig, ax = plt.subplots(figsize=(6, 4.2))
for kind, mk in (("core", "o"), ("bus", "s")):
    d = df[(df.kind == kind) & df.on_grid]
    ax.scatter(d.area_um2 / 1000, d.bw_gbps, marker=mk, label=kind)
    for _, r in d.iterrows():
        ax.annotate(f"{int(r.depth)}x{int(r.nread)}", (r.area_um2 / 1000, r.bw_gbps), fontsize=6)
ax.set_xlabel("cell area (1000 um^2)"); ax.set_ylabel("peak read bandwidth (Gbit/s)")
ax.set_title("Bandwidth bought per area (label = entries x read ports)"); ax.grid(alpha=0.3); ax.legend()
fig.tight_layout(); fig.savefig(PLOTS / "5_bandwidth_vs_area.png", dpi=160); plt.close(fig)

# ---- cell breakdown ----
pick = bus[(bus.nread == 4) & bus.depth.isin([8, 32, 64])].sort_values("depth")
fig, ax = plt.subplots(figsize=(6, 4))
other = pick.n_cells - pick.n_flops - pick.n_mux
x = np.arange(len(pick))
ax.bar(x, pick.n_flops, label="flops")
ax.bar(x, pick.n_mux, bottom=pick.n_flops, label="mux cells")
ax.bar(x, other, bottom=pick.n_flops + pick.n_mux, label="other")
ax.set_xticks(x); ax.set_xticklabels([f"{d} x 4" for d in pick.depth])
ax.set_ylabel("cells after synthesis"); ax.set_title("What the cells are (bus design, 4 read ports)")
ax.legend(); fig.tight_layout(); fig.savefig(PLOTS / "6_cell_breakdown.png", dpi=160); plt.close(fig)

# ---- area cost model: area = c0 + c1*D + c2*R*D (W fixed at 16) ----
def design(d):
    return np.column_stack([np.ones(len(d)), d.depth.values, (d.depth * d.nread).values])


def fit(d):
    c, *_ = np.linalg.lstsq(design(d), d.area_um2.values, rcond=None)
    return c


def pred(c, d):
    return design(d) @ c


lines.append("## Area cost model: area = c0 + c1*entries + c2*(read ports * entries)\n")
for kind in ("core", "bus"):
    g = df[(df.kind == kind) & df.on_grid]
    c = fit(g)
    resid = g.area_um2.values - pred(c, g)
    r2 = 1 - (resid ** 2).sum() / ((g.area_um2 - g.area_um2.mean()) ** 2).sum()
    lines.append(f"- {kind}: c0={c[0]:.0f}, c1={c[1]:.2f}, c2={c[2]:.2f} um^2, R^2={r2:.4f}, "
                 f"max residual {100*np.abs(resid/g.area_um2.values).max():.1f}%")
    tr = g[g.depth <= 32]
    te = g[g.depth == 64]
    if len(tr) >= 3 and len(te):
        c_tr = fit(tr)
        err = 100 * (pred(c_tr, te) - te.area_um2.values) / te.area_um2.values
        lines.append(f"  - trained on entries <= 32, predicted entries = 64: errors "
                     + ", ".join(f"{e:+.1f}%" for e in err))
    extra = df[(df.kind == kind) & ~df.on_grid]
    if len(extra):
        p = pred(c, extra)
        for (_, r), pp in zip(extra.iterrows(), p):
            lines.append(f"  - never-seen point {int(r.depth)} entries x {int(r.nread)} ports: "
                         f"predicted {pp:.0f}, measured {r.area_um2:.0f}, "
                         f"error {100*(pp-r.area_um2)/r.area_um2:+.1f}%")

lines.append("\n## Interface overhead (bus minus core), area\n")
for _, r in m.sort_values(["nread", "depth"]).iterrows():
    lines.append(f"- {int(r.depth)} x {int(r.nread)}: +{r.ovh_um2:.0f} um^2 ({r.ovh_pct:.1f}%), "
                 f"period estimate change {r.dperiod_ns:+.2f} ns")
if len(byp):
    lines.append("\n## Stretch S1: cost of the same-cycle bypass (BYPASS=1 vs 0)\n")
    mm = byp.merge(df, on=["kind", "depth", "nread"], suffixes=("_b1", "_b0"))
    for _, r in mm.sort_values(["kind", "nread", "depth"]).iterrows():
        lines.append(f"- {r.kind} {int(r.depth)} x {int(r.nread)}: area {100*(r.area_um2_b1-r.area_um2_b0)/r.area_um2_b0:+.1f}%, "
                     f"period estimate {r.period_est_ns_b1-r.period_est_ns_b0:+.2f} ns")
(OUT / "summary.md").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
print("plots in", PLOTS)
