# Results: bus wrapper (D3) and bus tests (D4)

Generated: 2026-11-03 00:54
Commit before this run: 58695c1
Tools: Icarus Verilog version 11.0 (stable) (), cocotb 1.9.2, Yosys 0.68+post

## Compile check: rtl/mmio_top.v with iverilog -Wall

| Depth | Read ports | Result |
| --- | --- | --- |
| 8 | 1 | ok, no warnings |
| 8 | 2 | ok, no warnings |
| 8 | 4 | ok, no warnings |
| 16 | 1 | ok, no warnings |
| 16 | 2 | ok, no warnings |
| 16 | 4 | ok, no warnings |
| 32 | 1 | ok, no warnings |
| 32 | 2 | ok, no warnings |
| 32 | 4 | ok, no warnings |
| 64 | 1 | ok, no warnings |
| 64 | 2 | ok, no warnings |
| 64 | 4 | ok, no warnings |

## Simulation: cocotb tests at every setting

| Design | Depth | Read ports | Bypass | Result |
| --- | --- | --- | --- | --- |
| regfile | 8 | 1 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 8 | 1 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 8 | 2 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 8 | 2 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 8 | 4 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 8 | 4 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 1 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 1 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 2 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 2 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 4 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 16 | 4 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 1 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 1 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 2 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 2 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 4 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 32 | 4 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 1 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 1 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 2 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 2 | 1 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 4 | 0 | TESTS=5 PASS=5 FAIL=0 |
| regfile | 64 | 4 | 1 | TESTS=5 PASS=5 FAIL=0 |
