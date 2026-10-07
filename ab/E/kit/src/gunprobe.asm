// gunprobe: every frame, read the external (light gun) latch and show H/V, with min/max since power-on.
architecture wdc65816-strict
output "gunprobe.sfc", create
fill 0x8000
origin 0
base 0x808000

constant ROW1 = 5*32+2
constant ROW2 = 8*32+2

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
  lda.b #$ff
  sta.w $4201
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
  // min = $FFFF, max = 0, frame = 0
  rep #$20
  lda.w #$ffff
  sta.b $30
  sta.b $34
  stz.b $32
  stz.b $36
  stz.b $38
  sep #$20
  stz.b $13
  lda.b #$0f
  sta.w $2100

Loop:
-
  lda.w $4212
  bpl -
  lda.w $213f
  sta.b $20
  lda.w $213c
  sta.b $21
  lda.w $213c
  and.b #$01
  sta.b $22
  lda.w $213d
  sta.b $23
  lda.w $213d
  and.b #$01
  sta.b $24
  rep #$20
  inc.b $38
  lda.b $20
  and.w #$0040
  beq NoLatch
  lda.b $21
  cmp.b $30
  bcs +
  sta.b $30
+
  cmp.b $32
  bcc +
  sta.b $32
+
  lda.b $23
  cmp.b $34
  bcs +
  sta.b $34
+
  cmp.b $36
  bcc +
  sta.b $36
+
NoLatch:
  sep #$20
  ldx.w #ROW1
  stx.w $2116
  lda.b $22
  jsr PutNib
  lda.b $21
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  lda.b $24
  jsr PutNib
  lda.b $23
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  lda.b $20
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  jsr PutSpace
  lda.b $39
  jsr PutByte
  lda.b $38
  jsr PutByte
  ldx.w #ROW2
  stx.w $2116
  lda.b $31
  jsr PutNib
  lda.b $30
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  lda.b $33
  jsr PutNib
  lda.b $32
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  lda.b $35
  jsr PutNib
  lda.b $34
  jsr PutByte
  jsr PutSpace
  jsr PutSpace
  lda.b $37
  jsr PutNib
  lda.b $36
  jsr PutByte
-
  lda.w $4212
  bmi -
  jmp Loop

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
Pal.end:
Hex:
  insert "hex.bin"
Map:
  insert "map.bin"
Font:
  insert "font.bin"
Font.end:

origin 0x7fc0
base 0x80ffc0
  db "GUNPROBE             "
  db $20, $00, $05, $00, $01, $33, $00
  dw $0000, $ffff
  dw 0, 0, Hang & $ffff, Hang & $ffff, Hang & $ffff, Hang & $ffff, 0, Hang & $ffff
  dw 0, 0, Hang & $ffff, 0, Hang & $ffff, Hang & $ffff, Reset & $ffff, Hang & $ffff
