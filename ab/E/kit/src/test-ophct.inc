// ophct: OPHCT/OPVCT read by $2137 as the first instruction of the IRQ handler, per (mode, HTIME) row (RefTab:
// mode htl hth flags bmin(2) bmax(2); flags bit0 = sled row, bit1 = VTIME=0 instead of VS). WAI rows: cli; wai -> the
// vector is taken on the wake. Sled rows: cli then a NOP loop until the IRQ arrives. NMI (enabled) rescues rows that
// never fire: H=V=$1FF.
// Results: $0400 + round*$100 + row*8 = Hlo Hhi Vlo Vhi.
// The vblank wait reads $4210 twice: a read that lands inside the 4-clock window in which the NMI flag is being set
// returns 1 without clearing it (core, bsnes, Mesen and fullsnes agree), and enabling NMI right after that would
// take an NMI at once (the 1FF rows of the first rig run). RACE=1 keeps the single read and shifts the poll phase per
// round to show that race on the emulators.

IrqEntry:
  lda.w $2137
  lda.w $213f
  lda.w $213c
  sta.b $40
  lda.w $213c
  and.b #$01
  sta.b $41
  lda.w $213d
  sta.b $42
  lda.w $213d
  and.b #$01
  sta.b $43
  jmp Done
NmiEntry:
  lda.b #$ff
  sta.b $40
  sta.b $42
  lda.b #$01
  sta.b $41
  sta.b $43
  jmp Done
Done:
  sei
  stz.w $4200
  lda.w $4211
  lda.w $4210
  ldx.w #$01ff
  txs
  ldx.b $22
  lda.b $40
  sta.w $0400,x
  lda.b $41
  sta.w $0401,x
  lda.b $42
  sta.w $0402,x
  lda.b $43
  sta.w $0403,x
  rep #$20
  inc.b $20
  lda.b $20
  cmp.w #NROWS
  sep #$20
  bne +
  stz.b $20
  stz.b $21
  inc.b $26
  lda.b $26
  cmp.b #NROUNDS
  bne +
  jmp Display
+
  jmp RowLoop

TestMain:
  ldx.w #0
  stx.b $20
  stz.b $26
  stz.b $27
RowLoop:
  // X = row*8 (RefTab), $22 = round*256 + row*8
  rep #$20
  lda.b $20
  asl
  asl
  asl
  tax
  sta.b $22
  lda.b $26
  and.w #$00ff
  xba
  ora.b $22
  sta.b $22
  sep #$20
  sei
  stz.w $4200
  lda.w RefTab+1,x
  sta.w $4207
  lda.w RefTab+2,x
  sta.w $4208
  lda.w RefTab+3,x
  and.b #$02
  beq +
  stz.w $4209
  bra ++
+
  lda.b #VS
  sta.w $4209
+
  stz.w $420a
  lda.w RefTab,x
  asl
  asl
  asl
  asl
  ora.b #$80
  sta.b $24
  lda.w RaceFlag
  beq VWait
  // RACE: shift the poll phase by round*16 clocks
  phx
  rep #$20
  lda.b $26
  and.w #$0007
  tax
  sep #$20
-
  beq +
  nop
  dex
  bra -
+
  plx
VWait:
  // wait for the start of vblank
  lda.w $4210
  bpl VWait
  lda.w RaceFlag
  bne +
  lda.w $4210
+
  lda.w $4211
  lda.b $24
  sta.w $4200
  lda.w RefTab+3,x
  and.b #$01
  bne Sled
  cli
  wai
  jmp Hang
Sled:
  cli
-
  x8(nop)
  x8(nop)
  bra -

// display: Hmin Hmax over rounds; dev build: green when both equal the bsnes ref; kit build: white
Rows:
  ldx.w #0
  stx.b $30
RowDisp:
  rep #$20
  lda.b $30
  asl
  tay
  lda.w RowPos,y
  sta.w $2116
  lda.b $30
  asl
  asl
  asl
  sta.b $32
  tax
  lda.w #$ffff
  sta.b $50
  stz.b $52
  ldy.w #NROUNDS
-
  lda.w $0400,x
  cmp.b $50
  bcs +
  sta.b $50
+
  cmp.b $52
  bcc +
  sta.b $52
+
  txa
  clc
  adc.w #$0100
  tax
  dey
  bne -
  ldx.b $32
  sep #$20
  lda.b #$04
  sta.b $13
  rep #$20
  lda.b $50
  cmp.w RefTab+4,x
  bne +
  lda.b $52
  cmp.w RefTab+6,x
  beq ++
+
  sep #$20
  lda.b #$08
  sta.b $13
+
  sep #$20
  lda.w KitFlag
  beq +
  stz.b $13
+
  lda.b $51
  jsr PutNib
  lda.b $50
  jsr PutByte
  jsr PutSpace
  lda.b $53
  jsr PutNib
  lda.b $52
  jsr PutByte
  rep #$20
  inc.b $30
  lda.b $30
  cmp.w #NROWS
  sep #$20
  beq +
  jmp RowDisp
+
  rts
