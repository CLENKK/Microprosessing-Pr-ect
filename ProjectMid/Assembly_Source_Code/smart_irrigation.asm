; ============================================================================
; PROJECT:  TOPIC #15 — SMART IRRIGATION CONTROLLER (PIC16F877A)
; MCU:      Microchip PIC16F877A (40-Pin PDIP) @ Fosc = 4 MHz (1 TCY = 1 us)
; COMPILER: MPASM / gpasm / PIC16F877A Python Mini Assembler (100% Compatible)
;
; PERIPHERALS USED (5 Hardware Peripherals >= 3 Required):
;   1. ADC 10-bit (AN0/RA0, left-justified 8-bit) -> Soil Moisture Sensor
;   2. Timer1 (16-bit) + Interrupt (TMR1IF)       -> 100 ms tick / 0.5 s sampling
;   3. External Interrupt (RB0/INT, falling edge) -> Mode Switch (AUTO / MANUAL)
;   4. GPIO (PORTB, PORTC, PORTD)                 -> LCD 16x2 (4-bit), Buttons,
;                                                    Pump Relay, LEDs, Buzzer
;   5. Internal Data EEPROM (256B, addr 0x00)     -> Persist moisture threshold
;
; PIN ASSIGNMENT (40-Pin PDIP):
;   RA0/AN0 (Pin 2)  : Soil Moisture Analog Input (0V = 0% Dry, 5V = 100% Wet)
;   RB0/INT (Pin 33) : Mode Button (AUTO <-> MANUAL, active-low, internal pull-up)
;   RB1     (Pin 34) : Threshold +5% (AUTO) / Manual Pump ON-OFF Toggle (MANUAL)
;   RB2     (Pin 35) : Threshold -5% (AUTO)
;   RC0     (Pin 15) : Water Pump Relay Control (1 = PUMP ON, 0 = PUMP OFF)
;   RC1     (Pin 16) : Green LED (Normal / Soil Moist)
;   RC2     (Pin 17) : Red LED (Dry Soil / Pump Active)
;   RC3     (Pin 18) : Buzzer Alarm (Active when critically dry < 20%)
;   RD2     (Pin 21) : LCD RS
;   RD3     (Pin 22) : LCD EN (LCD RW tied to GND)
;   RD4-RD7 (27-30)  : LCD Data Bus D4-D7 (4-bit interface)
;   OSC1/2  (13-14)  : 4 MHz Crystal + 2x 22 pF capacitors
;   ~MCLR   (Pin 1)  : Reset RC circuit (10k pull-up + Reset button)
; ============================================================================

        LIST        P=16F877A
        #include    <p16f877a.inc>
        ERRORLEVEL  -302

        ; Configuration Word (0x2007): 4 MHz XT Osc, WDT OFF, PWRTE ON,
        ; BOR OFF, LVP OFF (frees RB3), Code Protect OFF -> 0x3F31
        __CONFIG    _CP_OFF & _DEBUG_OFF & _WRT_OFF & _CPD_OFF & _LVP_OFF & _BODEN_OFF & _PWRTE_ON & _WDT_OFF & _XT_OSC

; ============================================================================
; CONSTANTS & BIT DEFINITIONS
; ============================================================================
HYSTERESIS      EQU     0x0A        ; 10% hysteresis deadband to prevent relay chatter
MIN_THRESH      EQU     0x0F        ; Minimum threshold = 15%
MAX_THRESH      EQU     0x55        ; Maximum threshold = 85%
DEFAULT_THRESH  EQU     0x28        ; Default moisture threshold = 40%
CRIT_DRY_PCT    EQU     0x14        ; Critical dry alarm level = 20%
EEPROM_TH_ADDR  EQU     0x00        ; EEPROM address storing threshold

; Timer1 preload for exact 100 ms @ 4 MHz, Prescaler 1:8:
; Fcy = 1 MHz -> T1clk = 125 kHz -> 12,500 counts -> 65536 - 12500 = 53036 = 0xCF2C
TMR1H_PRELOAD   EQU     0xCF
TMR1L_PRELOAD   EQU     0x2C
SAMPLE_TICKS    EQU     0x05        ; 5 x 100 ms = 500 ms (0.5 s) sampling period

