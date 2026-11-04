# Results, 4 Nov 2026

All runs use the 4.0 ns placeholder period, one run per point, sky130hd, default switching activity for power.
Numbers come from runs/*/6_report.json through parse.py into results/sweep.csv, and from analyse.py into results/summary.md.

## What was run
- Grid: 8, 16 and 32 entries at 1, 2 and 4 read ports, core and bus (18 points).
- Validation: 128 entries x 2 ports and 16 entries x 3 ports, core and bus (4 points).
- Probe: 64 entries x 4 ports, core and bus, tagged _p4 and kept out of the table.
- Not run: 64 entries at 1 and 2 ports. No period choice. No DRC or LVS.

## Cost model (fit on the 18 grid points, entries 8 to 32)
- Core: A = -598 + 739.72 D + 161.36 R D. R^2 0.997, largest residual 7.0%.
- Bus: A = 1096 + 789.68 D + 167.01 R D. R^2 0.998, largest residual 6.8%.

Validation error = (predicted - measured) / measured.

| Run | Type | Core | Bus |
|---|---|---|---|
| 16 x 3 | interpolation | +5.1% | +4.9% |
| 128 x 2 | extrapolation | +3.5% | +0.5% |

## Interface overhead (bus minus core, um2 and % of core)
| Entries | 1 port | 2 ports | 4 ports |
|---|---|---|---|
| 8 | 2286 (32.2%) | 2057 (24.2%) | 2327 (21.4%) |
| 16 | 2684 (20.2%) | 2352 (14.8%) | 2975 (14.6%) |
| 32 | 4043 (14.5%) | 2868 (8.3%) | 4272 (9.7%) |
| 64 (probe) | not run | not run | 4426 (4.7%) |
| 16 x 3 (validation) | 2685 (14.9%) at 3 ports | | |
| 128 x 2 (validation) | 13324 (10.2%) at 2 ports | | |

## Hypotheses
- H1 (area model fits): supported. Largest grid residual 7.0%. Validation errors 0.5% to 5.1%.
- H2 (overhead % falls, absolute stays flat): percentage part supported at every port count. Absolute part disproved: overhead grows from about 2,000 to 4,300 um2. The 64 x 4 prediction of under 4% was missed (4.7%).
- H3 (worst path addr to rdata): supported at 8 x 1 and 64 x 4. Both have addr[0] to rdata as the worst path.
- H4 (power ranks like area, Spearman at least 0.95): supported. Spearman 0.998.
- H5 (bandwidth per area at 4 ports is 1.5 to 2.5 times that at 1 port): direction supported, size missed. It rises at every depth, by 2.5 to 2.8 times.

## Timing at 4.0 ns (final WNS)
- core 8 x 1: +0.57 ns. bus 8 x 1: +0.03 ns.
- bus 64 x 4: -0.24 ns. core 128 x 2: -0.65 ns. bus 128 x 2: -0.78 ns.
Negative slack on the largest points means the period has to be chosen with those in mind. The period decision is still open.

## Limitations
- One run per point, one period, one platform.
- Power is relative (default activity).
- Timing is not closed at 128 x 2 or 64 x 4.

## Plots
- 
1. **1_area_vs_entries.png:** Cell area grows with depth and read ports, from about 7,000 µm² at 8 × 1 to about 44,000 µm² at 32 × 4 for the core. The bus interface adds area at every point, with the largest gap at 32 entries.

2. **2_period_vs_entries.png:** The core's achievable period rises with depth, from about 3.43 ns at 8 entries to about 4.09 ns at 32 × 4. With the bus, the period dips at 16 entries and recovers at 32.

3. **3_power_vs_entries.png:** Total power rises with depth and read ports, reaching about 15.5 mW for the core and about 16.5 mW for the bus at 32 × 4. The bus adds little power at 8 entries and more at 32.

4. **4_interface_overhead.png:** Absolute bus overhead is about 2,000 to 4,300 µm², growing with depth and ports. As a share of the core, it falls from about 32% at 8 × 1 to about 8 to 10% at 32 entries.

5. **5_bandwidth_vs_area.png:** Peak read bandwidth per unit area is highest at small depths with more ports, with 8 × 4 reaching about 18.6 Gbit/s at 11,000 µm² for the core. Core and bus points at the same depth and ports cluster together, so the bus costs area without changing bandwidth.

6. **6_cell_breakdown.png:** For the bus at 4 read ports, the design is about 860 cells at 8 entries and about 2,800 at 32, split into flops, mux cells and other cells. Only 8 × 4 and 32 × 4 are shown; 64 × 4 is to be added.
