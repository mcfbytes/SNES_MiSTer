#### busprobe (NTSC, final bitstreams, 16 rounds, H in dots)

| # | probe | stock core H | fixed core H | bsnes / MesenCE H | stock vs ref | fix vs ref |
|---|---|---|---|---|---|---|
| 00 | BASE | 66–67 | 67–68 | 67–68 | within 1 | match |
| 01 | NOP ROM | 94–95 | 95–96 | 95–96 | within 1 | match |
| 02 | NOP FAST | 85–86 | 87–88 | 87–88 | **-2/-2** | match |
| 03 | NOP WRAM | 104–105 | 105–106 | 105–106 | within 1 | match |
| 04 | LDA WRAM | 130–131 | 131–142 | 131–132 | within 1 | **+0/+10** |
| 05 | LDA 4300 | 126–127 | 127–128 | 127–128 | within 1 | match |
| 06 | LDA 4100 | 148–149 | 149–150 | 149–150 | within 1 | match |
| 07 | LDA 2101 | 126–127 | 127–128 | 127–128 | within 1 | match |
| 08 | LDA 6000 | 130–131 | 131–142 | 131–132 | within 1 | **+0/+10** |
| 09 | PHA 01FF | 110–111 | 111–112 | 111–112 | within 1 | match |
| 10 | PHA 437F | 106–107 | 107–108 | 107–108 | within 1 | match |
| 11 | PHA 41FF | 118–119 | 119–120 | 119–120 | within 1 | match |
| 12 | PHA 21FF | 106–107 | 107–108 | 107–108 | within 1 | match |
| 13 | IRQ 01FF | 76–77 | 77–78 | 77–78 | within 1 | match |
| 14 | IRQ 437F | 74–75 | 75–76 | 75–76 | within 1 | match |
| 15 | IRQ 41FF | 80–81 | 81–82 | 81–82 | within 1 | match |
| 16 | IRQ 4203H | 74–75 | 75–76 | 75–76 | within 1 | match |
| 17 | IRQ 4203L | 74–75 | 55–56 | 55–56 | **+19/+19** | match |
| 18 | BRK 217F | 91–92 | 92–93 | 92–93 | within 1 | match |
| 19 | BRK 2180 | 91–91 | 92–93 | 92–93 | **-1/-2** | match |
| 20 | WRIO 1-0 | 64–65 | 66–67 | 66–67 | **-2/-2** | match |
| 21 | WRIO 0-1 | 157–158 | 159–160 | 159–160 | **-2/-2** | match |
| 22 | LDA 2137 | 64–65 | 65–66 | 65–66 | within 1 | match |

#### irqprobe (NTSC, final bitstreams, 16 rounds, H in dots)

| # | probe | stock core H | fixed core H | bsnes / MesenCE H | stock vs ref | fix vs ref |
|---|---|---|---|---|---|---|
| 00 | WAKE H+V | 66–67 | 67–68 | 67–67 | within 1 | within 1 |
| 01 | WAKE V | 25–25 | 26–27 | 27–27 | **-2/-2** | within 1 |
| 02 | 2137 WR7F | 64–64 | 153–153 | 154–154 | **-90/-90** | within 1 |
| 03 | PHA 4201 | 62–63 | 64–64 | 65–65 | **-3/-2** | within 1 |
| 04 | SLED +0 | 110–110 | 111–112 | 112–112 | **-2/-2** | within 1 |
| 05 | SLED +1 | 110–111 | 111–112 | 111–111 | within 1 | within 1 |
| 06 | SLED +2 | 110–111 | 111–112 | 111–111 | within 1 | within 1 |
| 07 | SLED +3 | 110–111 | 112–112 | 112–112 | **-2/-1** | match |
| 08 | SLED +4 | 111–114 | 112–115 | 112–112 | **-1/+2** | **+0/+3** |
| 09 | SLED +5 | 114–114 | 115–115 | 115–115 | within 1 | match |
| 10 | SLED +6 | 114–114 | 116–116 | 116–116 | **-2/-2** | match |
| 11 | SLED +7 | 114–114 | 118–118 | 116–116 | **-2/-2** | **+2/+2** |
| 12 | SLED +8 | 117–117 | 118–118 | 118–118 | within 1 | match |
| 13 | SLED +9 | 118–118 | 119–119 | 119–119 | within 1 | match |
| 14 | SLED +10 | 118–118 | 119–119 | 119–119 | within 1 | match |
| 15 | SLED +11 | 121–121 | 122–122 | 122–122 | within 1 | match |
| 16 | SLED +12 | 121–121 | 123–123 | 123–123 | **-2/-2** | match |
| 17 | SLED +13 | 121–121 | 123–123 | 123–123 | **-2/-2** | match |

