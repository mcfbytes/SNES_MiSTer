// busprobe: per-access-type CPU bus timing, latched H/V after a WAI-synchronised start.
// Results: $0400 + (round*32 + probe)*8 = Hlo Hhi Vlo Vhi WMDATA-after; 16 rounds.
architecture wdc65816-strict
output "out.sfc", create
fill 0x8000
origin 0
base 0x808000
include "gen.inc"

constant NROUNDS = 16

macro x8(i) {
  {i}
  {i}
  {i}
  {i}
  {i}
  {i}
  {i}
  {i}
}
macro sync() {
  wai
  lda.w $4211
}

Reset:
  sei
  clc
  xce
  jml Main
IrqEntry:
  jml Done
BrkEntry:
  jml Done
Hang:
  bra Hang

Main:
  rep #$38
  ldx.w #$01ff
  txs
  lda.w #$0000
  tcd
  sep #$20
  lda.b #$00
  pha
  plb
  lda.b #$80
  sta.w $2100
  stz.w $4200
  stz.w $420c
  stz.w $420b
  stz.w $420d
  lda.b #$ff
  sta.w $4201
  stz.w $2181
  lda.b #$20
  sta.w $2182
  lda.b #$01
  sta.w $2183
  ldx.w #0
-
  txa
  sta.w $2180
  inx
  cpx.w #256
  bne -
  ldx.w #0
-
  lda.w Stub,x
  sta.l $7e1800,x
  inx
  cpx.w #Stub.end-Stub
  bne -
  lda.w $2143
  sta.b $40
  lda.w $213f
  sta.b $41
  stz.b $26
  stz.b $27
RoundLoop:
  ldx.w #0
  stx.b $20
ProbeLoop:
  rep #$20
  lda.b $26
  and.w #$00ff
  asl
  asl
  asl
  asl
  asl
  asl
  clc
  adc.b $20
  asl
  asl
  sta.b $22
  sep #$20
-
  lda.w $4212
  bpl -
  lda.b #$ff
  sta.w $4201
  lda.w $2137
  stz.w $2181
  lda.b #$20
  sta.w $2182
  lda.b #$01
  sta.w $2183
  lda.b #100
  sta.w $4209
  stz.w $420a
  lda.b #40
  sta.w $4207
  stz.w $4208
  lda.w $4211
  lda.b #$30
  sta.w $4200
  ldx.b $20
  jmp (ProbeTable,x)

Done:
  lda.w $2137
DoneNoLatch:
  sei
  lda.w $213f
  ldx.b $22
  lda.w $213c
  sta.w $0400,x
  lda.w $213c
  and.b #$01
  sta.w $0401,x
  lda.w $213d
  sta.w $0402,x
  lda.w $213d
  and.b #$01
  sta.w $0403,x
  lda.w $2180
  sta.w $0404,x
  lda.w $4211
  stz.w $4200
  stz.w $420d
  lda.b #$ff
  sta.w $4201
  ldx.w #$01ff
  txs
  jml AfterMeasure
AfterMeasure:
  ldx.b $20
  inx
  inx
  stx.b $20
  cpx.w #NPROBES*2
  beq +
  jmp ProbeLoop
+
  inc.b $26
  lda.b $26
  cmp.b #NROUNDS
  beq +
  jmp RoundLoop
+
  jmp Display

Stub:
  x8(db $ea)
  db $5c, Done, Done >> 8, Done >> 16
Stub.end:

// ---- display ----
Display:
  lda.b #$80
  sta.w $2100
  ldx.w #$2105
-
  stz.w $0000,x
  inx
  cpx.w #$210d
  bne -
  ldx.w #$210d
-
  stz.w $0000,x
  stz.w $0000,x
  inx
  cpx.w #$2115
  bne -
  ldx.w #$2123
