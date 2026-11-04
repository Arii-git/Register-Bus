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
