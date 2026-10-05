<!-- seedy:SNES -->
### Seedy — SNES: hvirq-only @ 3f054d6 vs c61bfd4

**Possible regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 3 of 30 seeds of hvirq-only, against 12 of 30 on c61bfd4. A difference that large is unlikely to be chance. The clock that fails more often is `emu c2` (5 → 20 seeds, p = < 0.001). The seed in the `.qsf` (1) does not close timing on hvirq-only (worst setup −0.390 ns, hold +0.225 ns).

**Flagged** (timing got measurably worse):

- WC slack: setup worse by 0.348 ns on average (p = 0.003); worst seed −1.892 ns
- Total negative setup slack worse by 1.575 ns on average (p = 0.013)
- fewer seeds meet timing (3/30 vs 12/30, Fisher p = 0.015)

|  | c61bfd4 | hvirq-only | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 12/30 | 3/30 | −9 | 0.02 |
| Worst setup slack (ns), average / typical seed | −0.173 / −0.089 | −0.521 / −0.395 | −0.348 / −0.305 | 0.003 |
| Worst setup slack (ns), unluckiest seed | −0.945 | −1.892 | −0.947 |  |
| Total negative slack (ns), average | −0.494 | −2.070 | −1.575 | 0.01 |
| Seeds with a hold violation | 4/30 | 1/30 | −3 | 0.35 |
| Logic used (ALMs), average | 35,138 (83.8%) | 35,087 (83.7%) | −51 | 0.005 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.452 / +0.199 ✗ | −0.390 / +0.225 ✗ | +0.062 / +0.026 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 18/30 | 21/30 | +3 | −0.089 | −0.137 | −0.048 | −0.945 | −1.892 | 0.59 |
| `pll_hdmi c0` | 10/30 | 18/30 | +8 | +0.058 | −0.025 | −0.083 | −0.217 | −0.565 | 0.07 |
| `emu c2` | 5/30 | 20/30 | +15 | +0.176 | −0.382 | −0.558 | −0.944 | −1.593 | < 0.001 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 1 seed of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 8 place(s) the baseline never fails: `ascal|o_poly_lum` (2), `emu|ddram|ram_address` (1), `emu|ddram|ram_burst` (1), `emu|ddram|state.10` (1), `hdmi_out_de` (1), `ascal|o_vcpt_pre3` (1), `auto_generated|altsyncram4|ram_block5a0~porta_datain_reg17` (1), `vs_r` (1). Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 18** (meets timing; worst slack +0.248 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −0.390 ns).

<details><summary>Top 5 seeds of hvirq-only</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 18 | ✓ | +0.248 | +0.260 | +0.248 | +4.443 | +0.665 | – | 81.20 | 35,031 |
| 15 | ✓ | +0.133 | +0.133 | +0.249 | +4.137 | +0.998 | – | 79.50 | 35,111 |
| 14 | ✓ | +0.110 | +0.110 | +0.252 | +3.127 | +0.763 | – | 74.78 | 35,274 |
| 4 |  | −0.057 | −0.057 | +0.052 | +4.213 | +0.923 | −0.549 | 75.59 | 35,133 |
| 9 |  | −0.110 | −0.110 | +0.179 | +3.801 | +0.679 | −0.131 | 84.28 | 35,010 |

</details>

<details><summary>How to read this</summary>

