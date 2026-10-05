architecture wdc65816-strict
output "patch.bin", create
origin 0
base 0x008600
include "mispos.inc"
// DP scratch: $10 mismatch count, $12 actual byte, $13 tilemap attribute

Start:
  sei
  rep #$30
  ldx.w #$01ff
  txs
  lda.w #$0000
  tcd
  sep #$20
  phk
  plb
  lda.b #$80
  sta.w $2100
  stz.w $4200
  stz.w $420c
  stz.w $420b
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
  stz.w $4304
  ldx.w #Font.end-Font
  stx.w $4305
  lda.b #$01
  sta.w $420b
  ldx.w #$0000
  stx.w $2116
  ldx.w #Map
  stx.w $4302
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
  stz.b $10
  ldx.w #0
Loop:
  lda.l $7f0000,x
  sta.b $12
  lda.w Chk,x
  beq Unchecked
  lda.b $12
  cmp.w Exp,x
  beq Match
  inc.b $10
  lda.b #$08
  bra +
Match:
  lda.b #$04
  bra +
Unchecked:
  lda.b #$0c
+
  sta.b $13
  rep #$20
  txa
  asl
  tay
  lda.w Pos,y
  sta.w $2116
  jsr PutByte
  inx
  cpx.w #60
  bne Loop
  lda.b #$04
  sta.b $13
  lda.b $10
  sta.b $12
  beq +
  lda.b #$08
+
  sta.b $13
  rep #$20
  lda.w #MISPOS
  sta.w $2116
  jsr PutByte
  lda.b #$0f
  sta.w $2100
-
  bra -

// enter a16; $12 = byte, $13 = attribute; leaves a8
PutByte:
  lda.b $12
  and.w #$00f0
  lsr
  lsr
  lsr
  lsr
  tay
  sep #$20
  lda.w Hex,y
  sta.w $2118
  lda.b $13
  sta.w $2119
  rep #$20
  lda.b $12
  and.w #$000f
  tay
  sep #$20
  lda.w Hex,y
  sta.w $2118
  lda.b $13
  sta.w $2119
  rts

Pal:
  dw $0000, $7fff, $0000, $0000
  dw $0000, $03e0, $0000, $0000
  dw $0000, $001f, $0000, $0000
  dw $0000, $4210, $0000, $0000
Pal.end:
Pos:
  insert "tables.bin", 0, 120
Exp:
  insert "tables.bin", 120, 60
Chk:
  insert "tables.bin", 180, 60
Hex:
  insert "tables.bin", 240, 16
Map:
  insert "map.bin"
Font:
  insert "font.bin"
Font.end:
