# Synthesis results

Yosys synthesis inside OpenROAD-flow-scripts, sky130hd, 4.0 ns target. Synthesis numbers come from `runs/<id>/synth_stat.txt` (end of the Yosys step). Final area comes from `results/sweep.csv` (`finish__design__instance__area`, tap cells counted, fill cells not). Probe areas come from `runs/<id>_p4/6_report.json`.

- **Flops** count `dfxtp` and `edfxtp` cells. Expected: DEPTH × 16 for the core, DEPTH × 16 + 40 for the bus (15 CTRL bits, 8 counter bits, 1 sticky error bit, 16 INPUT bits).
- **Mux cells** count `mux2`, `mux2i` and `mux4` cells only. Yosys also builds part of each read mux from AOI and OAI gates, so this column is a lower bound on the read logic, not a full count of it.
- **Sequential share** is the part of the synthesis area used by flops, as Yosys reports it.
- **Growth after synthesis** is final area ÷ synthesis area − 1. It covers buffers and resizing added by placement, CTS and timing repair, plus tap cells.

## All runs

| Run | Design | Entries x ports | Cells | Flops (measured / expected) | Mux cells | Synthesis area (µm²) | Sequential share | Final area (µm²) | Growth after synthesis |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| core_d8_r1 | core | 8 x 1 | 373 | 128 / 128 | 48 | 5,944 | 64.7% | 7,104 | +19.5% |
| core_d8_r2 | core | 8 x 2 | 430 | 128 / 128 | 96 | 6,999 | 54.9% | 8,483 | +21.2% |
| core_d8_r4 | core | 8 x 4 | 544 | 128 / 128 | 192 | 9,090 | 42.3% | 10,894 | +19.8% |
| core_d16_r1 | core | 16 x 1 | 722 | 256 / 256 | 64 | 11,561 | 66.5% | 13,256 | +14.7% |
| core_d16_r2 | core | 16 x 2 | 859 | 256 / 256 | 128 | 13,389 | 57.4% | 15,852 | +18.4% |
| core_d16_r3 | core | 16 x 3 (validation) | 996 | 256 / 256 | 192 | 15,242 | 50.4% | 18,054 | +18.4% |
| core_d16_r4 | core | 16 x 4 | 1133 | 256 / 256 | 256 | 17,094 | 45.0% | 20,443 | +19.6% |
| core_d32_r1 | core | 32 x 1 | 1757 | 512 / 512 | 256 | 23,878 | 64.4% | 27,828 | +16.5% |
| core_d32_r2 | core | 32 x 2 | 2326 | 512 / 512 | 512 | 28,300 | 54.3% | 34,377 | +21.5% |
| core_d32_r4 | core | 32 x 4 | 3464 | 512 / 512 | 1024 | 37,521 | 41.0% | 43,901 | +17.0% |
| core_d64_r4_p4 | core | 64 x 4 (probe) | 4790 | 1024 / 1024 | 1342 | 71,464 | 43.0% | 93,253 | +30.5% |
| core_d128_r2 | core | 128 x 2 (validation) | 6439 | 2048 / 2048 | 1376 | 109,111 | 56.4% | 130,837 | +19.9% |
| bus_d8_r1 | bus | 8 x 1 | 641 | 168 / 168 | 33 | 7,829 | 59.3% | 9,390 | +19.9% |
| bus_d8_r2 | bus | 8 x 2 | 687 | 168 / 168 | 83 | 8,705 | 53.4% | 10,540 | +21.1% |
| bus_d8_r4 | bus | 8 x 4 | 866 | 168 / 168 | 163 | 10,794 | 43.0% | 13,221 | +22.5% |
| bus_d16_r1 | bus | 16 x 1 | 939 | 296 / 296 | 82 | 13,684 | 62.0% | 15,940 | +16.5% |
| bus_d16_r2 | bus | 16 x 2 | 1087 | 296 / 296 | 171 | 15,527 | 54.7% | 18,204 | +17.2% |
| bus_d16_r3 | bus | 16 x 3 (validation) | 1219 | 296 / 296 | 265 | 17,450 | 48.6% | 20,739 | +18.8% |
| bus_d16_r4 | bus | 16 x 4 | 1390 | 296 / 296 | 380 | 19,683 | 43.1% | 23,419 | +19.0% |
| bus_d32_r1 | bus | 32 x 1 | 1910 | 552 / 552 | 257 | 25,616 | 63.1% | 31,871 | +24.4% |
| bus_d32_r2 | bus | 32 x 2 | 2182 | 552 / 552 | 433 | 29,538 | 54.8% | 37,244 | +26.1% |
| bus_d32_r4 | bus | 32 x 4 | 2794 | 552 / 552 | 755 | 37,507 | 43.1% | 48,172 | +28.4% |
| bus_d64_r4_p4 | bus | 64 x 4 (probe) | 5052 | 1064 / 1064 | 1109 | 71,992 | 43.8% | 97,679 | +35.7% |
| bus_d128_r2 | bus | 128 x 2 (validation) | 8045 | 2088 / 2088 | 1101 | 111,349 | 56.0% | 144,161 | +29.5% |

