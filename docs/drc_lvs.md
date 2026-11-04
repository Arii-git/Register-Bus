# Physical checks: DRC, LVS and detailed routing (8 × 1)

This file records the physical-design checks that have been run on the two 8 × 1 designs. It is the evidence trail for the statement "DRC clean, LVS match" in the README.

## Scope

| Item | Value |
| --- | --- |
| Designs | `regfile` (core only) and `mmio_top` (bus), from the same RTL |
| Parameters | `DEPTH = 8`, `NREAD = 1`, `BYPASS = 0`, `WIDTH = 16` |
| Platform | sky130hd (OpenROAD-flow-scripts) |
| Clock target | 4.0 ns, with 20% input and output delay |
| Run folders | `runs/core_d8_r1/`, `runs/bus_d8_r1/` |
| Flow results | `~/OpenROAD-flow-scripts/flow/results/sky130hd/rb_<design>_d8_r1/base/` |

Only these two points have been checked. Other sweep points have not been through DRC or LVS.

## Results

| Check | Core (`rb_core_d8_r1`) | Bus (`rb_bus_d8_r1`) | Evidence file |
| --- | --- | --- | --- |
| Detailed routing violations at end of routing | 0 | 0 | `logs/sky130hd/rb_<design>_d8_r1/base/5_2_route.log` |
| DRC violation count | 0 | 0 | `reports/sky130hd/rb_<design>_d8_r1/base/6_drc_count.rpt` |
| DRC marker database | written, no markers | written, no markers | `reports/sky130hd/rb_<design>_d8_r1/base/6_drc.lyrdb` |
| LVS | Netlists match | Netlists match | `logs/sky130hd/rb_<design>_d8_r1/base/6_lvs.log` |

The LVS log line is `INFO : Congratulations! Netlists match.` for both designs.

### Routing violations per iteration

The detailed router reduces its violation count over successive iterations.

| Design | Iteration counts | Final |
| --- | --- | --- |
| Core | 308, 113, 91, 13, 7, 2 | 0 |
| Bus | 418, 241, 223, 68 | 0 |

## Checks used

- DRC: the KLayout deck `platforms/sky130hd/drc/sky130hd.lydrc`, run by the flow's `drc` target.
- LVS: the KLayout deck `platforms/sky130hd/lvs/sky130hd.lylvs`, run by the flow's `lvs` target.
- Commands run:

```bash
rf make -C ~/OpenROAD-flow-scripts/flow DESIGN_CONFIG=$HOME/Register-Bus/runs/<design>_d8_r1/config.mk drc
rf make -C ~/OpenROAD-flow-scripts/flow DESIGN_CONFIG=$HOME/Register-Bus/runs/<design>_d8_r1/config.mk lvs
```

## What these checks do not establish

- They cover only 8 × 1 for both designs.
- They use the flow's default deck and settings. This is not a foundry signoff.
- DRC clean and LVS match say nothing about timing or power.

## Reproduce

```bash
cd ~/OpenROAD-flow-scripts/flow
cat reports/sky130hd/rb_core_d8_r1/base/6_drc_count.rpt
cat reports/sky130hd/rb_bus_d8_r1/base/6_drc_count.rpt
grep -h "Congratulations\|mismatch" logs/sky130hd/rb_core_d8_r1/base/6_lvs.log logs/sky130hd/rb_bus_d8_r1/base/6_lvs.log
```

Expected: both DRC counts are `0`, and both LVS lines show `Congratulations! Netlists match.`

## Layouts

- `docs/layouts/core_8x1_layout.png`
- `docs/layouts/bus_8x1_layout.png`

Both were captured from the OpenROAD GUI on the routed `6_final` database.
