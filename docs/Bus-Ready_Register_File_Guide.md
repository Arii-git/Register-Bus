# Bus-Ready Register File: 19-Day OpenROAD Build Guide (27 Oct to 14 Nov 2026)

Oct 27, 2026 · @Arihant Chordia

## Status on 31 Oct (read this first)

Day 1 is done. The tools now run inside Docker, so a few commands further down are different from what this guide says.

- Put `rf` in front of every tool command, for example `rf make test`, `rf python3 scripts/sweep.py` and `rf klayout file.gds`. Git, editing and `ls` stay plain. Ignore the `source env.sh` and venv lines.
- Repo: local folder `~/Register-Bus`, GitHub repo `Arii-git/Register-Bus` (private, pushed over SSH). Commit from your own terminal. The local folder was renamed from regbus to Register-Bus, so read any regbus path further down as Register-Bus.
- `COMMANDS.md` (your downloaded copy, kept outside the repo) has the open, commit and restart commands.
- Tool versions and the pinned image are in `log/versions.md`. Metric keys are in `log/keys.md`: `finish__design__instance__area`, `finish__timing__setup__ws`, `finish__power__total`.
- `docker/` in the repo holds the Dockerfile and the `rf` script.

**Catch-up plan** (proposed, free all days, still ends Sat 14 Nov)

| Date | Do |
| --- | --- |
| Sun 1 Nov | D2 and D3 |
| Mon 2 Nov | D4, then start D5 |
| Tue 3 Nov | Finish D5, start the D6 runs in the background |
| Wed 4 Nov | Close D6, do D7 (period choice), launch the sweep (D8) |
| Thu 5 Nov | Finish the sweep (D9). One day behind the original plan, and the buffer on Mon 9 Nov covers it. D10 onwards as written. |

## The project in one page

**Bus-Ready Register File** is a 19-day study of what a small memory block really costs once it has to talk to a bus. You build a parameterised register file, wrap it in a memory-mapped bus interface, push both through OpenROAD (OpenROAD-flow-scripts, sky130hd), and measure the gap.

**The question you answer:** how much area, speed and power does the bus interface add to a register file, and how do the number of entries and read ports change that cost?

**Why this matches the video (careful inference, not a promise):**

- The video says a CPU only drives a bus. Your testbench plays the CPU, so you practise that idea without building a CPU (which you already ruled out as too saturated).
- It is memory-first and interface-first, not a bare ALU or FIFO.
- It reports bandwidth per area and bandwidth per milliwatt, which is a direct way to talk about the memory-movement bottleneck.
- It still has the physical design flow and a fitted cost model that an AI cannot just generate for you.

**Definition of done (all six, checked on 14 Nov):**

- [ ] RTL and tests pass from one command (`make test`).
- [ ] 24 flow runs finished and collected into one CSV (4 sizes × 3 read-port counts × core-only and with-bus).
- [ ] A cost model fitted on the data and checked on at least 2 configs it never saw, with the error percentage reported.
- [ ] 6 plots and 2 layout screenshots made from your own data.
- [ ] Public GitHub repo with a README, a 4 to 6 page report, and a log of daily commits.
- [ ] Resume bullets that contain only numbers you measured.

**Honest limits, to state in your report:**

- Flip-flop based storage on sky130hd, no SRAM macro.
- Power comes from default switching activity, so treat it as a relative estimate.
- No signoff, no tapeout. Results compare designs against each other under one flow setting.

## Scope: what is in, what is stretch, what is out

The core is the 24-run sweep with and without the bus interface, plus a cost model checked on points it never saw. Everything else comes after the core is finished, in the order listed.

**Prior art you must cite.** The OpenROAD project already publishes a register file study called RegFileStudy (Chisel and Bazel, comparing read ports against write ports on a 32-bit by 64-row file). I did not mention it when I first suggested your register file project, and I should have. Your version is different in four ways: plain Verilog and Make, a bus interface with its own overhead measurement, bandwidth per area as the headline metric, and a model validated on new design points. Say this in your README and link their repo. Hiding it would hurt you in an interview.

| Item | Status | Where |
| --- | --- | --- |
| Parameterised register file (entries, read ports) | In | D2 to D3 |
| Bus wrapper: decoder, CTRL, STATUS, INPUT, error flag, scan read ports | In | D4 |
| cocotb tests with a Python reference model, mutation-checked | In | D3 to D5 |
| 24 flow runs: 4 sizes × 3 read-port counts × core-only and with-bus | In | D6 to D11 |
| Interface overhead (area, period, power) per size | In | D12 |
| Bandwidth per area and per milliwatt | In | D12 |
| Area cost model, trained on the grid, tested on unseen points | In | D13 |
| Critical path explained at 3 corners, with GUI screenshots | In | D12 |
| Repo, report, resume bullets | In | D15 to D19 |
| S1: cost of the same-cycle bypass (BYPASS=1) at 4 sizes | Stretch | D16 |
| S2: registered read output vs combinational read | Stretch | D16 to D17 |
| S3: second platform (nangate45) rerun of 6 points | Stretch | D17 |
| S4: one formal property with SymbiYosys | Stretch | D17 |
| S5: GitHub Actions running the tests | Stretch | D18 |
| 8-bit CPU, crypto core, accelerator | Out | You ruled these out as too saturated |
| SRAM macros, caches, MMU | Out | Too much new material for 19 days |
| FP8 vs posit8 multiplier | Out for now | Next study, same scaffold |
| Tapeout or signoff claims | Out | Only claim DRC/LVS clean if the reports say so |

**Three conflicts with your earlier decisions, stated so you can overrule me:**

1. Deadline moves from 9 Nov to 14 Nov, as you asked. The old guide's Days 8 to 14 are replaced by this plan.
2. The old sweep's second axis was BYPASS 0 or 1. Here the second axis is core-only vs with-bus, and BYPASS stays at 0 until stretch S1.
3. The register file stays the base, so your locked project is extended, not swapped.

Assumption: your Day 0 setup from the old guide (WSL2 on D:, ORFS, cocotb) is done. Day 1 starts with a 10-minute check of that.

## Rules of engagement

The plan assumes about 90 hours: 4 hours on weekdays and 7 hours on Sat 31 Oct, Sun 1 Nov, Sat 7 Nov, Sun 8 Nov and Sat 14 Nov. If exams eat a day, tell me which one and I will move the stretch items, never the gates.

**Every day, same protocol**

1. Before you start: write 3 lines in `log/YYYY-MM-DD.md`. Goal for today, the result you expect, one guess you will check.
2. Work in two blocks of at most 2 hours with a 10 minute break between them. Phone out of reach.
3. Before you stop: run `make test`, commit, push. Add 2 lines to the log: what you measured, what broke.

**Rules that stop you slipping**

- **Gates.** Each day ends with a checklist. If the gate is not met, you do not start the next day's material. You use the first 2 hours of the next day to close it, and you drop the lowest stretch item to pay for it.
- **Buffer days** are D7 (Mon 2 Nov), D14 (Mon 9 Nov) and D18 (Fri 13 Nov). They are for gates you missed, not for rest.
- **Feature freeze on D15 (Tue 10 Nov).** After that you only fix, measure, write and polish.
- **Only measured numbers.** Anything you expected but did not measure is labelled "guess". Write the guess down before you open the report.
- **Never delete a failed run.** Its log is data, and the failure goes in the report's limitations.
- **A day with no commit is a failed day.** Commit broken code if you must.
- **Stuck for 45 minutes:** write the question and the exact error in the log, try one fix from the troubleshooting section, then ask me with the log excerpt pasted in.
- **You type the RTL and the testbench yourself.** Ask me to explain or review it, not to produce the final files. The video's point is that boilerplate is cheap now. What stays valuable is that you can explain every line and every number in an interview.

**Hour budget (suggestion, not a measurement)**

| Phase | Days | Hours |
| --- | --- | --- |
| Environment check and first flow run | D1 | 4 |
| RTL and tests | D2 to D5 | 22 |
| Flow bring-up, period choice, first runs | D5 to D7 | 14 |
| Full sweep, parsing, analysis | D8 to D13 | 28 |
| Buffer, stretch, write-up, ship | D14 to D19 | 22 |

## Architecture and specs

