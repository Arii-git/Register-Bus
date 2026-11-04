## Area cost model: area = c0 + c1*entries + c2*(read ports * entries)

- core: c0=-598, c1=739.72, c2=161.36 um^2, R^2=0.9971, max residual 7.0%
- bus: c0=1096, c1=789.68, c2=167.01 um^2, R^2=0.9979, max residual 6.8%

## Interface overhead (bus minus core), area

- 8 x 1: +2286 um^2 (32.2%), period estimate change +0.54 ns
- 16 x 1: +2684 um^2 (20.2%), period estimate change -0.07 ns
- 32 x 1: +4043 um^2 (14.5%), period estimate change +0.00 ns
- 8 x 2: +2057 um^2 (24.2%), period estimate change +0.60 ns
- 16 x 2: +2352 um^2 (14.8%), period estimate change -0.04 ns
- 32 x 2: +2868 um^2 (8.3%), period estimate change -0.02 ns
- 8 x 4: +2327 um^2 (21.4%), period estimate change +0.55 ns
- 16 x 4: +2975 um^2 (14.6%), period estimate change -0.02 ns
- 32 x 4: +4272 um^2 (9.7%), period estimate change -0.05 ns
