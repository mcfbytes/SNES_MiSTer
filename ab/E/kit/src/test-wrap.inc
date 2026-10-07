// wrap: count H/V IRQs per frame for each case in RefTab (12 bytes: expmin16 expmax16 mode htl hth vtl vth setini hw
// bnd 0). Per case: 12 frames; frames 3..11 give min/max. Result $0400+case*8: min(2) max(2) nmilost(1).
// Frame boundary, two ways (RefTab byte 10, "bnd"):
//   bnd=0 (0-1 IRQs per frame): the NMI handler reads $4210 and sets $18; the first IRQ after that takes the boundary
//     (Snap) from inside the IRQ handler, or the main loop does after ~2 lines without an IRQ. An IRQ racing the NMI is
//     counted in exactly one frame whichever is serviced first.
//   bnd=1 (an IRQ on every line): the IRQ handler latches OPVCT; a V that does not increase is the frame wrap and takes
//     the boundary. The NMI plays no part in the count, so no ordering race exists. The NMI handler still sets $18, and
//     a wrap that finds $18 clear means a frame passed with no NMI serviced: the row is flagged N (sticky per case).
// Direct page: $10 count, $14 frame*2, $18 NMI seen, $1A bnd, $1B NMI lost, $1C/$1D last V.

NmiEntry:
  php
  sep #$20
  pha
  lda.w $4210
  lda.b #$01
  sta.b $18
  pla
  plp
  rti

IrqEntry:
  php
  rep #$20
  pha
  phx
  sep #$20
  lda.w $4211
  lda.b $1a
  bne ByWrap
  lda.b $18
  beq Count
  jsr Snap
  bra Count
ByWrap:
  lda.w $213f
  lda.w $2137
  lda.w $213d
  sta.b $40
  lda.w $213d
  and.b #$01
  sta.b $41
  rep #$20
  lda.b $40
  cmp.b $1c
  beq Wrapped
  bcs StoreV
Wrapped:
  // V <= last V: the frame wrapped; the boundary is before this IRQ
  sep #$20
  lda.b $18
  bne +
  lda.b $14
  cmp.b #4
  bcc +
  lda.b #$01
  sta.b $1b
+
  jsr Snap
  rep #$20
  lda.b $40
StoreV:
  sta.b $1c
  sep #$20
Count:
  rep #$20
  inc.b $10
  plx
  pla
  plp
  rti

// frame boundary (I=1 on entry): store the count at $0500+frame*2, reset it, advance the frame, clear $18
Snap:
  rep #$20
  lda.b $10
  ldx.b $14
  sta.w $0500,x
  stz.b $10
  inx
  inx
  stx.b $14
  sep #$20
  stz.b $18
  rts

TestMain:
  ldx.w #0
  stx.b $20
CaseLoop:
  // X = case*12
  rep #$20
  lda.b $20
  asl
  adc.b $20
  asl
  asl
  tax
  sep #$20
  sei
  stz.w $4200
  lda.w RefTab+9,x
  sta.w $2133
  lda.w RefTab+5,x
  sta.w $4207
  lda.w RefTab+6,x
  sta.w $4208
  lda.w RefTab+7,x
  sta.w $4209
  lda.w RefTab+8,x
  sta.w $420a
  lda.w RefTab+11,x
  sta.b $1a
  lda.w $4211
  lda.w $4210
  stz.b $10
  stz.b $11
  stz.b $14
  stz.b $15
  stz.b $18
  stz.b $1b
  lda.b #$ff
  sta.b $1c
  lda.b #$01
  sta.b $1d
  lda.w RefTab+4,x
  asl
  asl
  asl
  asl
  ora.b #$80
  sta.w $4200
  cli
Wait:
  lda.b $14
  cmp.b #24
  bcs WaitDone
  lda.b $1a
  bne Wait
  lda.b $18
  beq Wait
  // the NMI was seen: give the IRQ handler about two lines to take the boundary (IRQs stay enabled)
  ldx.w #80
-
  dex
  bne -
  sei
  lda.b $18
  beq +
  jsr Snap
+
  cli
  bra Wait
WaitDone:
  sei
  stz.w $4200
  lda.w $4211
  // min/max over frames 3..11 ($0506..$0516)
  rep #$20
  lda.w #$ffff
  sta.b $50
  stz.b $52
  ldx.w #6
-
  lda.w $0500,x
  cmp.b $50
  bcs +
  sta.b $50
+
  cmp.b $52
  bcc +
  sta.b $52
+
  inx
  inx
  cpx.w #24
  bne -
  lda.b $20
  asl
  asl
  asl
  tax
  lda.b $50
  sta.w $0400,x
  lda.b $52
  sta.w $0402,x
  sep #$20
  lda.b $1b
  sta.w $0404,x
  rep #$20
  inc.b $20
  lda.b $20
  cmp.w #NCASES
  sep #$20
  beq +
  jmp CaseLoop
+
  jmp Display

// one row: "mmm MMM" then N if an NMI was lost, at RowPos; dev build: green if == expected (hw rows), red otherwise,
// grey for model rows that match; kit build: white
Rows:
  ldx.w #0
  stx.b $30
RowLoop:
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
  tax
  lda.w $0400,x
  sta.b $40
  lda.w $0402,x
  sta.b $42
  sep #$20
  lda.w $0404,x
  sta.b $44
  rep #$20
  // ref offset = row*12
  lda.b $30
  asl
  adc.b $30
  asl
  asl
  tay
  lda.w RefTab,y
  cmp.b $40
  bne +
  lda.w RefTab+2,y
  cmp.b $42
  bne +
  sep #$20
  lda.b #$04
  sta.b $13
  lda.w RefTab+10,y
  bne ++
  lda.b #$0c
  sta.b $13
  bra ++
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
  jsr PutDec
  jsr PutSpace
  rep #$20
  lda.b $42
  sta.b $40
  sep #$20
  jsr PutDec
  jsr PutSpace
  lda.b $44
  beq +
  lda.b #$18
  sta.w $2118
  lda.b $13
  sta.w $2119
+
  rep #$20
  inc.b $30
  lda.b $30
  cmp.w #NCASES
  sep #$20
  beq +
  jmp RowLoop
+
  rts
