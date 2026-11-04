# Predictions for the validation runs, written 4 Nov 2026 before any of them run

Model from results/summary.md (fit on 9 points per design: 8, 16, 32 entries x 1, 2, 4 read ports):
- core: A = -598 + 739.72 D + 161.36 R D
- bus:  A = 1096 + 789.68 D + 167.01 R D

| Run | Kind | Predicted area (um2) | Type |
|---|---|---|---|
| 128 entries x 2 ports | core | 135394 | extrapolation (D outside the fit) |
| 128 entries x 2 ports | bus | 144930 | extrapolation |
| 16 entries x 3 ports | core | 18983 | interpolation (R=3 not in the fit) |
| 16 entries x 3 ports | bus | 21747 | interpolation |

Predicted interface overhead: 128 x 2 about 9536 um2 (7.0%). 16 x 3 about 2765 um2 (14.6%).
Coefficients are rounded in summary.md, so the predictions may differ from the exact model by about 0.1%.
