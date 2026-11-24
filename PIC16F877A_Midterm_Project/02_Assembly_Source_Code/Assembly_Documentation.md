# ASSEMBLY LANGUAGE PROGRAMMING DOCUMENTATION — TOPIC #15: SMART IRRIGATION CONTROLLER (COMPONENT 2)

- **Source File:** `smart_irrigation.asm`
- **Compiled Firmware:** `smart_irrigation.hex` (Standard Intel HEX `INHX32M`, `__CONFIG = 0x3F31`)
- **Listing File:** `smart_irrigation.lst` (**417 instruction words**, addresses `0x0000 – 0x01A3`, fits entirely within Page 0)
- **Target MCU & Clock:** Microchip `PIC16F877A` (40-Pin PDIP) @ `FOSC = 4 MHz` (`1 TCY = 1 µs`)

---

## 1. MCU Initialization and Register Configuration (`MAIN`)

| Step | Register & Bank | Value Written | Technical Purpose |
| :---: | :--- | :---: | :--- |
| 1 | `__CONFIG` (`2007h`) | `0x3F31` | `_XT_OSC` (4 MHz), `_WDT_OFF`, `_PWRTE_ON`, `_BODEN_OFF`, `_LVP_OFF` (frees `RB3`), `_CP_OFF`. |
| 2 | `OPTION_REG` (Bank 1, `81h`) | `0x00` | `RBPU = 0` enables internal `PORTB` weak pull-ups for 3 buttons; `INTEDG = 0` sets `RB0/INT` to falling-edge trigger. |
| 3 | `ADCON1` (Bank 1, `9Fh`) | `0x0E` | `ADFM = 0` (left-justified 8-bit in `ADRESH`, Bank 0), `PCFG = 1110` (`RA0/AN0` Analog only; `AN1–AN7` Digital). |
| 4 | `TRISA–TRISE` (Bank 1) | `01h, 07h, 00h, 00h, 00h` | `RA0` Input (ADC); `RB0–RB2` Input (Buttons); `PORTC` Output (Pump Relay, LEDs, Buzzer); `PORTD` Output (4-bit LCD). |
| 5 | `PIE1` (Bank 1, `8Ch`) | `TMR1IE = 1` | Enables Timer1 overflow peripheral interrupt. |
| 6 | `ADCON0` (Bank 0, `1Fh`) | `0x41` | Selects `FOSC/8` (`TAD = 2.0 µs ≥ 1.6 µs`), Channel `AN0 (000)`, powers on ADC (`ADON = 1`). |
| 7 | `T1CON`, `TMR1H:L` (Bank 0) | `0x31`, `0xCF2C` | `1:8` prescaler, internal `FOSC/4` clock, preload `53,036` → overflows every `100 ms`. |
| 8 | `INTCON` (`0Bh`) | `GIE=PEIE=INTE=1` | Enables global interrupts, peripheral interrupts (Timer1), and external `RB0/INT` interrupt. |

---

## 2. Interrupt Service Routine Explanation (`ISR` at `0x0004`)
1. **Bank-Safe Context Saving (`DS39582C` Example 14-1, p. 154):** Because PIC16F877A has no `PUSH`/`POP` instructions and all 15 interrupt sources share vector `0x0004`, `W_TEMP (0x70)`, `STATUS_TEMP (0x71)`, and `PCLATH_TEMP (0x72)` are placed in **Shared RAM (`0x70–0x7F`)**, which is mirrored across all 4 Banks. `SWAPF STATUS, W` is used instead of `MOVF` so the `Z` flag is preserved before saving.
2. **Dual-Source Flag Polling:**
   - **Source 1 (`PIR1.TMR1IF == 1`):** Clears `TMR1IF`, briefly stops Timer1 to reload `0xCF2C` cleanly, restarts Timer1, and decrements `TICK_COUNT` (from `5` to `0`). Every `500 ms` (`0.5 s`), it sets `SYS_FLAGS.F_SAMPLE` to notify the main loop without executing blocking delays inside the ISR.
   - **Source 2 (`INTCON.INTF == 1`):** Clears `INTF`, toggles `SYS_FLAGS.F_MANUAL` via `XORWF` (`AUTO ↔ MANUAL`), and sets `F_SAMPLE` for an immediate LCD update.
3. **Context Restoration:** Restores `PCLATH`, `STATUS` (via `SWAPF`), and `W` (using two `SWAPF` instructions to preserve `Z`), then exits via `RETFIE` (atomically re-enabling `GIE`).

---

## 3. Core Algorithms and Hardware Interaction

1. **Software 8×8 Moisture Scaling (`CALC_MOISTURE_PCT`):**
   - Because PIC16F877A lacks a hardware multiplier, an 8-bit shift-and-add routine multiplies `ADC_RAW (0..255)` by `100`. Reading the 16-bit product high byte `MUL_H` computes $\lfloor (\text{ADC\_RAW} \times 100) / 256 \rfloor$, accurately mapping `0..255` to `0..99%` (verified across all 256 inputs).
2. **10% Hysteresis Pump Control (`CONTROL_IRRIGATION`):**
   - Uses `SUBWF MOIST_PCT, W` with PIC's **inverted borrow flag (`C = 0` when `MOIST_PCT < THRESH_PCT`; `C = 1` when `MOIST_PCT ≥ STOP_THRESH`)**.
   - In **AUTO** mode, the pump turns **ON** when moisture falls below `THRESH_PCT` and turns **OFF** only after moisture reaches `THRESH_PCT + 10%`, preventing rapid relay chatter near the threshold.
3. **Anti-RMW Output Stage (`UPDATE_OUTPUTS`):**
   - All output indicators (`RC0` Pump Relay, `RC1` Green LED, `RC2` Red LED, `RC3` Buzzer when `< 20%`) are assembled in RAM shadow register `PORTC_IMG` and written atomically to `PORTC` via a single `MOVWF PORTC` instruction.
4. **EEPROM Threshold Persistence (`EEPROM_LOAD_THRESH` & `EEPROM_SAVE_THRESH`):**
   - Adjusting the threshold via `RB1` (`+5%`) or `RB2` (`-5%`) writes the new setting to internal EEPROM (`0x00`) using the mandatory `0x55 → EECON2`, `0xAA → EECON2`, `BSF EECON1, WR` unlock sequence with `GIE = 0`. On boot/reset, valid stored values (`15–85%`) are restored automatically; blank EEPROM (`0xFF`) safely defaults to `40%`.
5. **Hardware Stack Safety Verification:**
   - Maximum main-loop nesting: `MAIN_LOOP → UPDATE_LCD (1) → LCD_PRINT_2DIG (2) → LCD_DATA (3) → LCD_NIBBLE_CMD / DELAY_2MS (4)`. Adding an asynchronous interrupt yields **5 / 8 levels maximum**, leaving 3 levels of safety margin.
