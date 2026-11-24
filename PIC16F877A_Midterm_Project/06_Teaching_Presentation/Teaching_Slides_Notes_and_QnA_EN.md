# TEACHING SLIDES SCRIPT, ORAL EXAM Q&A BANK & MASTER REFERENCES (ENGLISH)
**Covers:** Component 6 (`Teaching_Slides.pdf`, 18 slides / 28 min), Oral Examination Q&A (5 marks), and Component 7 (`References.pdf`).

---

## PART A: 18-SLIDE PRESENTATION SCHEDULE (28 MINUTES TOTAL)

| Slide | Slide Title | Key Talking Points | Speaker & Time |
| :---: | :--- | :--- | :---: |
| 1 | Title Slide | PIC16F877A Study, Machine-Code Translation & Topic #15 Smart Irrigation Controller; Group Roles | Student 1 (0.5m) |
| 2 | Introduction & Key Specifications | Microchip Mid-Range 8-bit, 35 14-bit instructions, 5 MIPS @ 20 MHz, 4 selection reasons | Student 1 (1.0m) |
| 3 | Harvard CPU Architecture & Q1–Q4 Pipeline | 14-bit Program Bus vs 8-bit Data Bus, `W` register, `STATUS`, 1 vs 2 TCY execution | Student 1 (1.5m) |
| 4 | Memory Organization & 8-Level Hardware Stack | 8K Flash (4 Pages), 368B SRAM (4 Banks + Shared `70h–7Fh`), 256B EEPROM, circular Stack | Student 1 (1.5m) |
| 5 | 40-Pin PDIP Pinout & Critical GPIO Pitfalls | 33 I/O, `TRISx` (`1=In,0=Out`), 4 pitfalls: `ADCON1`, `RA4` open-drain, `_LVP_OFF`, RMW | Student 1 (1.0m) |
| 6 | 35-Instruction Set & Addressing Modes | Byte/Bit/Literal categories; Direct, Indirect (`FSR`/`INDF`), Immediate, Branch modes | Student 1 (1.0m) |
| 7 | Core Peripherals: Timers & Single-Vector Interrupts | TMR0/1/2 comparison; 15 interrupt sources on `0004h`, `SWAPF` context saving | Student 1 (1.0m) |
| 8 | Core Peripherals: 10-bit ADC, Serial & PWM | ADC `TACQ` & `ADFM`, USART `SPBRG`, MSSP (SPI/I²C), CCP 10-bit PWM | Student 1 (0.5m) |
| 9 | 14-Bit Machine-Code Encoding & Intel HEX | 3 formats, 5 worked hand-encoding examples, Little-Endian `2×Addr` Intel HEX rule | Student 2 (2.0m) |
| 10 | Assembly Programming Environment | MPASM / `gpasm` / Mini Assembler, key directives, `.asm → .hex/.lst` flow | Student 2 (1.0m) |
| 11 | Application Firmware Walkthrough (`smart_irrigation.asm`) | Dual-source ISR (`TMR1IF` + `INTF`), 8×8 scaling, 10% hysteresis using inverted `C` | Student 2 (2.0m) |
| 12 | Topic #15: Smart Irrigation Overview & Block Diagram | Objectives, 5 hardware peripherals used, block diagram & pinout summary | Student 3 (2.0m) |
| 13 | Circuit Schematic & Proteus Configuration | Power/clock/reset, `POT-HG` sensor, `2N2222+1N4007` relay driver, `LM016L` 4-bit LCD | Student 3 (2.0m) |
| 14 | Python GUI Mini Assembler — Live Demo | 5 modules, 35/35 instructions, 2-pass labels, live demo & error handling | Student 2 (3.0m) |
| 15 | Proteus Simulation & Testing — Live Demo | Live walkthrough of `TC01–TC06` (Auto, Hysteresis, Alarm, Manual `INT0`, EEPROM) | Student 3 (3.0m) |
| 16 | PIC16F877A vs. ATmega32 (Hardware Comparison) | All 10 mandatory Section 5.9 criteria compared side-by-side | Student 1 (1.0m) |
| 17 | PIC16F877A vs. ATmega32 (Assembly Code Comparison) | Side-by-side GPIO banking & unsigned comparison (inverted `C` vs standard `C`) | Student 2 (1.0m) |
| 18 | Conclusions, References & Q&A | Key takeaways, primary datasheets, open floor for 5-minute Q&A | All (5.0m Q&A) |

---

## PART B: ORAL EXAMINATION Q&A BANK (15 HIGH-PROBABILITY QUESTIONS)

1. **Q:** *Why does PIC16F877A achieve only 5 MIPS at 20 MHz, whereas ATmega32 achieves 16 MIPS at 16 MHz?*  
   **A:** Each PIC16 instruction cycle takes **4 oscillator clocks (`Q1–Q4`, `TCY = 4/FOSC = 200 ns` @ 20 MHz → 5 MIPS)**, while AVR executes most instructions in **1 clock cycle** (`62.5 ns` @ 16 MHz → 16 MIPS).
