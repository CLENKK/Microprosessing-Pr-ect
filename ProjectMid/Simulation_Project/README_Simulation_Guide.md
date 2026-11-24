# CIRCUIT DESIGN & SIMULATION GUIDE (PROTEUS / SIMULIDE) — TOPIC #15: SMART IRRIGATION CONTROLLER (COMPONENT 5)

This guide provides the complete Bill of Materials (BOM), pin-by-pin schematic netlist, MCU property settings, and test procedure to simulate the **Smart Irrigation Controller** using the compiled firmware: **`smart_irrigation.hex`** (`417` words, `__CONFIG = 0x3F31`).

---

## 1. Bill of Materials (Standard Proteus ISIS Component Names)

| # | RefDes | Proteus Component Name | Value / Specification | Function |
| :---: | :---: | :--- | :--- | :--- |
| 1 | `U1` | `PIC16F877A` | 40-pin PDIP, `Clock = 4MHz` | Main Microcontroller |
| 2 | `LCD1` | `LM016L` | 16×2 Character LCD (HD44780) | Displays moisture, threshold, mode, and pump state |
| 3 | `RV1` | `POT-HG` | `10 kΩ` (across `+5V` and `GND`) | Simulates analog soil moisture sensor (`0%–100%`) |
| 4 | `X1`, `C1–C2` | `CRYSTAL`, `CAP` | `4 MHz`, `2 × 22 pF` | External crystal oscillator (`_XT_OSC`) |
| 5 | `R1`, `SW_RST` | `RES`, `BUTTON` | `10 kΩ`, tactile switch | Active-low `~MCLR` Reset circuit |
| 6 | `SW1–SW3` | `BUTTON` | 3 switches to `GND` | `MODE (RB0)`, `+5%/PUMP (RB1)`, `-5% (RB2)` |
| 7 | `Q1`, `R2` | `2N2222`, `RES` | NPN transistor, `1 kΩ` | Low-side relay coil driver |
| 8 | `RL1`, `D1` | `RELAY`, `1N4007` | 5V SPDT Relay + flyback diode | Switches power to the water pump motor |
| 9 | `M1` | `MOTOR` (DC Motor) | `5V` or `12V DC` | Simulates irrigation water pump |
| 10 | `LED_G`, `LED_R`, `R3–R4` | `LED-GREEN`, `LED-RED`, `RES` | `2 × 330 Ω` | Normal (Green) and Irrigating (Red) indicators |
| 11 | `BUZ1` | `BUZZER` (Active 5V) | `5V` | Critical dryness alarm (`< 20%`) |
| 12 | `POWER`, `GROUND` | `POWER (+5V)`, `GROUND` | `+5V DC` | System power rails |

---

## 2. Schematic Wiring Table (Pin-to-Pin Netlist)

| Functional Block | PIC16F877A Pin | Connection Details |
| :--- | :--- | :--- |
| **Reset** | Pin 1 (`~MCLR/VPP`) | Pull up via `R1 (10 kΩ)` to `+5V`; connect `SW_RST` to `GND` |
| **Power** | Pins 11, 32 (`VDD`) / 12, 31 (`VSS`) | `+5V` / `GND` (hidden automatically in Proteus; add `0.1 µF` bypass caps for PCB) |
| **Oscillator** | Pin 13 (`OSC1`), Pin 14 (`OSC2`) | `4 MHz` crystal across pins; `22 pF` capacitor from each pin to `GND` |
| **Moisture Sensor** | Pin 2 (`RA0/AN0`) | Wiper of `POT-HG (RV1)` (`0% = 0V = 0% dry`, `100% = 5V = 99% wet`) |
| **Buttons** | Pin 33 (`RB0/INT`) | `SW1 (MODE: AUTO ↔ MANUAL)` to `GND` *(uses internal `PORTB` pull-ups)* |
| **Buttons** | Pin 34 (`RB1`) | `SW2 (+5% TH / MANUAL PUMP TOGGLE)` to `GND` |
| **Buttons** | Pin 35 (`RB2`) | `SW3 (-5% TH)` to `GND` |
| **Pump Relay** | Pin 15 (`RC0`) | Via `R2 (1 kΩ)` to Base of `Q1 (2N2222)`; Emitter to `GND`; Collector to `RL1` coil (other coil end to `+5V`, `1N4007` cathode to `+5V`); relay NO contact powers `MOTOR (M1)` |
| **Green LED** | Pin 16 (`RC1`) | Via `R3 (330 Ω)` → Anode of `LED_G` → Cathode to `GND` |
| **Red LED** | Pin 17 (`RC2`) | Via `R4 (330 Ω)` → Anode of `LED_R` → Cathode to `GND` |
| **Buzzer Alarm** | Pin 18 (`RC3`) | `+` terminal of `BUZZER (5V)` → `-` terminal to `GND` |
| **LCD 16×2** | Pin 21 (`RD2`) → `RS` (LCD Pin 4) | Tie LCD `VSS` (Pin 1) & `RW` (Pin 5) to `GND`; `VDD` (Pin 2) to `+5V`; `VEE` (Pin 3) to `GND` |
| **LCD 16×2** | Pin 22 (`RD3`) → `E` (LCD Pin 6) | Leave LCD `D0–D3` (Pins 7–10) unconnected |
| **LCD 16×2** | Pins 27–30 (`RD4–RD7`) | Connect directly to LCD `D4, D5, D6, D7` (LCD Pins 11–14) |

---

## 3. Proteus IC Configuration Checklist
1. Double-click `PIC16F877A` on the schematic:
   - **Program File:** Select `smart_irrigation.hex`
   - **Processor Clock Frequency:** Set to exactly **`4MHz`**
   - **Configuration Word:** Leave default (auto-loaded as `0x3F31` from `:02400E00313F40`)
2. Click **OK** → click **Play (Run Simulation)** and verify `TC01–TC06` below.

---

## 4. Verification Test Procedure (3-Minute Live Demo)

1. **TC01 – Power-On Default:** Set `RV1 = 50%` (`2.5V`), run simulation → LCD shows `MOIST:50% TH:40%` / `AUTO   PUMP:OFF`; Green LED ON, Motor stopped.
2. **TC02 – Automatic Irrigation ON:** Lower `RV1` to `35%` (`< 40%`) → Within `0.5 s`, LCD updates to `AUTO   PUMP:ON`, Relay closes, Motor spins, Red LED ON, Green LED OFF.
3. **TC03 – 10% Hysteresis Verification:** Raise `RV1` to `45%` (`> 40%` but `< 50%`) → **Motor remains ON** (no relay chatter). Raise to `52%` (`≥ 50%`) → Motor stops, Green LED turns ON.
4. **TC04 – Critical Dryness Alarm:** Lower `RV1` to `15%` (`< 20%`) → Pump ON, Red LED ON, and **Buzzer (`RC3`) sounds**.
5. **TC05 – External Interrupt Manual Override:** Press `SW1 (RB0/INT)` → LCD immediately switches to `MANUAL PUMP:...`; press `SW2 (RB1)` to force pump ON/OFF manually. Press `SW1` again to return to `AUTO`.
6. **TC06 – EEPROM Persistence Across Reset:** In `AUTO` mode, press `SW2` twice to raise threshold from `40%` to `50%` → press `SW_RST` (`~MCLR`) → after reboot, LCD retains `TH:50%` loaded from internal EEPROM (`0x00`).