; Output bit positions on PORTC
PUMP_BIT        EQU     0           ; RC0: Pump Relay
LED_GRN_BIT     EQU     1           ; RC1: Green LED (OK)
LED_RED_BIT     EQU     2           ; RC2: Red LED (Irrigating)
BUZZER_BIT      EQU     3           ; RC3: Buzzer (Critical Dry)

; LCD control bits on PORTD
LCD_RS_BIT      EQU     2           ; RD2
LCD_EN_BIT      EQU     3           ; RD3

; System flag bits in SYS_FLAGS
F_SAMPLE        EQU     0           ; Bit 0: 1 = 0.5 s elapsed, sample ADC now
F_MANUAL        EQU     1           ; Bit 1: 0 = AUTO mode, 1 = MANUAL mode
F_PUMP_ON       EQU     2           ; Bit 2: Current pump state (0 = OFF, 1 = ON)
F_MODE_CHG      EQU     3           ; Bit 3: Mode changed via RB0/INT (debounce)

; ============================================================================
; RAM VARIABLES (Bank 0: 0x20-0x6F, Shared RAM: 0x70-0x7F)
; ============================================================================
        CBLOCK  0x20
            SYS_FLAGS               ; System status flags
            TICK_COUNT              ; 100 ms tick divider (counts down from 5)
            ADC_RAW                 ; 8-bit ADC reading (0..255 from ADRESH)
            MOIST_PCT               ; Scaled Soil Moisture Percentage (0..99%)
            THRESH_PCT              ; Irrigation Start Threshold (15..85%)
            STOP_THRESH             ; Irrigation Stop Threshold (THRESH_PCT + 10%)
            MUL_A                   ; Multiplier operand A (ADC_RAW)
            MUL_B                   ; Multiplier operand B (100)
            MUL_H                   ; 16-bit product high byte (= (A*B)/256)
            MUL_L                   ; 16-bit product low byte
            BIT_CNT                 ; Loop counter for 8x8 multiplication
            BCD_TENS                ; Tens digit for LCD display
            BCD_ONES                ; Ones digit for LCD display
            LCD_TEMP                ; Temporary byte for LCD 4-bit send
            STR_IDX                 ; String table index
            DLY_1                   ; Delay loop counter 1
            DLY_2                   ; Delay loop counter 2
            EE_VAL                  ; Temporary value for EEPROM write
            PORTC_IMG               ; Shadow register for PORTC (prevents RMW)
        ENDC

        ; Shared RAM (0x70-0x7F): Accessible from ALL 4 Banks for safe ISR context save
        CBLOCK  0x70
            W_TEMP
            STATUS_TEMP
            PCLATH_TEMP
        ENDC

; ============================================================================
; RESET & INTERRUPT VECTORS
; ============================================================================
        ORG     0x0000
        GOTO    MAIN                ; Jump to initialization routine

        ORG     0x0004
; ----------------------------------------------------------------------------
; INTERRUPT SERVICE ROUTINE (ISR) — Handles Timer1 (100ms) & RB0/INT (Mode)
; Context saving follows Microchip DS39582C Example 14-1 (p. 154)
; ----------------------------------------------------------------------------
ISR:
        MOVWF   W_TEMP              ; Save W into Shared RAM (bank-independent)
        SWAPF   STATUS, W           ; Swap STATUS into W without affecting Z flag
        CLRF    STATUS              ; Switch to Bank 0
        MOVWF   STATUS_TEMP         ; Save STATUS
        MOVF    PCLATH, W
        MOVWF   PCLATH_TEMP         ; Save PCLATH
        CLRF    PCLATH              ; Select Page 0

        ; --- Check Source 1: Timer1 Overflow Interrupt (100 ms) ---
        BTFSS   PIR1, TMR1IF
        GOTO    ISR_CHK_INT0

        BCF     PIR1, TMR1IF        ; Clear Timer1 interrupt flag in software
        BCF     T1CON, TMR1ON       ; Stop Timer1 briefly to reload cleanly
        MOVLW   TMR1H_PRELOAD
        MOVWF   TMR1H
        MOVLW   TMR1L_PRELOAD
        MOVWF   TMR1L
        BSF     T1CON, TMR1ON       ; Restart Timer1

        DECFSZ  TICK_COUNT, F       ; 5 ticks x 100 ms = 500 ms?
        GOTO    ISR_CHK_INT0
        MOVLW   SAMPLE_TICKS
        MOVWF   TICK_COUNT          ; Reload 5-tick divider
        BSF     SYS_FLAGS, F_SAMPLE ; Signal main loop to sample ADC & refresh LCD

        ; --- Check Source 2: External Interrupt RB0/INT (AUTO <-> MANUAL) ---
