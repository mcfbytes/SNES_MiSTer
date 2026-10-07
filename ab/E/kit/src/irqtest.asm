// irqtest: common skeleton for the H/V IRQ test ROMs (test.inc = the variant: wrap / enable / ophct).
// Direct page: $10/$11 IRQ count, $14/$15 frame index*2, $13 text attr, $20 case index, $22 result ptr,
// $24 fired flag, $26 round, $30/$31 HTIME under test, $32 step. Results: WRAM $0400+.
architecture wdc65816-strict
output "out.sfc", create
fill 0x8000
origin 0
base 0x808000
include "gen.inc"

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

Reset:
  sei
  clc
  xce
  jml Main
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
  stz.w $2133
  lda.b #$ff
  sta.w $4201
  lda.w $4210
  lda.w $4211
  ldx.w #0
-
  stz.w $0400,x
  inx
  cpx.w #$1000
  bne -
  jmp TestMain

include "test.inc"

// ---- display: text map + hex at RowPos ----
Display:
  sei
  stz.w $4200
  stz.w $2133
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
  jsr Rows
  lda.b #$0f
  sta.w $2100
-
  bra -

// A = byte, $13 = attr
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
// A (8-bit) as 3 decimal digits
PutDec3:
  sta.b $40
  stz.b $41
  jmp PutDec
// $40/$41 (16-bit) as 3 decimal digits
PutDec:
  rep #$20
  lda.b $40
  ldx.w #0
-
  cmp.w #100
  bcc +
  sbc.w #100
  inx
  bra -
+
  sta.b $40
  sep #$20
  txa
  jsr PutNib
  rep #$20
  lda.b $40
  ldx.w #0
-
  cmp.w #10
  bcc +
  sbc.w #10
  inx
  bra -
+
  sta.b $40
  sep #$20
  txa
  jsr PutNib
  lda.b $40
  jmp PutNib

Pal:
  dw $0000, $7fff, $0000, $0000
  dw $0000, $03e0, $0000, $0000
  dw $0000, $001f, $0000, $0000
  dw $0000, $4210, $0000, $0000
Pal.end:
KitFlag:
  db KIT
RaceFlag:
  db RACE
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

origin 0x7fc0
base 0x80ffc0
  db "IRQTEST              "
  db $20, $00, $05, $00, COUNTRY, $33, $00
  dw $0000, $ffff
  dw 0, 0, Hang & $ffff, Hang & $ffff, Hang & $ffff, NmiEntry & $ffff, 0, IrqEntry & $ffff
  dw 0, 0, Hang & $ffff, 0, Hang & $ffff, Hang & $ffff, Reset & $ffff, Hang & $ffff
