# Hypotheses and predictions, written 4 Nov 2026 before the sweep

Data seen so far: core and bus at 8 entries, 1 read port (core 7104 um2, bus 9390 um2, +32.2%). These are not predictions.
Finished but not opened: core and bus at 16x1 and 32x1. They were started before this file existed. I have not looked at their numbers.
Not run yet: everything else.

All numbers below are guesses from cell sizes (about 30 um2 per enable flop, 11 um2 per mux2, 7 mux2 per bit per read port at 8 entries).

H1. Area of each design fits A = c0 + c1*D + c2*R*D. Largest relative residual under 10% on the 12 grid points. Core 64x4 area about 95000 um2, plus or minus 25%.
H2. Bus overhead as a share of core area falls as entries grow. At 64x1 the overhead is 2000 to 3500 um2, which is 3 to 6% of the core. At 64x4 it is under 4%.
H3. At 64x4 the worst bus path starts at an addr input bit and ends at an rdata output bit.
H4. Spearman rank correlation between power and area over the 24 runs is at least 0.95.
H5. bw_per_kum2 at NREAD=4 is 1.5 to 2.5 times the NREAD=1 value, at every depth.