## Checks

- The flop count matches the formula on all 24 runs. This shows the size macros (`P_DEPTH`, `P_NREAD`) reached Yosys on every run.
- Flops take 41% to 66% of the synthesis area. Their share falls as read ports are added, because each port adds a mux tree but no storage.
- Area grows by 15% to 36% between synthesis and the end of the flow. The largest growth is on the 64 × 4 probes (31% and 36%) and on the bus at 32 entries and above (24% to 30%). The core at 32 entries stays at 17% to 22%.

## Bus overhead: synthesis against end of flow

Bus minus core, as µm² and as a share of the core.

| Entries × ports | Overhead after synthesis | Overhead at end of flow | Extra cells after synthesis |
| --- | --- | --- | --- |
| 8 × 1 | 1,884 (31.7%) | 2,286 (32.2%) | 268 |
| 8 × 2 | 1,705 (24.4%) | 2,057 (24.2%) | 257 |
| 8 × 4 | 1,704 (18.7%) | 2,327 (21.4%) | 322 |
| 16 × 1 | 2,123 (18.4%) | 2,684 (20.2%) | 217 |
| 16 × 2 | 2,138 (16.0%) | 2,352 (14.8%) | 228 |
| 16 × 3 | 2,208 (14.5%) | 2,685 (14.9%) | 223 |
| 16 × 4 | 2,589 (15.1%) | 2,975 (14.6%) | 257 |
| 32 × 1 | 1,738 (7.3%) | 4,043 (14.5%) | 153 |
| 32 × 2 | 1,239 (4.4%) | 2,868 (8.3%) | −144 |
| 32 × 4 | −14 (0.0%) | 4,272 (9.7%) | −670 |
| 64 × 4 (probe) | 528 (0.7%) | 4,426 (4.7%) | 262 |
| 128 × 2 | 2,238 (2.1%) | 13,324 (10.2%) | 1,606 |

Up to 16 entries, the two columns agree within about 3 points, so most of the overhead is logic Yosys builds. From 32 entries on, most of the end-of-flow overhead appears after synthesis. At 32 × 4 the bus design is no bigger than the core after synthesis (Yosys found a smaller mapping with 670 fewer cells), yet ends 4,272 µm² bigger. This is the likely reason the 32 × 1 overhead is larger than the 32 × 2 overhead in the main results. It points to placement and timing repair, not the bus logic itself, as the source of the overhead at large sizes. That reading is my interpretation. It has not been checked against the per-stage reports yet.

## Schematics

| File | What it shows |
| --- | --- |
| `docs/figures/synth_rtl_mmio_top_8x1.png` | Yosys RTL-level view of `mmio_top` at 8 × 1: address decode, write enables, CTRL, STATUS and INPUT flops, response mux, and the register file as one block (`u_rf`) |
| `docs/figures/synth_gate_core_8x1_rdata0.png` | Gate-level sky130hd cells driving `rdata[0]` in the core 8 × 1: 8 `edfxtp_1` flops (flop with enable, one per entry), two `mux4` cells and one `mux2`. This is one bit of the read mux; the other 15 bits repeat it |
| `docs/figures/synth_gate_bus_8x1_err.png` | Gate-level cells driving `err` in the bus 8 × 1. A half adder's carry gives addr[1] AND addr[0] (offset 3), two NOR gates decode the region bits addr[4:3], and a final NOR3 with an inverted input applies `sel` |

The gate-level views come from the synthesised netlist `results/sky130hd/rb_<design>_d8_r1/base/1_2_yosys.v`, cut to the cells feeding one output and stopping at the flops. The RTL view was drawn with Yosys 0.33 from the RTL in `rtl/`; the flow itself uses Yosys 0.68, so a redraw inside `rf` may place boxes differently.

### Redraw inside the container

Not yet tested on my machine. Run from `~/Register-Bus` on the host prompt. Needs Graphviz `dot` on the host (`sudo apt install graphviz`) to turn the `.dot` files into PNG.

```bash
rf yosys -p "read_verilog -DP_DEPTH=8 -DP_NREAD=1 rtl/regfile.v rtl/mmio_top.v; hierarchy -top mmio_top; proc; opt -full; opt_clean -purge; show -format dot -prefix docs/figures/synth_rtl_mmio_top_8x1 -width -stretch mmio_top"
LIB=/home/aru/OpenROAD-flow-scripts/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
NL=/home/aru/OpenROAD-flow-scripts/flow/results/sky130hd/rb_core_d8_r1/base/1_2_yosys.v
rf yosys -p "read_liberty -lib $LIB; read_verilog $NL; hierarchy -top regfile; splitnets -ports; select -set c w:rdata[0] %ci*:-sky130_fd_sc_hd__edfxtp_1[D,DE,CLK]; select -set c @c %ci1; show -format dot -prefix docs/figures/synth_gate_core_8x1_rdata0 -width @c"
dot -Tpng -Gdpi=130 docs/figures/synth_gate_core_8x1_rdata0.dot -o docs/figures/synth_gate_core_8x1_rdata0.png
```
