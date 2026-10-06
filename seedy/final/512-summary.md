### <img src="https://raw.githubusercontent.com/mcfbytes/Seedy_MiSTer/master/art/seedy-kun.png" width="24" alt=""> [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) — SNES: f954038 vs 2302683

**Possible regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 7 of 30 seeds of f954038, against 8 of 30 on 2302683. With 30 seeds a difference that size can be chance (p = 1.00). The clock that fails more often is `emu c2` (8 → 16 seeds, p = 0.06). The seed in the `.qsf` (1) does not close timing on f954038 (worst setup −1.303 ns, hold +0.250 ns).

**Flagged** (timing got measurably worse):

- Total negative setup slack worse by 1.792 ns on average (p = 0.045)

|  | 2302683 | f954038 | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 8/30 | 7/30 | −1 | 1.00 |
| Worst setup slack (ns), average / typical seed | −0.208 / −0.189 | −0.313 / −0.189 | −0.105 / +0.000 | 0.23 |
| Worst setup slack (ns), unluckiest seed | −0.732 | −1.303 | −0.571 |  |
| Total negative slack (ns), average | −0.353 | −2.145 | −1.792 | 0.04 |
| Seeds with a hold violation | 1/30 | 1/30 | 0 | 1.00 |
| Logic used (ALMs), average | 35,054 (83.6%) | 35,041 (83.6%) | −13 | 0.47 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.345 / +0.199 ✗ | −1.303 / +0.250 ✗ | −0.958 / +0.051 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 14/30 | 18/30 | +4 | +0.003 | −0.057 | −0.060 | −0.690 | −0.827 | 0.44 |
| `pll_hdmi c0` | 13/30 | 16/30 | +3 | +0.039 | −0.037 | −0.076 | −0.359 | −0.300 | 0.61 |
| `emu c2` | 8/30 | 16/30 | +8 | +0.172 | −0.014 | −0.186 | −0.732 | −1.303 | 0.06 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 1 seed of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 12 place(s) the baseline never fails: `emu|sdram|SDRAM_nWE` (5), `emu|sdram|SDRAM_nCAS` (4), `emu|sdram|SDRAM_A` (3), `emu|sdram|SDRAM_DQ~reg0` (3), `emu|sdram|SDRAM_DQ~en` (2), `emu|sdram|SDRAM_nRAS` (2), `sl_r` (2), `ascal|o_hpixs.b` (1) and 4 more. Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 27** (meets timing; worst slack +0.250 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −1.303 ns).

<details><summary>Top 5 seeds of f954038</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 27 | ✓ | +0.250 | +0.250 | +0.251 | +4.160 | +0.725 | −0.178 | 80.11 | 35,159 |
| 12 | ✓ | +0.094 | +0.094 | +0.246 | +3.472 | +0.879 | – | 81.15 | 34,943 |
| 21 | ✓ | +0.068 | +0.068 | +0.199 | +3.989 | +0.893 | −0.148 | 77.11 | 35,077 |
| 19 | ✓ | +0.064 | +0.064 | +0.242 | +3.619 | +1.077 | −0.199 | 78.67 | 35,012 |
| 29 | ✓ | +0.038 | +0.038 | +0.184 | +3.939 | +0.698 | – | 81.77 | 35,001 |

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
| f(MAX) geomean | 79.13 | 78.96 | −0.17 | −0.02 [−1.39, +1.68] | 0.73 |  |
| WC slack: setup | −0.208 | −0.313 | −0.105 | +0.000 [−0.388, +0.213] | 0.23 |  |
| WC slack: hold | +0.205 | +0.198 | −0.007 | −0.003 [−0.044, +0.039] | 0.79 |  |
| WC slack: recovery | +3.782 | +3.721 | −0.061 | −0.129 [−0.319, +0.211] | 0.49 |  |
| WC slack: removal | +0.805 | +0.810 | +0.005 | −0.010 [−0.101, +0.087] | 0.88 |  |
| Total negative setup slack | −0.353 | −2.145 | −1.792 | −0.007 [−0.626, +0.248] | 0.04 | ⚠️ flagged |
| Logic utilization | 35,054 | 35,041 | −13 | −28 [−66, +37] | 0.47 |  |
| Compilation time | 00:53:32 | 00:37:03 | −00:16:29 | −00:10:04 [−00:31:24, −00:00:03] | < 0.001 |  |

</details>
<details><summary>Per-seed table (60 rows)</summary>

