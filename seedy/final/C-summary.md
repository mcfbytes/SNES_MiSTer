### <img src="https://raw.githubusercontent.com/mcfbytes/Seedy_MiSTer/master/art/seedy-kun.png" width="24" alt=""> [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) — SNES: 57160ab vs 2302683

**Possible regression** · Quartus 17.0.2 · 30 seeds each · NUM_PARALLEL_PROCESSORS ALL · timing at the slow 100 °C corner

Timing closed on 6 of 30 seeds of 57160ab, against 8 of 30 on 2302683. With 30 seeds a difference that size can be chance (p = 0.76). The clock that fails more often is `emu c2` (8 → 20 seeds, p = 0.004). The seed in the `.qsf` (1) does not close timing on 57160ab (worst setup −0.554 ns, hold −0.124 ns).

**Flagged** (timing got measurably worse):

- Total negative setup slack worse by 1.731 ns on average (p = 0.003)
- Logic utilization worse by 87.467 ALMs on average (p = 0.000)

|  | 2302683 | 57160ab | Δ | p |
|---|---|---|---|---|
| Seeds that close timing | 8/30 | 6/30 | −2 | 0.76 |
| Worst setup slack (ns), average / typical seed | −0.208 / −0.189 | −0.403 / −0.320 | −0.195 / −0.131 | 0.07 |
| Worst setup slack (ns), unluckiest seed | −0.732 | −1.620 | −0.888 |  |
| Total negative slack (ns), average | −0.353 | −2.085 | −1.732 | 0.003 |
| Seeds with a hold violation | 1/30 | 5/30 | +4 | 0.19 |
| Logic used (ALMs), average | 35,054 (83.6%) | 35,141 (83.8%) | +87 | < 0.001 |
| The `.qsf`'s seed (1): setup / hold (ns) | −0.345 / +0.199 ✗ | −0.554 / −0.124 ✗ | −0.209 / −0.323 |  |

| clock failing setup | seeds (base) | seeds (PR) | Δ | typical slack (base) | typical slack (PR) | Δ | unluckiest (base) | unluckiest (PR) | p |
|---|---|---|---|---|---|---|---|---|---|
| `emu c0` | 14/30 | 23/30 | +9 | +0.003 | −0.269 | −0.272 | −0.690 | −1.005 | 0.03 |
| `emu c2` | 8/30 | 20/30 | +12 | +0.172 | −0.160 | −0.332 | −0.732 | −1.620 | 0.004 |
| `pll_hdmi c0` | 13/30 | 8/30 | −5 | +0.039 | +0.180 | +0.141 | −0.359 | −0.153 | 0.28 |

- Timing constraints: nothing new is left untimed. Both sides share: 95 i/o pins with no timing constraint; see *Constraint health*.
- Outside the slow 100 °C corner, at the cold/fast corners Quartus also models but this core's report leaves out, hold fails on 1 seed of the baseline and 0 seeds of the PR. Real, but not what maintainers' own builds show.
- Failing paths end in 13 place(s) the baseline never fails: `emu|sdram|SDRAM_nCAS` (4), `emu|sdram|SDRAM_nWE` (4), `emu|sdram|SDRAM_A` (3), `emu|sdram|SDRAM_DQ~en` (2), `emu|sdram|old_sni_rd` (2), `emu|ddram|ram_address` (1), `emu|ddram|ram_burst` (1), `emu|ddram|state.11` (1) and 5 more. Each shows up on too few of 30 seeds to tell from placement luck.

**Recommended seed for hardware testing: 7** (meets timing; worst slack +0.252 ns).

- Its `.rbf` is in the `seedy-rbf` artifact; that exact bitstream is what was measured.
- The `.qsf`'s seed 1 does not meet timing (worst slack −0.554 ns).

<details><summary>Top 5 seeds of 57160ab</summary>