2. **Q:** *Why is PIC16F877A RAM split into 4 Banks, and which bits select the active bank?*  
   **A:** Direct-address instructions only provide **7 address bits (`00h–7Fh` = 128 bytes)**. Combining them with `RP1:RP0` (`STATUS<6:5>`) creates a 9-bit address spanning 4 Banks (`000h–1FFh`).
3. **Q:** *Why do digital reads on `PORTA` return `0` immediately after reset?*  
   **A:** On Power-on Reset, pins multiplexed with ADC (`RA0–RA3`, `RA5`, `RE0–RE2`) default to **Analog Input** mode (`DS39582C`, pp. 41, 128). You must configure `ADCON1` (`0x06` for all digital, or `0x0E` for `AN0` analog only).
4. **Q:** *Why must the ISR save `STATUS` using `SWAPF STATUS, W` instead of `MOVF STATUS, W`?*  
   **A:** `MOVF` modifies the `Z` flag in `STATUS`, corrupting the main program's zero flag before it is saved. `SWAPF` affects **no status flags** (`Table 15-2`, p. 160).
5. **Q:** *Why are `W_TEMP` and `STATUS_TEMP` placed at `0x70–0x7F`?*  
   **A:** An interrupt can occur in any RAM Bank. `0x70–0x7F` is **Shared RAM** mirrored across all 4 Banks (`F0h–FFh`, `170h–17Fh`, `1F0h–1FFh`), allowing `MOVWF W_TEMP` to execute safely before switching banks.
6. **Q:** *What is the Read-Modify-Write (RMW) issue on PIC16 GPIO, and how did our firmware prevent it?*  
   **A:** `BSF`/`BCF PORTC` reads actual pin voltages (Q2), modifies 1 bit, and writes all 8 bits back (Q4); capacitive loads can flip adjacent outputs. Our `UPDATE_OUTPUTS` routine composes all bits in a RAM shadow register (`PORTC_IMG`) and writes `PORTC` atomically via `MOVWF PORTC`.
7. **Q:** *How does the Carry/Borrow flag `C` behave during `SUBWF f, W`?*  
   **A:** PIC performs 2's complement addition, so `C` is **inverted for borrow**: `C = 1` means **no borrow (`f ≥ W`)**, and `C = 0` means **borrow (`f < W`)** — opposite of ATmega32.
8. **Q:** *What happens if a PIC16F877A program nests 9 `CALL` levels?*  
   **A:** The 8-level Hardware Stack is a **circular buffer with no overflow flag** (`DS39582C`, p. 30). The 9th push silently overwrites Level 1, corrupting the return path. Our firmware's worst-case nesting (including ISR) is strictly **5 / 8 levels**.
9. **Q:** *Why did we include `_LVP_OFF` in `__CONFIG` (`0x3F31`)?*  
   **A:** Low-Voltage Programming (`LVP = 1` by default) dedicates `RB3/PGM` to programming mode; floating `RB3` high can halt execution. `_LVP_OFF` frees `RB3` and stabilizes normal operation.
10. **Q:** *Why did our Smart Irrigation firmware choose left-justified ADC (`ADFM = 0`)?*  
    **A:** With `ADFM = 0`, the 8 MSBs (`0..255`) reside directly in `ADRESH` (Bank 0), eliminating a bank switch to `ADRESL` (Bank 1) and simplifying 8-bit `0–99%` scaling and threshold comparison.
11. **Q:** *Why does `CLRF TRISB` (`0x86`) produce the exact same 14-bit opcode (`0x0186`) as `CLRF PORTB` (`0x06`)?*  
    **A:** Only the lower 7 bits (`0x86 & 0x7F = 0x06`) fit in field `f`. Which physical register is cleared depends on `STATUS<RP1:RP0>` at execution time.
12. **Q:** *Why are Intel HEX byte addresses double the PIC word addresses, and why are bytes reversed?*  
    **A:** Intel HEX addresses 8-bit bytes while PIC instructions are 14-bit words (2 bytes/word), so `Byte_Addr = 2 × Word_Addr`. Microchip stores words in **Little-Endian** order (low byte first).
13. **Q:** *How does our Python Mini Assembler resolve forward `GOTO`/`CALL` labels?*  
    **A:** Via a **2-Pass architecture**: Pass 1 builds the complete Symbol Table (`label → word address`); Pass 2 encodes instructions using the resolved addresses.
14. **Q:** *How does the 10% hysteresis prevent relay damage in Smart Irrigation?*  
    **A:** In AUTO mode, the pump starts at `< THRESH_PCT` (e.g., `< 40%`) and only stops at `≥ THRESH_PCT + 10%` (`≥ 50%`), eliminating rapid ON/OFF chatter when soil moisture hovers near the setpoint.