ISR_CHK_INT0:
        BTFSS   INTCON, INTF
        GOTO    ISR_EXIT

        BCF     INTCON, INTF        ; Clear External Interrupt flag
        MOVLW   0x02                ; Mask for F_MANUAL (bit 1)
        XORWF   SYS_FLAGS, F        ; Toggle AUTO (0) <-> MANUAL (1)
        BSF     SYS_FLAGS, F_MODE_CHG
        BSF     SYS_FLAGS, F_SAMPLE ; Trigger immediate LCD refresh

ISR_EXIT:
        MOVF    PCLATH_TEMP, W      ; Restore PCLATH
        MOVWF   PCLATH
        SWAPF   STATUS_TEMP, W      ; Restore original STATUS & Bank
        MOVWF   STATUS
        SWAPF   W_TEMP, F           ; Restore W without corrupting Z flag
        SWAPF   W_TEMP, W
        RETFIE                      ; Re-enable GIE and pop PC from Stack

; ============================================================================
; MAIN INITIALIZATION
; ============================================================================
MAIN:
        ; --- 1. Configure Bank 1 Registers (I/O, ADC Pin Config, Pull-ups, PIE1) ---
        BCF     STATUS, RP1
        BSF     STATUS, RP0         ; Select Bank 1

        ; OPTION_REG: RBPU=0 (Enable PORTB pull-ups), INTEDG=0 (Falling edge RB0/INT)
        MOVLW   0x00
        MOVWF   OPTION_REG

        ; ADCON1: ADFM=0 (Left-justified 8-bit in ADRESH), ADCS2=0, PCFG=1110 (AN0 analog only)
        MOVLW   0x0E
        MOVWF   ADCON1

        ; Port Directions (1 = Input, 0 = Output)
        MOVLW   0x01                ; RA0/AN0 = Input, RA1-RA5 = Output
        MOVWF   TRISA
        MOVLW   0x07                ; RB0, RB1, RB2 = Input (Buttons), RB3-RB7 = Output
        MOVWF   TRISB
        CLRF    TRISC               ; RC0-RC7 = Output (Pump, LEDs, Buzzer)
        CLRF    TRISD               ; RD0-RD7 = Output (LCD 4-bit)
        CLRF    TRISE               ; RE0-RE2 = Output

        ; Enable Timer1 Peripheral Interrupt (PIE1.TMR1IE = 1)
        CLRF    PIE1
        BSF     PIE1, TMR1IE

        ; --- 2. Return to Bank 0 & Initialize Outputs and Peripherals ---
        BCF     STATUS, RP0         ; Select Bank 0
        CLRF    PORTA
        CLRF    PORTB
        CLRF    PORTC
        CLRF    PORTD
        CLRF    PORTC_IMG
        CLRF    SYS_FLAGS

        ; Initialize ADC (ADCON0): Fosc/8 (01), Channel AN0 (000), ADON=1 -> 0x41
        MOVLW   0x41
        MOVWF   ADCON0

        ; Load Saved Moisture Threshold from Internal EEPROM (address 0x00)
        CALL    EEPROM_LOAD_THRESH

        ; Initialize LCD 16x2 (4-bit mode)
        CALL    LCD_INIT

        ; Initialize Timer1: Prescaler 1:8 (11), Internal Clock Fosc/4, TMR1ON=1 -> 0x31
        MOVLW   TMR1H_PRELOAD
        MOVWF   TMR1H
        MOVLW   TMR1L_PRELOAD
        MOVWF   TMR1L
        MOVLW   SAMPLE_TICKS
        MOVWF   TICK_COUNT
        BCF     PIR1, TMR1IF
        MOVLW   0x31
        MOVWF   T1CON

        ; Enable Global, Peripheral, and RB0/INT Interrupts
        BCF     INTCON, INTF
        BSF     INTCON, INTE        ; Enable RB0/INT external interrupt
        BSF     INTCON, PEIE        ; Enable peripheral interrupts (Timer1)
        BSF     INTCON, GIE         ; Global Interrupt Enable

        ; Force first sample immediately on boot
        BSF     SYS_FLAGS, F_SAMPLE

