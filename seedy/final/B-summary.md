### <img src="https://raw.githubusercontent.com/mcfbytes/Seedy_MiSTer/master/art/seedy-kun.png" width="24" alt=""> [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) — SNES: 3f33d28 vs 2302683

**Possible regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 6 of 30 seeds of 3f33d28, against 8 of 30 on 2302683. With 30 seeds a difference that size can be chance (p = 0.76). The clock that fails more often is `emu c2` (8 → 15 seeds, p = 0.11). The seed in the `.qsf` (1) does not close timing on 3f33d28 (worst setup −1.680 ns, hold +0.251 ns).

**Flagged** (timing got measurably worse):

- Total negative setup slack worse by 0.986 ns on average (p = 0.024)

|  | 2302683 | 3f33d28 | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 8/30 | 6/30 | −2 | 0.76 |
| Worst setup slack (ns), average / typical seed | −0.208 / −0.189 | −0.367 / −0.180 | −0.159 / +0.009 | 0.15 |
| Worst setup slack (ns), unluckiest seed | −0.732 | −1.680 | −0.948 |  |
| Total negative slack (ns), average | −0.353 | −1.340 | −0.987 | 0.02 |
| Seeds with a hold violation | 1/30 | 2/30 | +1 | 1.00 |
| Logic used (ALMs), average | 35,054 (83.6%) | 34,994 (83.5%) | −60 | 0.001 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.345 / +0.199 ✗ | −1.680 / +0.251 ✗ | −1.335 / +0.052 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 14/30 | 19/30 | +5 | +0.003 | −0.102 | −0.105 | −0.690 | −1.501 | 0.30 |
| `emu c2` | 8/30 | 15/30 | +7 | +0.172 | −0.001 | −0.173 | −0.732 | −1.680 | 0.11 |
| `pll_hdmi c0` | 13/30 | 6/30 | −7 | +0.039 | +0.148 | +0.109 | −0.359 | −0.392 | 0.09 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 0 seeds of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 9 place(s) the baseline never fails: `emu|sdram|SDRAM_A` (4), `emu|sdram|SDRAM_nCAS` (3), `vs_r` (2), `ascal|o_h_poly_pix.r` (1), `ascal|o_vcpt_pre3` (1), `ascal|o_vcpt_sync` (1), `emu|sdram|SDRAM_DQ~en` (1), `emu|sdram|old_sni_wr` (1) and 1 more. Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 6** (meets timing; worst slack +0.204 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −1.680 ns).

