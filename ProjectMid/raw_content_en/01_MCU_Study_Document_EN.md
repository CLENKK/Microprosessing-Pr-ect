# MICROCONTROLLER TECHNICAL STUDY DOCUMENT: MICROCHIP PIC16F877A
**Course:** Micro-processing System — Midterm Project (Component 1)  
**Selected MCU:** Microchip PIC16F877A (40-Pin PDIP, 8-bit Mid-Range RISC)  
**Application Project:** Topic #15 — Smart Irrigation Controller  
**Primary Technical References:** Microchip *PIC16F87XA Data Sheet* (`DS39582C`, Jan. 2013), *PICmicro Mid-Range MCU Family Reference Manual* (`DS33023A`), and Atmel/Microchip *ATmega32(L) Data Sheet* (`2503Q–AVR–02/11`).

> **Figure Embedding Note:** Placeholders marked `[INSERT FIGURE: ...]` cite the exact figure number and page in the official datasheets (`docs/`) for direct insertion and proper academic referencing (Section 5.10).

---

## 5.1. Introduction

### 5.1.1. Manufacturer and Microcontroller Family
- **Selected Device:** **PIC16F877A** (flagship 40-pin member of the `PIC16F87XA` family: `873A`, `874A`, `876A`, `877A`).
- **Manufacturer:** **Microchip Technology Inc.** (USA).
- **Architecture Family:** **PICmicro Mid-Range 8-bit CMOS Enhanced Flash Microcontroller**, built on a modified Harvard architecture with a 14-bit program instruction bus and an 8-bit data bus (`DS39582C`, pp. 1, 5).
- **Manufacturing Technology:** Low-power, high-speed CMOS Flash/EEPROM process with a fully static design (operating from DC to 20 MHz), providing high memory endurance (`100,000` typical Flash erase/write cycles, `1,000,000` typical Data EEPROM erase/write cycles, and `> 40 years` data retention, pp. 1, 179).

### 5.1.2. Typical Applications
Because the `PIC16F877A` integrates an 8-channel 10-bit ADC, three hardware timers, two CCP/PWM modules, industrial serial interfaces (USART, SPI, I²C), an 8-bit Parallel Slave Port (PSP), and two analog comparators in a breadboard-friendly 40-pin DIP package, it is widely deployed in:
- **Sensor Monitoring & Data Acquisition:** Smart irrigation controllers, temperature monitors, digital voltmeters, and UART data loggers.
- **Industrial Control & Automation:** PWM DC/servo motor controllers, traffic light controllers, elevator controllers, and relay-based actuators.
- **Consumer Electronics & Education:** Electronic combination locks, digital clocks with alarms, home appliances, and university microprocessor laboratories.

### 5.1.3. Main Features and Specifications

| Specification Category | PIC16F877A Technical Parameters (`DS39582C`, Table 1-1 p. 5 & Section 17 pp. 173–179) |
| :--- | :--- |
| **CPU Core** | 8-bit RISC, Harvard architecture, 2-stage pipeline, **35 single-word (14-bit) instructions** |
| **Operating Speed & Cycle** | `DC – 20 MHz` (`1 TCY = 4 / FOSC`, min `200 ns` @ 20 MHz → up to **5 MIPS**) |
| **Operating Voltage (`VDD`)** | `4.0V – 5.5V` (`PIC16F877A`); `2.0V – 5.5V` (`PIC16LF877A`, max 10 MHz) |
| **Flash Program Memory** | **8K × 14-bit words** (`8,192` instructions ≈ 14.3 KB), self-reprogrammable under software control |
| **Data SRAM** | **368 bytes** (organized into 4 Banks), plus Special Function Registers (SFRs) |
| **Data EEPROM** | **256 bytes** (`00h – FFh`), `> 40 years` retention |
| **Digital I/O (GPIO)** | **33 I/O pins** across 5 Ports (`PORTA` 6b, `PORTB/C/D` 8b, `PORTE` 3b); max `25 mA/pin` |
| **Timers** | 3 modules: **Timer0** (8-bit), **Timer1** (16-bit, async during Sleep), **Timer2** (8-bit with `PR2`) |
| **Capture/Compare/PWM** | 2 modules: **CCP1, CCP2** (16-bit Capture `12.5 ns`, 16-bit Compare `200 ns`, **10-bit PWM**) |
| **10-bit ADC** | **8 input channels** (`AN0–AN7`), selectable `VREF+` / `VREF-` |
| **Serial & Parallel Interfaces** | **1 USART** (Sync/Async), **1 MSSP** (SPI Master/Slave or I²C 7/10-bit), **1 PSP** (8-bit) |
| **Analog Comparators** | **2 Analog Comparators** + 16-tap programmable internal voltage reference (**CVREF**) |
| **Interrupts & Stack** | **15 interrupt sources** (single vector `0004h`), **8-level × 13-bit Hardware Stack** |
| **Special Features** | Independent RC WDT, POR, BOR, PWRT (`72 ms`), OST (`1024 TOSC`), Sleep mode, 2-pin ICSP/ICD |
| **Packages** | 40-pin PDIP (used in this project), 44-pin PLCC, TQFP, QFN |

### 5.1.4. Reasons for Selecting PIC16F877A
1. **Strong Architectural Contrast with ATmega32:** PIC16F877A represents the classic **single-accumulator (`W`) + banked RAM + single interrupt vector + fixed hardware stack** paradigm, offering an insightful architectural comparison against the class MCU (ATmega32 with 32 general-purpose registers `R0–R31`, flat SRAM, and 21 interrupt vectors).
2. **Compact, Orthogonal 14-bit Instruction Set (Ideal for Components 3 & 4):** With only **35 fixed-length 14-bit instructions** structured into 3 contiguous bit formats, students can master manual machine-code translation and implement a 100%-verified **Python GUI Mini Assembler** supporting the entire instruction set.
3. **Complete Official Documentation & Reliable Simulation:** Backed by `DS39582C` and `DS33023A`, supported by **MPASM / `gpasm`**, and natively simulated with high accuracy in **Proteus ISIS** and **SimulIDE** (explicitly recommended in Section 3.1.A of the project assignment).
4. **Rich On-Chip Peripherals:** Easily supports our **Topic #15 Smart Irrigation Controller** using **5 independent hardware peripherals** (ADC, Timer1, External Interrupt `RB0/INT`, GPIO/LCD 4-bit, and internal Data EEPROM).

---

## 5.2. CPU Architecture

`[INSERT FIGURE: Figure 1-2 – PIC16F874A/877A Block Diagram, DS39582C, p. 7]`

