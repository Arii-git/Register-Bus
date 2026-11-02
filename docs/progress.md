# Progress

Project: a 16-bit register file wrapped in a memory-mapped bus, measured through OpenROAD (sky130hd) to find what the bus costs in area, timing and power. Deadline 14 Nov 2026.

## Done

| Day | What | Where |
| --- | --- | --- |
| 1 | Tools run through Docker (`rf`), versions pinned, metric names found | `log/versions.md`, `log/keys.md` |
| 2 | Register file, 5 tests, Yosys count (224 muxes, 128 flops), 3 mutation tests | `rtl/regfile.v`, `tb/test_regfile.py`, `log/mutations.md` |
| 3 | Bus wrapper: address decode, CTRL, STATUS, INPUT, read mux, scan output | `rtl/mmio_top.v`, `docs/spec.md` |
| 4 | Bus tests: 10 tests playing the processor | `tb/test_mmio.py` |

## Results so far

- Bus wrapper compiles with no warnings at 12 sizes: `log/results_compile_mmio_top.md`
- Register file tests pass in all 24 settings: `log/results_regfile.md`
- Bus tests pass in all 24 settings: `log/results_mmio_top.md`

A setting is one combination of depth (8, 16, 32, 64), read ports (1, 2, 4) and bypass (0, 1).

## Address map

The address is AW+2 bits. The top 2 bits pick the region and the bottom bits pick the box.

| Region | Contents |
| --- | --- |
| 0 | Data boxes (the register file) |
| 1 | Offset 0 CTRL, 1 STATUS, 2 INPUT, 3 unmapped |
| 2, 3 | Unmapped, `err` goes high |

## Still to do

- Mutation tests on the bus
- The 24-run OpenROAD sweep, then charts and the write-up