; ============================================================================
; MAIN SUPER-LOOP
; ============================================================================
MAIN_LOOP:
        ; --- Handle Debounce if Mode Button Pressed ---
        BTFSS   SYS_FLAGS, F_MODE_CHG
        GOTO    CHK_BUTTONS
        CALL    DELAY_50MS          ; Software debounce for RB0/INT
        BCF     SYS_FLAGS, F_MODE_CHG

CHK_BUTTONS:
        ; --- Check RB1 Button (Active-Low) ---
        BTFSC   PORTB, 1            ; Pressed (0)?
        GOTO    CHK_BTN_DEC
        CALL    DELAY_50MS          ; Debounce
        BTFSC   PORTB, 1
        GOTO    CHK_BTN_DEC

        ; If MANUAL mode -> toggle Pump manually; if AUTO mode -> Threshold +5%
        BTFSC   SYS_FLAGS, F_MANUAL
        GOTO    MANUAL_TOGGLE_PUMP
        CALL    THRESH_INC_5
        GOTO    WAIT_BTN1_REL

MANUAL_TOGGLE_PUMP:
        MOVLW   0x04                ; Mask for F_PUMP_ON (bit 2)
        XORWF   SYS_FLAGS, F
        BSF     SYS_FLAGS, F_SAMPLE ; Refresh outputs & LCD immediately

WAIT_BTN1_REL:
        BTFSS   PORTB, 1            ; Wait until button released
        GOTO    WAIT_BTN1_REL
        CALL    DELAY_20MS

CHK_BTN_DEC:
        ; --- Check RB2 Button (Threshold -5% in AUTO mode, Active-Low) ---
        BTFSC   PORTB, 2
        GOTO    CHK_SAMPLE_FLAG
        CALL    DELAY_50MS
        BTFSC   PORTB, 2
        GOTO    CHK_SAMPLE_FLAG
        BTFSS   SYS_FLAGS, F_MANUAL ; Only adjust threshold in AUTO mode
        CALL    THRESH_DEC_5

WAIT_BTN2_REL:
        BTFSS   PORTB, 2
        GOTO    WAIT_BTN2_REL
        CALL    DELAY_20MS

CHK_SAMPLE_FLAG:
        ; --- Check 0.5 s Periodic Sampling Flag from Timer1 ISR ---
        BTFSS   SYS_FLAGS, F_SAMPLE
        GOTO    MAIN_LOOP
        BCF     SYS_FLAGS, F_SAMPLE

        ; 1. Read Soil Moisture via ADC and scale to 0..99%
        CALL    READ_ADC_AN0
        CALL    CALC_MOISTURE_PCT

        ; 2. Run Irrigation Control Logic (AUTO with hysteresis or MANUAL)
        CALL    CONTROL_IRRIGATION

        ; 3. Drive Relay, Green/Red LEDs, and Critical-Dry Buzzer
        CALL    UPDATE_OUTPUTS

        ; 4. Refresh LCD 16x2 Display
        CALL    UPDATE_LCD

        GOTO    MAIN_LOOP

; ============================================================================
; SUBROUTINE: READ_ADC_AN0
; Reads 8-bit left-justified ADC value from AN0 into ADC_RAW (DS39582C Sec. 11)
; ============================================================================
READ_ADC_AN0:
        CALL    DELAY_20US          ; Mandatory acquisition delay TACQ >= 19.72 us
        BSF     ADCON0, GO          ; Start A/D conversion (GO/DONE = 1)
