# Flow notes

## Flow variables
- CORE_UTILIZATION = 40. Core utilisation is 40 percent: standard cell area is 40 percent of the core area. Source: scripts/variables.json.
- PLACE_DENSITY_LB_ADDON = 0.20. Target density = lb + (1 - lb) x 0.20 + 0.01. Source: scripts/util.tcl, place_density_with_lb_addon.
- Measured for bus_d8_r1 (logs/sky130hd/rb_bus_d8_r1/base/3_3_place_gp.log): lower bound lb = 0.48, placement target density = 0.594. The formula gives 0.48 + 0.52 x 0.20 + 0.01 = 0.594.

## bus_d8_r1 synthesis (runs/bus_d8_r1/synth_stat.txt)
- 641 cells in total: 168 flops, 33 mux cells, 440 others.
- Synthesis area 7829 um2. Final area 9390 um2. The 1561 um2 difference is added by placement and timing repair.

## Worst path, bus_d8_r1
- Path: addr[0] to rdata[14]. Slack 0.03 ns, MET.
- Port buffers: clkdlybuf4s50_1 on the input (0.46 ns) and the output (0.50 ns). Cause not yet checked.
- Logic between the port buffers: 1.41 ns.

## Probe runs, tagged _p4 (kept out of the sweep table)
- core_d64_r4_p4: ok, 9.8 min, 1024 flops (edfxtp_1).

## Area definition (core_d8_r1, from 6_report.json via keys.py)
- finish__design__instance__area = 7104.31 um2. It is the sum of the classes below.
- Tap cells are included: 230.2 um2.
- Fill cells are not included. The fill class is 7429.6 um2 and fills the core (14533.9 um2). It is excluded from the reported area.
- Other classes in the reported total: sequential 3843.7, multi-input combinational 1863.0, clock buffers 436.7, timing repair buffers 598.1, inverters 60.1, clock inverters 72.6.

## 64 x 4 probe (tag _p4, 4.0 ns target)

Run folders: runs/core_d64_r4_p4 and runs/bus_d64_r4_p4. Not in results/sweep.csv.
Area excludes fill cells, and includes tap cells, as defined in the README.

| Design | Area excl. fill (um^2) | Fill (um^2) | Total incl. fill (um^2) | WNS (ns) | Achievable period (ns) | Power (mW) | Runtime (min) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| core | 93253.2 | 83631.5 | 176885 | -0.240 | 4.240 | 33.2 | 9.8 |
| bus | 97678.7 | 80936.4 | 178615 | -0.242 | 4.242 | 34.1 | 11.1 |

Bus overhead at 64 x 4: +4425 um^2, +4.7% of core (excluding fill).
Both designs miss the 4.0 ns target by about 0.24 ns.

## Validation and checks (4 Nov 2026)

- Cost model validation errors on the held-back configurations: 0.5% to 5.1%.
- Largest relative residual over the 12 grid points: 7.0%, below the 10% threshold in H1.
- Power against area, Spearman rank correlation: 0.998, above the 0.9 threshold in H4.
- Bandwidth per unit area at 4 read ports is 2.5 to 2.8 times the 1-port value.

## Clock period probes (8 x 1, tags _p25 and _p60)

Run folders: runs/core_d8_r1_p25, runs/bus_d8_r1_p25, runs/core_d8_r1_p60, runs/bus_d8_r1_p60. All four finished with status ok. One run per point.

| Design | Target (ns) | Setup WNS (ns) | Meets target | Target minus WNS (ns) |
| --- | --- | --- | --- | --- |
| core | 2.5 | +0.005 | yes, barely | 2.495 |
| bus | 2.5 | +0.019 | yes, barely | 2.481 |
| core | 6.0 | +1.479 | yes | 4.521 |
| bus | 6.0 | +0.789 | yes | 5.211 |

The 2.5 ns and 6.0 ns results do not give the same design's maximum speed. A tighter target makes the flow add timing-repair buffers and choose faster cells, while a looser target lets it relax the design. So the two values are not one speed curve, and they should not be read as the maximum frequency of the design.

At 4.0 ns, the 8 x 1 designs met timing. The larger designs missed it: 32 x 4 by about 0.05 to 0.09 ns, and 64 x 4 by about 0.24 ns. The clock period decision is still open.

## Clock period probes (8 x 1, tags _p25 and _p60)

Run folders: runs/core_d8_r1_p25, runs/bus_d8_r1_p25, runs/core_d8_r1_p60, runs/bus_d8_r1_p60. All four finished with status ok. One run per point.

| Design | Target (ns) | Setup WNS (ns) | Meets target | Target minus WNS (ns) |
| --- | --- | --- | --- | --- |
| core | 2.5 | +0.005 | yes, barely | 2.495 |
| bus | 2.5 | +0.019 | yes, barely | 2.481 |
| core | 6.0 | +1.479 | yes | 4.521 |
| bus | 6.0 | +0.789 | yes | 5.211 |

The 2.5 ns and 6.0 ns results do not give the same design's maximum speed. A tighter target makes the flow add timing-repair buffers and choose faster cells, while a looser target lets it relax the design. So the two values are not one speed curve, and they should not be read as the maximum frequency of the design.

At 4.0 ns, the 8 x 1 designs met timing. The larger designs missed it: 32 x 4 by about 0.05 to 0.09 ns, and 64 x 4 by about 0.24 ns. The clock period decision is still open.
