# sweep.py

One line per function in `scripts/sweep.py`.

- `points()`: yields the 24 grid points (depths 8, 16, 32, 64 × read ports 1, 2, 4 × core and bus), depth first.
- `run_id(kind, d, r, b)`: builds the run name, for example `bus_d8_r1`, from kind, depth, read ports, bypass and `TAG`. It does not include the clock period.
- `nickname(rid)`: adds the `rb_` prefix for the flow's results folder.
- `write_inputs(kind, d, r, b, period)`: writes `constraint.sdc`, `config.mk` and `meta.json` into `runs/<id>`.
- `done(rid)`: true when the flow's `6_report.json` exists for that run.
- `run_one(args, kind, d, r, b)`: writes the inputs, skips finished points unless `--force`, runs the flow into `make.log`, then adds runtime and status to `meta.json`.
- `main()`: reads the arguments (`--period`, `--only`, `--tag`, `--force`, `--dry`, `--extra`, `--jobs`), builds the point list, checks that openroad and yosys are on PATH, and runs the points.

## Known issues (not fixed yet)

- **`meta.json` is overwritten on skip.** `write_inputs` runs before the `done()` check, so a skipped run's `meta.json` takes the current `--period`. A finished 4.0 ns run can end up recording 2.5 or 6.0 ns. Fix: write `meta.json` only after the skip check.
- **Period probes collide without `--tag`.** `run_id` does not include the period, so a probe without `--tag` reuses the 4.0 ns folder and is skipped. Always pass `--tag _p25` or `--tag _p60` for probes.
- **`--dry` writes files.** `write_inputs` runs before the dry-run check, so `--dry` still writes into `runs/`.