ADC_WAIT:
        BTFSC   ADCON0, GO          ; Wait until GO/DONE clears automatically
        GOTO    ADC_WAIT
        MOVF    ADRESH, W           ; Read 8 MSbs (left-justified, Bank 0)
        MOVWF   ADC_RAW
        RETURN

; ============================================================================
; SUBROUTINE: CALC_MOISTURE_PCT
; Computes MOIST_PCT = (ADC_RAW * 100) / 256  (maps 0..255 -> 0..99%)
; Uses exact 8x8 unsigned shift-and-add multiplication (product high byte = /256)
; ============================================================================
CALC_MOISTURE_PCT:
        CLRF    MUL_H
        CLRF    MUL_L
        MOVF    ADC_RAW, W
        MOVWF   MUL_A
        MOVLW   d'100'
        MOVWF   MUL_B
        MOVLW   0x08
        MOVWF   BIT_CNT
MUL_LOOP:
        BCF     STATUS, C
        RRF     MUL_B, F            ; Shift multiplier LSB into Carry
        BTFSS   STATUS, C
        GOTO    MUL_SHIFT
        MOVF    MUL_A, W
        ADDWF   MUL_H, F            ; Add multiplicand to high byte
MUL_SHIFT:
        RRF     MUL_H, F            ; Shift 16-bit product right (preserves Carry)
        RRF     MUL_L, F
        DECFSZ  BIT_CNT, F
        GOTO    MUL_LOOP
        MOVF    MUL_H, W            ; High byte = (ADC_RAW * 100) >> 8
        MOVWF   MOIST_PCT
        RETURN

; ============================================================================
; SUBROUTINE: CONTROL_IRRIGATION
; AUTO Mode with 10% Hysteresis:
;   - If MOIST_PCT < THRESH_PCT        -> Turn Pump ON
;   - If MOIST_PCT >= THRESH_PCT + 10  -> Turn Pump OFF
;   - Otherwise                        -> Retain current state (anti-chatter)
; MANUAL Mode: Keep F_PUMP_ON controlled by RB1 button.
; ============================================================================
CONTROL_IRRIGATION:
        BTFSC   SYS_FLAGS, F_MANUAL
        RETURN                      ; Manual override active

        ; Test 1: Is MOIST_PCT < THRESH_PCT?
        ; SUBWF computes (MOIST_PCT - THRESH_PCT): C=0 means Borrow (MOIST < THRESH)
        MOVF    THRESH_PCT, W
        SUBWF   MOIST_PCT, W
        BTFSS   STATUS, C           ; Skip if MOIST_PCT >= THRESH_PCT
        GOTO    CTRL_PUMP_ON        ; C=0 -> Dry soil -> Start Irrigation

        ; Test 2: Is MOIST_PCT >= THRESH_PCT + HYSTERESIS?
        MOVF    THRESH_PCT, W
        ADDLW   HYSTERESIS
        MOVWF   STOP_THRESH
        MOVF    STOP_THRESH, W
        SUBWF   MOIST_PCT, W        ; W = MOIST_PCT - STOP_THRESH
        BTFSC   STATUS, C           ; C=1 -> MOIST_PCT >= STOP_THRESH
        GOTO    CTRL_PUMP_OFF       ; Soil sufficiently wet -> Stop Irrigation
        RETURN                      ; Inside deadband -> keep previous state

CTRL_PUMP_ON:
        BSF     SYS_FLAGS, F_PUMP_ON
        RETURN

CTRL_PUMP_OFF:
        BCF     SYS_FLAGS, F_PUMP_ON
        RETURN

; ============================================================================
; SUBROUTINE: UPDATE_OUTPUTS
; Uses shadow register PORTC_IMG to avoid PIC16 Read-Modify-Write (RMW) glitches
; ============================================================================
UPDATE_OUTPUTS:
        CLRF    PORTC_IMG
        BTFSS   SYS_FLAGS, F_PUMP_ON
        GOTO    OUT_PUMP_IS_OFF

        ; Pump ON: Activate Relay (RC0) and Red LED (RC2)
        BSF     PORTC_IMG, PUMP_BIT
        BSF     PORTC_IMG, LED_RED_BIT
        GOTO    OUT_CHK_ALARM

