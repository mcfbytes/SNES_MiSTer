# Hold timing on PR B (Seedy run 37264587249: ppu-460 0148bb7 vs master 2302683)

Seedy flagged "WC hold slack 0.084 ns worse on average (p = 0.023)" and 6/30 seeds with a hold violation against 1/30.
Source: the per-seed TimeQuest reports in the run's `seedy-reports` artifact; `B-hold-paths-under-0.1ns.csv` here.

**Every failing hold path, on both sides, is a crossing from `emu c2` (clk_sys, 21.48 MHz) to `emu c0` (clk_mem,
85.9 MHz), into the DDR3 cache address registers of `rtl/ddram.sv`.** None start or end in the PPU or the CPU.

| side | seed | slack (slow 100 °C) | from | to |
|---|---|---|---|---|
| master | 13 | −0.020 | `savestates:ss|ss_ddr_addr[4]` | `ddram|cache_addr[4]` |
| PR | 2 | −0.177 | `msu_data_store|ram_address[26]` | `ddram|cache_addr2[29]` |
| PR | 6 | −0.342 | `msu_data_store|ram_address[25]` | `ddram|cache_addr2[28]` |
| PR | 18 | −0.228 | `msu_data_store|ram_address[26]` | `ddram|cache_addr2[29]` |
| PR | 20 | −0.426 | `savestates:ss|ss_ddr_addr[3]~DUPLICATE` | `ddram|cache_addr[3]` |
| PR | 25 | −0.009 | `savestates:ss|ss_ddr_addr[6]` | `ddram|cache_addr[6]` |
| PR | 28 | −0.118 | `msu_data_store|ram_address[25]` | `ddram|cache_addr2[28]` |

- Per clock (minimum hold slack per seed, slow 100 °C, mean over 30 seeds): `emu c0` +0.372 → +0.251 ns, 1 → 6 seeds
  below 0. `emu c2`, where the PPU and CPU run: +0.247 → +0.251 ns, 0 → 0 seeds below 0 (worst +0.143 → +0.224).
  `emu c1` +0.256 → +0.252. The whole mean shift comes from the `emu c0` tail.
- None of the PR's new registers (the delayed pixel/window pipeline, `H_BG`, the Mode 7 pixel delay, the /PAWR
  force-blank latch, the IRQ delay) appear among any seed's 20 worst setup or hold paths, at any corner.
  The only PPU registers among paths under +0.1 ns of hold are the existing `CGRAM_ADDR_CLR` → CGRAM port paths at the
  fast −40 °C corner (≥ +0.076 ns), on 5 master seeds and 3 PR seeds.
- The same crossings fail on master builds with no PPU or CPU change: the c61bfd4 baseline (30 seeds, runs
  37136647086 / 37189154113 / 37205363393 / 37214664117) fails `msu_data_store|ram_address[28] → ddram|cache_addr2[31]`
  at −0.319 ns (seed 8) and `savestates|ss_ddr_addr[4] → cache_addr[4]` at −0.138 ns (seed 13). Candidates in those
  runs that touch neither MSU nor DDR also fail them. Seeds with a negative hold path at the slow 100 °C corner, per
  30-seed group: master c61bfd4 4 (2 of them `sni → sdram`), IRQ+gate 4, power-on RAM 1, IRQ only 1, $2137 gate 1,
  master 2302683 1, this PR 6.
- The paths are `ddram.sv` capturing the read address of a request on clk_mem. `msu_data_store` changes `ram_address`
  only while no request is pending (`ram_ack == ram_req`) and toggles `ram_req` on the same clk_sys edge; `ddram`
  loads `cache_addr2` only while `rd_req2 != rd_ack2`. The savestate port follows the same req/ack pattern.
- So the PR does not create these paths and no PPU logic is on them; placement moved, and an existing,
  unconstrained clk_sys → clk_mem address crossing came out tighter more often. A change in this PR cannot target it.
  The fix, if wanted, belongs to `ddram.sv` / the SDC (for example a hold multicycle on the request-address crossing)
  and is out of scope here.
- The `.qsf` seed (1) meets setup and hold on the PR (+0.132 / +0.176 ns). Recommended seed 11: +0.217 / +0.242 ns.