-
  stz.w $0000,x
  inx
  cpx.w #$2134
  bne -
  lda.b #$01
  sta.w $210b
  sta.w $212c
  lda.b #$ff
  sta.w $210e
  stz.w $210e
  lda.b #$80
  sta.w $2115
  ldx.w #$1000
  stx.w $2116
  lda.b #$01
  sta.w $4300
  lda.b #$18
  sta.w $4301
  ldx.w #Font
  stx.w $4302
  lda.b #Font >> 16
  sta.w $4304
  ldx.w #Font.end-Font
  stx.w $4305
  lda.b #$01
  sta.w $420b
  ldx.w #$0000
  stx.w $2116
  ldx.w #Map
  stx.w $4302
  lda.b #Map >> 16
  sta.w $4304
  ldx.w #2048
  stx.w $4305
  lda.b #$01
  sta.w $420b
  stz.w $2121
  ldx.w #0
-
  lda.w Pal,x
  sta.w $2122
  inx
  cpx.w #Pal.end-Pal
  bne -
  // APU port 3 as seen at boot
  stz.b $13
  ldx.w #APUPOS
  stx.w $2116
  lda.b $40
  jsr PutByte
  ldx.w #STATPOS
  stx.w $2116
  lda.b $41
  jsr PutByte
  ldx.w #0
  stx.b $30
RowLoop:
  rep #$20
  lda.b $30
  asl
  asl
  asl
  sta.b $32
  lda.b $30
  asl
  tay
  lda.w RowPos,y
  sta.b $36
  sep #$20
  stz.b $34
  rep #$20
  lda.w #$ffff
  sta.b $50
  stz.b $52
  ldy.b $32
  lda.w RefTab+4,y
  sta.b $56
  ldx.b $32
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
  lda.w $0402,x
  cmp.b $56
  beq +
  inc.b $34
+
  txa
  clc
  adc.w #$0100
  tax
  dey
  bne -
  ldy.b $32
  lda.b $50
  cmp.w RefTab,y
  beq +
  inc.b $34
+
  lda.b $52
  cmp.w RefTab+2,y
  beq +
  inc.b $34
+
  sep #$20
  lda.w $0404,y
  cmp.w RefTab+6,y
  beq +
  inc.b $34
+
  lda.b #$04
  sta.b $13
  lda.b $34
  beq +
  lda.b #$08
  sta.b $13
+
  ldx.b $36
  stx.w $2116
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
  lda.b $36
  clc
  adc.w #16
  sta.w $2116
  sep #$20
  ldx.b $32
  lda.w $0404,x
  jsr PutByte
  ldx.b $30
  inx
  stx.b $30
  cpx.w #NPROBES
  beq +
  jmp RowLoop
+
  lda.b #$0f
  sta.w $2100
-
  bra -

PutByte:
  pha
  lsr
  lsr
  lsr
  lsr
  jsr PutNib
  pla
PutNib:
  rep #$20
  and.w #$000f
  tay
  sep #$20
  lda.w Hex,y
  sta.w $2118
  lda.b $13
  sta.w $2119
  rts
PutSpace:
  lda.b #$5f
  sta.w $2118
  stz.w $2119
  rts

Pal:
  dw $0000, $7fff, $0000, $0000
  dw $0000, $03e0, $0000, $0000
  dw $0000, $001f, $0000, $0000
  dw $0000, $4210, $0000, $0000
Pal.end:
Hex:
  insert "hex.bin"
RowPos:
  insert "rowpos.bin"
RefTab:
  insert "ref.bin"
Map:
  insert "map.bin"
Font:
  insert "font.bin"
Font.end:

include "probes.inc"

origin 0x7fc0
base 0x80ffc0
  db "BUSPROBE             "
  db $20, $00, $05, $00, COUNTRY, $33, $00
  dw $0000, $ffff
  dw 0, 0, Hang & $ffff, BrkEntry & $ffff, Hang & $ffff, Hang & $ffff, 0, IrqEntry & $ffff
  dw 0, 0, Hang & $ffff, 0, Hang & $ffff, Hang & $ffff, Reset & $ffff, Hang & $ffff