OUT_PUMP_IS_OFF:
        ; Pump OFF: Activate Green LED (RC1)
        BSF     PORTC_IMG, LED_GRN_BIT

OUT_CHK_ALARM:
        ; Sound Buzzer (RC3) if moisture < CRIT_DRY_PCT (20%)
        MOVLW   CRIT_DRY_PCT
        SUBWF   MOIST_PCT, W        ; C=0 if MOIST_PCT < 20%
        BTFSS   STATUS, C
        BSF     PORTC_IMG, BUZZER_BIT

        MOVF    PORTC_IMG, W
        MOVWF   PORTC               ; Atomic 8-bit write to PORTC
        RETURN

; ============================================================================
; THRESHOLD ADJUSTMENT & INTERNAL EEPROM PERSISTENCE (DS39582C Section 3.3-3.4)
; ============================================================================
THRESH_INC_5:
        MOVLW   MAX_THRESH
        SUBWF   THRESH_PCT, W       ; Already >= 85%?
        BTFSC   STATUS, C
        RETURN
        MOVLW   0x05
        ADDWF   THRESH_PCT, F
        CALL    EEPROM_SAVE_THRESH
        BSF     SYS_FLAGS, F_SAMPLE
        RETURN

THRESH_DEC_5:
        MOVLW   MIN_THRESH
        SUBWF   THRESH_PCT, W       ; Already <= 15%?
        BTFSS   STATUS, C
        RETURN
        BTFSC   STATUS, Z
        RETURN
        MOVLW   0x05
        SUBWF   THRESH_PCT, F
        CALL    EEPROM_SAVE_THRESH
        BSF     SYS_FLAGS, F_SAMPLE
        RETURN

EEPROM_LOAD_THRESH:
        ; Read byte from EEPROM address 0x00 (DS39582C Example 3-1, p. 35)
        BSF     STATUS, RP1
        BCF     STATUS, RP0         ; Bank 2
        MOVLW   EEPROM_TH_ADDR
        MOVWF   EEADR
        BSF     STATUS, RP0         ; Bank 3
        BCF     EECON1, EEPGD       ; Select Data EEPROM
        BSF     EECON1, RD          ; Start EEPROM read
        BCF     STATUS, RP0         ; Bank 2
        MOVF    EEDATA, W
        BCF     STATUS, RP1         ; Back to Bank 0
        MOVWF   THRESH_PCT

        ; Validate range (15..85); if unprogrammed (0xFF) or invalid -> default 40%
        MOVLW   MIN_THRESH
        SUBWF   THRESH_PCT, W
        BTFSS   STATUS, C
        GOTO    EE_USE_DEFAULT
        MOVLW   MAX_THRESH + 1
        SUBWF   THRESH_PCT, W
        BTFSC   STATUS, C
        GOTO    EE_USE_DEFAULT
        RETURN

EE_USE_DEFAULT:
        MOVLW   DEFAULT_THRESH
        MOVWF   THRESH_PCT
        RETURN

EEPROM_SAVE_THRESH:
        ; Write THRESH_PCT to EEPROM address 0x00 (DS39582C Example 3-2, p. 35)
        MOVF    THRESH_PCT, W
        MOVWF   EE_VAL
        BSF     STATUS, RP1
        BSF     STATUS, RP0         ; Bank 3