15. **Q:** *If asked to modify the default threshold from 40% to 50% or add an instruction to the Mini Assembler during Q&A, where do you edit?*  
    **A:** Change `DEFAULT_THRESH EQU 0x32` (50 decimal) in `smart_irrigation.asm` and re-assemble `.hex`; in Python, add one dictionary entry in `instruction_set.py` (all 35 PIC16 instructions are already supported!).

---

## PART C: REFERENCES & TECHNICAL FIGURE CITATION INDEX (`References.pdf`)

### C.1. Academic References (IEEE Format)
1. Microchip Technology Inc., *"PIC16F87XA Data Sheet: 28/40/44-Pin Enhanced Flash Microcontrollers,"* Literature Number **DS39582C**, Jan. 2013. [Online]. Available: https://www.microchip.com/
2. Microchip Technology Inc., *"PICmicro™ Mid-Range MCU Family Reference Manual,"* Literature Number **DS33023A**, Dec. 1997. [Online]. Available: https://www.microchip.com/
3. Atmel Corporation / Microchip Technology Inc., *"ATmega32 / ATmega32L 8-bit AVR Microcontroller with 32K Bytes In-System Programmable Flash Data Sheet,"* Document **2503Q–AVR–02/11**, Feb. 2011. [Online]. Available: https://ww1.microchip.com/downloads/en/DeviceDoc/doc2503.pdf
4. Microchip Technology Inc., *"MPASM™ Assembler, MPLINK™ Object Linker, MPLIB™ Object Librarian User's Guide,"* Literature Number **DS33014L**, 2013.
5. GNU PIC Utilities (`gputils`), *"gpasm, gplink, and gpdasm User Documentation,"* Open-Source Project. [Online]. Available: https://gputils.sourceforge.io/
6. Labcenter Electronics, *"Proteus VSM – PIC16 Microcontroller Simulation Support."* [Online]. Available: https://www.labcenter.com/microprocessors/
7. SimulIDE, *"Supported Microcontrollers Documentation."* [Online]. Available: https://simulide.com/p/mcus/
8. M. A. Mazidi, R. D. McKinlay, and D. Causey, *PIC Microcontroller and Embedded Systems: Using Assembly and C*, Pearson Prentice Hall, 2008.
9. Python Software Foundation, *"Python 3 Documentation — `tkinter` Graphical User Interfaces with Tk."* [Online]. Available: https://docs.python.org/3/library/tkinter.html

### C.2. Technical Figure & Table Citation Index (Section 5.10)

| Figure / Table Referenced in Study Document & Slides | Primary Official Source | Original Figure / Table & Page |
| :--- | :--- | :--- |
| PIC16F877A 40-Pin PDIP Pinout Diagram & Description | `PIC16F87XA Data Sheet (DS39582C)` | Pin Diagrams, p. 3; Table 1-3, pp. 10–13 |
| PIC16F874A/877A CPU Architecture Block Diagram | `PIC16F87XA Data Sheet (DS39582C)` | Figure 1-2, p. 7 |
| Program Memory Map (8K × 14-bit) & 8-Level Stack | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-1, p. 15 |
| Data Memory 4-Bank Register File Map & SFR Summary | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-3, p. 17; Table 2-1, pp. 19–21 |
| PC Loading (`PCL`/`PCLATH`) & Direct/Indirect Addressing | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-5, p. 30; Figure 2-6, p. 31 |
| Timer0 / Timer1 / Timer2 / PWM Block Diagrams | `PIC16F87XA Data Sheet (DS39582C)` | Figure 5-1 (p. 53), 6-2 (p. 58), 7-1 (p. 61), 8-3 (p. 67) |
| 10-bit A/D Block Diagram & Result Justification | `PIC16F87XA Data Sheet (DS39582C)` | Figure 11-1, p. 129; Figure 11-4, p. 132 |
| Crystal Oscillator, `~MCLR` Reset & Interrupt Logic | `PIC16F87XA Data Sheet (DS39582C)` | Figure 14-1 (p. 145), 14-5 (p. 148), 14-10 (p. 153) |
| 14-bit Instruction Formats & 35-Instruction Opcode Table | `PIC16F87XA Data Sheet (DS39582C)` | Figure 15-1, p. 159; Table 15-2, p. 160 |
| `Q1–Q4` Clock Cycle Timing (`TCY = 4/FOSC`) | `PIC16F87XA Data Sheet (DS39582C)` | Figure 17-4, p. 182 |
| ATmega32 Comparison Architecture, SREG, Memory & Vectors | `ATmega32(L) Data Sheet (2503Q–AVR–02/11)` | Block Diagram p. 5; SREG p. 10; Memory pp. 16–18; Vectors p. 45 |