- **Slack** is how much time a signal has to spare, in nanoseconds, under Quartus's worst-case model of the chip. Positive means on time; negative means late *in the model*.
- **Setup** means a signal must arrive before the next clock tick. A small negative setup slack (tens to a few hundred ps) is common in released MiSTer cores and usually works, because the model assumes a 100 °C chip. The risk grows with heat and varies from chip to chip.
- **Hold** means a signal must stay steady just after the tick. A cooler chip or a slower clock does not fix a hold violation, so it is the more serious of the two.
- **Closes timing** (✓, "met") means every setup, hold, recovery and removal slack of that seed is ≥ 0. A seed that doesn't close still builds and usually runs; it just has no guaranteed margin. Maintainers rebuild with other seeds until a release build closes.
- **Seed** shuffles where the fitter places logic. Each seed is an independent random draw, so one build proves little; Seedy compiles many seeds of both sides and compares the two groups. A PR should not make the group worse.
- **Total negative slack** adds up the lateness of every failing path: 0 when a seed closes, more negative when more paths fail or fail by more.
- **Recovery / removal** are setup and hold for reset signals. They appear above only when some seed fails them.
- **Δ** is this PR minus the baseline. For slack, negative Δ means less margin. For ALMs, negative means smaller.
- **p** is the chance of seeing a difference this large if the PR changed nothing. Below 0.05 deserves a look; about ten numbers are tested, so an occasional p < 0.05 is expected by chance alone.
- **Timing constraints** (the `.sdc` files) tell Quartus each clock's speed and which paths to check. A path with no constraint, or under a constraint that matches nothing, is never checked, so good slack says nothing about it.
- **Corner** is the temperature and voltage case the model assumes. Seedy's headline uses the corners the core's own Quartus report uses (MiSTer's template reports only slow 100 °C); every corner is in the detail tables.

</details>
<details><summary>Statistics (all metrics)</summary>

| metric | baseline mean | PR mean | Δ mean | median diff [95% CI] | perm. p |  |
|---|---|---|---|---|---|---|
| f(MAX) geomean | 78.72 | 78.89 | +0.17 | +0.05 [−1.45, +1.77] | 0.77 |  |
| WC slack: setup | −0.173 | −0.521 | −0.348 | −0.305 [−0.471, −0.080] | 0.003 | ⚠️ flagged |
| WC slack: hold | +0.154 | +0.182 | +0.029 | +0.011 [−0.044, +0.052] | 0.41 |  |
| WC slack: recovery | +3.731 | +3.613 | −0.118 | −0.064 [−0.365, +0.186] | 0.27 |  |
| WC slack: removal | +0.807 | +0.789 | −0.018 | −0.001 [−0.098, +0.072] | 0.56 |  |
| Total negative setup slack | −0.494 | −2.070 | −1.575 | −0.587 [−0.975, −0.160] | 0.01 | ⚠️ flagged |
| Logic utilization | 35,138 | 35,087 | −51 | −56 [−99, +9] | 0.005 |  |
| Compilation time | 00:31:09 | 00:31:19 | +00:00:11 | +00:02:20 [−00:05:06, +00:06:31] | 0.92 |  |

</details>
<details><summary>Per-seed table (60 rows)</summary>

| variant | seed | f(MAX) MHz | setup | hold | recovery | removal | ALMs | time | met |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 1 | 80.95 | −0.452 | +0.199 | +3.848 | +0.835 | 35,076 | 00:36:19 |  |
| baseline | 2 | 78.92 | +0.194 | +0.187 | +3.253 | +0.855 | 35,091 | 00:37:47 | ✓ |
| baseline | 3 | 77.85 | +0.045 | +0.258 | +3.543 | +0.712 | 35,198 | 00:43:05 | ✓ |
| baseline | 4 | 76.19 | −0.256 | +0.251 | +3.807 | +0.820 | 35,203 | 00:43:13 |  |
| baseline | 5 | 76.11 | −0.221 | +0.244 | +3.998 | +0.999 | 35,059 | 00:37:36 |  |
| baseline | 6 | 82.28 | −0.747 | +0.201 | +3.619 | +0.757 | 35,111 | 00:36:24 |  |
| baseline | 7 | 81.65 | −0.047 | +0.246 | +3.535 | +0.868 | 35,148 | 00:42:23 |  |
| baseline | 8 | 79.18 | −0.071 | −0.319 | +2.993 | +0.725 | 35,109 | 00:27:15 |  |
| baseline | 9 | 79.86 | −0.120 | +0.221 | +4.122 | +0.722 | 35,063 | 00:27:00 |  |
| baseline | 10 | 79.39 | +0.108 | +0.242 | +4.028 | +0.720 | 35,096 | 00:31:41 | ✓ |
| baseline | 11 | 75.87 | −0.566 | +0.248 | +3.842 | +0.738 | 35,221 | 00:40:13 |  |
| baseline | 12 | 78.45 | −0.428 | +0.225 | +4.105 | +0.988 | 35,064 | 00:35:17 |  |
| baseline | 13 | 76.23 | −0.218 | −0.138 | +3.800 | +0.690 | 35,219 | 00:38:59 |  |
| baseline | 14 | 76.02 | −0.945 | −0.257 | +3.978 | +1.151 | 35,317 | 00:38:27 |  |
| baseline | 15 | 78.12 | −0.643 | +0.143 | +4.325 | +0.926 | 35,237 | 00:28:57 |  |
| baseline | 16 | 76.15 | −0.087 | +0.185 | +3.982 | +0.749 | 35,267 | 00:28:06 |  |
| baseline | 17 | 79.84 | +0.052 | +0.118 | +3.566 | +1.037 | 35,064 | 00:23:07 | ✓ |
| baseline | 18 | 79.64 | +0.133 | +0.244 | +3.695 | +0.872 | 35,130 | 00:24:16 | ✓ |
| baseline | 19 | 79.98 | +0.036 | +0.224 | +4.186 | +0.899 | 35,086 | 00:25:22 | ✓ |
| baseline | 20 | 77.21 | +0.258 | +0.015 | +3.980 | +0.776 | 35,212 | 00:28:23 | ✓ |
| baseline | 21 | 79.32 | +0.074 | +0.191 | +3.746 | +0.829 | 35,148 | 00:28:16 | ✓ |
| baseline | 22 | 76.77 | −0.092 | +0.250 | +3.205 | +0.686 | 35,182 | 00:33:22 |  |
| baseline | 23 | 78.98 | −0.352 | +0.228 | +3.241 | +0.862 | 35,036 | 00:28:54 |  |
| baseline | 24 | 76.76 | −0.100 | +0.248 | +3.869 | +0.687 | 35,161 | 00:32:46 |  |
| baseline | 25 | 79.36 | −0.944 | +0.183 | +3.542 | +0.689 | 35,123 | 00:26:54 |  |
| baseline | 26 | 80.58 | +0.183 | +0.193 | +4.306 | +0.686 | 35,115 | 00:26:02 | ✓ |
| baseline | 27 | 79.09 | +0.396 | +0.250 | +3.692 | +0.632 | 35,122 | 00:27:04 | ✓ |
| baseline | 28 | 77.68 | −0.434 | −0.102 | +3.583 | +0.834 | 35,103 | 00:24:50 |  |
| baseline | 29 | 80.57 | +0.031 | +0.246 | +3.816 | +0.703 | 35,115 | 00:16:23 | ✓ |
| baseline | 30 | 82.51 | +0.032 | +0.192 | +2.713 | +0.755 | 35,076 | 00:15:56 | ✓ |
| candidate | 1 | 78.73 | −0.390 | +0.225 | +3.928 | +0.741 | 35,060 | 00:35:16 |  |
| candidate | 2 | 80.30 | −0.399 | +0.056 | +3.334 | +0.875 | 35,013 | 00:35:03 |  |
| candidate | 3 | 76.77 | −0.691 | +0.254 | +3.976 | +0.781 | 35,120 | 00:40:59 |  |
| candidate | 4 | 75.59 | −0.057 | +0.052 | +4.213 | +0.923 | 35,133 | 00:41:15 |  |
| candidate | 5 | 82.39 | −0.158 | +0.195 | +3.677 | +1.020 | 35,046 | 00:36:49 |  |
| candidate | 6 | 79.71 | −0.978 | +0.241 | +3.877 | +0.722 | 35,014 | 00:36:00 |  |
| candidate | 7 | 79.74 | −0.149 | +0.064 | +3.862 | +0.723 | 35,133 | 00:41:01 |  |
| candidate | 8 | 76.21 | −0.343 | +0.180 | +3.083 | +0.619 | 35,051 | 00:27:40 |  |
| candidate | 9 | 84.28 | −0.110 | +0.179 | +3.801 | +0.679 | 35,010 | 00:27:09 |  |
| candidate | 10 | 82.08 | −0.307 | +0.095 | +2.584 | +0.720 | 35,026 | 00:29:50 |  |
| candidate | 11 | 80.18 | −0.162 | +0.258 | +3.865 | +0.899 | 35,161 | 00:39:03 |  |
| candidate | 12 | 80.12 | −0.408 | +0.245 | +3.946 | +0.768 | 35,033 | 00:33:43 |  |
| candidate | 13 | 77.56 | −0.517 | +0.257 | +3.535 | +0.891 | 35,178 | 00:39:35 |  |
| candidate | 14 | 74.78 | +0.110 | +0.252 | +3.127 | +0.763 | 35,274 | 00:39:38 | ✓ |
| candidate | 15 | 79.50 | +0.133 | +0.249 | +4.137 | +0.998 | 35,111 | 00:29:15 | ✓ |
| candidate | 16 | 74.27 | −0.433 | −0.253 | +3.344 | +0.717 | 35,195 | 00:29:33 |  |
| candidate | 17 | 82.46 | −1.186 | +0.251 | +3.083 | +0.693 | 35,038 | 00:26:20 |  |
| candidate | 18 | 81.20 | +0.260 | +0.248 | +4.443 | +0.665 | 35,031 | 00:22:09 | ✓ |
| candidate | 19 | 78.23 | −1.593 | +0.209 | +4.040 | +0.554 | 35,040 | 00:22:16 |  |
| candidate | 20 | 77.33 | −0.509 | +0.200 | +3.535 | +0.810 | 35,135 | 00:25:12 |  |
| candidate | 21 | 77.80 | −0.388 | +0.253 | +3.476 | +0.756 | 35,087 | 00:25:55 |  |
| candidate | 22 | 77.55 | −0.162 | +0.234 | +3.869 | +0.980 | 35,152 | 00:32:16 |  |
| candidate | 23 | 81.41 | −0.949 | +0.121 | +3.156 | +0.840 | 35,076 | 00:30:15 |  |
| candidate | 24 | 75.64 | −0.202 | +0.248 | +3.819 | +0.902 | 35,163 | 00:36:08 |  |
| candidate | 25 | 81.95 | −0.441 | +0.135 | +2.790 | +0.795 | 35,016 | 00:33:22 |  |
| candidate | 26 | 74.37 | −1.334 | +0.253 | +3.990 | +0.716 | 35,060 | 00:33:13 |  |
| candidate | 27 | 79.45 | −0.189 | +0.255 | +3.526 | +0.815 | 35,131 | 00:30:01 |  |
| candidate | 28 | 78.03 | −1.892 | +0.172 | +2.991 | +0.838 | 35,040 | 00:27:23 |  |
| candidate | 29 | 78.61 | −0.604 | +0.220 | +3.820 | +0.741 | 35,032 | 00:16:42 |  |
| candidate | 30 | 80.45 | −1.583 | +0.125 | +3.560 | +0.720 | 35,064 | 00:16:34 |  |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.118 / +7.349 | +5.692 / +7.666 | −0.426 / +0.317 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.270 / +4.986 | +4.413 / +5.278 | +0.143 / +0.293 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +6.606 / +8.681 | +5.168 / +8.639 | −1.438 / −0.043 | 1.00 |
| `emu c0` | 18/30 | 21/30 | +3 | −0.945 / −0.089 | −1.892 / −0.137 | −0.947 / −0.048 | 0.59 |
| `emu c1` | 0/30 | 0/30 | 0 | +6.657 / +7.694 | +6.210 / +7.898 | −0.447 / +0.204 | 1.00 |
| `emu c2` | 5/30 | 20/30 | +15 | −0.944 / +0.176 | −1.593 / −0.382 | −0.649 / −0.558 | < 0.001 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.122 / +3.368 | +1.089 / +3.539 | −0.033 / +0.171 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.442 / +14.337 | +13.078 / +14.303 | −0.364 / −0.034 | 1.00 |
| `pll_hdmi c0` | 10/30 | 18/30 | +8 | −0.217 / +0.058 | −0.565 / −0.025 | −0.348 / −0.083 | 0.07 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.471 / +5.390 | +3.899 / +5.838 | −0.572 / +0.447 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.119 / +0.164 | +0.129 / +0.164 | +0.010 / −0.001 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.114 / +0.167 | +0.120 / +0.167 | +0.006 / +0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.082 / +0.124 | +0.016 / +0.139 | −0.066 / +0.015 | 1.00 |
| `emu c0` | 5/30 | 2/30 | −3 | −0.319 / +0.164 | −0.253 / +0.164 | +0.066 / +0.000 | 0.42 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.075 / +0.117 | +0.021 / +0.115 | −0.054 / −0.002 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.076 / +0.100 | +0.082 / +0.099 | +0.006 / −0.001 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.134 / +0.155 | +0.131 / +0.155 | −0.003 / +0.000 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.115 / +0.120 | +0.100 / +0.121 | −0.015 / +0.001 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.035 / +0.103 | +0.002 / +0.106 | −0.033 / +0.003 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.139 / +0.153 | +0.135 / +0.166 | −0.004 / +0.013 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 72.04 / 79.62 | 69.89 / 81.21 | −2.15 / +1.58 |
| `FPGA_CLK2_50` | 63.57 / 67.24 | 64.16 / 67.84 | +0.59 / +0.59 |
| `altera_reserved_tck` | 49.70 / 63.43 | 43.48 / 62.27 | −6.22 / −1.16 |
| `emu c0` | 79.45 / 85.56 | 73.89 / 84.45 | −5.56 / −1.11 |
| `emu c1` | 60.28 / 67.99 | 58.82 / 66.72 | −1.46 / −1.27 |
| `emu c2` | 24.89 / 25.94 | 24.99 / 26.01 | +0.10 / +0.07 |
| `h2f_user0_clk` | 112.64 / 145.20 | 112.22 / 145.70 | −0.42 / +0.51 |
| `pll_audio` | 36.71 / 38.03 | 36.23 / 37.89 | −0.48 / −0.14 |
| `pll_hdmi c0` | 143.91 / 150.36 | 137.04 / 147.76 | −6.87 / −2.60 |
| `spi_sck` | 180.86 / 220.39 | 163.91 / 234.76 | −16.95 / +14.37 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 35,036 … 35,317 | 35,010 … 35,274 | −51 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,134 … 33,466 | 33,145 … 33,472 | −16 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:40 … 00:04:28 | 00:03:47 … 00:04:29 | 00:00:00 |
| `Assembler` | 00:00:11 … 00:00:19 | 00:00:11 … 00:00:20 | 00:00:00 |
| `Fitter` | 00:11:31 … 00:39:00 | 00:11:46 … 00:36:50 | +00:00:11 |
| `TimeQuest Timing Analyzer` | 00:00:12 … 00:00:20 | 00:00:13 … 00:00:21 | 00:00:00 |
| `Total` | 00:15:56 … 00:43:13 | 00:16:34 … 00:41:15 | +00:00:11 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,839 | 3,506 … 3,775 | −248 |
| `Assembler` | 1,898 … 1,981 | 1,897 … 1,981 | +13 |
| `Fitter` | 6,297 … 6,404 | 6,351 … 6,437 | +4 |
| `TimeQuest Timing Analyzer` | 2,326 … 2,373 | 2,335 … 2,377 | +1 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 16 | 12 | −4 |
| `CPU\|P65C816\|P` | 5 | 20 | +15 |
| `emu\|sdram\|SDRAM_nCAS` | 4 | 3 | −1 |
| `emu\|sdram\|SDRAM_nWE` | 3 | 2 | −1 |
| `emu\|ddram\|cache_addr` | 1 | 1 | 0 |
| `emu\|sdram\|SDRAM_A` | 1 | 1 | 0 |
| `emu\|sdram\|old_sni_rd` | 2 | 0 | −2 |
| `ascal\|o_poly_lum` | 0 | 2 | +2 |
| `emu\|sdram\|SDRAM_nRAS` | 1 | 1 | 0 |
| `ascal\|o_vcpt_pre3` | 0 | 1 | +1 |
| `auto_generated\|altsyncram4\|ram_block5a0~porta_datain_reg17` | 0 | 1 | +1 |
| `emu\|ddram\|ram_burst` | 0 | 1 | +1 |
| `emu\|ddram\|state.10` | 0 | 1 | +1 |
| `emu\|ddram\|cache_addr2` | 1 | 0 | −1 |
| `hdmi_out_de` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_DQ~en` | 1 | 0 | −1 |
| `sl_r` | 1 | 0 | −1 |
| `emu\|ddram\|ram_address` | 0 | 1 | +1 |
| `P65C816\|AddrGen\|PCr` | 1 | 0 | −1 |
| `vs_r` | 0 | 1 | +1 |

</details>
<details><summary>Constraint health</summary>

|  | baseline | PR | Δ |
|---|---|---|---|
| Clocks with no constraint (paths not timed) | 0 | 0 | 0 |
| Constraints that match nothing (ignored) | 0 | 0 | 0 |
| Combinational loops timed as latches | 0 | 0 | 0 |
| I/O pins with no timing constraint | 95 | 95 | 0 |
| `.sdc` files not read cleanly | 0 | 0 | 0 |

**Unconstrained I/O pins (PR):** `HDMI_I2C_SCL`, `HDMI_I2C_SDA`, `HDMI_I2S`, `HDMI_LRCLK`, `HDMI_MCLK`, `HDMI_SCLK`, `HDMI_TX_CLK`, `HDMI_TX_DE`, `HDMI_TX_D[0]`, `HDMI_TX_D[10]`, `HDMI_TX_D[11]`, `HDMI_TX_D[12]`, `HDMI_TX_D[13]`, `HDMI_TX_D[14]`, `HDMI_TX_D[15]`, `HDMI_TX_D[16]`, `HDMI_TX_D[17]`, `HDMI_TX_D[18]`, `HDMI_TX_D[19]`, `HDMI_TX_D[1]`, `HDMI_TX_D[20]`, `HDMI_TX_D[21]`, `HDMI_TX_D[22]`, `HDMI_TX_D[23]`, `HDMI_TX_D[2]`, `HDMI_TX_D[3]`, `HDMI_TX_D[4]`, `HDMI_TX_D[5]`, `HDMI_TX_D[6]`, `HDMI_TX_D[7]` and 65 more

These do not depend on the seed. A clock with no constraint or an ignored constraint means the slack numbers above never looked at those paths. MiSTer's framework leaves many HDMI/SD/LED pins unconstrained on purpose; what matters is what the PR adds.

</details>

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37205363393). </sub>