#### pal-busprobe (PAL, final bitstreams, 16 rounds, H in dots)

| # | probe | stock core H | fixed core H | bsnes ∪ MesenCE band H | stock vs ref | fix vs ref |
|---|---|---|---|---|---|---|
| 00 | BASE | 66–66 | 68–68 | 67–68 | **-1/-2** | in band |
| 01 | NOP ROM | 95–95 | 96–96 | 95–96 | in band | in band |
| 02 | NOP FAST | 86–86 | 88–88 | 87–88 | **-1/-2** | in band |
| 03 | NOP WRAM | 104–104 | 106–106 | 105–106 | **-1/-2** | in band |
| 04 | LDA WRAM | 130–130 | 131–131 | 131–132 | **-1/-2** | in band |
| 05 | LDA 4300 | 127–127 | 128–128 | 127–128 | in band | in band |
| 06 | LDA 4100 | 148–148 | 150–150 | 149–150 | **-1/-2** | in band |
| 07 | LDA 2101 | 126–126 | 128–128 | 127–128 | **-1/-2** | in band |
| 08 | LDA 6000 | 130–130 | 131–131 | 131–132 | **-1/-2** | in band |
| 09 | PHA 01FF | 111–111 | 112–112 | 111–112 | in band | in band |
| 10 | PHA 437F | 107–107 | 108–108 | 107–108 | in band | in band |
| 11 | PHA 41FF | 118–118 | 119–119 | 119–120 | **-1/-2** | in band |
| 12 | PHA 21FF | 107–107 | 108–108 | 107–108 | in band | in band |
| 13 | IRQ 01FF | 77–77 | 78–78 | 77–78 | in band | in band |
| 14 | IRQ 437F | 74–74 | 76–76 | 75–76 | **-1/-2** | in band |
| 15 | IRQ 41FF | 80–80 | 82–82 | 81–82 | **-1/-2** | in band |
| 16 | IRQ 4203H | 75–75 | 76–76 | 75–76 | in band | in band |
| 17 | IRQ 4203L | 75–75 | 56–56 | 55–56 | **+20/+19** | in band |
| 18 | BRK 217F | 91–91 | 93–93 | 92–93 | **-1/-2** | in band |
| 19 | BRK 2180 | 91–91 | 92–92 | 92–93 | **-1/-2** | in band |
| 20 | WRIO 1-0 | 65–65 | 67–67 | 66–67 | **-1/-2** | in band |
| 21 | WRIO 0-1 | 158–158 | 160–160 | 159–160 | **-1/-2** | in band |
| 22 | LDA 2137 | 64–64 | 66–66 | 65–66 | **-1/-2** | in band |

#### pal-irqprobe (PAL, final bitstreams, 16 rounds, H in dots)

| # | probe | stock core H | fixed core H | bsnes ∪ MesenCE band H | stock vs ref | fix vs ref |
|---|---|---|---|---|---|---|
| 00 | WAKE H+V | 66–66 | 68–68 | 68–68 | **-2/-2** | in band |
| 01 | WAKE V | 26–26 | 27–27 | 26–27 | in band | in band |
| 02 | 2137 WR7F | 64–64 | 154–154 | 153–154 | **-89/-90** | in band |
| 03 | PHA 4201 | 63–63 | 64–64 | 64–65 | **-1/-2** | in band |
| 04 | SLED +0 | 110–110 | 111–111 | 111–112 | **-1/-2** | in band |
| 05 | SLED +1 | 111–111 | 112–112 | 111–112 | in band | in band |
| 06 | SLED +2 | 110–110 | 112–112 | 112–112 | **-2/-2** | in band |
| 07 | SLED +3 | 110–110 | 111–111 | 111–112 | **-1/-2** | in band |
| 08 | SLED +4 | 111–111 | 112–112 | 112–115 | **-1/-4** | in band |
| 09 | SLED +5 | 114–114 | 115–115 | 115–115 | **-1/-1** | in band |
| 10 | SLED +6 | 114–114 | 115–115 | 115–115 | **-1/-1** | in band |
| 11 | SLED +7 | 114–114 | 115–115 | 115–118 | **-1/-4** | in band |
| 12 | SLED +8 | 117–117 | 119–119 | 119–119 | **-2/-2** | in band |
| 13 | SLED +9 | 117–117 | 118–118 | 118–119 | **-1/-2** | in band |
| 14 | SLED +10 | 118–118 | 119–119 | 118–119 | in band | in band |
| 15 | SLED +11 | 121–121 | 122–122 | 119–122 | in band | in band |
| 16 | SLED +12 | 121–121 | 122–122 | 122–122 | **-1/-1** | in band |
| 17 | SLED +13 | 121–121 | 122–122 | 122–123 | **-1/-2** | in band |