Two designs go through the flow: the bare `regfile` (core-only) and `mmio_top` (the same register file behind a bus). Both take their size from the same macros, so one RTL covers every sweep point.

**Why it is built this way**

- A single bus master can only read one address per cycle. So read port 0 serves the bus, and read ports 1 and up are "scan ports", read by hardware on its own, like a display engine scanning a frame buffer. That gives NREAD a real meaning in the bus design.
- Zero wait states keep the bus read path (address in, decode, read mux, response mux, data out) inside one cycle. That path is where the interface cost shows up in timing.
- Flip-flop storage on purpose. It is what you can synthesise in sky130hd without an SRAM macro, and the RegFileStudy authors argue that for register files the access network dominates anyway.

**Sweep parameters**

| Parameter | Values | Note |
| --- | --- | --- |
| DEPTH (entries) | 8, 16, 32, 64 | Powers of two only, the address decode relies on it |
| WIDTH | 16 | Fixed. STATUS needs at least 9 bits |
| NREAD (read ports) | 1, 2, 4 | Validation points also use 3 |
| BYPASS | 0 | 1 only in stretch S1 |
| Design | core, bus | Top module `regfile` or `mmio_top` |

**Bus address map (word addresses, AW = log2(DEPTH), address is AW+2 bits)**

| Region (top 2 bits) | Offset | Name | Access | Behaviour |
| --- | --- | --- | --- | --- |
| 0 | 0 to DEPTH-1 | DATA | RW | Register file entry |
| 1 | 0 | CTRL | RW | Bit 0 SCAN\_EN, bits 14:1 scratch, bit 15 CLEAR (write 1 clears STATUS, reads 0) |
| 1 | 1 | STATUS | RO | Bits 7:0 count of accepted DATA writes (wraps), bit 8 sticky error |
| 1 | 2 | INPUT | RO | Registered copy of the `in_port` pins, like a keyboard register |
| 1 | 3 | none | n/a | Unmapped, raises err |
| 2 and 3 | any | none | n/a | Unmapped, raises err |

**Bus rules**

- A write lands on the rising clock edge when `sel` and `we` are both 1.
- Read data is combinational from `addr` while `sel` is 1, and 0 when `sel` is 0.
- `err` is 1 in the same cycle as any access to an unmapped address. STATUS bit 8 remembers it until CLEAR.
- `scan_data` is 0 unless CTRL bit 0 is 1.

**Sanity numbers from a generic Yosys run on my side (not the full flow)**

Core design: DEPTH × 16 flops. Bus design: DEPTH × 16 + 40 flops (15 CTRL bits, 8 counter bits, 1 error bit, 16 INPUT bits). With 64 entries and 4 read ports, the core had 4,032 mux cells, which is 4 ports × 16 bits × 63 two-input muxes. After the real flow maps cells to sky130 the numbers will move a little. If yours are off by a lot, the defines did not reach synthesis (see troubleshooting).

**Repo layout**

```
regbus/
  rtl/        regfile.v, mmio_top.v
  tb/         Makefile, test_regfile.py, test_mmio.py
  scripts/    sweep.py, parse.py, keys.py, analyse.py
  runs/       one folder per sweep point, written by sweep.py
  results/    sweep.csv, summary.md, plots/
  log/        one file per day
  Makefile    test, test-all, sweep, parse, analyse
  README.md
  .gitignore  sim_build_*, __pycache__, results.xml
```

## Experiment design

Twenty-four grid runs (core and bus, 4 sizes, 3 read-port counts) plus four validation runs, all on sky130hd with identical flow settings. Only the design and its parameters change between runs.

**Flow settings held constant**

| Setting | Value | Why |
| --- | --- | --- |
| Platform | sky130hd | One PDK, one corner, stated as a limit |
| CORE\_UTILIZATION | 40 | Same for every run so die size follows cell area |
| PLACE\_DENSITY\_LB\_ADDON | 0.20 | Keeps placement from failing on small designs |
| Clock period (target) | one value, chosen on D7 | The smallest design meets it, larger ones may miss it |
| Input and output delay | 20% of the period | Makes the combinational bus read path a timed path |
| Tool versions | recorded in the README | `openroad -version`, `yosys -V`, ORFS git commit |

**Metrics, with the caveat each one carries**

| Metric | Definition | Source | Caveat |
| --- | --- | --- | --- |
| area\_um2 | Standard cell area after the full flow | `finish__design__instance__area` | Cell area, not die area |
| wns\_ns | Worst setup slack at the end | `finish__timing__setup__ws` | Negative means the target period is missed |
| period\_est\_ns | target period − wns | derived | An estimate. Input-to-output paths only get 60% of the period, so for them the true limit is closer to target − wns/0.6. Compare designs with this number, do not quote it as fmax |
| power\_mw | Total power × 1000 | `finish__power__total` | Default switching activity, so use it for ranking only |
| n\_flops, n\_mux, n\_cells | Cell counts after synthesis | `synth_stat.txt` | Regex may need adapting to your file |
| bw\_gbps | NREAD × 16 ÷ period\_est\_ns | derived | Peak, if every read port delivers one word per cycle |
| bw\_per\_kum2 | bw\_gbps ÷ (area ÷ 1000) | derived | Your memory-movement number |
| pj\_per\_bit | power\_mw ÷ bw\_gbps | derived | Relative only, see power caveat |
| interface overhead | bus area − core area, also as % of core | derived | Same DEPTH and NREAD on both sides |

**Cost model**

With width fixed at 16, area is modelled per design as:

```latex
A(D, R) = c_0 + c_1 D + c_2 R D
```

D is entries and R is read ports. Reasoning (careful inference, the fit will tell you if it is wrong): storage grows with D, each read port adds a mux tree that also grows with D, and decode, IO and control add a constant.

**Validation protocol**

1. Fit on the 12 grid points of each design. Report R² and the largest residual.
2. Refit on entries ≤ 32 only and predict entries = 64. Report the error.
3. Write your predictions for the two unseen points before running them: 128 entries × 2 ports and 16 entries × 3 ports, on both designs. Then run them and report the error. Whatever the error is, it goes in the report. I picked 10% as a point to start asking why, not as a pass mark from any standard.

**Hypotheses to write down before any run, each with what would kill it**

| # | Guess | What disproves it |
| --- | --- | --- |
| H1 | Core area grows roughly linearly in entries × read ports | The model's residual is above 10% at the corners |
| H2 | The bus overhead in percent shrinks as entries grow | Overhead % at 64 entries is not lower than at 8 |
| H3 | The bus design's critical path runs from `addr` to `rdata` through decode and the read mux | The report's start and end points are something else |
| H4 | Power ranks the designs in the same order as area | The two orderings differ |
| H5 | Extra read ports cost less area per bit of bandwidth than extra entries cost per bit of storage | bw\_per\_kum2 falls as ports go from 1 to 4 |

**Threats to validity, to list in the report**

One PDK and corner. Default activity for power. Flip-flop storage only. Fixed utilisation. A single tool version. No silicon, so every number is a pre-silicon estimate.

## Day-by-day plan (D1 = Tue 27 Oct, D19 = Sat 14 Nov)