| seed | met | worst | setup | hold | recovery | removal | TNS sum | f(MAX) | ALMs |
|---|---|---|---|---|---|---|---|---|---|
| 7 | ✓ | +0.252 | +0.324 | +0.252 | +3.401 | +0.709 | – | 77.83 | 35,145 |
| 16 | ✓ | +0.188 | +0.188 | +0.253 | +4.282 | +0.739 | – | 79.44 | 35,279 |
| 9 | ✓ | +0.167 | +0.302 | +0.167 | +3.667 | +0.708 | – | 78.49 | 35,091 |
| 23 | ✓ | +0.147 | +0.218 | +0.147 | +3.483 | +0.790 | – | 77.14 | 35,097 |
| 19 | ✓ | +0.138 | +0.294 | +0.138 | +3.667 | +0.737 | – | 80.33 | 35,107 |

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
| f(MAX) geomean | 79.13 | 78.95 | −0.18 | −0.34 [−1.56, +1.35] | 0.70 |  |
| WC slack: setup | −0.208 | −0.403 | −0.195 | −0.132 [−0.429, +0.033] | 0.07 |  |
| WC slack: hold | +0.205 | +0.131 | −0.074 | −0.042 [−0.075, +0.028] | 0.05 |  |
| WC slack: recovery | +3.782 | +3.543 | −0.239 | −0.210 [−0.426, +0.058] | 0.02 | significant shift, but no seed fails recovery |
| WC slack: removal | +0.805 | +0.781 | −0.024 | −0.094 [−0.132, +0.008] | 0.42 |  |
| Total negative setup slack | −0.353 | −2.085 | −1.732 | −0.359 [−0.825, −0.021] | 0.003 | ⚠️ flagged |
| Logic utilization | 35,054 | 35,141 | +87 | +78 [+32, +146] | < 0.001 | ⚠️ flagged |
| Compilation time | 00:53:32 | 00:48:46 | −00:04:46 | +00:01:06 [−00:19:40, +00:10:54] | 0.27 |  |

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
| candidate | 1 | 81.57 | −0.554 | −0.124 | +3.477 | +0.658 | 35,086 | 00:50:25 |  |
| candidate | 2 | 80.78 | −0.284 | +0.135 | +3.338 | +0.717 | 35,121 | 00:50:19 |  |
| candidate | 3 | 77.14 | −0.618 | +0.252 | +3.596 | +0.704 | 35,205 | 00:58:11 |  |
| candidate | 4 | 78.45 | +0.075 | +0.247 | +3.626 | +1.001 | 35,178 | 00:58:10 | ✓ |
| candidate | 5 | 82.69 | −0.298 | +0.179 | +3.569 | +0.671 | 35,110 | 00:49:57 |  |
| candidate | 6 | 81.16 | −0.542 | +0.251 | +3.744 | +0.673 | 35,090 | 00:51:14 |  |
| candidate | 7 | 77.83 | +0.324 | +0.252 | +3.401 | +0.709 | 35,145 | 00:57:30 | ✓ |
| candidate | 8 | 81.74 | −0.300 | +0.185 | +3.362 | +0.712 | 35,066 | 00:48:02 |  |
| candidate | 9 | 78.49 | +0.302 | +0.167 | +3.667 | +0.708 | 35,091 | 00:30:46 | ✓ |
| candidate | 10 | 78.98 | −0.241 | +0.223 | +2.894 | +0.658 | 35,045 | 00:47:24 |  |
| candidate | 11 | 77.94 | −0.250 | +0.250 | +3.845 | +0.882 | 35,204 | 01:01:42 |  |
| candidate | 12 | 79.45 | −0.626 | +0.189 | +3.948 | +0.812 | 35,055 | 00:47:02 |  |
| candidate | 13 | 76.24 | −0.143 | −0.302 | +3.699 | +0.828 | 35,287 | 01:09:00 |  |
| candidate | 14 | 75.69 | −0.852 | −0.376 | +4.151 | +0.977 | 35,228 | 01:05:16 |  |
| candidate | 15 | 77.92 | −1.620 | +0.243 | +3.521 | +1.008 | 35,228 | 01:03:38 |  |
| candidate | 16 | 79.44 | +0.188 | +0.253 | +4.282 | +0.739 | 35,279 | 01:04:08 | ✓ |
| candidate | 17 | 80.81 | −0.540 | +0.245 | +2.812 | +0.680 | 35,115 | 00:41:56 |  |
| candidate | 18 | 79.34 | −0.907 | +0.168 | +3.986 | +0.745 | 35,070 | 00:33:44 |  |
| candidate | 19 | 80.33 | +0.294 | +0.138 | +3.667 | +0.737 | 35,107 | 00:33:21 | ✓ |
| candidate | 20 | 77.40 | −0.369 | +0.244 | +3.778 | +0.801 | 35,176 | 00:27:31 |  |
| candidate | 21 | 77.35 | −0.476 | −0.234 | +3.591 | +0.728 | 35,159 | 00:38:39 |  |
| candidate | 22 | 77.56 | −0.627 | +0.248 | +3.368 | +1.003 | 35,190 | 01:00:59 |  |
| candidate | 23 | 77.14 | +0.218 | +0.147 | +3.483 | +0.790 | 35,097 | 00:48:40 | ✓ |
| candidate | 24 | 78.25 | −0.090 | +0.239 | +3.287 | +0.956 | 35,127 | 00:59:29 |  |
| candidate | 25 | 81.33 | −0.409 | +0.199 | +4.144 | +0.945 | 35,105 | 00:48:24 |  |
| candidate | 26 | 79.71 | −0.217 | −0.344 | +3.481 | +0.738 | 35,063 | 00:49:09 |  |
| candidate | 27 | 77.52 | −0.340 | +0.253 | +3.697 | +0.705 | 35,219 | 00:53:55 |  |
| candidate | 28 | 78.99 | −1.503 | +0.151 | +2.816 | +0.713 | 35,173 | 00:44:38 |  |
| candidate | 29 | 76.55 | −0.281 | +0.247 | +2.599 | +0.705 | 35,133 | 00:28:18 |  |
| candidate | 30 | 80.59 | −1.394 | +0.198 | +3.475 | +0.721 | 35,085 | 00:21:25 |  |

