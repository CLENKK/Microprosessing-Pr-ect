; ============================================================================
; PIC16F877A Verification Sample Program (examples/sample.asm)
; Covers all 5 instruction groups: Data Transfer, Arithmetic, Logical,
; Bit/Register operations, and Branch/Control with Forward & Backward Labels.
; Verified 100% against Microchip DS39582C Table 15-2 (p. 160).
; ============================================================================
        LIST    P=16F877A
        __CONFIG _CP_OFF & _DEBUG_OFF & _WRT_OFF & _CPD_OFF & _LVP_OFF & _BODEN_OFF & _PWRTE_ON & _WDT_OFF & _XT_OSC

COUNT   EQU     0x20
ACCUM   EQU     0x21
MASK    EQU     0x22

        ORG     0x0000
START:
        ; --- 1. Bit Operations & Bank Switching ---
        BSF     STATUS, RP0     ; Select Bank 1 (0x1683)
        MOVLW   0x06            ; Configure PORTA/PORTE as Digital I/O (0x3006)
        MOVWF   ADCON1          ; Write ADCON1 in Bank 1 (0x009F)
        CLRF    TRISB           ; PORTB as Output (0x0186)
        BCF     STATUS, RP0     ; Return to Bank 0 (0x1283)

        ; --- 2. Data Transfer & Arithmetic ---
        CLRF    PORTB           ; Clear PORTB (0x0186)
        MOVLW   0x05            ; W = 5 (0x3005)
        MOVWF   COUNT           ; COUNT = 5 (0x00A0)
        MOVLW   0x0A            ; W = 10 (0x300A)
        ADDLW   0x05            ; W = 15 (0x3E05)
        MOVWF   ACCUM           ; ACCUM = 15 (0x00A1)

        ; --- 3. Logical & Register Operations ---
        MOVLW   0x0F            ; W = 0x0F (0x300F)
        ANDWF   ACCUM, W        ; W = ACCUM & 0x0F (0x0521)
        IORLW   0x80            ; Set bit 7 (0x3880)
        XORLW   0xFF            ; Toggle all bits (0x3AFF)
        MOVWF   MASK            ; Store in MASK (0x00A2)
        SWAPF   MASK, F         ; Swap nibbles (0x0EA2)

        ; --- 4. Loop & Subroutine Call (Forward + Backward Labels) ---
LOOP:
        INCF    PORTB, F        ; Increment PORTB (0x0A86)
        CALL    DELAY_STEP      ; Forward call to subroutine
        DECFSZ  COUNT, F        ; Decrement COUNT, skip if 0 (0x0BA0)
        GOTO    LOOP            ; Backward jump to LOOP
        GOTO    DONE            ; Forward jump to DONE

DELAY_STEP:
        NOP                     ; 1-cycle delay (0x0000)
        SUBLW   0x20            ; W = 0x20 - W (0x3C20)
        RETURN                  ; Return from subroutine (0x0008)

DONE:
        SLEEP                   ; Low-power standby (0x0063)
        END
