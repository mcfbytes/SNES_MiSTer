// enable: a $4200 / $4207 write stepped across the trigger point.
// Sync: HV IRQ at (VS, HS), WAI with I=1 (no vector), then the row's action with HTIME = HS+BASE+d (d=0..15, $30/$31
// precomputed before the WAI so the wake-to-write latency is the same for every d). After a ~60-dot delay the
// row reads $4211.7 -> bit0 of the sample at $0400+round*256+row*16+d. Rows E9/E10 also store an early read in bit1.
// NROUNDS rounds (outer loop); the screen shows min and max over the rounds per step.

NmiEntry:
  rti
IrqEntry:
  rti

macro delay() {
  ldx.w #8
-
  dex
  bne -
}
macro sync() {
  wai
  lda.w $4211
}
// arm the sync IRQ: HV at (V, H) from A (htime lo) / $34 (htime hi) / Y (vtime)
macro arm(v, hl, hh) {
  sei
  stz.w $4200
  lda.b #{hl}
  sta.w $4207
  lda.b #{hh}
  sta.w $4208
  lda.b #{v}
  sta.w $4209
  stz.w $420a
  lda.w $4211
  lda.b #$30
  sta.w $4200
}

TestMain:
  stz.b $26
  stz.b $27
RoundLoop:
  ldx.w #0
  stx.b $20
RowLoop:
  ldx.w #0
  stx.b $32
StepLoop:
  // $30/$31 = HS + BASE(row) + d ; result index in $22 = round*256 + row*16 + d
  rep #$20
  lda.b $20
  asl
  tax
  lda.w BaseTab,x
  clc
  adc.b $32
  adc.w #HS
  sta.b $30
  lda.b $20
  asl
  asl
  asl
  asl
  clc
  adc.b $32
  sta.b $22
  lda.b $26
  and.w #$00ff
  xba
  ora.b $22
  sta.b $22
  lda.b $20
  asl
  tax
  sep #$20
  jmp (RowTable,x)

Record:
  // A = result byte
  ldx.b $22
  sta.w $0400,x
  stz.w $4200
  lda.w $4211
  rep #$20
  inc.b $32
  lda.b $32
  cmp.w #16
  sep #$20
  beq +
  jmp StepLoop
+
  rep #$20
  inc.b $20
  lda.b $20
  cmp.w #NROWS
  sep #$20
  beq +
  jmp RowLoop
+
  inc.b $26
  lda.b $26
  cmp.b #NROUNDS
  beq +
  jmp RoundLoop
+
  jmp Display

BaseTab:
  dw BASE0, BASE1, BASE2, BASE3, BASE4, BASE5, BASE6, BASE7, BASE8, BASE9, BASE10, BASE11
RowTable:
  dw E0, E0, E2, E2, E4, E4, E6, E7, E7, E9, E10, E11

// E0/E1: wake, disable, set HTIME=$30, enable HV, delay, read
E0:
  arm(VS, HS, 0)
  sync()
  stz.w $4200
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  lda.w $4211
  lda.b #$30
  sta.w $4200
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record
// E2/E3: as E0 with one NOP before the enable (+14 clocks)
E2:
  arm(VS, HS, 0)
  sync()
  stz.w $4200
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  lda.w $4211
  lda.b #$30
  nop
  sta.w $4200
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record
// E4/E5: HV stays enabled through the wake; the HTIME write is the event
E4:
  arm(VS, HS, 0)
  sync()
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record
// E6: HV wake at (VS, HS), then enable V-only with VTIME = VS-8+d: only d=8 (the current line) can fire within the delay
E6:
  arm(VS, HS, 0)
  sync()
  stz.w $4200
  lda.b $32
  clc
  adc.b #VS-8
  sta.w $4209
  stz.w $420a
  lda.w $4211
  lda.b #$20
  sta.w $4200
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record
// E7: HV enabled; HTIME=$30; disable then re-enable back to back; delay; read
E7:
  arm(VS, HS, 0)
  sync()
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  stz.w $4200
  lda.b #$30
  sta.w $4200
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record
// E9: HV enabled; HTIME=$30; an early $4211 read (bit1), delay, a late read (bit0)
E9:
  arm(VS, HS, 0)
  sync()
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  lda.w $4211
  rol
  rol
  and.b #$01
  asl
  sta.b $36
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  ora.b $36
  jmp Record
// E10: E9 with one NOP before the early read
E10:
  arm(VS, HS, 0)
  sync()
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  nop
  lda.w $4211
  rol
  rol
  and.b #$01
  asl
  sta.b $36
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  ora.b $36
  jmp Record
// E11: as E0 but H-only
E11:
  arm(VS, HS, 0)
  sync()
  stz.w $4200
  lda.b $30
  sta.w $4207
  lda.b $31
  sta.w $4208
  lda.w $4211
  lda.b #$10
  sta.w $4200
  delay()
  lda.w $4211
  rol
  rol
  and.b #$01
  jmp Record

// display: per row a min line and a max line of 16 hex digits (over the rounds); dev build: green if all 32 equal
// the bsnes ref bytes (RefTab: min16 max16 per row); kit build: white
Rows:
  ldx.w #0
  stx.b $30
RowDisp:
  // $32 = row*16; min/max per step -> $0060+step / $0070+step
  rep #$20
  lda.b $30
  asl
  asl
  asl
  asl
  sta.b $32
  sep #$20
  ldy.w #0
StepMM:
  lda.b #$ff
  sta.b $40
  stz.b $41
  rep #$20
  tya
  clc
  adc.b $32
  tax
  sep #$20
  lda.b #NROUNDS
  sta.b $42
-
  lda.w $0400,x
  cmp.b $40
  bcs +
  sta.b $40
+
  cmp.b $41
  bcc +
  sta.b $41
+
  rep #$20
  txa
  clc
  adc.w #$0100
  tax
  sep #$20
  dec.b $42
  bne -
  lda.b $40
  sta.w $0060,y
  lda.b $41
  sta.w $0070,y
  iny
  cpy.w #16
  bne StepMM
  // colour: compare $60..$7F with RefTab + row*32
  rep #$20
  lda.b $30
  asl
  asl
  asl
  asl
  asl
  tax
  sep #$20
  lda.b #$04
  sta.b $13
  ldy.w #0
-
  lda.w $0060,y
  cmp.w RefTab,x
  beq +
  lda.b #$08
  sta.b $13
+
  inx
  iny
  cpy.w #32
  bne -
  lda.w KitFlag
  beq +
  stz.b $13
+
  // print min at RowPos[row*2], max at RowPos[row*2+1]
  rep #$20
  lda.b $30
  asl
  asl
  tay
  lda.w RowPos,y
  sta.w $2116
  sep #$20
  ldy.w #0
-
  lda.w $0060,y
  phy
  jsr PutNib
  ply
  iny
  cpy.w #16
  bne -
  rep #$20
  lda.b $30
  asl
  asl
  tay
  lda.w RowPos+2,y
  sta.w $2116
  sep #$20
  ldy.w #0
-
  lda.w $0070,y
  phy
  jsr PutNib
  ply
  iny
  cpy.w #16
  bne -
  rep #$20
  inc.b $30
  lda.b $30
  cmp.w #NROWS
  sep #$20
  beq +
  jmp RowDisp
+
  rts