### 5.2.1. Harvard Architecture and Internal Buses
The PIC16F877A employs a **Harvard architecture** with physically separate instruction and data memory buses (`DS39582C`, Figure 1-2, p. 7):
- **14-bit Program Bus:** Connects Flash Program Memory directly to the Instruction Register, fetching a complete 14-bit instruction (opcode + operands) in a single cycle.
- **8-bit Data Bus:** Connects SRAM/SFRs, the `W` register, the 8-bit ALU, I/O ports, and peripheral modules.
- **9-bit RAM Address Bus:** Combines the 7-bit direct address from the instruction word with `STATUS<RP1:RP0>` (or the 8-bit `FSR` register with `STATUS<IRP>`), addressing `512` byte locations (`000h–1FFh`).
- **13-bit Program Address Bus:** Connects the 13-bit Program Counter (`PC<12:0>`) to Flash memory and the 8-level Hardware Stack (`0000h–1FFFh`).

### 5.2.2. ALU, Control Unit, and Core CPU Registers
- **8-bit ALU:** Performs arithmetic (addition, 2's complement subtraction), bitwise logic (`AND`, `OR`, `XOR`, complement), increment/decrement, nibble swap, and rotate operations between `W` and any file register `f` (or 8-bit literal `k`). The destination bit `d` routes the result to `W` (`d = 0`) or back to `f` (`d = 1`).
- **Working Register (`W`):** The sole 8-bit accumulator (not memory-mapped in RAM), acting as the primary ALU operand and data transfer intermediary.
- **Instruction Decode & Timing Generation:** Divides the external `OSC1` clock into four non-overlapping quadrature phases (`Q1, Q2, Q3, Q4`) forming one instruction cycle (`TCY = 4 × TOSC`).
- **`STATUS` Register (`03h, 83h, 103h, 183h` — accessible from all 4 Banks, `Register 2-1`, p. 22):**

| Bit | Name | Access / POR | Detailed Function |
| :---: | :---: | :---: | :--- |
| 7 | `IRP` | R/W-0 | Register Bank Select for indirect addressing: `0` = Banks 0–1 (`00h–FFh`), `1` = Banks 2–3 (`100h–1FFh`) |
| 6–5 | `RP1:RP0` | R/W-00 | Register Bank Select for direct addressing: `00`=Bank 0, `01`=Bank 1, `10`=Bank 2, `11`=Bank 3 |
| 4 | `~TO` | R-1 | Time-out bit: `1` after POR/`CLRWDT`/`SLEEP`; `0` after Watchdog Timer time-out |
| 3 | `~PD` | R-1 | Power-down bit: `1` after POR/`CLRWDT`; `0` upon executing `SLEEP` |
| 2 | `Z` | R/W-x | Zero flag: `1` if the result of an arithmetic or logic operation is zero; otherwise `0` |
| 1 | `DC` | R/W-x | Digit Carry / `~Borrow` (carry from bit 3 to bit 4); **polarity reversed for subtraction** |
| 0 | `C` | R/W-x | Carry / `~Borrow` (carry from bit 7); **polarity reversed for subtraction** (`C=1` no borrow / ≥, `C=0` borrow / <) |

- **13-bit Program Counter (`PC<12:0>`, `Figure 2-5`, p. 30):** Comprises readable/writable `PCL` (`02h`, bits `7:0`) and non-directly-readable `PCH` (bits `12:8`), updated indirectly via the `PCLATH` holding register (`0Ah`).
- **8-Level × 13-bit Hardware Stack (Section 2.3.2, p. 30):** Isolated from both Flash and RAM with an invisible stack pointer. Operates as a **circular buffer**: pushing a 9th return address silently overwrites Level 1 with **no overflow flag**. There are no `PUSH` or `POP` instructions; stack operations occur exclusively on `CALL`, `RETURN`, `RETLW`, `RETFIE`, and interrupts.

### 5.2.3. Two-Stage Instruction Pipeline and `Q1–Q4` Execution Cycle
Separate program and data buses allow the CPU to fetch the next instruction while executing the current one (`Figure 17-4`, p. 182):
- **Q1 (Decode):** Decode the latched 14-bit instruction and increment `PC`.
- **Q2 (Read):** Read source operand from file register `f` or physical I/O pin (*Read* phase of RMW).
- **Q3 (Process):** Execute ALU computation.
- **Q4 (Write):** Write result to `W` or `f` (*Write* phase of RMW) while completing the Flash fetch of the next instruction.
- **Execution Time:** Normal instructions complete in **1 `TCY`** (`1 µs` at 4 MHz; `200 ns` at 20 MHz). Any instruction modifying `PC` (`GOTO`, `CALL`, `RETURN`, `RETFIE`, `RETLW`, write to `PCL`) or a conditional skip (`BTFSC`, `BTFSS`, `DECFSZ`, `INCFSZ`) whose condition evaluates true flushes the prefetched instruction (inserting a dummy `NOP`), requiring **2 `TCY`**.

```text
Instruction Cycle: |---- TCY 1 ----|---- TCY 2 ----|---- TCY 3 ----|---- TCY 4 ----|
Clock Phases:      | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   |
Fetch Stage:       | Fetch Inst 1  | Fetch Inst 2  | Fetch Inst 3  | Fetch Target  |
Execute Stage:     |               | Exec Inst 1   | Exec GOTO     | Flush (NOP)   | -> Exec Target
```

---

## 5.3. Memory Organization

The PIC16F877A contains three independent memory spaces: **Flash Program Memory**, **SRAM Data Memory (Register File)**, and **Data EEPROM**.

### 5.3.1. Flash Program Memory (`Figure 2-1`, p. 15)
`[INSERT FIGURE: Figure 2-1 – PIC16F876A/877A Program Memory Map and Stack, DS39582C, p. 15]`
- **Capacity:** `8,192 × 14-bit words` (`0000h – 1FFFh`).
- **Fixed Vectors:**
  - **Reset Vector:** `0000h` (typically `GOTO MAIN`).
  - **Single Interrupt Vector:** `0004h` (shared by all 15 interrupt sources).
  - **Configuration Space (outside user Flash):** User ID Locations (`2000h–2003h`) and Configuration Word (`2007h`).
- **Program Memory Paging (Section 2.4, p. 30):** Because `CALL` and `GOTO` encode only an **11-bit address** (`2,048 words = 2K`), the 8K Flash is partitioned into **4 Pages**:
  - **Page 0:** `0000h – 07FFh` (`PCLATH<4:3> = 00`)
  - **Page 1:** `0800h – 0FFFh` (`PCLATH<4:3> = 01`)
  - **Page 2:** `1000h – 17FFh` (`PCLATH<4:3> = 10`)
  - **Page 3:** `1800h – 1FFFh` (`PCLATH<4:3> = 11`)
  - Cross-page `CALL`/`GOTO` requires updating `PCLATH<4:3>` (or using `PAGESEL`). `RETURN`/`RETFIE` restores all 13 bits of `PC` from the stack without modifying `PCLATH`.

### 5.3.2. Data Memory / Register File (`Figure 2-3`, p. 17)
`[INSERT FIGURE: Figure 2-3 – PIC16F876A/877A Register File Map, DS39582C, p. 17]`
- **Banked Organization:** Each direct-address instruction carries only 7 address bits (`00h–7Fh` = 128 bytes/bank). Therefore, the 512-byte register space (`000h–1FFh`) is divided into **4 Banks** selected by `STATUS<6:5>` (`RP1:RP0`):

| Bank | `RP1:RP0` | Address Range | SFR Region | General Purpose RAM (GPR) | Shared / Mirrored RAM |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Bank 0** | `00` | `000h–07Fh` | `00h–1Fh` (32B) | `20h–6Fh` (80B) + `70h–7Fh` (16B) = **96B** | `70h–7Fh` (16B physical) |
| **Bank 1** | `01` | `080h–0FFh` | `80h–9Fh` (32B) | `A0h–EFh` (**80B**) | `F0h–FFh` → mirrors `70h–7Fh` |
| **Bank 2** | `10` | `100h–17Fh` | `100h–10Fh` (16B) | `110h–16Fh` (**96B**) | `170h–17Fh` → mirrors `70h–7Fh` |
| **Bank 3** | `11` | `180h–1FFh` | `180h–18Fh` (16B) | `190h–1EFh` (**96B**) | `1F0h–1FFh` → mirrors `70h–7Fh` |
| **Total GPR** | — | — | — | **96 + 80 + 96 + 96 = 368 bytes** | 16B common across all 4 Banks |

- **Core SFRs Mirrored in All 4 Banks:** `INDF` (`00h`), `PCL` (`02h`), `STATUS` (`03h`), `FSR` (`04h`), `PCLATH` (`0Ah`), `INTCON` (`0Bh`).
- **Key Peripheral SFR Distribution (`Table 2-1`, pp. 19–21):**
  - **Bank 0:** `TMR0 (01h)`, `PORTA–PORTE (05h–09h)`, `PIR1–PIR2 (0Ch–0Dh)`, `TMR1L/H (0Eh–0Fh)`, `T1CON (10h)`, `TMR2 (11h)`, `T2CON (12h)`, `SSPBUF/SSPCON (13h–14h)`, `CCPR1L/H, CCP1CON (15h–17h)`, `RCSTA/TXREG/RCREG (18h–1Ah)`, `CCPR2L/H, CCP2CON (1Bh–1Dh)`, `ADRESH (1Eh)`, `ADCON0 (1Fh)`.
  - **Bank 1:** `OPTION_REG (81h)`, `TRISA–TRISE (85h–89h)`, `PIE1–PIE2 (8Ch–8Dh)`, `PCON (8Eh)`, `SSPCON2/PR2/SSPADD/SSPSTAT (91h–94h)`, `TXSTA/SPBRG (98h–99h)`, `CMCON/CVRCON (9Ch–9Dh)`, `ADRESL (9Eh)`, `ADCON1 (9Fh)`.
  - **Bank 2:** `EEDATA (10Ch)`, `EEADR (10Dh)`, `EEDATH (10Eh)`, `EEADRH (10Fh)`.
  - **Bank 3:** `EECON1 (18Ch)`, `EECON2 (18Dh)` (virtual unlock register).

### 5.3.3. Data EEPROM (256 Bytes) and Flash Self-Programming (`Section 3.0`, pp. 33–39)
- Accessed indirectly via six SFRs in Banks 2–3 (`EEADR/H`, `EEDATA/H`, `EECON1`, `EECON2`).
- **EEPROM Read (`Example 3-1`, p. 35):** Write address to `EEADR` → `BCF EECON1, EEPGD` → `BSF EECON1, RD` → read byte immediately from `EEDATA`.
- **EEPROM Write (`Example 3-2`, p. 35):** Poll `EECON1.WR == 0` → load `EEADR` & `EEDATA` → `EEPGD = 0`, `WREN = 1` → **disable interrupts (`GIE = 0`)** → execute mandatory 5-instruction unlock sequence (`MOVLW 0x55 → MOVWF EECON2 → MOVLW 0xAA → MOVWF EECON2 → BSF EECON1, WR`) → re-enable `GIE`, clear `WREN`. Typical write duration is `4 ms` (max `8 ms`, p. 179).
- **Flash Write (`Section 3.6`, p. 37):** Performed in aligned **4-word erase/write blocks** requiring two `NOP` instructions immediately after `BSF EECON1, WR`.

### 5.3.4. Addressing Modes (`Figure 2-6`, p. 31)
`[INSERT FIGURE: Figure 2-6 – Direct/Indirect Addressing, DS39582C, p. 31]`
1. **Direct Addressing:** Concatenates `RP1:RP0` (`STATUS<6:5>`) with the 7-bit file register field `f` → 9-bit address (`000h–1FFh`). Example: `MOVWF 0x20`.
2. **Indirect Addressing:** Loads an 8-bit pointer into `FSR` (`04h`) combined with `IRP` (`STATUS<7>`); any operation targeting the virtual register `INDF` (`00h`) accesses the memory location pointed to by `IRP:FSR`.
3. **Immediate (Literal) Addressing:** An 8-bit constant `k` is embedded directly inside the instruction word (`MOVLW 0x55`, `ADDLW d'10'`).
4. **Branch / Computed Addressing:** `GOTO`/`CALL` combine `PCLATH<4:3>` with an 11-bit target `k`; lookup tables use Computed GOTO (`ADDWF PCL, F`) with `RETLW`.

---

## 5.4. Pin Configuration (40-Pin PDIP)

`[INSERT FIGURE: Pin Diagrams – 40-Pin PDIP PIC16F874A/877A, DS39582C, p. 3]`

### 5.4.1. Complete 40-Pin PDIP Pinout Table (`Table 1-3`, pp. 10–13)

| Pin | Pin Name | Type | Buffer | Primary & Alternate Functions |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `~MCLR/VPP` | I/P | ST | Active-low Master Clear Reset (`~MCLR`) / Programming Voltage (`VPP`) |
| 2 | `RA0/AN0` | I/O | TTL | Digital I/O or Analog Input `AN0` *(Analog by default on POR)* |
| 3 | `RA1/AN1` | I/O | TTL | Digital I/O or Analog Input `AN1` *(Analog on POR)* |
| 4 | `RA2/AN2/VREF-/CVREF` | I/O | TTL | Digital I/O, `AN2`, ADC Low Reference `VREF-`, Comparator `CVREF` output |
| 5 | `RA3/AN3/VREF+` | I/O | TTL | Digital I/O, `AN3`, ADC High Reference `VREF+` |
| 6 | `RA4/T0CKI/C1OUT` | I/O | ST | Digital I/O (**Open-Drain output**, requires external pull-up), Timer0 clock, `C1OUT` |
| 7 | `RA5/AN4/~SS/C2OUT` | I/O | TTL | Digital I/O, `AN4`, SPI Slave Select `~SS`, Comparator 2 output `C2OUT` |
| 8 | `RE0/~RD/AN5` | I/O | ST/TTL | Digital I/O, PSP Read `~RD`, Analog Input `AN5` *(Analog on POR)* |
| 9 | `RE1/~WR/AN6` | I/O | ST/TTL | Digital I/O, PSP Write `~WR`, Analog Input `AN6` *(Analog on POR)* |
| 10 | `RE2/~CS/AN7` | I/O | ST/TTL | Digital I/O, PSP Chip Select `~CS`, Analog Input `AN7` *(Analog on POR)* |
| 11 | `VDD` | P | — | Positive power supply `+5V` (`4.0V – 5.5V`, place `0.1 µF` decoupling cap) |
| 12 | `VSS` | P | — | Ground reference (`GND`, tied with Pin 31) |
| 13 | `OSC1/CLKI` | I | ST/CMOS | Crystal oscillator input or external clock input |
| 14 | `OSC2/CLKO` | O | — | Crystal oscillator output (or `FOSC/4` output in RC mode) |
| 15 | `RC0/T1OSO/T1CKI` | I/O | ST | Digital I/O, Timer1 oscillator output, Timer1 external clock input |
| 16 | `RC1/T1OSI/CCP2` | I/O | ST | Digital I/O, Timer1 oscillator input, **Capture2 / Compare2 / PWM2** |
| 17 | `RC2/CCP1` | I/O | ST | Digital I/O, **Capture1 / Compare1 / PWM1** |
| 18 | `RC3/SCK/SCL` | I/O | ST | Digital I/O, **SPI (`SCK`)** or **I²C (`SCL`)** serial clock |
| 19–22 | `RD0/PSP0 – RD3/PSP3` | I/O | ST/TTL | Digital I/O (PORTD bits 0–3) or Parallel Slave Port data bits 0–3 |
| 23 | `RC4/SDI/SDA` | I/O | ST | Digital I/O, **SPI Data In (`SDI`)** or **I²C Data (`SDA`)** |
| 24 | `RC5/SDO` | I/O | ST | Digital I/O, **SPI Data Out (`SDO`)** |
| 25 | `RC6/TX/CK` | I/O | ST | Digital I/O, **USART Async TX** or Sync Clock `CK` |
| 26 | `RC7/RX/DT` | I/O | ST | Digital I/O, **USART Async RX** or Sync Data `DT` |
| 27–30 | `RD4/PSP4 – RD7/PSP7` | I/O | ST/TTL | Digital I/O (PORTD bits 4–7) or Parallel Slave Port data bits 4–7 |
| 31 | `VSS` | P | — | Ground reference (`GND`) |
| 32 | `VDD` | P | — | Positive power supply `+5V` |
| 33 | `RB0/INT` | I/O | TTL/ST | Digital I/O (internal weak pull-up), **External Interrupt `INT`** |
| 34–35 | `RB1, RB2` | I/O | TTL | Digital I/O (internal weak pull-up) |
| 36 | `RB3/PGM` | I/O | TTL | Digital I/O or **LVP** enable pin *(disable via `_LVP_OFF` for general I/O)* |
| 37–38 | `RB4, RB5` | I/O | TTL | Digital I/O (weak pull-up + **Interrupt-on-Change**) |
| 39 | `RB6/PGC` | I/O | TTL/ST | Digital I/O (IOC + pull-up) or **ICSP/ICD Clock (`PGC`)** |
| 40 | `RB7/PGD` | I/O | TTL/ST | Digital I/O (IOC + pull-up) or **ICSP/ICD Data (`PGD`)** |

### 5.4.2. GPIO Operation and Critical Hardware Pitfalls
- **Direction Control (`TRISx`):** `1 = Input` (high-impedance), `0 = Output` (opposite of AVR `DDRx`). All `TRISx` registers default to `1` (Input) on reset.
- **Read-Modify-Write (RMW) Phenomenon (Section 4.1 p. 41, Section 15.1 p. 159):** Because PIC16 lacks separate `LATx` output latches, bit instructions (`BSF`/`BCF PORTx, b`) read the actual pin voltage levels, modify one bit, and write all 8 bits back. Heavy capacitive loads or back-to-back bit writes can inadvertently corrupt adjacent pins. *Best practice:* maintain a RAM shadow register (`PORTC_IMG`) and write the full byte atomically via `MOVWF PORTC`.
- **Three Default Reset Traps on PIC16F877A:**
  1. `PORTA` & `PORTE` default to **Analog Input** (digital reads always return `0`) → write `ADCON1 = 0x06` (all digital) or `0x0E` (`AN0` analog only).
  2. `RA4` is an **Open-Drain** output → requires an external pull-up resistor (`4.7 kΩ – 10 kΩ`) to drive logic high.
  3. `RB3/PGM` defaults to **Low-Voltage Programming enabled (`LVP = 1`)** → always specify `_LVP_OFF` in `__CONFIG` to free `RB3` as normal I/O.

### 5.4.3. Clock, Reset (`~MCLR`), and Power Supply Requirements
- **Oscillator Modes (`Section 14.2`, pp. 145–146 — `[INSERT FIGURE: Figure 14-1, p. 145]`):** Configured by `FOSC1:FOSC0`: `LP` (`32–200 kHz`), `XT` (crystal `≤ 4 MHz`, `C1=C2=15–33 pF`), `HS` (high-speed crystal `4–20 MHz`, `C1=C2=15–33 pF`), and `RC` (`3 kΩ ≤ REXT ≤ 100 kΩ`, `CEXT > 20 pF`).
- **Reset Circuit (`Figure 14-5`, p. 148):** Connect `~MCLR` to `VDD` via an RCR network (`R1 = 10 kΩ < 40 kΩ`, `R2 ≥ 1 kΩ`, `C1 = 0.1 µF`, plus push-button to `VSS`). Built-in `POR`, `PWRT` (`72 ms`), and `OST` (`1024 TOSC`) ensure reliable startup.
- **Power Supply & Electrical Limits (`Section 17.0`, pp. 173–176):** Connect both `VDD`/`VSS` pairs with `0.1 µF` bypass capacitors. Typical active current: `1.6 mA` @ `4 MHz / 5.5V`, `7 mA` @ `20 MHz / 5.5V`; Sleep current (WDT off): `1.5 µA` typ. Max pin sink/source: `25 mA/pin`, `200 mA` combined per port group (`PORTA+B+E` and `PORTC+D`).

---

## 5.5. Instruction Set (`Section 15.0`, pp. 159–165)

`[INSERT FIGURE: Figure 15-1 – General Format for Instructions, DS39582C, p. 159]`

The PIC16F877A features **35 single-word instructions**, each exactly **14 bits** wide, organized into three orthogonal categories:
1. **Byte-Oriented File Register Operations (18 instructions):** `ADDWF`, `ANDWF`, `CLRF`, `CLRW`, `COMF`, `DECF`, `DECFSZ`, `INCF`, `INCFSZ`, `IORWF`, `MOVF`, `MOVWF`, `NOP`, `RLF`, `RRF`, `SUBWF`, `SWAPF`, `XORWF`.
   - Format: `[13:8 OPCODE (6b)] | [7 d (1b)] | [6:0 f (7b)]`.
2. **Bit-Oriented File Register Operations (4 instructions):** `BCF`, `BSF`, `BTFSC`, `BTFSS`.
   - Format: `[13:10 OPCODE (4b)] | [9:7 b (3b)] | [6:0 f (7b)]`.
3. **Literal and Control Operations (13 instructions):** `ADDLW`, `ANDLW`, `CALL`, `CLRWDT`, `GOTO`, `IORLW`, `MOVLW`, `RETFIE`, `RETLW`, `RETURN`, `SLEEP`, `SUBLW`, `XORLW`.
   - 8-bit Literal format: `[13:8 OPCODE (6b)] | [7:0 k (8b)]`; 11-bit Branch/Call format (`CALL`/`GOTO`): `[13:11 OP (3b)] | [10:0 k (11b)]`.

**Examples of Key Instructions:**
- `MOVLW 0x55` (`0x3055`, 1 `TCY`): Loads immediate `0x55` into `W` without altering `STATUS`.
- `SUBWF f, W` (`(f) - (W) → W`): Uses 2's complement subtraction with **inverted Carry/Borrow** (`C = 1` when `f ≥ W`, `C = 0` when `f < W`).
- `DECFSZ COUNT, F` (1 or 2 `TCY`): Decrements `COUNT` and skips the next instruction when zero — ideal for compact delay loops.
- `SWAPF STATUS, W` (`0x0E03`, 1 `TCY`): Exchanges nibbles of `STATUS` into `W` **without affecting `Z`** — essential for ISR context saving (`Example 14-1`, p. 154).
- *(The complete 35-instruction master opcode table, binary patterns, and hand-encoding walkthroughs are provided in `Instruction_Set_Opcode_Table.pdf`.)*

---

## 5.6. Peripheral Modules

### 5.6.1. GPIO (`Section 4.0`, pp. 41–52)
Five bidirectional ports (`PORTA–PORTE`) controlled by `TRISA–TRISE`. `PORTB` additionally provides global weak pull-ups (`OPTION_REG<7> = 0`) and Interrupt-on-Change on `RB7:RB4`.

### 5.6.2. Timers and Counters (`Sections 5.0–7.0`, pp. 53–62)

| Feature | **Timer0** (`TMR0`, `OPTION_REG`) | **Timer1** (`TMR1H:TMR1L`, `T1CON`) | **Timer2** (`TMR2`, `PR2`, `T2CON`) |
| :--- | :--- | :--- | :--- |
| **Width** | 8-bit (`00h–FFh`) | **16-bit** (`0000h–FFFFh`) | 8-bit (`00h` to `PR2`) |
| **Prescaler** | `1:2` to `1:256` *(shared with WDT)* | `1:1, 1:2, 1:4, 1:8` (`T1CKPS1:0`) | `1:1, 1:4, 1:16` (`T2CKPS1:0`) |
| **Postscaler** | None | None | `1:1` to `1:16` (`TOUTPS3:0`) |
| **Clock Source** | Internal (`FOSC/4`) or `RA4/T0CKI` | Internal (`FOSC/4`) or external `32.768 kHz` | Internal (`FOSC/4`) only |
| **Runs in Sleep** | No | **Yes** (Asynchronous Counter mode) | No |
| **Interrupt Flag / Enable** | `INTCON.TMR0IF` / `TMR0IE` | `PIR1.TMR1IF` / `TMR1IE` (+ `PEIE`) | `PIR1.TMR2IF` / `TMR2IE` (+ `PEIE`) |
| **Period Formula** | $T = (256 - \text{TMR0}) \times \text{PS} \times \frac{4}{F_{\text{OSC}}}$ | $T = (65536 - \text{TMR1}) \times \text{PS} \times \frac{4}{F_{\text{OSC}}}$ | $T = (\text{PR2}+1) \times \text{PS} \times \text{Post} \times \frac{4}{F_{\text{OSC}}}$ |

### 5.6.3. Interrupt System (`Sections 14.11–14.12`, pp. 153–154)
`[INSERT FIGURE: Figure 14-10 – Interrupt Logic, DS39582C, p. 153]`
- **15 interrupt sources** share **1 single vector at `0004h`**:
  - **Core Interrupts (`INTCON` `0Bh` — requires `GIE = 1` + individual enable):** `TMR0IF`, `INTF` (`RB0/INT` edge selected by `OPTION_REG.INTEDG`), `RBIF` (`RB7:RB4` change — read `PORTB` before clearing `RBIF`).
  - **Peripheral Interrupts (`PIE1/PIR1` & `PIE2/PIR2` — requires `GIE = 1` and `PEIE = 1`):** `PSPIF`, `ADIF`, `RCIF`/`TXIF`, `SSPIF`, `CCP1IF`, `TMR2IF`, `TMR1IF`, `CMIF`, `EEIF`, `BCLIF`, `CCP2IF`.
- **ISR Sequence:** Hardware clears `GIE`, pushes `PC`, and jumps to `0004h` (3–4 `TCY` latency). Firmware saves `W`, `STATUS`, and `PCLATH` into Shared RAM `70h–7Fh` (using `SWAPF`), polls flag bits, clears active flags in software, restores context, and exits via `RETFIE`.

### 5.6.4. 10-Bit Analog-to-Digital Converter (`Section 11.0`, pp. 127–133)
`[INSERT FIGURE: Figure 11-1 – A/D Block Diagram (p. 129) & Figure 11-4 – A/D Result Justification (p. 132)]`
- **8 single-ended channels (`AN0–AN7`)** selected via `ADCON0<5:3>` (`CHS2:0`), enabled via `ADCON0.ADON = 1`, started via `ADCON0.GO/DONE = 1`.
- **Pin Configuration (`ADCON1<3:0>` / `PCFG3:0`, p. 128):** `0110` (`0x06`) = all Digital; `1110` (`0x0E` with `ADFM=0`) = `AN0` Analog only (`VREF+=VDD, VREF-=VSS`); `0000` = all 8 Analog.
- **Justification (`ADCON1.ADFM`):** `ADFM = 1` (Right-justified 10-bit across `ADRESH` Bank 0 & `ADRESL` Bank 1); `ADFM = 0` (Left-justified — upper 8 bits conveniently read from `ADRESH` in Bank 0).
- **Mandatory Timing:** `TAD ≥ 1.6 µs` (`12 TAD` per conversion; use `FOSC/8` at 4 MHz → `2.0 µs`, `Table 11-1` p. 131) and **Acquisition Time `TACQ ≥ 19.72 µs`** (`Equation 11-1`, p. 130) before setting `GO/DONE` (`RS ≤ 2.5 kΩ`).

### 5.6.5. Serial Communication (USART & MSSP) and CCP/PWM
- **USART (`Section 10.0`, pp. 111–125):** Full-duplex async on `RC6/TX` & `RC7/RX` (`TXSTA`, `RCSTA`, `SPBRG`, `TXREG`, `RCREG`). Async high-speed (`BRGH = 1`) formula: $\text{Baud} = \frac{F_{\text{OSC}}}{16(\text{SPBRG}+1)}$ → for **9600 bps** at `4 MHz`, `SPBRG = 25` (`0.16%` error, `Table 10-4` p. 114).
- **MSSP (`Section 9.0`, pp. 71–109):** Shared hardware supporting **SPI** (all 4 clock modes, up to `FOSC/4`) *or* **I²C** (Master/Multi-Master/Slave, 7-bit & 10-bit addressing, $F_{\text{SCL}} = \frac{F_{\text{OSC}}}{4(\text{SSPADD}+1)}$) on `RC3–RC5`.
- **CCP1/CCP2 PWM (`Section 8.3`, pp. 67–68):** Up to 10-bit PWM on `RC2/CCP1` & `RC1/CCP2` clocked by `Timer2`: $\text{Period} = [(\text{PR2})+1] \times 4 T_{\text{OSC}} \times \text{PS}$, $\text{Duty} = (\text{CCPR1L}:\text{CCP1CON}\langle 5:4\rangle) \times T_{\text{OSC}} \times \text{PS}$.
- **Analog Comparators & PSP (`Sections 4.6, 12–13`):** 2 comparators (`CMCON`) + 16-tap `CVREF` (`CVRCON`), plus 8-bit Parallel Slave Port on `PORTD/PORTE`.

---

## 5.7. Assembly Programming Environment

### 5.7.1. Assemblers and Development Tools (`Section 16.0`, pp. 167–168)
1. **MPLAB IDE v8.92 / MPLAB X IDE (≤ v5.35) + MPASM Assembler:** Official Microchip macro assembler with `MPLAB SIM` and `MPLINK`. *(Note: MPLAB X v5.40+ removed MPASM in favor of `XC8 pic-as` with different directive syntax; classic datasheet assembly uses MPASM or `gpasm`.)*
2. **`gputils` (`gpasm` / `gplink` / `gpdasm`):** Open-source MPASM-compatible CLI toolchain (`gpasm -p p16f877a smart_irrigation.asm`).
3. **PIC16F877A Python GUI Mini Assembler (Component 4):** Our group's custom 2-pass educational assembler supporting all 35 instructions, MPASM directives, listing generation (`.lst`), and `INHX32M` Intel HEX export (`.hex`).

### 5.7.2. Standard Assembly Source Code Structure & Key Directives

| Directive | Example | Purpose |
| :--- | :--- | :--- |
| `LIST` | `LIST P=16F877A` | Declares target MCU and listing format |
| `#include` | `#include <p16f877a.inc>` | Imports official SFR addresses and bit constants |
| `__CONFIG` | `__CONFIG 0x3F31` *(or bit masks)* | Programs 14-bit Configuration Word at `0x2007` (`Register 14-1`, p. 144) |
| `EQU` | `HYSTERESIS EQU 0x0A` | Assigns a symbolic name to a constant or register address |
| `CBLOCK` / `ENDC` | `CBLOCK 0x20 ... ENDC` | Sequentially allocates RAM variables |
| `ORG` | `ORG 0x0000` / `ORG 0x0004` | Sets Program Memory origin address for subsequent code |
| `BANKSEL` / `PAGESEL` | `BANKSEL TRISB` | Automatically emits `STATUS<RP1:RP0>` or `PCLATH<4:3>` instructions |
| `DT` / `DW` | `DT "OK", 0` | Generates `RETLW` lookup table bytes or raw 14-bit Flash words |
| `ERRORLEVEL` | `ERRORLEVEL -302` | Suppresses Bank-1 reminder messages when banking is handled explicitly |
| `END` | `END` | Marks end of assembly source file |

### 5.7.3. Configuration Word (`2007h`), Compilation Flow, and Intel HEX Format
- **Configuration Word (`Register 14-1`, p. 144):** For our `4 MHz` project (`_CP_OFF & _DEBUG_OFF & _WRT_OFF & _CPD_OFF & _LVP_OFF & _BODEN_OFF & _PWRTE_ON & _WDT_OFF & _XT_OSC`), the encoded 14-bit value is **`0x3F31`** (`11 1111 0011 0001`).
- **Build Flow:** `smart_irrigation.asm` → Assembler → `smart_irrigation.hex` (Proteus firmware) + `smart_irrigation.lst` (address/hex/source verification listing).
- **Intel HEX (`INHX32M`) Format (`:LLAAAATT[DD...]CC`):** Each 14-bit PIC word occupies **2 bytes in Little-Endian order** (Low Byte first, High Byte second) at **`Byte_Address = 2 × Word_Address`**, terminated by an 8-bit 2's complement checksum. Example (`0x0000: MOVLW 0x55 = 3055h`, `0x0001: MOVWF 0x20 = 00A0h`): **`:040000005530A000D7`**.
- **Loading Firmware in Proteus / SimulIDE:** Double-click `PIC16F877A` → browse **Program File** to `smart_irrigation.hex` → set **Processor Clock Frequency = `4MHz`** → leave Configuration Word auto-loaded (`0x3F31`) → click **Play**.

---

## 5.8. Application Project: Topic #15 — Smart Irrigation Controller

### 5.8.1. Project Objectives and 5 Hardware Peripherals Used
Design and implement an intelligent soil-moisture irrigation controller completely in **PIC16F877A Assembly (`smart_irrigation.asm`, 417 words in Page 0)** at `4 MHz` (`1 TCY = 1 µs`). The system measures real-time soil moisture (`0%–99%`), drives a water pump with a **10% hysteresis deadband** (eliminating relay chatter), sounds a critical-dryness alarm (`< 20%`), supports instant **AUTO / MANUAL** switching via external interrupt, and persists user-configured thresholds in **internal EEPROM**.

**Five Hardware Peripherals Utilized (exceeding the minimum 3 required):**
1. **10-bit ADC (`RA0/AN0`, left-justified 8-bit in `ADRESH`):** Samples analog soil moisture (`0–5V`, simulated via `POT-HG` in Proteus).
2. **16-bit Timer1 + Interrupt (`PIR1.TMR1IF`):** Generates precise `100 ms` interrupts (`Prescaler 1:8`, preload `0xCF2C`), divided by `5` for a non-blocking `0.5 s` sampling interval.
3. **External Interrupt (`RB0/INT`, falling edge):** Immediately toggles **AUTO** ↔ **MANUAL** operation.
4. **GPIO (`PORTB`, `PORTC`, `PORTD`):** Drives a 4-bit **16×2 LCD**, reads 3 push-buttons with internal `PORTB` pull-ups, and controls the **Pump Relay, Green/Red LEDs, and Buzzer** via an anti-RMW shadow register (`PORTC_IMG`).
5. **Internal Data EEPROM (`0x00`):** Persists the adjustable moisture threshold (`15%–85%`, default `40%`, step `5%`) across power cycles and resets.

### 5.8.2. System Block Diagram and Pin Assignment (40-Pin PDIP)

```text
  [Soil Moisture Sensor (0..5V)] ──► [RA0/AN0 (ADC)]
                                           │
  [SW1 MODE (RB0/INT), SW2 +5%/PUMP (RB1), SW3 -5% (RB2)]
                                           ▼
                       [ PIC16F877A @ 4 MHz | Timer1 100ms | EEPROM 256B ]
                           │                                       │
                           ▼                                       ▼
            PORTD (RD2-RD7): LCD 16x2 4-bit          PORTC: RC0 Pump Relay (2N2222+1N4007)
            Line 1: MOIST:35% TH:40%                        RC1 Green LED | RC2 Red LED
            Line 2: AUTO   PUMP:ON                          RC3 Buzzer Alarm (< 20%)
```

| PIC16F877A Pin | Hardware Connection | `TRIS` Direction | Special Configuration |
| :--- | :--- | :---: | :--- |
| `RA0/AN0` (Pin 2) | Soil Moisture Sensor (`0V=0%`, `5V=100%`) | Input (`1`) | `ADCON1 = 0x0E` (`AN0` Analog, left-justified) |
| `RB0/INT` (Pin 33) | Push-button `SW1` (**MODE**: AUTO ↔ MANUAL) | Input (`1`) | `OPTION_REG = 0x00` (pull-up ON, falling edge) |
| `RB1` (Pin 34) | Push-button `SW2` (**+5% TH** in AUTO / **Pump Toggle** in MANUAL) | Input (`1`) | Internal pull-up + `50 ms` software debounce |
| `RB2` (Pin 35) | Push-button `SW3` (**-5% TH** in AUTO) | Input (`1`) | Internal pull-up + auto-save to EEPROM |
| `RC0` (Pin 15) | **Pump Relay Driver** (`1kΩ → 2N2222 → 5V Relay + 1N4007 → Motor`) | Output (`0`) | `1 = PUMP ON`, `0 = PUMP OFF` |
| `RC1`, `RC2` (Pin 16–17) | **Green LED** (Moist/OK) & **Red LED** (Irrigating) | Output (`0`) | `330 Ω` resistors; updated via `PORTC_IMG` |
| `RC3` (Pin 18) | **5V Active Buzzer** (Critical Dryness Alarm) | Output (`0`) | Activated when `MOIST_PCT < 20%` |
| `RD2`, `RD3` (Pin 21–22) | **LCD 16×2** `RS`, `EN` (`RW` tied to GND) | Output (`0`) | 4-bit HD44780 interface |
| `RD4–RD7` (Pin 27–30) | **LCD 16×2** Data Bus `D4–D7` | Output (`0`) | High nibble first, low nibble second |
| `OSC1/OSC2` (Pin 13–14) | `4 MHz` Crystal + `2 × 22 pF` caps | Clock | `__CONFIG = 0x3F31` (`_XT_OSC`, `_LVP_OFF`) |

### 5.8.3. Engineering Calculations (Timer1, ADC Scaling, and Hysteresis)
1. **Timer1 `100 ms` Preload @ `4 MHz`:** $F_{\text{CY}} = 1\text{ MHz}$, Prescaler `1:8` → `125 kHz` (`8 µs`/tick) → `12,500` counts for `100 ms` → preload $= 65,536 - 12,500 = 53,036 = \text{0xCF2C}$. Dividing by `SAMPLE_TICKS = 5` yields an exact `0.5 s` sampling period.
2. **Software 8×8 Multiplication (`CALC_MOISTURE_PCT`):** Since PIC16F877A has no hardware multiplier, an 8-iteration shift-and-add loop computes $\text{MOIST\_PCT} = \lfloor (\text{ADC\_RAW} \times 100) / 256 \rfloor$ by taking the upper byte `MUL_H`, verified across all 256 ADC values (`0..255 → 0..99%`).
3. **10% Hysteresis Control (`CONTROL_IRRIGATION`):** Using `SUBWF` (inverted borrow `C`): turns Pump **ON** when `MOIST_PCT < THRESH_PCT` (`C = 0`), turns Pump **OFF** only when `MOIST_PCT ≥ THRESH_PCT + 10%` (`C = 1`), and holds state inside `[THRESH_PCT, THRESH_PCT + 10%)`.

### 5.8.4. System Flowchart
```text
[RESET 0x0000] -> [Init Bank 1: OPTION_REG, ADCON1=0x0E, TRISx, TMR1IE]
               -> [Init Bank 0: ADCON0=0x41, EEPROM_LOAD_THRESH, LCD_INIT, TMR1=0xCF2C, Enable GIE/PEIE/INTE]
                       │
                       ▼
┌────────────► [Poll Buttons RB1 (+5% / Manual Pump Toggle) & RB2 (-5% & Save EEPROM)]
│                      │
│                      ▼
│              [F_SAMPLE == 1 (set every 0.5 s by Timer1 ISR or RB0/INT)?] ──(No)──┐
│                      │ (Yes)                                                     │
│                      ▼                                                           │
│              [Clear F_SAMPLE -> Wait TACQ (25us) -> Read ADRESH -> CALC_MOISTURE_PCT]
│                      │                                                           │
│                      ▼                                                           │
│              [AUTO Mode?] ──(No / MANUAL)──► Keep user F_PUMP_ON state           │
│                 │ (Yes)                                                          │
│                 ├── MOIST < TH       ──► F_PUMP_ON = 1 (Pump ON)                 │
│                 ├── MOIST >= TH + 10 ──► F_PUMP_ON = 0 (Pump OFF)                │
│                 └── Deadband         ──► Retain previous Pump state              │
│                      │                                                           │
│                      ▼                                                           │
│              [UPDATE_OUTPUTS (via PORTC_IMG): RC0 Relay, RC1 Grn, RC2 Red, RC3 Buzzer (<20%)]
│                      │                                                           │
│                      ▼                                                           │
│              [UPDATE_LCD: L1 "MOIST:XX% TH:YY%", L2 "AUTO/MANUAL PUMP:ON/OFF"]   │
└──────────────────────────────────────────────────────────────────────────────────┘

[ISR 0x0004]: Context Save (W/STATUS/PCLATH -> Shared RAM 70h-72h via SWAPF)
  ├── TMR1IF==1: Clear TMR1IF, reload 0xCF2C, dec TICK_COUNT (5) -> set F_SAMPLE
  ├── INTF==1:   Clear INTF, toggle F_MANUAL (AUTO <-> MANUAL), set F_SAMPLE
  └── Context Restore -> RETFIE
```

### 5.8.5. Simulation Verification & Troubleshooting Summary
`[INSERT FIGURE: Proteus Circuit Schematic & Running Simulation Screenshots (TC01–TC06)]`
- **Stack Safety:** Worst-case call depth (`MAIN → UPDATE_LCD → LCD_PRINT_2DIG → LCD_DATA → LCD_NIBBLE_CMD + ISR`) = **5 / 8 hardware stack levels**.
- **Test Cases (`TC01–TC06`):** Verified startup default (`40%`), automatic pump activation (`<40%`), 10% hysteresis hold (`45%` stays ON, `52%` turns OFF), critical dryness buzzer (`<20%`), instant `RB0/INT` manual override, and EEPROM threshold persistence across `~MCLR` resets. *(Full matrix in `Test_Results.pdf`.)*

---

## 5.9. Comparison with ATmega32 (All 10 Mandatory Criteria)

| # | Criterion (Section 5.9) | **PIC16F877A** (`DS39582C`) | **ATmega32(L)** (`doc2503.pdf`) |
| :---: | :--- | :--- | :--- |
| 1 | **CPU Architecture** | 8-bit Harvard RISC, 2-stage pipeline; **single `W` accumulator**; **no hardware multiplier**; `1 TCY = 4 clocks` → max **5 MIPS @ 20 MHz** (`200 ns`); no internal CPU RC oscillator. | 8-bit Harvard Enhanced RISC, 2-stage pipeline; **32 general-purpose registers** wired to ALU; **2-cycle hardware multiplier (`MUL`)**; `1 clock/instruction` → max **16 MIPS @ 16 MHz** (`62.5 ns`); calibrated **internal RC (1/2/4/8 MHz)**. |
| 2 | **Register Organization** | Single `W` + **4 RAM Banks** (`STATUS<RP1:RP0>`); `STATUS` lacks signed flags (`N, V, S`) and uses **inverted Borrow (`C`)**; single 9-bit indirect pointer (`IRP:FSR`). | **32 registers (`R0–R31`)** (`R16–R31` support `LDI`), three 16-bit pointers (`X, Y, Z`) with auto-increment (`X+`); `SREG` includes full signed flags (`I, T, H, S, V, N, Z, C`) with standard borrow polarity. |
| 3 | **Program & Data Memory** | Flash **8K × 14-bit** (~14.3 KB, **4 Pages × 2K**, `PCLATH<4:3>`, `100K` E/W typ); SRAM **368 B** (4 Banks, 16B shared `70h–7Fh`); EEPROM **256 B** (`1M` E/W typ); **8-level Hardware Stack** (no `PUSH/POP`). | Flash **32 KB** (`16K × 16-bit`, linear, RWW Bootloader, `10K` E/W); SRAM **2 KB linear** (no banking); EEPROM **1 KB** (`100K` E/W); **SRAM Stack** (`SPH:SPL`, supports `PUSH/POP`). |
| 4 | **Instruction Set** | **35 instructions**, fixed **14-bit** word, 3 contiguous bit formats → simple to learn and ideal for building an assembler. | **131 instructions**, variable **16-bit / 32-bit**, non-contiguous operand bitfields (e.g., `LDI`: `1110 KKKK dddd KKKK`) → richer but more complex to encode. |
| 5 | **GPIO** | **33 pins** (5 Ports `A–E`); 2 regs/port (`TRISx`: **`1`=In, `0`=Out**; `PORTx`); prone to **RMW**; pull-ups only on `PORTB`; reset traps: `PORTA/E` Analog (`ADCON1`), `RA4` open-drain, `RB3` LVP. | **32 pins** (4 Ports `A–D`); 3 regs/port (`DDRx`: **`1`=Out, `0`=In**; `PORTx`; `PINx`); **immune to output RMW**; per-pin pull-ups on all ports; reset trap: `PC2–PC5` default JTAG (`JTAGEN`). |
| 6 | **Timers** | 3 Timers (`TMR0` 8b shares prescaler with WDT, `TMR1` 16b async RTC, `TMR2` 8b with `PR2`); 2 CCP modules → **2 PWM channels (max 10-bit)**. | 3 Timers (`T0` 8b, `T1` 16b with Input Capture + Noise Canceler, `T2` 8b async RTC); **4 PWM channels**, up to **16-bit** on `T1`. |
| 7 | **Interrupts** | **15 sources** sharing **1 single vector (`0004h`)**; software flag polling, manual flag clearing, and manual `SWAPF` context saving into `70h–7Fh`. | **21 distinct vectors** (`$000–$028`), hardware priority; hardware auto-clears most flags; fast `PUSH/POP` context saving. |
| 8 | **ADC** | 10-bit, **8 single-ended channels**, no internal VREF, no differential gain, requires software `TACQ` wait; `ADRESH` (Bank 0) & `ADRESL` (Bank 1) in different banks. | 10-bit, 8 single-ended + **differential channels (1x/10x/200x gain)**, internal **2.56V VREF**, Auto-Trigger; `ADCL`/`ADCH` in same I/O space (read `ADCL` first). |
| 9 | **Serial Communication** | 1 USART (no hardware parity, 8-bit `SPBRG`) + **1 shared MSSP (SPI or I²C 7/10-bit, not simultaneous)**; adds **8-bit PSP** and **2 Comparators + CVREF**. | **3 independent simultaneous interfaces**: USART (hardware parity, 12-bit `UBRR`), SPI, TWI (I²C 7-bit); 1 Analog Comparator; no PSP. |
| 10 | **Assembly Programming Tools** | **MPLAB IDE v8.92 / MPLAB X (≤ v5.35) + MPASM**, open-source **`gputils` (`gpasm`)**; 2-pin **ICSP/ICD** (`PICkit`); `__CONFIG` embedded in `.asm`; Proteus & SimulIDE support. | **Microchip Studio (Atmel Studio) + AVRASM2**, open-source **`avra` / `avr-as`**; 6-pin **SPI ISP** or 4-pin **JTAG**; external **2 Fuse Bytes**; Proteus & SimulIDE support. |

---

## 5.10. References

1. Microchip Technology Inc., *PIC16F87XA Data Sheet: 28/40/44-Pin Enhanced Flash Microcontrollers*, Document **DS39582C**, Jan. 2013. (Cited figures/tables: Pin Diagrams p. 3, Figure 1-2 p. 7, Table 1-3 pp. 10–13, Figure 2-1 p. 15, Figure 2-3 p. 17, Table 2-1 pp. 19–21, Figure 2-5 p. 30, Figure 2-6 p. 31, Figures 11-1/11-4 pp. 129/132, Figures 14-1/14-5/14-10 pp. 145/148/153, Figure 15-1 p. 159, Table 15-2 p. 160).
2. Microchip Technology Inc., *PICmicro™ Mid-Range MCU Family Reference Manual*, Document **DS33023A**, Dec. 1997.
3. Atmel Corporation / Microchip Technology Inc., *ATmega32 / ATmega32L 8-bit AVR Microcontroller Data Sheet*, Document **2503Q–AVR–02/11**, Feb. 2011.
4. Microchip Technology Inc., *MPASM™ Assembler, MPLINK™ Object Linker, MPLIB™ Object Librarian User's Guide*, Document **DS33014L**, 2013.
5. GNU PIC Utilities (`gputils`), *gpasm / gplink / gpdasm Documentation*, https://gputils.sourceforge.io/.
6. M. A. Mazidi, R. D. McKinlay, and D. Causey, *PIC Microcontroller and Embedded Systems*, Pearson Education, 2008.
7. Labcenter Electronics, *Proteus VSM Microcontroller Support*, https://www.labcenter.com/microprocessors/.