<details><summary>Top 5 seeds of 3f33d28</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 6 | ✓ | +0.204 | +0.216 | +0.204 | +4.048 | +0.816 | – | 82.57 | 34,992 |
| 22 | ✓ | +0.199 | +0.221 | +0.199 | +3.461 | +0.888 | – | 78.71 | 35,009 |
| 23 | ✓ | +0.189 | +0.189 | +0.248 | +3.281 | +0.706 | – | 81.46 | 34,998 |
| 10 | ✓ | +0.097 | +0.097 | +0.244 | +3.091 | +0.672 | – | 79.62 | 34,941 |
| 5 | ✓ | +0.086 | +0.136 | +0.086 | +4.321 | +0.707 | – | 79.22 | 34,902 |

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
| f(MAX) geomean | 79.13 | 79.14 | +0.01 | +0.22 [−0.79, +1.63] | 0.97 |  |
| WC slack: setup | −0.208 | −0.367 | −0.159 | +0.009 [−0.335, +0.183] | 0.15 |  |
| WC slack: hold | +0.205 | +0.189 | −0.016 | +0.002 [−0.043, +0.043] | 0.56 |  |
| WC slack: recovery | +3.782 | +3.727 | −0.055 | −0.110 [−0.314, +0.252] | 0.58 |  |
| WC slack: removal | +0.805 | +0.809 | +0.004 | −0.017 [−0.079, +0.090] | 0.88 |  |
| Total negative setup slack | −0.353 | −1.340 | −0.987 | −0.110 [−0.778, +0.167] | 0.02 | ⚠️ flagged |
| Logic utilization | 35,054 | 34,994 | −60 | −52 [−107, −0] | 0.001 |  |
| Compilation time | 00:53:32 | 00:49:23 | −00:04:09 | +00:02:02 [−00:18:59, +00:11:28] | 0.33 |  |

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
| candidate | 1 | 80.38 | −1.680 | +0.251 | +3.129 | +0.862 | 34,945 | 00:51:18 |  |
| candidate | 2 | 81.46 | −0.106 | +0.101 | +4.284 | +0.711 | 34,976 | 00:49:25 |  |
| candidate | 3 | 76.27 | −0.165 | +0.252 | +4.043 | +0.918 | 35,032 | 00:59:56 |  |
| candidate | 4 | 77.20 | −0.068 | +0.251 | +3.638 | +0.853 | 35,042 | 01:00:03 |  |
| candidate | 5 | 79.22 | +0.136 | +0.086 | +4.321 | +0.707 | 34,902 | 00:53:12 | ✓ |
| candidate | 6 | 82.57 | +0.216 | +0.204 | +4.048 | +0.816 | 34,992 | 00:51:08 | ✓ |
| candidate | 7 | 79.05 | −1.281 | +0.240 | +3.036 | +0.679 | 35,136 | 00:59:37 |  |
| candidate | 8 | 78.95 | −0.323 | +0.183 | +3.462 | +0.754 | 34,929 | 00:50:00 |  |
| candidate | 9 | 81.98 | +0.044 | +0.192 | +3.659 | +0.948 | 34,977 | 00:37:09 | ✓ |
| candidate | 10 | 79.62 | +0.097 | +0.244 | +3.091 | +0.672 | 34,941 | 00:42:35 | ✓ |
| candidate | 11 | 79.46 | −0.324 | +0.248 | +4.367 | +0.937 | 34,969 | 01:04:16 |  |
| candidate | 12 | 80.11 | −0.519 | +0.154 | +3.415 | +1.002 | 34,943 | 00:49:21 |  |
| candidate | 13 | 73.33 | −0.993 | −0.062 | +3.645 | +0.923 | 35,075 | 01:10:06 |  |
| candidate | 14 | 78.94 | −0.174 | +0.244 | +4.141 | +0.801 | 35,091 | 01:06:52 |  |
| candidate | 15 | 77.87 | −0.566 | +0.241 | +3.780 | +0.669 | 35,080 | 01:05:06 |  |
| candidate | 16 | 79.55 | −0.460 | +0.108 | +3.420 | +0.713 | 35,070 | 01:01:43 |  |
| candidate | 17 | 78.28 | −0.017 | +0.246 | +3.913 | +0.849 | 34,996 | 00:45:10 |  |
| candidate | 18 | 82.55 | −0.408 | +0.247 | +3.618 | +0.891 | 34,887 | 00:40:18 |  |
| candidate | 19 | 78.75 | −0.006 | +0.236 | +3.702 | +0.770 | 34,936 | 00:34:28 |  |
| candidate | 20 | 77.23 | −0.103 | −0.317 | +3.905 | +0.797 | 35,029 | 00:27:31 |  |
| candidate | 21 | 76.25 | −0.422 | +0.254 | +3.287 | +0.936 | 34,996 | 00:40:07 |  |
| candidate | 22 | 78.71 | +0.221 | +0.199 | +3.461 | +0.888 | 35,009 | 00:53:22 | ✓ |
| candidate | 23 | 81.46 | +0.189 | +0.248 | +3.281 | +0.706 | 34,998 | 00:45:34 | ✓ |
| candidate | 24 | 78.18 | −0.072 | +0.254 | +4.286 | +0.851 | 35,056 | 00:56:45 |  |
| candidate | 25 | 81.28 | −1.378 | +0.187 | +3.620 | +0.778 | 34,898 | 00:50:58 |  |
| candidate | 26 | 79.73 | −0.186 | +0.250 | +3.978 | +0.830 | 34,966 | 00:49:17 |  |
| candidate | 27 | 75.29 | −0.375 | +0.250 | +3.907 | +0.714 | 35,066 | 00:52:11 |  |
| candidate | 28 | 80.70 | −0.659 | +0.245 | +3.955 | +0.704 | 34,910 | 00:43:30 |  |
| candidate | 29 | 80.58 | −1.501 | +0.200 | +3.595 | +0.851 | 34,924 | 00:27:06 |  |
| candidate | 30 | 79.38 | −0.141 | +0.247 | +3.815 | +0.751 | 35,036 | 00:23:13 |  |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.344 / +7.689 | +6.675 / +7.897 | +0.331 / +0.208 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.508 / +4.968 | +3.770 / +5.133 | −0.738 / +0.165 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +7.742 / +8.726 | +4.298 / +8.476 | −3.444 / −0.250 | 1.00 |
| `emu c0` | 14/30 | 19/30 | +5 | −0.690 / +0.003 | −1.501 / −0.102 | −0.811 / −0.105 | 0.30 |
| `emu c1` | 0/30 | 0/30 | 0 | +4.082 / +8.079 | +6.060 / +8.066 | +1.978 / −0.013 | 1.00 |
| `emu c2` | 8/30 | 15/30 | +7 | −0.732 / +0.172 | −1.680 / −0.001 | −0.948 / −0.173 | 0.11 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.266 / +3.341 | +1.184 / +2.734 | −0.082 / −0.607 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.039 / +14.311 | +13.049 / +14.102 | +0.010 / −0.209 | 1.00 |
| `pll_hdmi c0` | 13/30 | 6/30 | −7 | −0.359 / +0.039 | −0.392 / +0.148 | −0.033 / +0.109 | 0.09 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.288 / +5.460 | +4.154 / +5.798 | −0.134 / +0.338 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.129 / +0.162 | +0.126 / +0.164 | −0.003 / +0.002 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.122 / +0.166 | +0.116 / +0.167 | −0.006 / +0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.108 / +0.139 | +0.109 / +0.139 | +0.001 / +0.000 | 1.00 |
| `emu c0` | 2/30 | 2/30 | 0 | −0.020 / +0.161 | −0.317 / +0.163 | −0.297 / +0.002 | 1.00 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.076 / +0.118 | +0.075 / +0.116 | −0.001 / −0.002 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.050 / +0.098 | +0.074 / +0.098 | +0.024 / +0.000 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.133 / +0.155 | +0.112 / +0.158 | −0.021 / +0.003 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.082 / +0.121 | +0.047 / +0.120 | −0.035 / −0.001 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.032 / +0.095 | +0.044 / +0.097 | +0.012 / +0.002 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.132 / +0.154 | +0.134 / +0.158 | +0.002 / +0.004 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 73.23 / 80.93 | 75.05 / 82.66 | +1.82 / +1.73 |
| `FPGA_CLK2_50` | 64.55 / 66.84 | 61.61 / 67.24 | −2.94 / +0.40 |
| `altera_reserved_tck` | 56.03 / 64.02 | 40.43 / 61.59 | −15.60 / −2.43 |
| `emu c0` | 81.10 / 85.56 | 76.09 / 84.60 | −5.01 / −0.96 |
| `emu c1` | 61.47 / 67.69 | 62.19 / 68.62 | +0.72 / +0.93 |
| `emu c2` | 24.80 / 26.10 | 25.01 / 26.01 | +0.21 / −0.09 |
| `h2f_user0_clk` | 114.50 / 146.15 | 113.43 / 143.53 | −1.07 / −2.62 |
| `pll_audio` | 36.18 / 37.88 | 36.19 / 37.60 | +0.01 / −0.28 |
| `pll_hdmi c0` | 141.02 / 148.74 | 140.37 / 150.71 | −0.65 / +1.97 |
| `spi_sck` | 175.07 / 228.86 | 171.06 / 236.13 | −4.01 / +7.27 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 34,961 … 35,204 | 34,887 … 35,136 | −60 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,164 … 33,375 | 33,197 … 33,544 | +77 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:53 … 00:05:19 | 00:04:22 … 00:05:54 | +00:00:25 |
| `Assembler` | 00:00:12 … 00:00:24 | 00:00:13 … 00:00:24 | +00:00:01 |
| `Fitter` | 00:19:01 … 01:20:49 | 00:16:52 … 01:04:46 | −00:04:38 |
| `TimeQuest Timing Analyzer` | 00:00:15 … 00:00:28 | 00:00:16 … 00:00:28 | +00:00:03 |
| `Total` | 00:24:22 … 01:26:10 | 00:23:13 … 01:10:06 | −00:04:10 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,570 | 3,506 … 3,570 | 0 |
| `Assembler` | 1,897 … 1,979 | 1,897 … 1,980 | +14 |
| `Fitter` | 6,358 … 6,415 | 6,424 … 6,465 | +66 |
| `TimeQuest Timing Analyzer` | 2,337 … 2,371 | 2,329 … 2,402 | −1 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 13 | 15 | +2 |
| `CPU\|P65C816\|P` | 7 | 13 | +6 |
| `ascal\|o_poly_lum` | 3 | 1 | −2 |
| `hps_io\|video_calc\|dout` | 2 | 2 | 0 |
| `emu\|sdram\|SDRAM_A` | 0 | 4 | +4 |
| `emu\|sdram\|SDRAM_nCAS` | 0 | 3 | +3 |
| `emu\|ddram\|cache_addr` | 1 | 1 | 0 |
| `vs_r` | 0 | 2 | +2 |
| `ascal\|o_h_poly_pix.r` | 0 | 1 | +1 |
| `ascal\|o_lastv` | 1 | 0 | −1 |
| `ascal\|o_vacpt` | 1 | 0 | −1 |
| `ascal\|o_vcpt_pre3` | 0 | 1 | +1 |
| `ascal\|o_vcpt_sync` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_DQ~en` | 0 | 1 | +1 |
| `emu\|sdram\|old_sni_wr` | 0 | 1 | +1 |
| `hdmi_out_d` | 0 | 1 | +1 |

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

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37395104680). Report by [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) 1.2.0, multi-seed Quartus timing CI for MiSTer cores.</sub>