| variant | seed | f(MAX) MHz | setup | hold | recovery | removal | ALMs | time | met |
|---|---|---|---|---|---|---|---|---|---|
| baseline | 1 | 79.42 | −0.345 | +0.199 | +4.026 | +0.738 | 34,965 | 01:15:49 |  |
| baseline | 2 | 80.81 | −0.098 | +0.244 | +3.712 | +0.826 | 35,022 | 01:15:28 |  |
| baseline | 3 | 75.92 | −0.008 | +0.239 | +3.810 | +0.837 | 35,077 | 01:23:08 |  |
| baseline | 4 | 77.17 | −0.309 | +0.248 | +3.974 | +0.862 | 35,129 | 01:23:41 |  |
| baseline | 5 | 80.55 | +0.161 | +0.211 | +3.845 | +0.826 | 35,023 | 01:13:12 | ✓ |
| baseline | 6 | 79.25 | −0.260 | +0.251 | +3.205 | +0.660 | 34,961 | 01:14:59 |  |
| baseline | 7 | 78.34 | −0.012 | +0.252 | +4.014 | +0.827 | 35,152 | 01:23:53 |  |
| baseline | 8 | 78.91 | +0.149 | +0.245 | +3.429 | +0.730 | 34,999 | 00:33:05 | ✓ |
| baseline | 9 | 77.78 | −0.521 | +0.200 | +3.963 | +0.752 | 35,009 | 00:40:38 |  |
| baseline | 10 | 78.14 | −0.373 | +0.243 | +3.431 | +0.936 | 34,991 | 00:41:34 |  |
| baseline | 11 | 80.08 | +0.030 | +0.253 | +4.175 | +0.615 | 35,169 | 00:56:07 | ✓ |
| baseline | 12 | 83.08 | −0.342 | +0.226 | +3.530 | +1.032 | 35,014 | 00:49:44 |  |
| baseline | 13 | 77.66 | −0.314 | −0.020 | +3.559 | +0.687 | 35,155 | 01:26:10 |  |
| baseline | 14 | 80.48 | +0.136 | +0.244 | +3.574 | +0.893 | 35,204 | 01:14:18 | ✓ |
| baseline | 15 | 77.63 | −0.690 | +0.059 | +3.229 | +0.760 | 35,192 | 01:08:20 |  |
| baseline | 16 | 76.79 | −0.488 | +0.245 | +4.349 | +0.948 | 35,085 | 01:10:05 |  |
| baseline | 17 | 79.35 | −0.683 | +0.252 | +4.369 | +1.010 | 34,963 | 00:59:00 |  |
| baseline | 18 | 80.85 | +0.055 | +0.192 | +3.837 | +0.903 | 34,967 | 00:48:32 | ✓ |
| baseline | 19 | 80.60 | −0.066 | +0.141 | +4.011 | +0.656 | 35,050 | 00:48:22 |  |
| baseline | 20 | 76.66 | −0.028 | +0.222 | +3.371 | +0.598 | 35,081 | 00:35:54 |  |
| baseline | 21 | 77.75 | −0.732 | +0.192 | +3.791 | +0.869 | 35,124 | 00:28:48 |  |
| baseline | 22 | 77.22 | +0.001 | +0.253 | +3.239 | +0.914 | 35,076 | 00:35:14 | ✓ |
| baseline | 23 | 84.06 | +0.073 | +0.248 | +3.446 | +0.704 | 34,975 | 00:31:51 | ✓ |
| baseline | 24 | 77.83 | −0.525 | +0.256 | +3.551 | +0.995 | 35,064 | 00:46:50 |  |
| baseline | 25 | 82.03 | −0.210 | +0.165 | +3.755 | +0.852 | 35,078 | 00:40:20 |  |
| baseline | 26 | 78.34 | −0.666 | +0.254 | +4.661 | +0.667 | 34,987 | 00:39:40 |  |
| baseline | 27 | 77.76 | +0.262 | +0.252 | +4.135 | +0.780 | 35,076 | 00:38:44 | ✓ |
| baseline | 28 | 79.50 | −0.015 | +0.178 | +3.790 | +0.772 | 35,042 | 00:32:20 |  |
| baseline | 29 | 80.28 | −0.263 | +0.033 | +4.402 | +0.673 | 34,998 | 00:26:02 |  |
| baseline | 30 | 79.59 | −0.167 | +0.183 | +3.289 | +0.831 | 34,985 | 00:24:22 |  |
| candidate | 1 | 78.34 | −1.303 | +0.250 | +3.127 | +0.859 | 34,982 | 00:39:47 |  |
| candidate | 2 | 80.17 | −0.185 | +0.251 | +3.589 | +1.007 | 34,991 | 00:40:45 |  |
| candidate | 3 | 77.21 | −0.595 | +0.240 | +4.122 | +0.686 | 35,085 | 00:47:35 |  |
| candidate | 4 | 77.56 | +0.016 | +0.251 | +4.141 | +0.850 | 35,072 | 00:47:44 | ✓ |
| candidate | 5 | 79.87 | −0.025 | +0.168 | +3.214 | +0.710 | 34,975 | 00:40:27 |  |
| candidate | 6 | 81.62 | −0.454 | +0.068 | +3.854 | +0.699 | 35,035 | 00:40:34 |  |
| candidate | 7 | 77.31 | −0.394 | +0.234 | +3.656 | +0.731 | 35,053 | 00:47:40 |  |
| candidate | 8 | 79.89 | −0.492 | +0.168 | +3.583 | +0.647 | 35,008 | 00:30:42 |  |
| candidate | 9 | 80.02 | −0.192 | +0.244 | +3.325 | +0.833 | 34,994 | 00:35:55 |  |
| candidate | 10 | 79.10 | −0.439 | +0.250 | +4.011 | +0.931 | 34,972 | 00:37:00 |  |
| candidate | 11 | 75.42 | −0.537 | +0.247 | +3.450 | +0.969 | 35,115 | 00:48:11 |  |
| candidate | 12 | 81.15 | +0.094 | +0.246 | +3.472 | +0.879 | 34,943 | 00:40:43 | ✓ |
| candidate | 13 | 77.17 | −0.054 | +0.248 | +3.906 | +0.916 | 35,155 | 00:47:36 |  |
| candidate | 14 | 79.69 | −0.827 | +0.251 | +3.485 | +0.805 | 35,180 | 00:45:58 |  |
| candidate | 15 | 75.92 | −0.043 | +0.242 | +3.881 | +0.736 | 35,141 | 00:27:19 |  |
| candidate | 16 | 77.10 | −0.389 | +0.257 | +3.939 | +0.837 | 35,058 | 00:31:11 |  |
| candidate | 17 | 78.56 | −0.071 | +0.209 | +4.497 | +0.841 | 35,003 | 00:29:22 |  |
| candidate | 18 | 82.12 | −0.625 | +0.131 | +3.693 | +0.797 | 35,016 | 00:30:06 |  |
| candidate | 19 | 78.67 | +0.064 | +0.242 | +3.619 | +1.077 | 35,012 | 00:31:12 | ✓ |
| candidate | 20 | 80.52 | −0.002 | −0.306 | +3.628 | +0.827 | 35,054 | 00:40:16 |  |
| candidate | 21 | 77.11 | +0.068 | +0.199 | +3.989 | +0.893 | 35,077 | 00:41:44 | ✓ |
| candidate | 22 | 76.63 | +0.015 | +0.185 | +3.567 | +0.745 | 35,090 | 00:40:36 | ✓ |
| candidate | 23 | 78.25 | −0.130 | +0.237 | +3.797 | +0.599 | 34,986 | 00:35:22 |  |
| candidate | 24 | 77.50 | −0.814 | +0.218 | +4.005 | +1.018 | 35,049 | 00:41:09 |  |
| candidate | 25 | 81.11 | −1.067 | +0.139 | +3.667 | +0.728 | 34,998 | 00:31:49 |  |
| candidate | 26 | 80.65 | −0.520 | +0.250 | +3.582 | +0.873 | 35,017 | 00:30:30 |  |
| candidate | 27 | 80.11 | +0.250 | +0.251 | +4.160 | +0.725 | 35,159 | 00:31:28 | ✓ |
| candidate | 28 | 79.02 | −0.140 | +0.183 | +3.396 | +0.706 | 34,998 | 00:29:16 |  |
| candidate | 29 | 81.77 | +0.038 | +0.184 | +3.939 | +0.698 | 35,001 | 00:26:22 | ✓ |
| candidate | 30 | 79.28 | −0.650 | +0.196 | +3.322 | +0.677 | 35,019 | 00:23:02 |  |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.344 / +7.689 | +6.593 / +7.700 | +0.249 / +0.011 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.508 / +4.968 | +4.381 / +5.178 | −0.127 / +0.210 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +7.742 / +8.726 | +6.929 / +8.454 | −0.813 / −0.272 | 1.00 |
| `emu c0` | 14/30 | 18/30 | +4 | −0.690 / +0.003 | −0.827 / −0.057 | −0.137 / −0.060 | 0.44 |
| `emu c1` | 0/30 | 0/30 | 0 | +4.082 / +8.079 | +5.751 / +8.023 | +1.669 / −0.056 | 1.00 |
| `emu c2` | 8/30 | 16/30 | +8 | −0.732 / +0.172 | −1.303 / −0.014 | −0.571 / −0.186 | 0.06 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.266 / +3.341 | +1.363 / +3.271 | +0.097 / −0.070 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.039 / +14.311 | +12.850 / +14.178 | −0.189 / −0.133 | 1.00 |
| `pll_hdmi c0` | 13/30 | 16/30 | +3 | −0.359 / +0.039 | −0.300 / −0.037 | +0.059 / −0.076 | 0.61 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.288 / +5.460 | +4.419 / +5.583 | +0.131 / +0.123 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.129 / +0.162 | +0.126 / +0.163 | −0.003 / +0.001 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.122 / +0.166 | +0.121 / +0.167 | −0.001 / +0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.108 / +0.139 | +0.109 / +0.139 | +0.001 / +0.000 | 1.00 |
| `emu c0` | 2/30 | 2/30 | 0 | −0.020 / +0.161 | −0.306 / +0.164 | −0.286 / +0.003 | 1.00 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.076 / +0.118 | +0.078 / +0.116 | +0.002 / −0.002 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.050 / +0.098 | +0.058 / +0.103 | +0.008 / +0.005 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.133 / +0.155 | +0.134 / +0.152 | +0.001 / −0.003 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.082 / +0.121 | +0.116 / +0.122 | +0.034 / +0.001 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.032 / +0.095 | +0.016 / +0.090 | −0.016 / −0.005 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.132 / +0.154 | +0.140 / +0.168 | +0.008 / +0.014 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 73.23 / 80.93 | 74.59 / 81.27 | +1.36 / +0.34 |
| `FPGA_CLK2_50` | 64.55 / 66.84 | 64.02 / 67.58 | −0.53 / +0.74 |
| `altera_reserved_tck` | 56.03 / 64.02 | 51.35 / 62.20 | −4.68 / −1.82 |
| `emu c0` | 81.10 / 85.56 | 80.27 / 85.86 | −0.83 / +0.30 |
| `emu c1` | 61.47 / 67.69 | 62.81 / 68.09 | +1.34 / +0.40 |
| `emu c2` | 24.80 / 26.10 | 24.96 / 26.02 | +0.16 / −0.08 |
| `h2f_user0_clk` | 114.50 / 146.15 | 115.78 / 146.96 | +1.28 / +0.81 |
| `pll_audio` | 36.18 / 37.88 | 35.93 / 37.64 | −0.25 / −0.24 |
| `pll_hdmi c0` | 141.02 / 148.74 | 142.21 / 149.01 | +1.19 / +0.27 |
| `spi_sck` | 175.07 / 228.86 | 179.18 / 225.56 | +4.11 / −3.30 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 34,961 … 35,204 | 34,943 … 35,180 | −12 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,164 … 33,375 | 33,220 … 33,511 | +65 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:53 … 00:05:19 | 00:04:10 … 00:05:17 | −00:00:13 |
| `Assembler` | 00:00:12 … 00:00:24 | 00:00:12 … 00:00:24 | −00:00:01 |
| `Fitter` | 00:19:01 … 01:20:49 | 00:18:02 … 00:43:02 | −00:16:14 |
| `TimeQuest Timing Analyzer` | 00:00:15 … 00:00:28 | 00:00:14 … 00:00:28 | −00:00:02 |
| `Total` | 00:24:22 … 01:26:10 | 00:23:02 … 00:48:11 | −00:16:30 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,570 | 3,506 … 3,570 | −4 |
| `Assembler` | 1,897 … 1,979 | 1,897 … 1,980 | +22 |
| `Fitter` | 6,358 … 6,415 | 6,359 … 6,508 | +5 |
| `TimeQuest Timing Analyzer` | 2,337 … 2,371 | 2,350 … 2,395 | +11 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 13 | 9 | −4 |
| `CPU\|P65C816\|P` | 7 | 12 | +5 |
| `emu\|sdram\|SDRAM_nWE` | 0 | 5 | +5 |
| `emu\|sdram\|SDRAM_nCAS` | 0 | 4 | +4 |
| `ascal\|o_poly_lum` | 3 | 0 | −3 |
| `hps_io\|video_calc\|dout` | 2 | 1 | −1 |
| `emu\|sdram\|SDRAM_A` | 0 | 3 | +3 |
| `emu\|sdram\|SDRAM_DQ~reg0` | 0 | 3 | +3 |
| `emu\|ddram\|cache_addr` | 1 | 1 | 0 |
| `emu\|sdram\|SDRAM_DQ~en` | 0 | 2 | +2 |
| `emu\|sdram\|SDRAM_nRAS` | 0 | 2 | +2 |
| `sl_r` | 0 | 2 | +2 |
| `ascal\|o_hpixs.b` | 0 | 1 | +1 |
| `ascal\|o_lastv` | 1 | 0 | −1 |
| `ascal\|o_vacpt` | 1 | 0 | −1 |
| `emu\|ddram\|ram_address` | 0 | 1 | +1 |
| `emu\|ddram\|ram_burst` | 0 | 1 | +1 |
| `emu\|ddram\|ram_q` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_A~_Duplicate_1` | 0 | 1 | +1 |

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

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37395120515). Report by [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) 1.2.0, multi-seed Quartus timing CI for MiSTer cores.</sub>