</details>
<details><summary>Per-clock setup slack, every clock</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +6.344 / +7.689 | +5.965 / +7.723 | −0.379 / +0.034 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +4.508 / +4.968 | +4.339 / +5.186 | −0.169 / +0.218 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +7.742 / +8.726 | +6.986 / +8.442 | −0.756 / −0.284 | 1.00 |
| `emu c0` | 14/30 | 23/30 | +9 | −0.690 / +0.003 | −1.005 / −0.269 | −0.315 / −0.272 | 0.03 |
| `emu c1` | 0/30 | 0/30 | 0 | +4.082 / +8.079 | +6.342 / +7.595 | +2.260 / −0.484 | 1.00 |
| `emu c2` | 8/30 | 20/30 | +12 | −0.732 / +0.172 | −1.620 / −0.160 | −0.888 / −0.332 | 0.004 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +1.266 / +3.341 | +1.075 / +3.362 | −0.191 / +0.021 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +13.039 / +14.311 | +13.348 / +14.517 | +0.309 / +0.206 | 1.00 |
| `pll_hdmi c0` | 13/30 | 8/30 | −5 | −0.359 / +0.039 | −0.153 / +0.180 | +0.206 / +0.141 | 0.28 |
| `spi_sck` | 0/30 | 0/30 | 0 | +4.288 / +5.460 | +3.886 / +5.708 | −0.402 / +0.248 | 1.00 |

</details>
<details><summary>Per-clock hold slack</summary>

| clock | base fails | PR fails | Δ fails | base min / median | PR min / median | Δ min / median | Fisher p |
|---|---|---|---|---|---|---|---|
| `FPGA_CLK1_50` | 0/30 | 0/30 | 0 | +0.129 / +0.162 | +0.130 / +0.164 | +0.001 / +0.002 | 1.00 |
| `FPGA_CLK2_50` | 0/30 | 0/30 | 0 | +0.122 / +0.166 | +0.120 / +0.165 | −0.002 / −0.001 | 1.00 |
| `altera_reserved_tck` | 0/30 | 0/30 | 0 | +0.108 / +0.139 | +0.073 / +0.139 | −0.035 / +0.000 | 1.00 |
| `emu c0` | 2/30 | 5/30 | +3 | −0.020 / +0.161 | −0.376 / +0.163 | −0.356 / +0.002 | 0.42 |
| `emu c1` | 0/30 | 0/30 | 0 | +0.076 / +0.118 | +0.074 / +0.115 | −0.002 / −0.003 | 1.00 |
| `emu c2` | 0/30 | 0/30 | 0 | +0.050 / +0.098 | +0.050 / +0.104 | +0.000 / +0.006 | 1.00 |
| `h2f_user0_clk` | 0/30 | 0/30 | 0 | +0.133 / +0.155 | +0.131 / +0.153 | −0.002 / −0.002 | 1.00 |
| `pll_audio` | 0/30 | 0/30 | 0 | +0.082 / +0.121 | +0.086 / +0.121 | +0.004 / +0.000 | 1.00 |
| `pll_hdmi c0` | 0/30 | 0/30 | 0 | +0.032 / +0.095 | +0.013 / +0.086 | −0.019 / −0.009 | 1.00 |
| `spi_sck` | 0/30 | 0/30 | 0 | +0.132 / +0.154 | +0.136 / +0.159 | +0.004 / +0.005 | 1.00 |

</details>
<details><summary>f(MAX) per clock (worst corner)</summary>

