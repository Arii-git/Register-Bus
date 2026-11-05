# Clock period: 4.0 ns for every run

Decided 5 Nov 2026. Every point in the sweep (grid, validation and probes) uses the same target, so area, timing and power are compared at one clock.

## Order of events

1. The first runs on 31 Oct to 4 Nov used 4.0 ns as a placeholder (`PERIOD ?= 4.0` in the root `Makefile`).
2. Probes on 4 Nov: 8 × 1 at 2.5 ns and 6.0 ns (tags `_p25`, `_p60`), and 64 × 4 at 4.0 ns (tag `_p4`). Probe runs are kept out of `results/sweep.csv`.
3. 4.5 ns and 5.0 ns were considered on 4 Nov but not probed.
4. 5 Nov: the placeholder was kept as the final value. The 18 grid points and 4 validation points already at 4.0 ns did not need to be rerun.

## Probe results

Setup WNS is the final worst setup slack from `6_report.json` (`finish__timing__setup__ws`). Slack as a share of the period is WNS ÷ target.

| Design | Size | Target (ns) | Setup WNS (ns) | Slack as share of period | Flow finished |
| --- | --- | --- | --- | --- | --- |
| core | 8 × 1 | 2.5 | +0.005 | 0.2% | yes |
| bus | 8 × 1 | 2.5 | +0.019 | 0.8% | yes |
| core | 8 × 1 | 4.0 | +0.575 | 14.4% | yes |
| bus | 8 × 1 | 4.0 | +0.031 | 0.8% | yes |
| core | 8 × 1 | 6.0 | +1.479 | 24.7% | yes |
| bus | 8 × 1 | 6.0 | +0.789 | 13.2% | yes |
| core | 64 × 4 | 4.0 | −0.240 | −6.0% | yes |
| bus | 64 × 4 | 4.0 | −0.242 | −6.1% | yes |

## Decision rule (set in the plan before the probes)

Pick the period where `core_d8_r1` has slack between 10% and 30% of the period, and `bus_d64_r4` still completes the flow. A small negative slack on the biggest design is acceptable and is reported as a result. If the biggest design misses by more than half the period, take the next larger period.

| Target | core 8 × 1 slack in 10 to 30%? | bus 64 × 4 completes? | 64 × 4 miss under half the period? | Passes the rule |
| --- | --- | --- | --- | --- |
| 2.5 ns | no (0.2%) | not probed | not probed | no |
| 4.0 ns | yes (14.4%) | yes | yes (0.24 ns against a 2.0 ns limit) | yes |
| 6.0 ns | yes (24.7%) | not probed | not probed | not tested |

## Why 4.0 ns and not 6.0 ns

- 4.0 ns is the tightest target tested that passes the rule.
- The study measures what the bus interface costs, timing included. At 4.0 ns the bus read path (addr, decode, read mux, response mux, rdata) uses almost all of the cycle at 8 × 1 (slack +0.031 ns against +0.575 ns for the core). At 6.0 ns the same path has 0.79 ns of slack, and the timing cost of the bus is much harder to see.
- All 22 points in `results/sweep.csv` were already run at 4.0 ns, so no rerun was needed.

## What 4.0 ns costs

Setup misses at 4.0 ns, from `results/sweep.csv` and the probe folders:

| Points | Setup WNS (ns) |
| --- | --- |
| bus 8 × 2 | −0.066 |
| core and bus at 32 entries, 1, 2 and 4 ports | −0.020 to −0.094 |
| core and bus 64 × 4 (probe) | −0.240, −0.242 |
| core 128 × 2, bus 128 × 2 (validation) | −0.649, −0.782 |
| core and bus 64 × 1, 64 × 2 (run 5 Nov) | *fill in from `results/sweep.csv` after `make parse`* |

On every run: hold slack is positive, and there are 0 max slew, 0 max capacitance and 0 max fanout violations.

The 32-entry misses are all under 2.4% of the period. The bus 8 × 2 miss is odd, because 8 × 1 (+0.031 ns) and 8 × 4 (+0.018 ns) both pass. There is one run per point, so run-to-run noise has not been measured yet; a repeat of `bus_d8_r2` would show whether this miss is noise.

## How timing is reported because of this

- `period_est_ns = target − WNS` is used to compare designs. It is not the maximum clock frequency.
- The 8 × 1 probes show why: at 2.5 ns both designs still meet timing, because a tighter target makes the flow upsize cells and add repair buffers. The design changes with the target, so the 2.5, 4.0 and 6.0 ns results are not points on one speed curve.
- Area depends on the target for the same reason. All area figures in this study are at 4.0 ns.
- Points with negative slack are kept in the results and marked. They are not rerun at a looser period, because that would break the "same clock for every run" rule.