Each day has tasks, then a gate. Code for the files named here is in the reference code section. Times are my estimates, not measurements. Wherever a command shows \`--period 4.0\`, use the period you choose on D7 instead.

### D1 · Tue 27 Oct · Check the toolchain, run the example (4 h)

Goal: prove every tool works before you write any design.

- [ ] Open Ubuntu and load the environment:

```
cd ~/OpenROAD-flow-scripts && source ./env.sh
openroad -version
yosys -V
klayout -v
iverilog -V | head -1
source ~/venvs/rf/bin/activate && python3 -c "import cocotb; print(cocotb.__version__)"
```

- [ ] Paste all five version lines into `log/versions.md`. They go in your README later.
- [ ] Make `env.sh` load in every new terminal: `echo 'source ~/OpenROAD-flow-scripts/env.sh' >> ~/.bashrc`
- [ ] Run the example design (first run may take several minutes):

```
cd ~/OpenROAD-flow-scripts/flow
make DESIGN_CONFIG=./designs/sky130hd/gcd/config.mk
make DESIGN_CONFIG=./designs/sky130hd/gcd/config.mk gui_final
```

- [ ] List the output folders and write one line per stage in `log/stages.md` (1 synth, 2 floorplan, 3 place, 4 cts, 5 route, 6 finish): `ls results/sky130hd/gcd/base logs/sky130hd/gcd/base reports/sky130hd/gcd/base`
- [ ] Open the final layout in KLayout: `klayout results/sky130hd/gcd/base/6_final.gds`
- [ ] Find the real metric key names. This settles the one thing I could not check for you:

```
grep -o '"finish__[a-z_]*"' logs/sky130hd/gcd/base/6_report.json | sort -u
grep -io '"[a-z_]*power[a-z_]*"' logs/sky130hd/gcd/base/6_report.json | sort -u
```

- [ ] Write the exact key names for area, worst setup slack and total power in `log/keys.md`.
- [ ] Make the repo (rename your old `regfile-ppa` repo to `regbus` if you made one): folders from the layout section, the `.gitignore`, first commit, push.

**Gate D1:** gcd finished, GDS opened, versions logged, three key names written, repo pushed.

### D2 · Wed 28 Oct · Register file RTL and its tests (4 h)

Goal: a register file you can explain line by line, with tests that fail when the RTL is wrong.

- [ ] Type `rtl/regfile.v` yourself from the reference code. Above each block, write a comment in your own words saying what it does.
- [ ] Compile with no warnings: `iverilog -g2012 -Wall -DP_DEPTH=8 -DP_NREAD=2 -s regfile -o /tmp/a.vvp rtl/regfile.v`
- [ ] Copy `tb/Makefile` and `tb/test_regfile.py`. Type the first two tests yourself, paste the rest, then run:

```
make -C tb TOP=regfile DEPTH=8 NREAD=2 BYPASS=0
make -C tb TOP=regfile DEPTH=8 NREAD=2 BYPASS=1
```

- [ ] On paper, draw the read mux for 8 entries and 2 read ports. Write your guess for the Yosys mux count (hint: ports × 16 bits × (entries − 1)) in `log/2026-10-28.md`.
- [ ] Run generic synthesis and compare with your guess:

```
yosys -p "verilog_defaults -add -D P_DEPTH=8 -D P_NREAD=2; read_verilog rtl/regfile.v; synth -top regfile -flatten; stat" | tee log/yosys_core_d8_r2.txt
```

- [ ] Mutation check. Break the RTL three ways, one at a time, run the tests, and confirm at least one test fails each time. Restore with `git checkout rtl/regfile.v` after each. Suggested breaks: remove the `we` condition on the write, make reset do nothing, ignore BYPASS.

**Gate D2:** 5 tests pass for BYPASS 0 and 1, all 3 mutations caught, Yosys counts logged next to your guess.

### D3 · Thu 29 Oct · The bus wrapper (4 h)

Goal: `mmio_top` compiles clean for several sizes and you can explain every signal.

- [ ] First 30 minutes: write `docs/spec.md` in your own words from the address map and bus rules in the architecture section.
- [ ] Type `rtl/mmio_top.v` in four steps and compile after each one: (1) decode and `err`, (2) the register file instance and read mux, (3) CTRL, STATUS and INPUT registers, (4) the scan ports.
- [ ] Compile for four settings with zero warnings:

```
for c in "8 1" "8 4" "64 4" "16 2"; do set -- $c
  iverilog -g2012 -Wall -DP_DEPTH=$1 -DP_NREAD=$2 -s mmio_top -o /tmp/a.vvp rtl/regfile.v rtl/mmio_top.v && echo "ok $c"
done
```

- [ ] Draw the block diagram by hand, photograph it, save it as `docs/block.jpg`.
- [ ] Run generic synthesis for the bus design at 8 × 1 and 64 × 4. The flop counts should be 8 × 16 + 40 and 64 × 16 + 40:

```
yosys -p "verilog_defaults -add -D P_DEPTH=64 -D P_NREAD=4; read_verilog rtl/regfile.v rtl/mmio_top.v; synth -top mmio_top -flatten; stat" | tee log/yosys_bus_d64_r4.txt
```

**Gate D3:** four clean compiles, spec written, diagram saved, flop counts match or you can explain the gap.

### D4 · Fri 30 Oct · Bus tests and mutation checks (4 h)

Goal: tests that catch real bugs in the bus design.

- [ ] Copy `tb/test_mmio.py`. Type the `Bus` class and the first three tests yourself, paste the rest.
- [ ] Run: `make -C tb TOP=mmio_top DEPTH=8 NREAD=2 BYPASS=0`
- [ ] For each of the 10 tests, write one line in `docs/tests.md`: which bug it would catch.
- [ ] Mutation check, four breaks, each must fail at least one test, restore after each: counter adds 2 instead of 1, offset 3 treated as mapped, scan gate removed, bypass ignored.
- [ ] Write 2 tests of your own. Ideas: writing to STATUS changes nothing, a CTRL write never changes DATA.
- [ ] Copy the root `Makefile`, then run `make test-all`. It runs 48 configurations (both designs, 4 sizes, 3 port counts, BYPASS 0 and 1). It took about 3 minutes on my machine.

**Gate D4:** `make test-all` prints ALL PASS, 4 mutations caught, 2 tests of your own committed.

### D5 · Sat 31 Oct · First real flow run on your own design (7 h)

Goal: one core run and one bus run finished, with every number checked by hand.

- [ ] Copy `scripts/sweep.py`, `keys.py`, `parse.py`. Read `sweep.py` top to bottom and write what each function does in `docs/sweep.md`.
- [ ] Dry run first, then the real run. The period 4.0 is a placeholder until D7:

```
python3 scripts/sweep.py --period 4.0 --only core_d8_r1 --dry
python3 scripts/sweep.py --period 4.0 --only core_d8_r1
```

- [ ] If it fails, read the last 40 lines of `runs/core_d8_r1/make.log` and use the troubleshooting section.
- [ ] Check that the defines reached synthesis: `grep -E "dfxtp|dfrtp" ~/OpenROAD-flow-scripts/flow/reports/sky130hd/rb_core_d8_r1/base/synth_stat.txt`. Expect about 128 flops.
- [ ] Confirm the key names against `log/keys.md`: `python3 scripts/keys.py core_d8_r1 area`, then `power`, then `setup`. Edit the constants at the top of `parse.py` if they differ.
- [ ] Run `bus_d8_r1` the same way, then compare area and slack with the core run by hand.
- [ ] Open the layout: `make -C ~/OpenROAD-flow-scripts/flow DESIGN_CONFIG=$HOME/Register-Bus/runs/bus_d8_r1/config.mk gui_final`. Screenshot it into `docs/`.
- [ ] `python3 scripts/parse.py` and open `results/sweep.csv`.

**Gate D5:** two finished runs, key names confirmed, flop counts within a few percent of D2 and D3, `sweep.csv` has 2 rows, screenshot saved.

### D6 · Sun 1 Nov · Run the biggest points, read what the tools did (7 h)

Goal: learn how long the largest runs take, read the reports properly, and commit your guesses before the sweep.

- [ ] Start the two largest points in the background. They are probes at the placeholder period, so they are tagged and kept out of the sweep table:

```
nohup python3 scripts/sweep.py --period 4.0 --only d64_r4 --tag _p4 > log/big.out 2>&1 &
```

- [ ] While they run, open `reports/sky130hd/rb_bus_d8_r1/base/synth_stat.txt` from D5. Build a small table by hand: flops, mux cells, other cells, total.
- [ ] Open the timing report (`ls reports/sky130hd/rb_bus_d8_r1/base` to see the file names, the final one is usually `6_finish.rpt`). Search for `report_checks -path_delay max`. Write down the start point, end point and the cells on the worst path.
- [ ] Read the ORFS flow variable docs for `CORE_UTILIZATION` and `PLACE_DENSITY`. Write 2 lines on each in `docs/flow-notes.md`.
- [ ] Write the hypotheses H1 to H5 from the experiment section into `log/hypotheses.md`, each with a number. Examples: the core area at 64 × 4, the overhead percentage at 8 × 1 and at 64 × 4, the start and end point you expect on the critical path. Commit it with the message "hypotheses before sweep". Do this before you open any result beyond 8 × 1 and 64 × 4.

**Gate D6:** both 64 × 4 runs finished, or failed with a cause written down. Hypotheses committed. Stage-by-stage notes written.

### D7 · Mon 2 Nov · Choose the clock period, close old gates (4 h, buffer day)

Goal: one clock period for the whole sweep, picked from data.

- [ ] Probe three periods on the smallest core point and the largest bus point. The 4.0 runs from D6 are reused automatically:

```
for p in 2.5 4.0 6.0; do t=_p${p%.*}
  python3 scripts/sweep.py --period $p --only core_d8_r1 --tag $t
  python3 scripts/sweep.py --period $p --only bus_d64_r4 --tag $t