EE_WAIT_WR:
        BTFSC   EECON1, WR          ; Wait for any previous write to finish
        GOTO    EE_WAIT_WR
        BCF     STATUS, RP0         ; Bank 2
        MOVLW   EEPROM_TH_ADDR
        MOVWF   EEADR
        BCF     STATUS, RP1         ; Bank 0 (read EE_VAL)
        MOVF    EE_VAL, W
        BSF     STATUS, RP1         ; Bank 2
        MOVWF   EEDATA
        BSF     STATUS, RP0         ; Bank 3
        BCF     EECON1, EEPGD       ; Select Data EEPROM
        BSF     EECON1, WREN        ; Enable EEPROM writes
        BCF     INTCON, GIE         ; Disable interrupts during mandatory sequence
        MOVLW   0x55                ; --- Required 5-instruction unlock sequence ---
        MOVWF   EECON2
        MOVLW   0xAA
        MOVWF   EECON2
        BSF     EECON1, WR          ; Begin write cycle
        BSF     INTCON, GIE         ; Re-enable interrupts
        BCF     EECON1, WREN        ; Disable further writes
        BCF     STATUS, RP1
        BCF     STATUS, RP0         ; Return to Bank 0
        RETURN

; ============================================================================
; LCD 16x2 4-BIT DRIVER & DISPLAY FORMATTER (PORTD: RD2=RS, RD3=EN, RD4-7=D4-7)
; ============================================================================
UPDATE_LCD:
        ; --- Line 1 (DDRAM 0x80): "MOIST:XX% TH:YY%" ---
        MOVLW   0x80
        CALL    LCD_CMD
        MOVLW   'M'
        CALL    LCD_DATA
        MOVLW   'O'
        CALL    LCD_DATA
        MOVLW   'I'
        CALL    LCD_DATA
        MOVLW   'S'
        CALL    LCD_DATA
        MOVLW   'T'
        CALL    LCD_DATA
        MOVLW   ':'
        CALL    LCD_DATA
        MOVF    MOIST_PCT, W
        CALL    LCD_PRINT_2DIG
        MOVLW   '%'
        CALL    LCD_DATA
        MOVLW   ' '
        CALL    LCD_DATA
        MOVLW   'T'
        CALL    LCD_DATA
        MOVLW   'H'
        CALL    LCD_DATA
        MOVLW   ':'
        CALL    LCD_DATA
        MOVF    THRESH_PCT, W
        CALL    LCD_PRINT_2DIG
        MOVLW   '%'
        CALL    LCD_DATA

        ; --- Line 2 (DDRAM 0xC0): "AUTO   PUMP:ON  " or "MANUAL PUMP:OFF " ---
        MOVLW   0xC0
        CALL    LCD_CMD
        BTFSC   SYS_FLAGS, F_MANUAL
        GOTO    LCD_SHOW_MANUAL

        MOVLW   'A'
        CALL    LCD_DATA
        MOVLW   'U'
        CALL    LCD_DATA
        MOVLW   'T'
        CALL    LCD_DATA
        MOVLW   'O'
        CALL    LCD_DATA
        MOVLW   ' '
        CALL    LCD_DATA
        MOVLW   ' '
        CALL    LCD_DATA
        GOTO    LCD_SHOW_PUMP

LCD_SHOW_MANUAL:
        MOVLW   'M'
        CALL    LCD_DATA
        MOVLW   'A'
        CALL    LCD_DATA
        MOVLW   'N'
        CALL    LCD_DATA
        MOVLW   'U'
        CALL    LCD_DATA
        MOVLW   'A'
        CALL    LCD_DATA
        MOVLW   'L'
        CALL    LCD_DATA

LCD_SHOW_PUMP:
        MOVLW   ' '
        CALL    LCD_DATA
        MOVLW   'P'
        CALL    LCD_DATA
        MOVLW   'U'
        CALL    LCD_DATA
        MOVLW   'M'
        CALL    LCD_DATA
        MOVLW   'P'
        CALL    LCD_DATA
        MOVLW   ':'
        CALL    LCD_DATA

        BTFSS   SYS_FLAGS, F_PUMP_ON
        GOTO    LCD_SHOW_OFF
        MOVLW   'O'
        CALL    LCD_DATA
        MOVLW   'N'
        CALL    LCD_DATA
        MOVLW   ' '
        CALL    LCD_DATA
        RETURN

LCD_SHOW_OFF:
        MOVLW   'O'
        CALL    LCD_DATA
        MOVLW   'F'
        CALL    LCD_DATA
        MOVLW   'F'
        CALL    LCD_DATA
        RETURN

