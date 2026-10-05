ProbeTable:
  dw P0, P1, P2, P3, P4, P5, P6, P7, P8, P9, P10, P11
  dw P12, P13, P14, P15, P16, P17, P18, P19, P20, P21, P22

P0:
  sync()
  jmp Done
P1:
  sync()
  x8(nop)
  jmp Done
P2:
  lda.b #$01
  sta.w $420d
  sync()
  x8(nop)
  jmp Done
P3:
  sync()
  jml $7e1800
P4:
  sync()
  x8(lda.w $0000)
  jmp Done
P5:
  sync()
  x8(lda.w $4300)
  jmp Done
P6:
  sync()
  x8(lda.w $4100)
  jmp Done
P7:
  sync()
  x8(lda.w $2101)
  jmp Done
P8:
  sync()
  x8(lda.w $6000)
  jmp Done
P9:
  sync()
  x8(pha)
  jmp Done
P10:
  ldx.w #$437f
  txs
  sync()
  x8(pha)
  jmp Done
P11:
  ldx.w #$41ff
  txs
  sync()
  x8(pha)
  jmp Done
P12:
  ldx.w #$21ff
  txs
  sync()
  x8(pha)
  jmp Done
P13:
  rep #$c3
  cli
  wai
P14:
  ldx.w #$437f
  txs
  rep #$c3
  cli
  wai
P15:
  ldx.w #$41ff
  txs
  rep #$c3
  cli
  wai
P18:
  sync()
  jml $00217f
P19:
  sync()
  jml $002180
P20:
  sync()
  lda.b #$7f
  sta.w $4201
  jmp DoneNoLatch
P21:
  lda.b #$7f
  sta.w $4201
  sync()
  lda.b #$ff
  sta.w $4201
  jmp DoneNoLatch
P22:
  sync()
  lda.b #$ff
  lda.w $2137
  jmp DoneNoLatch

// IRQ entry with S=$4203: pushes PB,PCH,PCL,P to $4203..$4200; PCL lands on WRIO.
origin 0x7088
base 0x80f088
P16:
  ldx.w #$4203
  txs
  rep #$c3
  cli
  wai
origin 0x7138
base 0x80f138
P17:
  ldx.w #$4203
  txs
  rep #$c3
  cli
  wai