done
python3 scripts/parse.py --all
```

- [ ] Read `wns_ns` for the six probes. Decision rule: pick the period where `core_d8_r1` has slack between 10% and 30% of the period, and `bus_d64_r4` still completes the flow. A small negative slack on the biggest design is fine and is part of the result. If the biggest design misses by more than half the period, take the next larger period.
- [ ] Write the table and your choice in `log/period.md`. Set `PERIOD ?=` to your value in the root `Makefile`. Commit.
- [ ] Spend the rest of the day closing any gate from D1 to D6.

**Gate D7:** period chosen with a table of evidence, Makefile updated, every earlier gate closed.

### D8 · Tue 3 Nov · Launch the full sweep (4 h)

Goal: all 24 points running unattended by the end of the session.

- [ ] Check resources: `nproc` and `free -g`. Use `--jobs 1` if WSL has under 8 GB free, otherwise `--jobs 2`.
- [ ] Windows power settings: sleep set to Never while plugged in. Keep the charger connected. A sleeping laptop silently kills the sweep.
- [ ] Launch (replace 4.0 with your period). The points run smallest first, in core and bus pairs, so a late stop still leaves complete pairs:

```
nohup python3 scripts/sweep.py --period 4.0 --jobs 1 > log/sweep_all.out 2>&1 &
echo $!
```

- [ ] Monitor with `tail -f log/sweep_all.out` (Ctrl+C stops the tail, not the sweep) and count finished runs with `ls ~/OpenROAD-flow-scripts/flow/logs/sky130hd | grep -c "^rb_"`.
- [ ] While it runs, run `python3 scripts/parse.py` on whatever has finished. Check `n_flops` in the CSV: DEPTH × 16 for core, DEPTH × 16 + 40 for bus, within a few percent. If `n_flops` is 0, open one `synth_stat.txt` and fix the regex in `synth_counts()`.
- [ ] Write the README skeleton: headings only, from the write-up template.

**Gate D8:** sweep running or finished, at least 12 points done, `parse.py` works on real files and flop counts make sense.

### D9 · Wed 4 Nov · Finish the sweep, explain every failure (4 h)

Goal: 24 rows in `results/sweep.csv`, or a written reason for each missing row.

- [ ] Run `python3 scripts/parse.py`. The last line lists problems. For each failed run, read the last 40 lines of `runs/<id>/make.log`.
- [ ] Copy each failed log to `log/failed/<id>.log` before touching anything. Failed runs go in the report.
- [ ] Fix the cause using the troubleshooting section and rerun just that point: `python3 scripts/sweep.py --period 4.0 --only <id> --force` (this wipes that point's old results first).
- [ ] Print the table and read every row:

```
python3 -c "import pandas as pd; d=pd.read_csv('results/sweep.csv'); print(d[['id','area_um2','wns_ns','power_mw','n_flops']].to_string())"
```

- [ ] Anything odd, like a bigger design with a smaller area, gets an explanation in `log/anomalies.md` before you move on.

**Gate D9:** `sweep.csv` has 24 rows or each missing one has a documented cause, anomalies explained.

### D10 · Thu 5 Nov · Plots, hypotheses verdicts, model fit, predictions (4 h)

Goal: read the results honestly and commit your predictions before the validation runs exist.

- [ ] Copy `scripts/analyse.py` and run `python3 scripts/analyse.py`. Open the six plots in `results/plots/`.
- [ ] For each plot write 2 sentences in `docs/results.md`: what it shows and one thing that surprised you.
- [ ] Mark each of H1 to H5 as supported or not supported, with the number that decides it. Do not edit the original hypotheses file.
- [ ] Read the model coefficients in `results/summary.md`. By hand, compute the predicted area for 128 entries × 2 ports and 16 entries × 3 ports, for both designs, using A = c0 + c1·D + c2·R·D. Write the four predictions in `log/predictions.md`. Commit with the message "predictions before validation runs".
- [ ] Launch the four validation runs. The 24 grid points are skipped automatically:

```
nohup python3 scripts/sweep.py --period 4.0 --extra bus:128:2 core:128:2 bus:16:3 core:16:3 > log/sweep_val.out 2>&1 &
```

**Gate D10:** 6 plots committed, 5 verdicts with numbers, four predictions committed before the runs started.

### D11 · Fri 6 Nov · Critical paths and validation results (4 h)

Goal: explain what goes critical, and score your model on points it never saw.

- [ ] When the validation runs finish, run `python3 scripts/parse.py` then `python3 scripts/analyse.py`. The "never-seen point" lines in `results/summary.md` give the errors. Copy them into `docs/results.md` next to your own predictions.
- [ ] Critical paths at three corners: bus 8 × 1, bus 64 × 1, bus 64 × 4. In each `6_finish.rpt`, record the start point, end point, slack and the cell types on the worst path in a table in `docs/critical-paths.md`.
- [ ] Open each corner in the GUI (`gui_final` as on D5), open the timing report panel from the Windows menu, select the worst path, screenshot it into `docs/`.
- [ ] Answer H3 with the evidence: is the worst path from `addr` to `rdata` through decode and the read mux, or something else? If it is something else, say so plainly.
- [ ] Compare each with your D6 guess and write one line on where you were wrong.

**Gate D11:** validation errors recorded, 3-row critical path table with screenshots, H3 answered.

### D12 · Sat 7 Nov · Report draft v1 (7 h)

Goal: a complete first draft where every number can be traced.

- [ ] Write `README.md` following the write-up template. All sections get real text, none is left as a heading.
- [ ] Put in the six plots and your GUI screenshots. Each figure gets a caption that says what to notice.
- [ ] Add the sweep table (trimmed to area, period estimate, power) and link `results/sweep.csv`.
- [ ] Write the limitations and threats section from the experiment section, plus your tool versions from `log/versions.md`.
- [ ] Trace check: pick 5 numbers at random from your draft. For each one, find it in `sweep.csv`, then in the raw report or JSON it came from. Write the trace in `log/trace.md`.
- [ ] Cite RegFileStudy in the README with a link, and say in two sentences how your study differs.

**Gate D12:** draft v1 complete, 5 numbers traced to raw files, prior art cited.

### D13 · Sun 8 Nov · The headline results and a reproducibility check (7 h)

Goal: turn the data into the three answers you promised, and prove the flow repeats.

- [ ] **Interface overhead:** a table of the 12 core and bus pairs with extra area (µm² and %), period estimate change and power change. One sentence on the trend, and the H2 verdict with its number.
- [ ] **Bandwidth per area:** for each design, name the entries and ports combination with the best `bw_per_kum2`. Give the H5 verdict with numbers. If the winner is a corner of the grid, say the true optimum may lie outside it.
- [ ] **Design rules:** write up to 3 rules a designer could use, but only ones your data supports. Fewer than 3 is fine.
- [ ] **Reproducibility:** note the area of `bus_d8_r2` from `sweep.csv`. Then in a fresh clone (`git clone <your repo> /tmp/regbus-clean`), run `make test`, then rerun that one point with `--force`. Compare the area. I expect identical numbers (a guess). If they differ, report the difference and treat it as your noise level.
- [ ] Update the report with all of this.

**Gate D13:** overhead and bandwidth sections written with verdicts, reproducibility result recorded.

### D14 · Mon 9 Nov · Buffer, DRC and LVS statement, clean clone (4 h)

Goal: close every open gate and state exactly what is and is not checked.

- [ ] Close any unfinished gate from D1 to D13 first.
- [ ] Look for DRC and LVS output: `ls ~/OpenROAD-flow-scripts/flow/reports/sky130hd/rb_bus_d8_r1/base | grep -i -E "drc|lvs"`. If reports exist, read them for bus 8 × 1 and bus 64 × 4. Write "clean" only if they report zero violations. Otherwise write what they say, or "not run".
- [ ] Clean clone test: clone the repo into `/tmp`, follow only the README, run `make test`. Fix every instruction that was missing or wrong.

**Gate D14:** all earlier gates closed, DRC and LVS statement written, README works from a clean clone.

### D15 · Tue 10 Nov · Feature freeze and outside review (4 h)

Goal: lock the scope, then let someone attack the report.

- [ ] Tag `v0.9`. From now on: no new RTL, no new sweep points, except the stretch items on D16 and D17.
- [ ] Write the 5-line summary at the top of the README: the question, the method, your three headline numbers, the main limit, and the rerun command.
- [ ] Ask one person with VLSI knowledge (a senior, a TA, a professor) to read it and name the weakest claim. Paste the report into Claude as well and ask it to find the weakest claim and the most likely misreading. Write both answers in `log/review.md`.
- [ ] Fix what they found, or write why you disagree.

**Gate D15:** `v0.9` tagged, review notes written, each point fixed or answered.

### D16 · Wed 11 Nov · Stretch S1 and S2 (4 h)

Goal: add depth only where the core is already done.

- [ ] **S1, bypass cost:** run the 8 points with 2 read ports and BYPASS=1, then analyse. `analyse.py` prints a separate bypass table and keeps these rows out of the main plots.

```
python3 scripts/sweep.py --period 4.0 --bypass 1 --only _r2_b1
python3 scripts/parse.py && python3 scripts/analyse.py
```

- [ ] **S2, registered read output:** add a `REGREAD` parameter that puts a flop on `rdata`. The tests need a one-cycle latency change. Compare area and period against the combinational read at 4 sizes. I left this one less detailed on purpose. Come back to me when you start it.
- [ ] Each stretch item that finishes gets its own short section in the report with its numbers. One that does not finish gets one line under "not done".

**Gate D16:** none. Stretch is optional, and the report must still be complete without it.

### D17 · Thu 12 Nov · Polish, resume bullets, post draft (4 h)

Goal: turn the work into things other people can read in a minute.

- [ ] Re-read the report out loud once. Cut every sentence you cannot defend.
- [ ] Write resume bullets from the template in the write-up section. Every number in them must exist in `sweep.csv` or `summary.md`.
- [ ] Draft a short post: the question, one plot, one finding, the repo link.
- [ ] Optional stretch S3 or S4 only if the report is already final.

**Gate D17:** 2 to 3 resume bullets, each number traced. Post drafted.

### D18 · Fri 13 Nov · Final regeneration (4 h, buffer)

Goal: everything in the repo comes from the repo.

- [ ] `make test-all` prints ALL PASS.
- [ ] Regenerate the CSV, plots and summary: `make parse && make analyse`. Confirm the report's numbers still match.
- [ ] Export the report to PDF and put it in the repo.
- [ ] Clean clone test once more.

**Gate D18:** tests pass, regenerated results match the report, PDF in the repo.

### D19 · Sat 14 Nov · Ship (7 h)

Goal: published and shared by evening.

- [ ] Morning: final read of the README and the limitations section.
- [ ] Tag `v1.0`. Make the repo public.
- [ ] Publish the post. Send the repo to a professor and two seniors with one sentence on what you want from them.
- [ ] Write `log/next.md`: what this study did not answer, and the first three steps of the FP8 vs posit8 study, reusing `sweep.py`.
- [ ] Tick the definition of done at the top of this guide.

**Gate D19:** repo public, `v1.0` tagged, post out, definition of done fully ticked.

## Reference code

These files compiled and passed in iverilog and cocotb 1.9.2 on my side. Type them yourself as the plan says, using these as the answer key. The scripts were exercised only on made-up data, never on a real ORFS run, so expect small fixes on D5 and D8.

### rtl/regfile.v

```verilog
// Parameterised flop-based register file.
// One write port (synchronous), NREAD read ports (combinational).
// Defaults come from macros so the flow can set them with -D P_DEPTH=16 etc.
`ifndef P_DEPTH
 `define P_DEPTH 8