; Convert binary W (0..99) to 2 ASCII decimal digits and print to LCD
LCD_PRINT_2DIG:
        MOVWF   BCD_ONES
        CLRF    BCD_TENS
BCD_LOOP:
        MOVLW   d'10'
        SUBWF   BCD_ONES, W         ; W = BCD_ONES - 10
        BTFSS   STATUS, C           ; C=0 if < 10
        GOTO    BCD_DONE
        MOVWF   BCD_ONES
        INCF    BCD_TENS, F
        GOTO    BCD_LOOP
BCD_DONE:
        MOVF    BCD_TENS, W
        ADDLW   0x30                ; Convert to ASCII '0'-'9'
        CALL    LCD_DATA
        MOVF    BCD_ONES, W
        ADDLW   0x30
        CALL    LCD_DATA
        RETURN

LCD_INIT:
        CALL    DELAY_50MS          ; Power-on wait > 40 ms
        MOVLW   0x30                ; HD44780 4-bit initialization sequence
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_5MS
        MOVLW   0x30
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_5MS
        MOVLW   0x30
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_5MS
        MOVLW   0x20                ; Switch to 4-bit bus mode
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_5MS

        MOVLW   0x28                ; 4-bit, 2 lines, 5x8 font
        CALL    LCD_CMD
        MOVLW   0x0C                ; Display ON, Cursor OFF, Blink OFF
        CALL    LCD_CMD
        MOVLW   0x06                ; Entry mode: increment cursor right
        CALL    LCD_CMD
        MOVLW   0x01                ; Clear display
        CALL    LCD_CMD
        CALL    DELAY_5MS
        RETURN

LCD_CMD:
        MOVWF   LCD_TEMP
        ANDLW   0xF0                ; High nibble, RS = 0
        CALL    LCD_NIBBLE_CMD
        SWAPF   LCD_TEMP, W
        ANDLW   0xF0                ; Low nibble, RS = 0
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_2MS
        RETURN

LCD_DATA:
        MOVWF   LCD_TEMP
        ANDLW   0xF0                ; High nibble
        IORLW   0x04                ; RS = 1 (RD2)
        CALL    LCD_NIBBLE_CMD
        SWAPF   LCD_TEMP, W
        ANDLW   0xF0                ; Low nibble
        IORLW   0x04                ; RS = 1 (RD2)
        CALL    LCD_NIBBLE_CMD
        CALL    DELAY_2MS
        RETURN

LCD_NIBBLE_CMD:
        MOVWF   PORTD               ; Put D7..D4 and RS on PORTD
        BSF     PORTD, LCD_EN_BIT   ; Pulse EN High
        NOP
        NOP
        BCF     PORTD, LCD_EN_BIT   ; Latch on falling edge
        RETURN

; ============================================================================
; CALIBRATED SOFTWARE DELAYS @ Fosc = 4 MHz (1 TCY = 1 us)
; ============================================================================
DELAY_20US:                         ; ~25 us (> 19.72 us TACQ requirement)
        MOVLW   0x07
        MOVWF   DLY_1
D20_LP:
        DECFSZ  DLY_1, F
        GOTO    D20_LP
        RETURN

DELAY_2MS:                          ; ~2 ms
        MOVLW   0x03
        MOVWF   DLY_2
        GOTO    D_MS_OUTER

DELAY_5MS:                          ; ~5 ms
        MOVLW   0x07
        MOVWF   DLY_2
        GOTO    D_MS_OUTER

DELAY_20MS:                         ; ~20 ms
        MOVLW   0x1A
        MOVWF   DLY_2
        GOTO    D_MS_OUTER

DELAY_50MS:                         ; ~50 ms (debounce & LCD power-up)
        MOVLW   0x41
        MOVWF   DLY_2
D_MS_OUTER:
        MOVLW   0xFA
        MOVWF   DLY_1
D_MS_INNER:
        DECFSZ  DLY_1, F
        GOTO    D_MS_INNER
        DECFSZ  DLY_2, F
        GOTO    D_MS_OUTER
        RETURN

        END
