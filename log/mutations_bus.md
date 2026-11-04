# Mutation tests: mmio_top.v

Generated: 2026-11-05 01:43

| # | Break | Depth | Read ports | Bypass | Result | Caught |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | write counter adds 2 | 8 | 2 | 0 | TESTS=10 PASS=9 FAIL=1 | yes |
| 2 | offset 3 treated as mapped | 8 | 2 | 0 | TESTS=10 PASS=9 FAIL=1 | yes |
| 3 | scan gate removed | 8 | 2 | 0 | TESTS=10 PASS=9 FAIL=1 | yes |
| 4 | bypass ignored | 8 | 2 | 1 | TESTS=10 PASS=9 FAIL=1 | yes |
