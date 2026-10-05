ProbeTable:
  dw Q0, Q1, Q2, Q3, S0, S1, S2, S3, S4, S5, S6, S7, S8, S9, S10, S11, S12, S13

// H+V wake, as busprobe P0
Q0:
  sync()
  jmp Done
// V-only wake: VTIME=100, HTIME ignored
Q1:
  lda.b #$20
  sta.w $4200
  sync()
  jmp Done
// $2137 with WRIO bit 7 clear: no latch expected (stale vblank value)
Q2:
  lda.b #$7f
  sta.w $4201
  sync()
  lda.b #$7f
  lda.w $2137
  jmp DoneNoLatch
// PHA of $7F onto $4201 (WRIO 1->0 by a stack write)
Q3:
  ldx.w #$4201
  txs
  sync()
  lda.b #$7f
  pha
  jmp DoneNoLatch

// IRQ arriving inside a slow-ROM NOP sled; HTIME = 72+d steps the phase by 4 clocks against the 14-clock NOP
macro sweep(d) {
  sync()
  lda.b #72+{d}
  sta.w $4207
  lda.w $4211
  cli
  x8(nop)
  x8(nop)
  x8(nop)
  x8(nop)
  jmp Done
}
S0:
  sweep(0)
S1:
  sweep(1)
S2:
  sweep(2)
S3:
  sweep(3)
S4:
  sweep(4)
S5:
  sweep(5)
S6:
  sweep(6)
S7:
  sweep(7)
S8:
  sweep(8)
S9:
  sweep(9)
S10:
  sweep(10)
S11:
  sweep(11)
S12:
  sweep(12)
S13:
  sweep(13)