`endif
`ifndef P_WIDTH
 `define P_WIDTH 16
`endif
`ifndef P_NREAD
 `define P_NREAD 2
`endif
`ifndef P_BYPASS
 `define P_BYPASS 0
`endif

module regfile #(
  parameter DEPTH  = `P_DEPTH,
  parameter WIDTH  = `P_WIDTH,
  parameter NREAD  = `P_NREAD,
  parameter BYPASS = `P_BYPASS,
  parameter AW     = $clog2(DEPTH)
)(
  input  wire                   clk,
  input  wire                   rst,
  input  wire                   we,
  input  wire [AW-1:0]          waddr,
  input  wire [WIDTH-1:0]       wdata,
  input  wire [NREAD*AW-1:0]    raddr,
  output wire [NREAD*WIDTH-1:0] rdata
);
  reg [WIDTH-1:0] mem [0:DEPTH-1];
  integer i;

  always @(posedge clk) begin
    if (rst) begin
      for (i = 0; i < DEPTH; i = i + 1) mem[i] <= {WIDTH{1'b0}};
    end else if (we) begin
      mem[waddr] <= wdata;
    end
  end

  genvar p;
  generate
    for (p = 0; p < NREAD; p = p + 1) begin : rd
      wire [AW-1:0] a   = raddr[p*AW +: AW];
      wire          hit = (BYPASS != 0) && we && (waddr == a);
      assign rdata[p*WIDTH +: WIDTH] = hit ? wdata : mem[a];
    end
  endgenerate
endmodule
```

### rtl/mmio\_top.v

```verilog
// Register file behind a memory-mapped bus slave interface.
// Address map (word addresses, ABITS = log2(DEPTH) + 2), region = addr[ABITS-1:ABITS-2]
//   region 0 : DATA, index = addr[AW-1:0]
//   region 1 : offset 0 CTRL (RW), 1 STATUS (RO), 2 INPUT (RO), 3 unmapped
//   regions 2,3 : unmapped (err = 1, read data 0)
// Zero wait states. Write lands on the clock edge when sel & we.
// Read data is combinational from addr while sel = 1.
// Read ports 1..NREAD-1 are scan ports, returning 0 unless CTRL.SCAN_EN = 1.
`ifndef P_DEPTH
 `define P_DEPTH 8
`endif
`ifndef P_WIDTH
 `define P_WIDTH 16
`endif
`ifndef P_NREAD
 `define P_NREAD 2
`endif
`ifndef P_BYPASS
 `define P_BYPASS 0
`endif

module mmio_top #(
  parameter DEPTH  = `P_DEPTH,
  parameter WIDTH  = `P_WIDTH,
  parameter NREAD  = `P_NREAD,
  parameter BYPASS = `P_BYPASS,
  parameter AW     = $clog2(DEPTH),
  parameter SCW    = (NREAD > 1) ? (NREAD - 1) : 1
)(
  input  wire                 clk,
  input  wire                 rst,
  input  wire                 sel,
  input  wire                 we,
  input  wire [AW+1:0]        addr,
  input  wire [WIDTH-1:0]     wdata,
  output wire [WIDTH-1:0]     rdata,
  output wire                 err,
  input  wire [SCW*AW-1:0]    scan_addr,
  output wire [SCW*WIDTH-1:0] scan_data,
  input  wire [WIDTH-1:0]     in_port
);
  localparam ABITS = AW + 2;

  // ---- decode ----
  wire [1:0] region  = addr[ABITS-1:ABITS-2];
  wire [1:0] off     = addr[1:0];
  wire is_data   = (region == 2'b00);
  wire is_ctrl   = (region == 2'b01);
  wire ctrl_ok   = is_ctrl && (off != 2'b11);
  wire mapped    = is_data | ctrl_ok;
  assign err     = sel & ~mapped;

  wire wr_data   = sel & we & is_data;
  wire wr_ctrl   = sel & we & is_ctrl & (off == 2'b00);

  // ---- register file ----
  wire [NREAD*AW-1:0]    rf_raddr;
  wire [NREAD*WIDTH-1:0] rf_rdata;

  assign rf_raddr[AW-1:0] = addr[AW-1:0];
  genvar p;
  generate
    for (p = 1; p < NREAD; p = p + 1) begin : g_scan_addr
      assign rf_raddr[p*AW +: AW] = scan_addr[(p-1)*AW +: AW];
    end
  endgenerate

  regfile #(.DEPTH(DEPTH), .WIDTH(WIDTH), .NREAD(NREAD), .BYPASS(BYPASS)) u_rf (
    .clk(clk), .rst(rst),
    .we(wr_data), .waddr(addr[AW-1:0]), .wdata(wdata),
    .raddr(rf_raddr), .rdata(rf_rdata)
  );

  // ---- control / status / input registers ----
  reg [WIDTH-1:0] ctrl_q;
  reg [7:0]       wr_cnt;
  reg             err_sticky;
  reg [WIDTH-1:0] in_q;
  wire clear = wr_ctrl & wdata[15];

  always @(posedge clk) begin
    if (rst) begin
      ctrl_q     <= {WIDTH{1'b0}};
      wr_cnt     <= 8'd0;
      err_sticky <= 1'b0;
      in_q       <= {WIDTH{1'b0}};
    end else begin
      in_q <= in_port;
      if (wr_ctrl) ctrl_q <= wdata & {1'b0, {(WIDTH-1){1'b1}}};
      if (clear) begin
        wr_cnt     <= 8'd0;
        err_sticky <= 1'b0;
      end else begin
        if (wr_data) wr_cnt <= wr_cnt + 8'd1;
        if (err)     err_sticky <= 1'b1;
      end
    end
  end

  wire [WIDTH-1:0] status = {{(WIDTH-9){1'b0}}, err_sticky, wr_cnt};

  // ---- read mux ----
  reg [WIDTH-1:0] rd_mux;
  always @* begin
    rd_mux = {WIDTH{1'b0}};
    if (is_data) begin
      rd_mux = rf_rdata[WIDTH-1:0];
    end else if (is_ctrl) begin
      case (off)
        2'b00:   rd_mux = ctrl_q;
        2'b01:   rd_mux = status;
        2'b10:   rd_mux = in_q;
        default: rd_mux = {WIDTH{1'b0}};
      endcase
    end
  end
  assign rdata = sel ? rd_mux : {WIDTH{1'b0}};

  // ---- scan data ----
  generate
    if (NREAD > 1) begin : g_scan
      assign scan_data = ctrl_q[0] ? rf_rdata[NREAD*WIDTH-1:WIDTH] : {SCW*WIDTH{1'b0}};
    end else begin : g_noscan
      assign scan_data = {SCW*WIDTH{1'b0}};
    end
  endgenerate
endmodule
```

### tb/Makefile

```make
# usage:  make DEPTH=16 NREAD=2 BYPASS=0 TOP=mmio_top
SIM            ?= icarus
TOPLEVEL_LANG   = verilog
DEPTH          ?= 8
NREAD          ?= 2
BYPASS         ?= 0
TOP            ?= mmio_top
VERILOG_SOURCES = $(PWD)/../rtl/regfile.v $(PWD)/../rtl/mmio_top.v
TOPLEVEL        = $(TOP)
MODULE          = $(if $(filter mmio_top,$(TOP)),test_mmio,test_regfile)
COMPILE_ARGS   += -DP_DEPTH=$(DEPTH) -DP_NREAD=$(NREAD) -DP_BYPASS=$(BYPASS)
SIM_BUILD       = sim_build_$(TOP)_d$(DEPTH)_r$(NREAD)_b$(BYPASS)
export DEPTH NREAD BYPASS
include $(shell cocotb-config --makefiles)/Makefile.sim
```

### Makefile (repo root) and .gitignore

The recipe lines under each target must start with a TAB, not spaces.

```make
PERIOD ?= 4.0

test:
	$(MAKE) -C tb TOP=regfile  DEPTH=8 NREAD=2 BYPASS=0
	$(MAKE) -C tb TOP=mmio_top DEPTH=8 NREAD=2 BYPASS=0

test-all:
	@for top in regfile mmio_top; do for d in 8 16 32 64; do for r in 1 2 4; do for b in 0 1; do \
	  echo "== $$top D=$$d R=$$r B=$$b"; \
	  $(MAKE) -s -C tb TOP=$$top DEPTH=$$d NREAD=$$r BYPASS=$$b > /tmp/t.log 2>&1; \
	  grep -q "FAIL=0" /tmp/t.log || { tail -40 /tmp/t.log; exit 1; }; \
	done; done; done; done; echo ALL PASS

sweep:
	python3 scripts/sweep.py --period $(PERIOD) --jobs 1

parse:
	python3 scripts/parse.py

analyse:
	python3 scripts/analyse.py

.PHONY: test test-all sweep parse analyse
```

```
sim_build*/
__pycache__/
results.xml
*.vcd
runs/*/make.log
```

### tb/test\_regfile.py

```python
"""Tests for the bare register file (core-only design)."""
import os, random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

D = int(os.environ.get("DEPTH", 8))
R = int(os.environ.get("NREAD", 2))
B = int(os.environ.get("BYPASS", 0))
W = 16
AW = (D - 1).bit_length()
MASK = (1 << W) - 1


async def setup(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    dut.rst.value = 1
    dut.we.value = 0
    dut.waddr.value = 0
    dut.wdata.value = 0
    dut.raddr.value = 0
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.rst.value = 0


def pack(addrs):
    return sum(a << (p * AW) for p, a in enumerate(addrs))


async def write(dut, a, d):
    await FallingEdge(dut.clk)
    dut.we.value = 1
    dut.waddr.value = a
    dut.wdata.value = d
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.we.value = 0


async def read_all(dut, addrs):
    dut.raddr.value = pack(addrs)
    await Timer(1, units="ns")
    v = int(dut.rdata.value)
    return [(v >> (p * W)) & MASK for p in range(R)]


@cocotb.test()
async def reset_clears_everything(dut):
    await setup(dut)
    for a in range(D):
        assert (await read_all(dut, [a] * R)) == [0] * R


@cocotb.test()
async def write_then_read_every_address(dut):
    await setup(dut)
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        await write(dut, a, vals[a])
    for a in range(D):
        assert (await read_all(dut, [a] * R)) == [vals[a]] * R


@cocotb.test()
async def same_cycle_read_of_written_address(dut):
    await setup(dut)
    await write(dut, 1 % D, 0x1111)
    await FallingEdge(dut.clk)
    dut.we.value = 1
    dut.waddr.value = 1 % D
    dut.wdata.value = 0x2222
    got = await read_all(dut, [1 % D] * R)
    expect = 0x2222 if B else 0x1111
    assert got == [expect] * R, f"BYPASS={B}: got {got}, expected {expect:#x}"
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.we.value = 0
    assert (await read_all(dut, [1 % D] * R)) == [0x2222] * R


@cocotb.test()
async def no_write_when_we_is_low(dut):
    await setup(dut)
    await write(dut, 0, 0xAAAA)
    await FallingEdge(dut.clk)
    dut.we.value = 0
    dut.waddr.value = 0
    dut.wdata.value = 0x5555
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    assert (await read_all(dut, [0] * R))[0] == 0xAAAA


@cocotb.test()
async def random_traffic(dut):
    await setup(dut)
    model = [0] * D
    n = int(os.environ.get("TRAFFIC", 3000))
    for _ in range(n):
        await FallingEdge(dut.clk)
        we = random.randint(0, 1)
        wa = random.randrange(D)
        wd = random.getrandbits(W)
        ras = [random.randrange(D) for _ in range(R)]
        dut.we.value = we
        dut.waddr.value = wa
        dut.wdata.value = wd
        got = await read_all(dut, ras)
        for p, a in enumerate(ras):
            exp = wd if (B and we and wa == a) else model[a]
            assert got[p] == exp, f"port {p} addr {a}: got {got[p]:#x} exp {exp:#x}"
        await RisingEdge(dut.clk)
        if we:
            model[wa] = wd
```

### tb/test\_mmio.py

```python
"""Tests for the register file behind the memory-mapped bus (bus design)."""
import os, random
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

D = int(os.environ.get("DEPTH", 8))
R = int(os.environ.get("NREAD", 2))
B = int(os.environ.get("BYPASS", 0))
W = 16
AW = (D - 1).bit_length()
MASK = (1 << W) - 1

DATA_BASE = 0
CTRL_BASE = 1 << AW          # region 1
CTRL, STATUS, INPUT = CTRL_BASE + 0, CTRL_BASE + 1, CTRL_BASE + 2
UNMAPPED_A = CTRL_BASE + 3   # region 1, offset 3
UNMAPPED_B = 2 << AW         # region 2


class Bus:
    """The testbench plays the CPU: it only drives a bus."""

    def __init__(self, dut):
        self.dut = dut

    async def reset(self):
        d = self.dut
        cocotb.start_soon(Clock(d.clk, 10, units="ns").start())
        d.rst.value = 1
        d.sel.value = 0
        d.we.value = 0
        d.addr.value = 0
        d.wdata.value = 0
        d.scan_addr.value = 0
        d.in_port.value = 0
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.rst.value = 0

    async def write(self, a, v):
        d = self.dut
        await FallingEdge(d.clk)
        d.sel.value = 1
        d.we.value = 1
        d.addr.value = a
        d.wdata.value = v
        await Timer(1, units="ns")
        err = int(d.err.value)
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.sel.value = 0
        d.we.value = 0
        return err

    async def read(self, a):
        d = self.dut
        await FallingEdge(d.clk)
        d.sel.value = 1
        d.we.value = 0
        d.addr.value = a
        await Timer(1, units="ns")
        v = int(d.rdata.value)
        err = int(d.err.value)
        await RisingEdge(d.clk)
        await FallingEdge(d.clk)
        d.sel.value = 0
        return v, err


def scan_word(dut, p):
    v = int(dut.scan_data.value)
    return (v >> (p * W)) & MASK


@cocotb.test()
async def reset_state(dut):
    b = Bus(dut)
    await b.reset()
    for a in range(D):
        assert await b.read(DATA_BASE + a) == (0, 0)
    assert await b.read(CTRL) == (0, 0)
    assert await b.read(STATUS) == (0, 0)
    assert await b.read(INPUT) == (0, 0)


@cocotb.test()
async def data_region_write_read(dut):
    b = Bus(dut)
    await b.reset()
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        assert await b.write(DATA_BASE + a, vals[a]) == 0
    for a in range(D):
        assert await b.read(DATA_BASE + a) == (vals[a], 0)


@cocotb.test()
async def ctrl_register_behaviour(dut):
    b = Bus(dut)
    await b.reset()
    await b.write(CTRL, 0x7ABC)
    assert (await b.read(CTRL))[0] == 0x7ABC
    await b.write(CTRL, 0xFFFF)               # bit15 is a clear pulse, reads 0
    assert (await b.read(CTRL))[0] == 0x7FFF


@cocotb.test()
async def unmapped_access_sets_error(dut):
    b = Bus(dut)
    await b.reset()
    for a in (UNMAPPED_A, UNMAPPED_B, (3 << AW) + 1):
        v, e = await b.read(a)
        assert (v, e) == (0, 1), f"addr {a}: {v:#x}, err {e}"
        assert await b.write(a, 0x1234) == 1
    st, _ = await b.read(STATUS)
    assert (st >> 8) & 1 == 1, "sticky error not set"


@cocotb.test()
async def write_counter_and_clear(dut):
    b = Bus(dut)
    await b.reset()
    for i in range(5):
        await b.write(DATA_BASE + (i % D), i)
    assert (await b.read(STATUS))[0] & 0xFF == 5
    await b.write(CTRL, 0x8000)               # clear
    assert (await b.read(STATUS))[0] == 0
    for i in range(260):                      # 8-bit counter wraps
        await b.write(DATA_BASE, i & MASK)
    assert (await b.read(STATUS))[0] & 0xFF == 260 % 256
    await b.write(UNMAPPED_B, 1)
    assert (await b.read(STATUS))[0] >> 8 == 1
    await b.write(CTRL, 0x8000)
    assert (await b.read(STATUS))[0] == 0


@cocotb.test()
async def input_register(dut):
    b = Bus(dut)
    await b.reset()
    dut.in_port.value = 0xBEEF
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert (await b.read(INPUT))[0] == 0xBEEF
    dut.in_port.value = 0x1234
    await RisingEdge(dut.clk)
    await RisingEdge(dut.clk)
    assert (await b.read(INPUT))[0] == 0x1234


@cocotb.test()
async def idle_bus_reads_zero(dut):
    b = Bus(dut)
    await b.reset()
    await b.write(DATA_BASE, 0xFFFF)
    await FallingEdge(dut.clk)
    dut.sel.value = 0
    dut.addr.value = DATA_BASE
    await Timer(1, units="ns")
    assert int(dut.rdata.value) == 0


@cocotb.test()
async def scan_ports(dut):
    if R < 2:
        return
    b = Bus(dut)
    await b.reset()
    vals = [random.getrandbits(W) for _ in range(D)]
    for a in range(D):
        await b.write(DATA_BASE + a, vals[a])
    dut.scan_addr.value = sum((p % D) << ((p - 1) * AW) for p in range(1, R))
    await Timer(1, units="ns")
    assert int(dut.scan_data.value) == 0, "scan data must be 0 while SCAN_EN = 0"
    await b.write(CTRL, 0x0001)
    dut.scan_addr.value = sum((p % D) << ((p - 1) * AW) for p in range(1, R))
    await Timer(1, units="ns")
    for p in range(1, R):
        assert scan_word(dut, p - 1) == vals[p % D]


@cocotb.test()
async def scan_port_bypass_behaviour(dut):
    if R < 2:
        return
    b = Bus(dut)
    await b.reset()
    await b.write(CTRL, 0x0001)
    await b.write(DATA_BASE + 1, 0x1111)
    await FallingEdge(dut.clk)
    dut.scan_addr.value = sum(1 << ((p - 1) * AW) for p in range(1, R))
    dut.sel.value = 1
    dut.we.value = 1
    dut.addr.value = DATA_BASE + 1
    dut.wdata.value = 0x2222
    await Timer(1, units="ns")
    expect = 0x2222 if B else 0x1111
    assert scan_word(dut, 0) == expect, f"BYPASS={B}: {scan_word(dut, 0):#x}"
    await RisingEdge(dut.clk)
    await FallingEdge(dut.clk)
    dut.sel.value = 0
    dut.we.value = 0


@cocotb.test()
async def random_bus_traffic(dut):
    b = Bus(dut)
    await b.reset()
    model = [0] * D
    ctrl = 0
    n = int(os.environ.get("TRAFFIC", 1500))
    for _ in range(n):
        a = random.randrange(D)
        if random.random() < 0.5:
            v = random.getrandbits(W)
            await b.write(DATA_BASE + a, v)
            model[a] = v
        else:
            assert await b.read(DATA_BASE + a) == (model[a], 0)
        if random.random() < 0.05:
            ctrl = random.getrandbits(W) & 0x7FFF
            await b.write(CTRL, ctrl)
            assert (await b.read(CTRL))[0] == ctrl
```

### scripts/sweep.py

```python
#!/usr/bin/env python3
"""Generate one ORFS config per design point and run the flow.

Examples:
  python3 scripts/sweep.py --period 4.0 --only bus_d8_r1 --dry   # show, do not run
  python3 scripts/sweep.py --period 4.0 --only bus_d8_r1         # one real run
  python3 scripts/sweep.py --period 4.0                          # all 24 points
Needs: `source ~/OpenROAD-flow-scripts/env.sh` first, so `openroad` and `yosys` are on PATH.
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
        sys.exit("openroad/yosys not on PATH. Run: source ~/OpenROAD-flow-scripts/env.sh")
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
```

### scripts/keys.py

```python
#!/usr/bin/env python3
"""Print metric keys (and values) of a finished run that contain a substring.
usage: python3 scripts/keys.py bus_d8_r1 power
       python3 scripts/keys.py bus_d8_r1 area"""
import json, os, pathlib, sys
FLOW = pathlib.Path(os.environ.get("ORFS_FLOW", pathlib.Path.home() / "OpenROAD-flow-scripts" / "flow"))
rid, sub = sys.argv[1], sys.argv[2].lower()
logdir = FLOW / "logs" / "sky130hd" / ("rb_" + rid) / "base"
for f in sorted(logdir.glob("*.json")):
    d = json.loads(f.read_text())
    for k, v in d.items():
        if sub in k.lower():
            print(f"{f.name:22s} {k} = {v}")
```

### scripts/parse.py

The three key constants and the `synth_counts` regex are the parts most likely to need a fix on D5.

```python
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
```

### scripts/analyse.py

```python
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
```

## Troubleshooting

Try one fix, rerun, and note the result in your log before trying a second. Entries marked "check" are things I could not verify against a live run.

| Symptom | Likely cause | What to do |
| --- | --- | --- |
| `openroad: command not found` | Environment not loaded | `source ~/OpenROAD-flow-scripts/env.sh` |
| `sweep.py` says the flow directory is not found | Your ORFS folder is somewhere else | `export ORFS_FLOW=$HOME/OpenROAD-flow-scripts/flow` |
| `ModuleNotFoundError: cocotb` or `cocotb-config: command not found` | Python venv not active | `source ~/venvs/rf/bin/activate` |
| `make: *** missing separator` in the root Makefile | Spaces where a TAB must be | Retype the indent of recipe lines as a TAB |
| Flop count after synthesis ignores your DEPTH | The `-D` defines did not reach Yosys | Check `grep VERILOG_DEFINES ~/OpenROAD-flow-scripts/flow/scripts/synth_preamble.tcl` finds something, and that `runs/<id>/config.mk` has the line. If your ORFS has `VERILOG_TOP_PARAMS`, you can instead write `export VERILOG_TOP_PARAMS = DEPTH 16 NREAD 2 BYPASS 0` in the config. Last resort: generate a tiny wrapper module per run with the parameters fixed (check) |
| Synthesis stops complaining about memory size | `SYNTH_MEMORY_MAX_BITS` (the ORFS docs list 4096 as the default) | Your largest point is 2,048 bits, so this should not trigger. If it does, read the variable's entry in the flow variable docs. Do not use `SYNTH_MOCK_LARGE_MEMORIES`: it shrinks memories to one row and ruins the comparison |
| Placement fails, or the log recommends a minimum placement density | Too tight for a small design | Raise `PLACE_DENSITY_LB_ADDON` or lower `CORE_UTILIZATION`, then rerun every point with the same value so the comparison stays fair |
| A run sits in timing repair for a very long time | Target period far too tight | Use a larger period. Rerun the probes from D7 |
| Every slack is large and positive | Period too loose, so `period_est_ns` says little | Pick a tighter period and rerun the probes |
| Every slack is hugely negative | Period too tight | Pick a looser one |
| `gui_final` does not open a window | WSLg missing or outdated | Run `wsl --update` in PowerShell, restart WSL. Fallback: view the GDS with `klayout` and read the text reports |
| `parse.py` says area or slack key missing | Key names differ on your install | `python3 scripts/keys.py <id> area` and edit the constants at the top of `parse.py` |
| `n_flops` is 0 in the CSV | The `synth_stat.txt` layout differs from my regex | Open one file, copy three cell lines, adapt `synth_counts()` |
| Power column is NaN | Power key name differs | `python3 scripts/keys.py <id> power`, then fix `KEY_POWER` |
| Sweep died when you closed the terminal or the laptop slept | Foreground process, or Windows sleep | Use `nohup ... &`, set sleep to Never, rerun. Finished points are skipped |
| Disk filling up | ORFS results and objects folders are large | `df -h` and `du -sh ~/OpenROAD-flow-scripts/flow/{results,objects,logs}`. Keep logs and reports. Wipe probe runs you no longer need with `make clean_all` on their config |
| A bigger design has a smaller area than a smaller one | Optimiser decisions, or a wrong parameter | Check flop counts first, then the log for that point. Write the explanation in `log/anomalies.md` |
| Rerun gives a different number | Possible nondeterminism or a changed config | Diff the two `config.mk` files. If they match, report the difference as your noise level |
| By D9 the sweep is far from done | Machine too slow | Cut the 64-entry points for 2 read ports, say so in the report's limitations, and keep complete core and bus pairs |

## Write-up templates

Everything in angle brackets is a placeholder. Fill it only with a number you measured, and delete any line you cannot fill. Write in your own words, in short plain sentences.

**README skeleton**

```markdown
# Register-Bus: what a bus interface costs a small register file

**Question.** How much area, speed and power does a memory-mapped bus
interface add to a flip-flop register file, and how does that change with
the number of entries and read ports?

**Short answer.** <one sentence with your main numbers from results/summary.md>

## Design
What regfile.v and mmio_top.v do, the address map, the scan ports, and why.

## Verification
What the tests check, the Python reference model, the mutation checks
(<n> breaks, <n> caught), and the <n> configurations that pass.

## Method
Platform, flow settings held constant, the clock period and how you chose it,
the metric definitions, tool versions.

## Results
### Interface overhead
Table and plot 4. Verdict on H2.
### Bandwidth per area
Plot 5. Verdict on H5.
### Cost model and its test on unseen points
Coefficients, R^2, error on entries = 64, error on the two unseen points.
### What goes critical
The 3-row critical path table and screenshots. Verdict on H3.

## Limitations
One PDK and corner. Default switching activity for power. Flip-flop storage
only. Fixed utilisation. period_est_ns is an estimate. DRC and LVS: <status>.
Failed or odd runs: <list>.

## Prior work
OpenROAD's RegFileStudy (link). What is different here: <two sentences>.

## Reproduce
Exact commands from a clean clone: make test-all, the sweep command with
your period, make parse, make analyse.
```

**Resume bullets (2 or 3, choose the ones that are true)**

- Designed a parameterised register file and a memory-mapped bus wrapper in Verilog, verified with cocotb against a Python reference model (\<n> tests, \<n> deliberate bugs caught).
- Automated \<n> OpenROAD-flow-scripts runs on sky130hd and measured the bus interface cost at \<x> to \<y> % of core area, falling as entries grow from \<a> to \<b>.
- Fitted an area cost model (R² \<r2>) and predicted \<n> unseen configurations to within \<e> % of the flow result.

If a number is not in `sweep.csv` or `summary.md`, the bullet loses that number.

**Post, 5 lines**

- The question in one sentence.
- One plot, the one a stranger would understand fastest.
- One finding, with its number.
- One thing that surprised you or that you got wrong.
- The repo link, and a thank-you to the RegFileStudy authors for the idea of studying register files this way.

## Stretch goals, in priority order

Start none of these until the Definition of Done at the top is fully ticked, except S1 and S2, which have slots on D16. Each one that finishes gets its own short section in the report. One that does not finish gets a single line under "not done".

| # | Goal | What you add | Effort | Day |
| --- | --- | --- | --- | --- |
| S1 | Cost of the same-cycle bypass | 8 runs with BYPASS=1 at 2 read ports. `analyse.py` already prints the comparison | 3 hours | D16 |
| S2 | Registered read output | A `REGREAD` parameter that adds a flop on `rdata`. Update the tests for one cycle of latency. Compare area and period at 4 sizes. This is the classic speed-for-latency trade | half a day | D16 |
| S3 | Second platform | Rerun 3 points (8 × 1, 32 × 2, 64 × 4, core and bus) on nangate45. Compare scaling ratios, not absolute numbers, since the libraries differ. Needs `PLATFORM` and the folder names changed in the scripts | half a day | D17 |
| S4 | One formal property | With SymbiYosys: after a write to address a, a later read of a returns that data until the next write to a. Check the install route first and skip it if it is not working by midday | 1 day | D17 if time |
| S5 | CI | A GitHub Actions job that runs `make test` on every push (workflow below, untested) | 2 hours | D18 if the buffer is unused |

```yaml
name: tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: sudo apt-get update && sudo apt-get install -y iverilog
      - run: pip install "cocotb<2"
      - run: make test
```

**After the deadline, not before**

- FP8 vs posit8 multiplier, reusing `sweep.py`, `parse.py` and `analyse.py`. Memory-movement angle: smaller number formats move fewer bytes per operation, so compare bytes moved per result as well as area (a guess to test, not a claim).
- Banked register file against a flat one.
- Latch-based storage, which is smaller but much harder to time.
- A tiny cache-style block built on the register file, to touch the memory hierarchy from the video.

What this project will not teach you: manufacturing, test, packaging, customers and pricing. Those come from internships, reading and talking to people in industry.
