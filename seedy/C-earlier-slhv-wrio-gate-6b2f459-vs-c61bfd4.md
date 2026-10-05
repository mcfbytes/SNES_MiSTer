<!-- seedy:SNES -->
### Seedy — SNES: slhv-wrio-gate @ 6b2f459 vs c61bfd4

**No measurable regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 8 of 30 seeds of slhv-wrio-gate, against 12 of 30 on c61bfd4. With 30 seeds a difference that size can be chance (p = 0.41). The clock that fails more often is `pll_hdmi c0` (10 → 15 seeds, p = 0.29). The seed in the `.qsf` (1) does not close timing on slhv-wrio-gate (worst setup −0.356 ns, hold +0.251 ns).

|  | c61bfd4 | slhv-wrio-gate | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 12/30 | 8/30 | −4 | 0.41 |
| Worst setup slack (ns), average / typical seed | −0.173 / −0.089 | −0.265 / −0.140 | −0.092 / −0.051 | 0.33 |
| Worst setup slack (ns), unluckiest seed | −0.945 | −1.467 | −0.522 |  |
| Total negative slack (ns), average | −0.494 | −0.475 | +0.020 | 0.94 |
| Seeds with a hold violation | 4/30 | 1/30 | −3 | 0.35 |
| Logic used (ALMs), average | 35,138 (83.8%) | 35,138 (83.8%) | −1 | 0.98 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.452 / +0.199 ✗ | −0.356 / +0.251 ✗ | +0.096 / +0.052 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 18/30 | 14/30 | −4 | −0.089 | +0.020 | +0.110 | −0.945 | −1.467 | 0.44 |
| `pll_hdmi c0` | 10/30 | 15/30 | +5 | +0.058 | +0.002 | −0.056 | −0.217 | −0.291 | 0.29 |
| `emu c2` | 5/30 | 9/30 | +4 | +0.176 | +0.095 | −0.081 | −0.944 | −0.667 | 0.36 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 2 seeds of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 6 place(s) the baseline never fails: `ascal|o_poly_lum` (2), `ascal|o_vcpt_pre3` (2), `emu|sdram|SDRAM_A~_Duplicate_1` (1), `ascal|o_vcpt` (1), `hdmi_osd|osd_en` (1), `hps_io|video_calc|dout` (1). Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 11** (meets timing; worst slack +0.174 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −0.356 ns).

