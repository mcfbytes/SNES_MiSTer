### <img src="https://raw.githubusercontent.com/mcfbytes/Seedy_MiSTer/master/art/seedy-kun.png" width="24" alt=""> [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) — SNES: dcde04d vs 2302683

**Possible regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 9 of 30 seeds of dcde04d, against 8 of 30 on 2302683. With 30 seeds a difference that size can be chance (p = 1.00). The clock that fails more often is `emu c2` (8 → 11 seeds, p = 0.58). The seed in the `.qsf` (1) does not close timing on dcde04d (worst setup −0.655 ns, hold +0.242 ns).

**Flagged** (timing got measurably worse):

- Logic utilization worse by 202.900 ALMs on average (p = 0.000)

|  | 2302683 | dcde04d | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 8/30 | 9/30 | +1 | 1.00 |
| Worst setup slack (ns), average / typical seed | −0.208 / −0.189 | −0.249 / −0.190 | −0.041 / −0.001 | 0.62 |
| Worst setup slack (ns), unluckiest seed | −0.732 | −0.957 | −0.225 |  |
| Total negative slack (ns), average | −0.353 | −0.687 | −0.334 | 0.10 |
| Seeds with a hold violation | 1/30 | 1/30 | 0 | 1.00 |
| Logic used (ALMs), average | 35,054 (83.6%) | 35,257 (84.1%) | +203 | < 0.001 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.345 / +0.199 ✗ | −0.655 / +0.242 ✗ | −0.310 / +0.043 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 14/30 | 15/30 | +1 | +0.003 | −0.042 | −0.045 | −0.690 | −0.957 | 1.00 |
| `emu c2` | 8/30 | 11/30 | +3 | +0.172 | +0.050 | −0.122 | −0.732 | −0.901 | 0.58 |
| `pll_hdmi c0` | 13/30 | 6/30 | −7 | +0.039 | +0.127 | +0.088 | −0.359 | −0.206 | 0.09 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 0 seeds of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 8 place(s) the baseline never fails: `emu|sdram|SDRAM_nCAS` (5), `emu|sdram|SDRAM_A` (3), `emu|sdram|SDRAM_nWE` (3), `emu|sdram|SDRAM_DQ~en` (2), `emu|sdram|SDRAM_nRAS` (2), `ascal|o_vcpt_pre3` (1), `ascal|o_vpixq_pre.r` (1), `emu|sdram|old_sni_rd` (1). Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 21** (meets timing; worst slack +0.252 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −0.655 ns).