| clock | baseline min / mean MHz | PR min / mean MHz | Δ min / mean |
|---|---|---|---|
| `FPGA_CLK1_50` | 73.23 / 80.93 | 71.25 / 80.72 | −1.98 / −0.21 |
| `FPGA_CLK2_50` | 64.55 / 66.84 | 63.85 / 67.27 | −0.70 / +0.43 |
| `altera_reserved_tck` | 56.03 / 64.02 | 51.65 / 61.03 | −4.38 / −2.99 |
| `emu c0` | 81.10 / 85.56 | 79.08 / 84.42 | −2.02 / −1.14 |
| `emu c1` | 61.47 / 67.69 | 59.23 / 67.80 | −2.24 / +0.11 |
| `emu c2` | 24.80 / 26.10 | 24.55 / 25.76 | −0.25 / −0.34 |
| `h2f_user0_clk` | 114.50 / 146.15 | 112.04 / 144.24 | −2.46 / −1.91 |
| `pll_audio` | 36.18 / 37.88 | 36.58 / 38.07 | +0.40 / +0.19 |
| `pll_hdmi c0` | 141.02 / 148.74 | 145.24 / 152.12 | +4.22 / +3.38 |
| `spi_sck` | 175.07 / 228.86 | 163.56 / 235.95 | −11.51 / +7.09 |

</details>
<details><summary>Utilization</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `alms` | 34,961 … 35,204 | 35,045 … 35,287 | +87 |
| `alms_total` | 41,910 … 41,910 | 41,910 … 41,910 | 0 |
| `block_memory_bits` | 4,153,666 … 4,153,937 | 4,153,666 … 4,153,937 | 0 |
| `dsp_blocks` | 60 … 61 | 60 … 61 | 0 |
| `pins` | 145 … 145 | 145 … 145 | 0 |
| `plls` | 3 … 3 | 3 … 3 | 0 |
| `ram_blocks` | 544 … 547 | 544 … 547 | 0 |
| `registers` | 33,164 … 33,375 | 33,069 … 33,424 | +34 |

</details>
<details><summary>Runtime</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 00:03:53 … 00:05:19 | 00:04:13 … 00:05:57 | +00:00:19 |
| `Assembler` | 00:00:12 … 00:00:24 | 00:00:13 … 00:00:24 | 00:00:00 |
| `Fitter` | 00:19:01 … 01:20:49 | 00:14:57 … 01:03:45 | −00:05:08 |
| `TimeQuest Timing Analyzer` | 00:00:15 … 00:00:28 | 00:00:17 … 00:00:30 | +00:00:02 |
| `Total` | 00:24:22 … 01:26:10 | 00:21:25 … 01:09:00 | −00:04:47 |

</details>
<details><summary>Peak memory (MB)</summary>

|  | baseline (min … max) | PR (min … max) | Δ mean |
|---|---|---|---|
| `Analysis & Synthesis` | 3,506 … 3,570 | 3,506 … 3,570 | −3 |
| `Assembler` | 1,897 … 1,979 | 1,898 … 1,981 | +2 |
| `Fitter` | 6,358 … 6,415 | 6,397 … 6,458 | +52 |
| `TimeQuest Timing Analyzer` | 2,337 … 2,371 | 2,324 … 2,376 | −2 |

</details>
<details><summary>Failing endpoints</summary>

| failing endpoint (normalised) | baseline seeds | PR seeds | Δ |
|---|---|---|---|
| `emu\|sdram\|din` | 13 | 18 | +5 |
| `CPU\|P65C816\|P` | 7 | 19 | +12 |
| `emu\|ddram\|cache_addr` | 1 | 3 | +2 |
| `emu\|sdram\|SDRAM_nCAS` | 0 | 4 | +4 |
| `emu\|sdram\|SDRAM_nWE` | 0 | 4 | +4 |
| `ascal\|o_poly_lum` | 3 | 0 | −3 |
| `hps_io\|video_calc\|dout` | 2 | 1 | −1 |
| `emu\|sdram\|SDRAM_A` | 0 | 3 | +3 |
| `emu\|sdram\|SDRAM_DQ~en` | 0 | 2 | +2 |
| `emu\|sdram\|old_sni_rd` | 0 | 2 | +2 |
| `ascal\|o_lastv` | 1 | 0 | −1 |
| `ascal\|o_vacpt` | 1 | 0 | −1 |
| `emu\|ddram\|ram_address` | 0 | 1 | +1 |
| `emu\|ddram\|ram_burst` | 0 | 1 | +1 |
| `emu\|ddram\|state.11` | 0 | 1 | +1 |
| `P65C816\|AddrGen\|PCr` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_A~_Duplicate_1` | 0 | 1 | +1 |
| `emu\|sdram\|SDRAM_nRAS` | 0 | 1 | +1 |
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

<sub>30 seeds per variant detect only large shifts; seeds are unpaired samples. ~10 metrics tested, p-values uncorrected (two-sided permutation test on means, 20,000 shuffles, fixed RNG; Fisher exact for counts). QoF exists only for DSE runs. [Run and artifacts](https://github.com/mcfbytes/SNES_MiSTer/actions/runs/37395112714). Report by [MiSTer Seedy](https://github.com/mcfbytes/Seedy_MiSTer) 1.2.0, multi-seed Quartus timing CI for MiSTer cores.</sub>