# PIC16F877A INSTRUCTION SET, 14-BIT OPCODE TABLE & MACHINE-CODE TRANSLATION GUIDE
**Course:** Micro-processing System — Midterm Project (Component 3 — 10 Marks)  
**Target MCU:** Microchip PIC16F877A (Mid-Range 14-bit Core)  
**Official Reference:** Microchip *PIC16F87XA Data Sheet* (`DS39582C`, Section 15.0, Table 15-1, Figure 15-1, Table 15-2, pp. 159–165).

---

## 1. Assembly-to-Machine-Code Translation Fundamentals (Section 7.1 — All 10 Topics)

1. **Machine-Code Representation:** The PIC16F877A CPU executes fixed **14-bit binary instruction words** fetched from Flash Program Memory (`0000h–1FFFh`). For readability and verification against `.lst`/`.hex` files, each 14-bit word is written as a **4-digit hexadecimal number** in `0x0000 – 0x3FFF` (with the two unused MSBs 15–14 padded as `00`).
2. **Opcode and Operand Fields (`Table 15-1`, p. 159):**
   - `OPCODE`: Upper bits identifying the operation.
   - `f` (**7 bits**, `0x00 – 0x7F`): File register offset within the active RAM Bank. *(Note: For banked SFRs like `TRISB = 0x86`, only the lower 7 bits `0x86 & 0x7F = 0x06` are encoded in the instruction; bank selection comes from `STATUS<RP1:RP0>`.)*
   - `d` (**1 bit**, `0` or `1`): Destination select (`0` or `W` → store in `W`; `1` or `F` → store back in register `f`; MPASM default is `1`).
   - `b` (**3 bits**, `0 – 7`): Target bit index within an 8-bit file register.
   - `k` (**8 bits**, `0x00 – 0xFF` or **11 bits**, `0x000 – 0x7FF`): Immediate constant or branch/call target address.
   - `x` (**Don't care**): Per Microchip `Table 15-1` (p. 159), assemblers always encode `x = 0` for full tool compatibility.
3. **Three 14-Bit Instruction Formats (`Figure 15-1`, p. 159):**
   ```text
   (A) Byte-Oriented File Register Operations:
       Bit:  13 12 11 10  9  8 |  7  |  6  5  4  3  2  1  0
            [   OPCODE (6b)    |  d  |       f (7-bit)      ]

   (B) Bit-Oriented File Register Operations:
       Bit:  13 12 11 10 |  9  8  7 |  6  5  4  3  2  1  0
            [ OPCODE(4b) |  b (3b)  |       f (7-bit)      ]

   (C1) Literal & Control (8-bit immediate):
       Bit:  13 12 11 10  9  8 |  7  6  5  4  3  2  1  0
            [   OPCODE (6b)    |        k (8-bit)        ]

   (C2) Branch / Call (CALL & GOTO, 11-bit address):
       Bit:  13 12 11 | 10  9  8  7  6  5  4  3  2  1  0
            [ OP (3b) |            k (11-bit)            ]
   ```
4. **Fixed Instruction Length:** Every PIC16F877A instruction occupies exactly **1 word (14 bits)**, so `PC` increments by `+1` per instruction.
5. **Addressing Modes:** Direct (`RP1:RP0` + 7-bit `f`), Indirect (`IRP:FSR` via `INDF`), Immediate (`k` 8-bit), and Absolute/Paged Branch (`PCLATH<4:3>` + 11-bit `k`).
6. **Binary-to-Hexadecimal Conversion:** Prepend `00` to the 14-bit binary word to form 16 bits, group into four 4-bit nibbles, and convert each nibble to hex (`0–F`). Example: `11 0000 0101 0101` → `0011 0000 0101 0101` → **`0x3055`**.
7. **Encoding Rules:** Combine the 14-bit base opcode with shifted, range-checked operands using bitwise OR (`|`).
8. **Labels & Branch Address Resolution (Two-Pass Assembly):**
   - **Pass 1:** Scan source from `ORG`, building the Symbol Table (`label → word_address`), advancing `PC` by `+1` per instruction.
   - **Pass 2:** Resolve every `GOTO label` / `CALL label` (both forward and backward jumps) by encoding `k = symbol_table[label] & 0x7FF`.
9. **Relationship to Program Memory and Intel HEX (`INHX32M`):**
   - Flash stores 14-bit words sequentially at `Word_Addr = 0x0000, 0x0001, ...`.
   - Intel HEX stores each 14-bit word as **2 bytes in Little-Endian order** (`Low Byte` then `High Byte`) at **`Byte_Addr = 2 × Word_Addr`**, with an 8-bit 2's complement checksum at the end of every record.

---

## 2. Complete Master Opcode Table — All 35 PIC16F877A Instructions (`Table 15-2`, p. 160)

### 2.1. Byte-Oriented File Register Operations (18 Instructions)

| # | Mnemonic & Operands | Description | Cycles | 14-Bit Binary Opcode (`MSb → LSb`) | Base Hex (`x=0`) | Python Encoding Expression | Status Affected |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 1 | `ADDWF f, d` | Add `W` and `f` (`W + f → dest`) | 1 | `00 0111 dfff ffff` | `0x0700` | `0x0700 \| (d << 7) \| (f & 0x7F)` | `C, DC, Z` |
| 2 | `ANDWF f, d` | AND `W` with `f` (`W & f → dest`) | 1 | `00 0101 dfff ffff` | `0x0500` | `0x0500 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 3 | `CLRF f` | Clear `f` (`0 → f`) | 1 | `00 0001 1fff ffff` | `0x0180` | `0x0180 \| (f & 0x7F)` | `Z` |
| 4 | `CLRW` | Clear `W` (`0 → W`) | 1 | `00 0001 0xxx xxxx` | `0x0100` | `0x0100` | `Z` |
| 5 | `COMF f, d` | Complement `f` (`~f → dest`) | 1 | `00 1001 dfff ffff` | `0x0900` | `0x0900 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 6 | `DECF f, d` | Decrement `f` (`f - 1 → dest`) | 1 | `00 0011 dfff ffff` | `0x0300` | `0x0300 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 7 | `DECFSZ f, d` | Decrement `f`, Skip if `0` | 1(2) | `00 1011 dfff ffff` | `0x0B00` | `0x0B00 \| (d << 7) \| (f & 0x7F)` | None |
| 8 | `INCF f, d` | Increment `f` (`f + 1 → dest`) | 1 | `00 1010 dfff ffff` | `0x0A00` | `0x0A00 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 9 | `INCFSZ f, d` | Increment `f`, Skip if `0` | 1(2) | `00 1111 dfff ffff` | `0x0F00` | `0x0F00 \| (d << 7) \| (f & 0x7F)` | None |
| 10 | `IORWF f, d` | Inclusive OR `W` with `f` | 1 | `00 0100 dfff ffff` | `0x0400` | `0x0400 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 11 | `MOVF f, d` | Move `f` (`f → dest`, sets `Z`) | 1 | `00 1000 dfff ffff` | `0x0800` | `0x0800 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 12 | `MOVWF f` | Move `W` to `f` (`W → f`) | 1 | `00 0000 1fff ffff` | `0x0080` | `0x0080 \| (f & 0x7F)` | None |
| 13 | `NOP` | No Operation | 1 | `00 0000 0xx0 0000` | `0x0000` | `0x0000` | None |
| 14 | `RLF f, d` | Rotate Left `f` through Carry | 1 | `00 1101 dfff ffff` | `0x0D00` | `0x0D00 \| (d << 7) \| (f & 0x7F)` | `C` |
| 15 | `RRF f, d` | Rotate Right `f` through Carry | 1 | `00 1100 dfff ffff` | `0x0C00` | `0x0C00 \| (d << 7) \| (f & 0x7F)` | `C` |
| 16 | `SUBWF f, d` | Subtract `W` from `f` (`f - W`) | 1 | `00 0010 dfff ffff` | `0x0200` | `0x0200 \| (d << 7) \| (f & 0x7F)` | `C, DC, Z` |
| 17 | `SWAPF f, d` | Swap nibbles in `f` | 1 | `00 1110 dfff ffff` | `0x0E00` | `0x0E00 \| (d << 7) \| (f & 0x7F)` | None |
| 18 | `XORWF f, d` | Exclusive OR `W` with `f` | 1 | `00 0110 dfff ffff` | `0x0600` | `0x0600 \| (d << 7) \| (f & 0x7F)` | `Z` |

### 2.2. Bit-Oriented File Register Operations (4 Instructions)

| # | Mnemonic & Operands | Description | Cycles | 14-Bit Binary Opcode (`MSb → LSb`) | Base Hex | Python Encoding Expression | Status Affected |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 19 | `BCF f, b` | Bit Clear `f` (`0 → f<b>`) | 1 | `01 00bb bfff ffff` | `0x1000` | `0x1000 \| ((b & 7) << 7) \| (f & 0x7F)` | None |
| 20 | `BSF f, b` | Bit Set `f` (`1 → f<b>`) | 1 | `01 01bb bfff ffff` | `0x1400` | `0x1400 \| ((b & 7) << 7) \| (f & 0x7F)` | None |
| 21 | `BTFSC f, b` | Bit Test `f`, Skip if Clear | 1(2) | `01 10bb bfff ffff` | `0x1800` | `0x1800 \| ((b & 7) << 7) \| (f & 0x7F)` | None |
| 22 | `BTFSS f, b` | Bit Test `f`, Skip if Set | 1(2) | `01 11bb bfff ffff` | `0x1C00` | `0x1C00 \| ((b & 7) << 7) \| (f & 0x7F)` | None |

### 2.3. Literal and Control Operations (13 Instructions)

| # | Mnemonic & Operands | Description | Cycles | 14-Bit Binary Opcode (`MSb → LSb`) | Base Hex (`x=0`) | Python Encoding Expression | Status Affected |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 23 | `ADDLW k` | Add Literal `k` and `W` | 1 | `11 111x kkkk kkkk` | `0x3E00` | `0x3E00 \| (k & 0xFF)` | `C, DC, Z` |
| 24 | `ANDLW k` | AND Literal `k` with `W` | 1 | `11 1001 kkkk kkkk` | `0x3900` | `0x3900 \| (k & 0xFF)` | `Z` |
| 25 | `CALL k` | Call Subroutine at 11-bit `k` | 2 | `10 0kkk kkkk kkkk` | `0x2000` | `0x2000 \| (k & 0x7FF)` | None |
| 26 | `CLRWDT` | Clear Watchdog Timer | 1 | `00 0000 0110 0100` | `0x0064` | `0x0064` | `~TO, ~PD` |
| 27 | `GOTO k` | Unconditional Branch to `k` | 2 | `10 1kkk kkkk kkkk` | `0x2800` | `0x2800 \| (k & 0x7FF)` | None |
| 28 | `IORLW k` | Inclusive OR Literal with `W` | 1 | `11 1000 kkkk kkkk` | `0x3800` | `0x3800 \| (k & 0xFF)` | `Z` |
| 29 | `MOVLW k` | Move Literal `k` to `W` | 1 | `11 00xx kkkk kkkk` | `0x3000` | `0x3000 \| (k & 0xFF)` | None |
| 30 | `RETFIE` | Return from Interrupt (`1 → GIE`) | 2 | `00 0000 0000 1001` | `0x0009` | `0x0009` | None |
| 31 | `RETLW k` | Return with Literal `k` in `W` | 2 | `11 01xx kkkk kkkk` | `0x3400` | `0x3400 \| (k & 0xFF)` | None |
| 32 | `RETURN` | Return from Subroutine | 2 | `00 0000 0000 1000` | `0x0008` | `0x0008` | None |
| 33 | `SLEEP` | Enter Standby Sleep Mode | 1 | `00 0000 0110 0011` | `0x0063` | `0x0063` | `~TO, ~PD` |
| 34 | `SUBLW k` | Subtract `W` from Literal (`k - W`) | 1 | `11 110x kkkk kkkk` | `0x3C00` | `0x3C00 \| (k & 0xFF)` | `C, DC, Z` |
| 35 | `XORLW k` | Exclusive OR Literal with `W` | 1 | `11 1010 kkkk kkkk` | `0x3A00` | `0x3A00 \| (k & 0xFF)` | `Z` |

---

## 3. Step-by-Step Hand-Encoding Examples

1. **Literal (`MOVLW 0x55`):** Pattern `11 0000 kkkk kkkk` (`x=0`), `k = 0101 0101` → `11 0000 0101 0101` = **`0x3055`**.
2. **Byte-Oriented (`ADDWF 0x20, F`):** Pattern `00 0111 dfff ffff`, `d = 1`, `f = 010 0000` → `00 0111 1010 0000` = **`0x07A0`** (`d = 0` gives `0x0720`).
3. **Bit-Oriented (`BSF STATUS, RP0` → `BSF 0x03, 5`):** Pattern `01 01bb bfff ffff`, `b = 101`, `f = 000 0011` → `01 0110 1000 0011` = **`0x1683`**.
4. **Branch with Label (`GOTO LOOP`, where `LOOP = 0x0005`):** Pattern `10 1kkk kkkk kkkk`, `k = 000 0000 0101` → `10 1000 0000 0101` = **`0x2805`**.
5. **Bank-1 SFR Masking (`CLRF TRISB`, `TRISB = 0x86`):** 7-bit masked `f = 0x86 & 0x7F = 0x06` → `00 0001 1000 0110` = **`0x0186`** (hardware bank comes from `STATUS.RP0 = 1`).

---

## 4. Complete Worked Mini-Program Translation & Intel HEX Output

| Word Addr | Assembly Line | Binary (14-bit) | Hex | Size | Little-Endian Bytes |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `0x0000` | `BSF STATUS, RP0` (`0x03, 5`) | `01 0110 1000 0011` | `0x1683` | 1 word | `83 16` |
| `0x0001` | `CLRF TRISB` (`0x86 → 0x06`) | `00 0001 1000 0110` | `0x0186` | 1 word | `86 01` |
| `0x0002` | `BCF STATUS, RP0` (`0x03, 5`) | `01 0010 1000 0011` | `0x1283` | 1 word | `83 12` |
| `0x0003` | `MOVLW 0x05` | `11 0000 0000 0101` | `0x3005` | 1 word | `05 30` |
| `0x0004` | `MOVWF 0x20` | `00 0000 1010 0000` | `0x00A0` | 1 word | `A0 00` |
| `0x0005` | `LOOP: INCF PORTB, F` (`0x06, 1`) | `00 1010 1000 0110` | `0x0A86` | 1 word | `86 0A` |
| `0x0006` | `DECFSZ 0x20, F` (`0x20, 1`) | `00 1011 1010 0000` | `0x0BA0` | 1 word | `A0 0B` |
| `0x0007` | `GOTO LOOP` (`0x005`) | `10 1000 0000 0101` | `0x2805` | 1 word | `05 28` |

**Verified Intel HEX Output:**
- Byte count = `16` (`0x10`), Start Byte Address = `0x0000`, Record Type = `00`, Sum of bytes = `1026 (0x0402)` → 2's complement checksum = `(0x100 - 0x02) & 0xFF = 0xFE`.
```text
:020000040000FA
:100000008316860183120530A000860AA00B0528FE
:00000001FF
```