<details><summary>Top 5 seeds of dcde04d</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 21 | ✓ | +0.252 | +0.372 | +0.252 | +3.480 | +0.752 | – | 80.48 | 35,293 |
| 3 | ✓ | +0.101 | +0.101 | +0.217 | +3.441 | +0.656 | – | 76.33 | 35,269 |
| 5 | ✓ | +0.100 | +0.100 | +0.201 | +3.815 | +0.717 | – | 79.85 | 35,204 |
| 29 | ✓ | +0.095 | +0.095 | +0.247 | +3.131 | +0.762 | – | 78.97 | 35,164 |
| 9 | ✓ | +0.059 | +0.059 | +0.237 | +3.720 | +0.866 | – | 79.78 | 35,186 |

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
| f(MAX) geomean | 79.13 | 78.77 | −0.36 | −0.07 [−1.36, +1.57] | 0.51 |  |
| WC slack: setup | −0.208 | −0.249 | −0.041 | −0.002 [−0.244, +0.254] | 0.62 |  |
| WC slack: hold | +0.205 | +0.216 | +0.011 | −0.003 [−0.019, +0.040] | 0.55 |  |
| WC slack: recovery | +3.782 | +3.682 | −0.100 | −0.109 [−0.419, +0.204] | 0.35 |  |
| WC slack: removal | +0.805 | +0.753 | −0.052 | −0.102 [−0.136, −0.010] | 0.10 |  |
| Total negative setup slack | −0.353 | −0.687 | −0.334 | +0.022 [−0.500, +0.285] | 0.10 |  |
| Logic utilization | 35,054 | 35,257 | +203 | +199 [+148, +266] | < 0.001 | ⚠️ flagged |
| Compilation time | 00:53:32 | 00:50:17 | −00:03:15 | +00:02:12 [−00:18:16, +00:13:10] | 0.46 |  |

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
| candidate | 1 | 81.20 | −0.655 | +0.242 | +3.030 | +0.426 | 35,187 | 00:52:10 |  |
| candidate | 2 | 81.82 | −0.256 | +0.183 | +3.334 | +0.993 | 35,245 | 00:54:15 |  |
| candidate | 3 | 76.33 | +0.101 | +0.217 | +3.441 | +0.656 | 35,269 | 01:01:35 | ✓ |
| candidate | 4 | 74.92 | −0.056 | +0.240 | +4.377 | +1.028 | 35,352 | 01:01:56 |  |
| candidate | 5 | 79.85 | +0.100 | +0.201 | +3.815 | +0.717 | 35,204 | 00:48:47 | ✓ |
| candidate | 6 | 81.40 | +0.079 | −0.083 | +3.996 | +0.708 | 35,205 | 00:50:36 |  |
| candidate | 7 | 77.49 | +0.006 | +0.248 | +3.736 | +0.808 | 35,288 | 01:01:42 | ✓ |
| candidate | 8 | 79.53 | −0.901 | +0.196 | +3.277 | +0.666 | 35,238 | 00:53:22 |  |
| candidate | 9 | 79.78 | +0.059 | +0.237 | +3.720 | +0.866 | 35,186 | 00:31:10 | ✓ |
| candidate | 10 | 79.05 | −0.815 | +0.147 | +3.550 | +0.702 | 35,262 | 00:40:18 |  |
| candidate | 11 | 76.92 | −0.316 | +0.256 | +2.952 | +0.695 | 35,373 | 01:02:18 |  |
| candidate | 12 | 82.30 | −0.128 | +0.176 | +3.092 | +0.775 | 35,182 | 00:46:42 |  |
| candidate | 13 | 73.02 | −0.261 | +0.244 | +4.163 | +0.657 | 35,348 | 01:15:05 |  |
| candidate | 14 | 77.36 | −0.252 | +0.247 | +4.120 | +0.829 | 35,359 | 01:09:37 |  |
| candidate | 15 | 77.16 | −0.579 | +0.254 | +3.935 | +0.850 | 35,354 | 01:05:49 |  |
| candidate | 16 | 80.24 | −0.713 | +0.249 | +4.481 | +0.924 | 35,312 | 01:07:29 |  |
| candidate | 17 | 78.33 | −0.386 | +0.252 | +4.097 | +0.709 | 35,201 | 00:49:45 |  |
| candidate | 18 | 82.56 | −0.017 | +0.250 | +4.060 | +0.727 | 35,194 | 00:42:21 |  |
| candidate | 19 | 80.72 | +0.005 | +0.143 | +3.420 | +0.697 | 35,183 | 00:34:56 | ✓ |
| candidate | 20 | 76.60 | −0.289 | +0.247 | +4.466 | +0.749 | 35,284 | 00:27:56 |  |
| candidate | 21 | 80.48 | +0.372 | +0.252 | +3.480 | +0.752 | 35,293 | 00:44:25 | ✓ |
| candidate | 22 | 75.44 | −0.480 | +0.232 | +3.409 | +0.743 | 35,284 | 00:54:30 |  |
| candidate | 23 | 80.38 | −0.957 | +0.251 | +3.655 | +0.714 | 35,178 | 00:47:28 |  |
| candidate | 24 | 78.72 | +0.012 | +0.218 | +4.175 | +0.726 | 35,328 | 00:58:47 | ✓ |
| candidate | 25 | 78.61 | −0.836 | +0.232 | +3.170 | +0.723 | 35,219 | 00:50:24 |  |
| candidate | 26 | 78.54 | −0.091 | +0.242 | +3.428 | +0.987 | 35,244 | 00:50:42 |  |
| candidate | 27 | 76.32 | +0.015 | +0.224 | +3.707 | +0.602 | 35,303 | 00:55:10 | ✓ |
| candidate | 28 | 79.37 | −0.265 | +0.236 | +3.409 | +0.701 | 35,216 | 00:45:58 |  |
| candidate | 29 | 78.97 | +0.095 | +0.247 | +3.131 | +0.762 | 35,164 | 00:22:36 | ✓ |
| candidate | 30 | 79.71 | −0.062 | +0.203 | +3.823 | +0.696 | 35,245 | 00:20:44 |  |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.344 / +7.689 | +6.784 / +7.725 | +0.440 / +0.036 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.508 / +4.968 | +4.273 / +5.036 | −0.235 / +0.068 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +7.742 / +8.726 | +4.990 / +8.681 | −2.752 / −0.045 | 1.00 |
| `emu c0` | 14/30 | 15/30 | +1 | −0.690 / +0.003 | −0.957 / −0.042 | −0.267 / −0.045 | 1.00 |
| `emu c1` | 0/30 | 0/30 | 0 | +4.082 / +8.079 | +4.266 / +7.711 | +0.184 / −0.368 | 1.00 |
| `emu c2` | 8/30 | 11/30 | +3 | −0.732 / +0.172 | −0.901 / +0.050 | −0.169 / −0.122 | 0.58 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.266 / +3.341 | +1.255 / +3.420 | −0.011 / +0.079 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.039 / +14.311 | +13.352 / +14.108 | +0.313 / −0.203 | 1.00 |
| `pll_hdmi c0` | 13/30 | 6/30 | −7 | −0.359 / +0.039 | −0.206 / +0.127 | +0.153 / +0.088 | 0.09 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.288 / +5.460 | +4.522 / +5.515 | +0.234 / +0.055 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.129 / +0.162 | +0.131 / +0.164 | +0.002 / +0.002 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.122 / +0.166 | +0.119 / +0.167 | −0.003 / +0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.108 / +0.139 | +0.069 / +0.139 | −0.039 / +0.000 | 1.00 |
| `emu c0` | 2/30 | 1/30 | −1 | −0.020 / +0.161 | −0.083 / +0.164 | −0.063 / +0.003 | 1.00 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.076 / +0.118 | +0.074 / +0.118 | −0.002 / +0.000 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.050 / +0.098 | +0.067 / +0.102 | +0.017 / +0.004 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.133 / +0.155 | +0.135 / +0.154 | +0.002 / −0.001 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.082 / +0.121 | +0.079 / +0.121 | −0.003 / +0.000 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.032 / +0.095 | +0.020 / +0.091 | −0.012 / −0.004 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.132 / +0.154 | +0.142 / +0.161 | +0.010 / +0.007 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 73.23 / 80.93 | 75.67 / 81.16 | +2.44 / +0.23 |
| `FPGA_CLK2_50` | 64.55 / 66.84 | 63.58 / 67.24 | −0.97 / +0.40 |
| `altera_reserved_tck` | 56.03 / 64.02 | 42.82 / 61.93 | −13.21 / −2.09 |
| `emu c0` | 81.10 / 85.56 | 79.38 / 85.18 | −1.72 / −0.38 |
| `emu c1` | 61.47 / 67.69 | 60.61 / 66.65 | −0.86 / −1.04 |
| `emu c2` | 24.80 / 26.10 | 25.05 / 26.17 | +0.25 / +0.07 |
| `h2f_user0_clk` | 114.50 / 146.15 | 114.35 / 145.47 | −0.15 / −0.68 |
| `pll_audio` | 36.18 / 37.88 | 36.59 / 37.69 | +0.41 / −0.19 |
| `pll_hdmi c0` | 141.02 / 148.74 | 144.13 / 151.62 | +3.11 / +2.88 |
| `spi_sck` | 175.07 / 228.86 | 182.55 / 225.92 | +7.48 / −2.94 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 34,961 … 35,204 | 35,164 … 35,373 | +203 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,164 … 33,375 | 33,131 … 33,419 | +30 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:53 … 00:05:19 | 00:04:27 … 00:06:03 | +00:00:21 |
| `Assembler` | 00:00:12 … 00:00:24 | 00:00:14 … 00:00:24 | +00:00:01 |
| `Fitter` | 00:19:01 … 01:20:49 | 00:14:55 … 01:09:44 | −00:03:41 |
| `TimeQuest Timing Analyzer` | 00:00:15 … 00:00:28 | 00:00:16 … 00:00:30 | +00:00:03 |
| `Total` | 00:24:22 … 01:26:10 | 00:20:44 … 01:15:05 | −00:03:15 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,570 | 3,506 … 3,570 | −11 |
| `Assembler` | 1,897 … 1,979 | 1,899 … 1,982 | +8 |
| `Fitter` | 6,358 … 6,415 | 6,383 … 6,436 | +28 |
| `TimeQuest Timing Analyzer` | 2,337 … 2,371 | 2,334 … 2,379 | +3 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 13 | 11 | −2 |
| `CPU\|P65C816\|P` | 7 | 9 | +2 |
| `emu\|sdram\|SDRAM_nCAS` | 0 | 5 | +5 |
| `hps_io\|video_calc\|dout` | 2 | 2 | 0 |
| `ascal\|o_poly_lum` | 3 | 0 | −3 |
| `emu\|sdram\|SDRAM_A` | 0 | 3 | +3 |
| `emu\|sdram\|SDRAM_nWE` | 0 | 3 | +3 |
| `emu\|sdram\|SDRAM_DQ~en` | 0 | 2 | +2 |
| `emu\|sdram\|SDRAM_nRAS` | 0 | 2 | +2 |
| `ascal\|o_lastv` | 1 | 0 | −1 |
| `ascal\|o_vacpt` | 1 | 0 | −1 |
| `ascal\|o_vcpt_pre3` | 0 | 1 | +1 |
| `ascal\|o_vpixq_pre.r` | 0 | 1 | +1 |
| `emu\|ddram\|cache_addr` | 1 | 0 | −1 |
| `emu\|sdram\|old_sni_rd` | 0 | 1 | +1 |

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

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37395097159). Report by [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) 1.2.0, multi-seed Quartus timing CI for MiSTer cores.</sub>