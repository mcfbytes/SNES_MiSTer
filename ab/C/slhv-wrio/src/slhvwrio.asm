// slhv-wrio: does a $2137 (SLHV) read, or a $4201 (WRIO) bit 7 edge, latch OPHCT/OPVCT?
// Each case: WRIO=$FF, V-IRQ wake at line P, read $2137 (prime latch V=P), read $213F, then the action.
// Results: $0400 + case*8 = Hlo Hhi Vlo Vhi STAT78-after.
architecture wdc65816-strict
output "out.sfc", create
fill 0x8000
origin 0
base 0x808000
include "gen.inc"

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
  ldx.w #0
  stx.b $20
CaseLoop:
  lda.b #$ff
  sta.w $4201
  lda.b #LP
  jsr SyncV
  lda.w $2137
  lda.w $213f
  ldx.b $20
  jmp (CaseTable,x)

Record:
  lda.w $213f
  sta.b $24
  rep #$20
  lda.b $20
  asl
  asl
  tax
  sep #$20
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
  lda.b $24
  sta.w $0404,x
  lda.b #$ff
  sta.w $4201
  ldx.b $20
  inx
  inx
  stx.b $20
  cpx.w #NCASES*2
  bne CaseLoop
  jmp Display

// A = line: V-IRQ at that line, WAI with I=1 (no vector), ack
SyncV:
  sta.w $4209
  stz.w $420a
  lda.w $4211
  lda.b #$20
  sta.w $4200
  wai
  lda.w $4211
  stz.w $4200
  rts

// 1: WRIO.7 set, read $2137 at A
C1:
  lda.b #LA
  jsr SyncV
  lda.w $2137
  jmp Record
// 2: WRIO=$7F at P (that 1->0 edge itself latches at P), read $2137 at A
C2:
  lda.b #$7f
  sta.w $4201
  lda.b #LA
  jsr SyncV
  lda.w $2137
  jmp Record
// 3: "or was": $7F at P; at M write $FF then $7F; read $2137 at A
C3:
  lda.b #$7f
  sta.w $4201
  lda.b #LM
  jsr SyncV
  lda.b #$ff
  sta.w $4201
  lda.b #$7f
  sta.w $4201
  lda.b #LA
  jsr SyncV
  lda.w $2137
  jmp Record
// 4: WRIO.7 set; at A write $7F (1->0), no $2137 read
C4:
  lda.b #LA
  jsr SyncV
  lda.b #$7f
  sta.w $4201
  jmp Record
// 5: $7F at P; at A write $FF (0->1), no $2137 read
C5:
  lda.b #$7f
  sta.w $4201
  lda.b #LA
  jsr SyncV
  lda.b #$ff
  sta.w $4201
  jmp Record
// 6: $7F at P; read $2137 at A, at A+40 and at A+80
C6:
  lda.b #$7f
  sta.w $4201
  lda.b #LA
  jsr SyncV
  lda.w $2137
  lda.b #LA+40
  jsr SyncV
  lda.w $2137
  lda.b #LA+80
  jsr SyncV
  lda.w $2137
  jmp Record

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
  // verdict: V == expV and F == expF (ref table: eVlo eVhi eF use)
  stz.b $34
  ldx.b $32
  rep #$20
  lda.w $0402,x
  cmp.w RefTab,x
  sep #$20
  beq +
  inc.b $34
+
  lda.w $0404,x
  rol
  rol
  rol
  and.b #$01
  cmp.w RefTab+2,x
  beq +
  inc.b $34
+
  lda.w RefTab+3,x
  sta.b $35
  lda.b #$04
  sta.b $13
  lda.b $34
  beq +
  lda.b #$08
  sta.b $13
+
  lda.b $35
  bne +
  lda.b #$0c
  sta.b $13
+
  ldx.b $36
  stx.w $2116
  ldx.b $32
  rep #$20
  lda.w $0400,x
  jsr PutDec
  jsr PutSpace
  ldx.b $32
  rep #$20
  lda.w $0402,x
  jsr PutDec
  jsr PutSpace
  ldx.b $32
  lda.w $0404,x
  rol
  rol
  rol
  and.b #$01
  jsr PutNib
  // verdict text
  rep #$20
  lda.b $36
  clc
  adc.w #VERDOFS
  sta.w $2116
  sep #$20
  ldy.w #0
  lda.b $35
  beq NoVerdict
  lda.b $34
  beq +
  ldy.w #4
+
-
  lda.w Words,y
  sta.w $2118
  lda.b $13
  sta.w $2119
  iny
  tya
  and.b #$03
  bne -
NoVerdict:
  ldx.b $30
  inx
  stx.b $30
  cpx.w #NCASES
  beq +
  jmp RowLoop
+
  lda.b #$0f
  sta.w $2100
-
  bra -

// A (16-bit, M=0 on entry) -> three decimal digits; returns with M=1
PutDec:
  ldy.w #0
-
  cmp.w #100
  bcc +
  sbc.w #100
  iny
  bra -
+
  sta.b $38
  sep #$20
  tya
  jsr PutNib
  rep #$20
  lda.b $38
  ldy.w #0
-
  cmp.w #10
  bcc +
  sbc.w #10
  iny
  bra -
+
  sta.b $38
  sep #$20
  tya
  jsr PutNib
  lda.b $38
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
Words:
  insert "words.bin"
RowPos:
  insert "rowpos.bin"
RefTab:
  insert "ref.bin"
Map:
  insert "map.bin"
Font:
  insert "font.bin"
Font.end:

CaseTable:
  dw C1, C2, C3, C4, C5, C6

origin 0x7fc0
base 0x80ffc0
  db "SLHV-WRIO            "
  db $20, $00, $05, $00, COUNTRY, $33, $00
  dw $0000, $ffff
  dw 0, 0, Hang & $ffff, Hang & $ffff, Hang & $ffff, Hang & $ffff, 0, Hang & $ffff
  dw 0, 0, Hang & $ffff, 0, Hang & $ffff, Hang & $ffff, Reset & $ffff, Hang & $ffff