<details><summary>Top 5 seeds of slhv-wrio-gate</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 11 | ✓ | +0.174 | +0.174 | +0.244 | +3.992 | +0.859 | – | 78.50 | 35,252 |
| 29 | ✓ | +0.076 | +0.076 | +0.245 | +3.643 | +0.850 | −1.269 | 80.69 | 35,078 |
| 30 | ✓ | +0.070 | +0.070 | +0.205 | +3.845 | +0.732 | – | 80.39 | 35,126 |
| 6 | ✓ | +0.046 | +0.098 | +0.046 | +3.419 | +0.879 | −0.181 | 80.86 | 35,058 |
| 3 | ✓ | +0.024 | +0.024 | +0.256 | +4.199 | +0.763 | −0.132 | 78.11 | 35,252 |

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
| f(MAX) geomean | 78.72 | 79.02 | +0.30 | −0.13 [−1.15, +2.11] | 0.59 |  |
| WC slack: setup | −0.173 | −0.265 | −0.092 | −0.051 [−0.261, +0.132] | 0.33 |  |
| WC slack: hold | +0.154 | +0.191 | +0.037 | +0.007 [−0.035, +0.052] | 0.26 |  |
| WC slack: recovery | +3.731 | +3.620 | −0.111 | −0.115 [−0.317, +0.119] | 0.28 |  |
| WC slack: removal | +0.807 | +0.798 | −0.009 | +0.026 [−0.088, +0.101] | 0.78 |  |
| Total negative setup slack | −0.494 | −0.475 | +0.020 | −0.068 [−0.387, +0.211] | 0.94 |  |
| Logic utilization | 35,138 | 35,138 | −1 | +2 [−44, +46] | 0.98 |  |
| Compilation time | 00:31:09 | 00:30:56 | −00:00:13 | +00:03:18 [−00:05:23, +00:07:28] | 0.92 |  |

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
| candidate | 1 | 79.44 | −0.356 | +0.251 | +4.085 | +0.696 | 35,079 | 00:36:50 |  |
| candidate | 2 | 81.20 | −0.693 | +0.199 | +3.456 | +0.705 | 35,124 | 00:37:16 |  |
| candidate | 3 | 78.11 | +0.024 | +0.256 | +4.199 | +0.763 | 35,252 | 00:42:59 | ✓ |
| candidate | 4 | 75.45 | −0.418 | +0.220 | +3.861 | +0.636 | 35,211 | 00:42:34 |  |
| candidate | 5 | 81.58 | +0.002 | +0.126 | +4.223 | +0.786 | 35,118 | 00:35:49 | ✓ |
| candidate | 6 | 80.86 | +0.098 | +0.046 | +3.419 | +0.879 | 35,058 | 00:36:57 | ✓ |
| candidate | 7 | 76.87 | −0.013 | +0.245 | +3.099 | +0.799 | 35,162 | 00:42:46 |  |
| candidate | 8 | 81.30 | −0.667 | +0.176 | +2.597 | +0.809 | 35,067 | 00:24:05 |  |
| candidate | 9 | 81.77 | −0.115 | −0.100 | +2.759 | +0.684 | 35,050 | 00:31:04 |  |
| candidate | 10 | 80.89 | −1.467 | +0.248 | +3.669 | +0.539 | 35,060 | 00:32:20 |  |
| candidate | 11 | 78.50 | +0.174 | +0.244 | +3.992 | +0.859 | 35,252 | 00:39:40 | ✓ |
| candidate | 12 | 77.70 | −0.123 | +0.244 | +3.828 | +0.745 | 35,113 | 00:35:33 |  |
| candidate | 13 | 73.14 | −0.706 | +0.251 | +2.921 | +0.957 | 35,255 | 00:42:29 |  |
| candidate | 14 | 78.90 | −0.050 | +0.256 | +3.720 | +0.710 | 35,248 | 00:41:28 |  |
| candidate | 15 | 74.95 | −0.813 | +0.128 | +3.542 | +0.774 | 35,265 | 00:24:52 |  |
| candidate | 16 | 76.53 | −0.403 | +0.255 | +3.410 | +0.861 | 35,187 | 00:24:09 |  |
| candidate | 17 | 77.11 | −0.593 | +0.189 | +3.810 | +0.864 | 35,077 | 00:21:49 |  |
| candidate | 18 | 83.66 | −0.145 | +0.159 | +3.707 | +0.832 | 35,086 | 00:20:36 |  |
| candidate | 19 | 81.87 | +0.102 | +0.023 | +3.646 | +0.652 | 35,032 | 00:20:29 | ✓ |
| candidate | 20 | 78.84 | −0.261 | +0.200 | +3.720 | +0.939 | 35,155 | 00:27:23 |  |
| candidate | 21 | 77.95 | +0.021 | +0.247 | +3.957 | +0.986 | 35,153 | 00:33:04 | ✓ |
| candidate | 22 | 80.59 | −0.024 | +0.250 | +3.816 | +0.825 | 35,207 | 00:34:34 |  |
| candidate | 23 | 78.40 | −0.149 | +0.236 | +4.023 | +0.720 | 35,099 | 00:32:06 |  |
| candidate | 24 | 77.18 | −0.135 | +0.245 | +3.936 | +0.905 | 35,125 | 00:35:43 |  |
| candidate | 25 | 80.39 | −0.170 | +0.217 | +3.276 | +0.689 | 35,077 | 00:30:11 |  |
| candidate | 26 | 78.92 | −0.269 | +0.178 | +3.371 | +0.957 | 35,106 | 00:29:21 |  |
| candidate | 27 | 77.12 | −0.825 | +0.091 | +3.656 | +1.062 | 35,196 | 00:20:56 |  |
| candidate | 28 | 80.20 | −0.114 | +0.195 | +3.405 | +0.718 | 35,117 | 00:17:54 |  |
| candidate | 29 | 80.69 | +0.076 | +0.245 | +3.643 | +0.850 | 35,078 | 00:16:58 | ✓ |
| candidate | 30 | 80.39 | +0.070 | +0.205 | +3.845 | +0.732 | 35,126 | 00:16:03 | ✓ |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.118 / +7.349 | +6.730 / +7.784 | +0.612 / +0.434 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.270 / +4.986 | +4.049 / +5.322 | −0.221 / +0.336 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +6.606 / +8.681 | +5.092 / +8.650 | −1.514 / −0.031 | 1.00 |
| `emu c0` | 18/30 | 14/30 | −4 | −0.945 / −0.089 | −1.467 / +0.020 | −0.522 / +0.110 | 0.44 |
| `emu c1` | 0/30 | 0/30 | 0 | +6.657 / +7.694 | +5.705 / +7.774 | −0.952 / +0.080 | 1.00 |
| `emu c2` | 5/30 | 9/30 | +4 | −0.944 / +0.176 | −0.667 / +0.095 | +0.277 / −0.081 | 0.36 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.122 / +3.368 | +1.017 / +3.402 | −0.105 / +0.034 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.442 / +14.337 | +12.791 / +14.221 | −0.651 / −0.116 | 1.00 |
| `pll_hdmi c0` | 10/30 | 15/30 | +5 | −0.217 / +0.058 | −0.291 / +0.002 | −0.074 / −0.056 | 0.29 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.471 / +5.390 | +4.337 / +5.462 | −0.134 / +0.072 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.119 / +0.164 | +0.131 / +0.164 | +0.012 / +0.000 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.114 / +0.167 | +0.121 / +0.167 | +0.007 / +0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.082 / +0.124 | +0.001 / +0.139 | −0.081 / +0.015 | 1.00 |
| `emu c0` | 5/30 | 3/30 | −2 | −0.319 / +0.164 | −0.100 / +0.163 | +0.219 / −0.001 | 0.71 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.075 / +0.117 | +0.074 / +0.118 | −0.001 / +0.001 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.076 / +0.100 | +0.083 / +0.098 | +0.007 / −0.002 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.134 / +0.155 | +0.126 / +0.158 | −0.008 / +0.003 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.115 / +0.120 | +0.115 / +0.120 | +0.000 / +0.000 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.035 / +0.103 | +0.022 / +0.096 | −0.013 / −0.008 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.139 / +0.153 | +0.142 / +0.167 | +0.003 / +0.014 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 72.04 / 79.62 | 75.36 / 81.84 | +3.32 / +2.22 |
| `FPGA_CLK2_50` | 63.57 / 67.24 | 62.69 / 67.83 | −0.88 / +0.59 |
| `altera_reserved_tck` | 49.70 / 63.43 | 43.20 / 62.36 | −6.50 / −1.07 |
| `emu c0` | 79.45 / 85.56 | 76.29 / 85.35 | −3.16 / −0.22 |
| `emu c1` | 60.28 / 67.99 | 60.05 / 66.94 | −0.23 / −1.05 |
| `emu c2` | 24.89 / 25.94 | 24.61 / 26.29 | −0.28 / +0.35 |
| `h2f_user0_clk` | 112.64 / 145.20 | 111.32 / 146.82 | −1.32 / +1.63 |
| `pll_audio` | 36.71 / 38.03 | 35.85 / 37.66 | −0.86 / −0.37 |
| `pll_hdmi c0` | 143.91 / 150.36 | 142.39 / 148.88 | −1.52 / −1.48 |
| `spi_sck` | 180.86 / 220.39 | 176.58 / 227.92 | −4.28 / +7.53 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 35,036 … 35,317 | 35,032 … 35,265 | −1 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,134 … 33,466 | 33,103 … 33,469 | −7 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:40 … 00:04:28 | 00:03:42 … 00:04:28 | −00:00:01 |
| `Assembler` | 00:00:11 … 00:00:19 | 00:00:11 … 00:00:20 | −00:00:01 |
| `Fitter` | 00:11:31 … 00:39:00 | 00:11:38 … 00:38:41 | −00:00:11 |
| `TimeQuest Timing Analyzer` | 00:00:12 … 00:00:20 | 00:00:13 … 00:00:22 | 00:00:00 |
| `Total` | 00:15:56 … 00:43:13 | 00:16:03 … 00:42:59 | −00:00:13 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,839 | 3,506 … 3,570 | −257 |
| `Assembler` | 1,898 … 1,981 | 1,897 … 1,981 | +5 |
| `Fitter` | 6,297 … 6,404 | 6,350 … 6,404 | +3 |
| `TimeQuest Timing Analyzer` | 2,326 … 2,373 | 2,335 … 2,376 | 0 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 16 | 12 | −4 |
| `CPU\|P65C816\|P` | 5 | 8 | +3 |
| `emu\|sdram\|SDRAM_nCAS` | 4 | 5 | +1 |
| `emu\|sdram\|SDRAM_nWE` | 3 | 2 | −1 |
| `ascal\|o_vcpt_pre3` | 0 | 2 | +2 |
| `emu\|sdram\|SDRAM_DQ~en` | 1 | 1 | 0 |
| `emu\|ddram\|cache_addr` | 1 | 1 | 0 |
| `emu\|sdram\|old_sni_rd` | 2 | 0 | −2 |
| `ascal\|o_poly_lum` | 0 | 2 | +2 |
| `emu\|sdram\|SDRAM_A` | 1 | 1 | 0 |
| `emu\|ddram\|cache_addr2` | 1 | 0 | −1 |
| `ascal\|o_vcpt` | 0 | 1 | +1 |
| `hdmi_osd\|osd_en` | 0 | 1 | +1 |
| `sl_r` | 1 | 0 | −1 |
| `emu\|sdram\|SDRAM_A~_Duplicate_1` | 0 | 1 | +1 |
| `P65C816\|AddrGen\|PCr` | 1 | 0 | −1 |
| `hps_io\|video_calc\|dout` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_nRAS` | 1 | 0 | −1 |

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

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37214664117). </sub>