"""
Complete PIC16F877A 14-bit Instruction Set (All 35 Instructions) and SFR Definitions.
Verified directly against Microchip PIC16F87XA Data Sheet (DS39582C, Table 2-1 pp. 19-21 & Table 15-2 p. 160).
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class InstructionDef:
    mnemonic: str
    fmt: str            # 'BYTE_FD', 'BYTE_F', 'BIT_FB', 'LIT_8', 'ADDR_11', 'FIXED'
    base_opcode: int    # 14-bit base opcode (don't-care bits x = 0 per DS39582C Table 15-1)
    category: str       # Data Transfer, Arithmetic, Logical, Bit/Register, Branch/Control
    syntax: str
    pattern: str        # 14-bit binary pattern from DS39582C Table 15-2
    cycles: str
    flags: str
    description: str


# All 35 official PIC16F877A Mid-Range instructions
INSTRUCTION_SET: Dict[str, InstructionDef] = {
    # --- BYTE-ORIENTED FILE REGISTER OPERATIONS (18 instructions) ---
    "ADDWF":  InstructionDef("ADDWF",  "BYTE_FD", 0x0700, "Arithmetic",    "ADDWF f, d",  "00 0111 dfff ffff", "1",    "C, DC, Z", "Add W and f"),
    "ANDWF":  InstructionDef("ANDWF",  "BYTE_FD", 0x0500, "Logical",       "ANDWF f, d",  "00 0101 dfff ffff", "1",    "Z",        "AND W with f"),
    "CLRF":   InstructionDef("CLRF",   "BYTE_F",  0x0180, "Data Transfer", "CLRF f",      "00 0001 1fff ffff", "1",    "Z",        "Clear f (0 -> f)"),
    "CLRW":   InstructionDef("CLRW",   "FIXED",   0x0100, "Data Transfer", "CLRW",        "00 0001 0xxx xxxx", "1",    "Z",        "Clear W (0 -> W)"),
    "COMF":   InstructionDef("COMF",   "BYTE_FD", 0x0900, "Logical",       "COMF f, d",   "00 1001 dfff ffff", "1",    "Z",        "Complement f (~f -> dest)"),
    "DECF":   InstructionDef("DECF",   "BYTE_FD", 0x0300, "Arithmetic",    "DECF f, d",   "00 0011 dfff ffff", "1",    "Z",        "Decrement f (f - 1 -> dest)"),
    "DECFSZ": InstructionDef("DECFSZ", "BYTE_FD", 0x0B00, "Branch/Control","DECFSZ f, d", "00 1011 dfff ffff", "1(2)", "None",     "Decrement f, Skip if 0"),
    "INCF":   InstructionDef("INCF",   "BYTE_FD", 0x0A00, "Arithmetic",    "INCF f, d",   "00 1010 dfff ffff", "1",    "Z",        "Increment f (f + 1 -> dest)"),
    "INCFSZ": InstructionDef("INCFSZ", "BYTE_FD", 0x0F00, "Branch/Control","INCFSZ f, d", "00 1111 dfff ffff", "1(2)", "None",     "Increment f, Skip if 0"),
    "IORWF":  InstructionDef("IORWF",  "BYTE_FD", 0x0400, "Logical",       "IORWF f, d",  "00 0100 dfff ffff", "1",    "Z",        "Inclusive OR W with f"),
    "MOVF":   InstructionDef("MOVF",   "BYTE_FD", 0x0800, "Data Transfer", "MOVF f, d",   "00 1000 dfff ffff", "1",    "Z",        "Move f (f -> dest)"),
    "MOVWF":  InstructionDef("MOVWF",  "BYTE_F",  0x0080, "Data Transfer", "MOVWF f",     "00 0000 1fff ffff", "1",    "None",     "Move W to f (W -> f)"),
    "NOP":    InstructionDef("NOP",    "FIXED",   0x0000, "Branch/Control","NOP",         "00 0000 0xx0 0000", "1",    "None",     "No Operation"),
    "RLF":    InstructionDef("RLF",    "BYTE_FD", 0x0D00, "Bit/Register",  "RLF f, d",    "00 1101 dfff ffff", "1",    "C",        "Rotate Left f through Carry"),
    "RRF":    InstructionDef("RRF",    "BYTE_FD", 0x0C00, "Bit/Register",  "RRF f, d",    "00 1100 dfff ffff", "1",    "C",        "Rotate Right f through Carry"),
    "SUBWF":  InstructionDef("SUBWF",  "BYTE_FD", 0x0200, "Arithmetic",    "SUBWF f, d",  "00 0010 dfff ffff", "1",    "C, DC, Z", "Subtract W from f (f - W)"),
    "SWAPF":  InstructionDef("SWAPF",  "BYTE_FD", 0x0E00, "Bit/Register",  "SWAPF f, d",  "00 1110 dfff ffff", "1",    "None",     "Swap nibbles in f"),
    "XORWF":  InstructionDef("XORWF",  "BYTE_FD", 0x0600, "Logical",       "XORWF f, d",  "00 0110 dfff ffff", "1",    "Z",        "Exclusive OR W with f"),

    # --- BIT-ORIENTED FILE REGISTER OPERATIONS (4 instructions) ---
    "BCF":    InstructionDef("BCF",    "BIT_FB",  0x1000, "Bit/Register",  "BCF f, b",    "01 00bb bfff ffff", "1",    "None",     "Bit Clear f (0 -> f<b>)"),
    "BSF":    InstructionDef("BSF",    "BIT_FB",  0x1400, "Bit/Register",  "BSF f, b",    "01 01bb bfff ffff", "1",    "None",     "Bit Set f (1 -> f<b>)"),
    "BTFSC":  InstructionDef("BTFSC",  "BIT_FB",  0x1800, "Branch/Control","BTFSC f, b",  "01 10bb bfff ffff", "1(2)", "None",     "Bit Test f, Skip if Clear"),
    "BTFSS":  InstructionDef("BTFSS",  "BIT_FB",  0x1C00, "Branch/Control","BTFSS f, b",  "01 11bb bfff ffff", "1(2)", "None",     "Bit Test f, Skip if Set"),

    # --- LITERAL AND CONTROL OPERATIONS (13 instructions) ---
    "ADDLW":  InstructionDef("ADDLW",  "LIT_8",   0x3E00, "Arithmetic",    "ADDLW k",     "11 111x kkkk kkkk", "1",    "C, DC, Z", "Add Literal and W"),
    "ANDLW":  InstructionDef("ANDLW",  "LIT_8",   0x3900, "Logical",       "ANDLW k",     "11 1001 kkkk kkkk", "1",    "Z",        "AND Literal with W"),
    "CALL":   InstructionDef("CALL",   "ADDR_11", 0x2000, "Branch/Control","CALL k",      "10 0kkk kkkk kkkk", "2",    "None",     "Call Subroutine"),
    "CLRWDT": InstructionDef("CLRWDT", "FIXED",   0x0064, "Branch/Control","CLRWDT",      "00 0000 0110 0100", "1",    "TO, PD",   "Clear Watchdog Timer"),
    "GOTO":   InstructionDef("GOTO",   "ADDR_11", 0x2800, "Branch/Control","GOTO k",      "10 1kkk kkkk kkkk", "2",    "None",     "Go to Address"),
    "IORLW":  InstructionDef("IORLW",  "LIT_8",   0x3800, "Logical",       "IORLW k",     "11 1000 kkkk kkkk", "1",    "Z",        "Inclusive OR Literal with W"),
    "MOVLW":  InstructionDef("MOVLW",  "LIT_8",   0x3000, "Data Transfer", "MOVLW k",     "11 00xx kkkk kkkk", "1",    "None",     "Move Literal to W"),
    "RETFIE": InstructionDef("RETFIE", "FIXED",   0x0009, "Branch/Control","RETFIE",      "00 0000 0000 1001", "2",    "None",     "Return from Interrupt"),
    "RETLW":  InstructionDef("RETLW",  "LIT_8",   0x3400, "Branch/Control","RETLW k",     "11 01xx kkkk kkkk", "2",    "None",     "Return with Literal in W"),
    "RETURN": InstructionDef("RETURN", "FIXED",   0x0008, "Branch/Control","RETURN",      "00 0000 0000 1000", "2",    "None",     "Return from Subroutine"),
    "SLEEP":  InstructionDef("SLEEP",  "FIXED",   0x0063, "Branch/Control","SLEEP",       "00 0000 0110 0011", "1",    "TO, PD",   "Go into Standby mode"),
    "SUBLW":  InstructionDef("SUBLW",  "LIT_8",   0x3C00, "Arithmetic",    "SUBLW k",     "11 110x kkkk kkkk", "1",    "C, DC, Z", "Subtract W from Literal (k - W)"),
    "XORLW":  InstructionDef("XORLW",  "LIT_8",   0x3A00, "Logical",       "XORLW k",     "11 1010 kkkk kkkk", "1",    "Z",        "Exclusive OR Literal with W"),
}


# Predefined PIC16F877A SFRs, Bit Names, Destination Constants, and Config Bit Masks (p16f877a.inc)
PREDEFINED_SYMBOLS: Dict[str, int] = {
    # Destination constants
    "W": 0,
    "F": 1,

    # Bank 0 SFRs (DS39582C Table 2-1, p. 19)
    "INDF": 0x00, "TMR0": 0x01, "PCL": 0x02, "STATUS": 0x03, "FSR": 0x04,
    "PORTA": 0x05, "PORTB": 0x06, "PORTC": 0x07, "PORTD": 0x08, "PORTE": 0x09,
    "PCLATH": 0x0A, "INTCON": 0x0B, "PIR1": 0x0C, "PIR2": 0x0D,
    "TMR1L": 0x0E, "TMR1H": 0x0F, "T1CON": 0x10, "TMR2": 0x11, "T2CON": 0x12,
    "SSPBUF": 0x13, "SSPCON": 0x14, "CCPR1L": 0x15, "CCPR1H": 0x16, "CCP1CON": 0x17,
    "RCSTA": 0x18, "TXREG": 0x19, "RCREG": 0x1A, "CCPR2L": 0x1B, "CCPR2H": 0x1C,
    "CCP2CON": 0x1D, "ADRESH": 0x1E, "ADCON0": 0x1F,

    # Bank 1 SFRs (DS39582C Table 2-1, p. 20)
    "OPTION_REG": 0x81, "TRISA": 0x85, "TRISB": 0x86, "TRISC": 0x87,
    "TRISD": 0x88, "TRISE": 0x89, "PIE1": 0x8C, "PIE2": 0x8D, "PCON": 0x8E,
    "SSPCON2": 0x91, "PR2": 0x92, "SSPADD": 0x93, "SSPSTAT": 0x94,
    "TXSTA": 0x98, "SPBRG": 0x99, "CMCON": 0x9C, "CVRCON": 0x9D,
    "ADRESL": 0x9E, "ADCON1": 0x9F,

    # Bank 2 & 3 SFRs (DS39582C Table 2-1, p. 21)
    "EEDATA": 0x10C, "EEADR": 0x10D, "EEDATH": 0x10E, "EEADRH": 0x10F,
    "EECON1": 0x18C, "EECON2": 0x18D,

    # STATUS bits
    "IRP": 7, "RP1": 6, "RP0": 5, "NOT_TO": 4, "NOT_PD": 3, "Z": 2, "DC": 1, "C": 0,

    # INTCON bits
    "GIE": 7, "PEIE": 6, "TMR0IE": 5, "T0IE": 5, "INTE": 4, "RBIE": 3,
    "TMR0IF": 2, "T0IF": 2, "INTF": 1, "RBIF": 0,

    # OPTION_REG bits
    "NOT_RBPU": 7, "RBPU": 7, "INTEDG": 6, "T0CS": 5, "T0SE": 4,
    "PSA": 3, "PS2": 2, "PS1": 1, "PS0": 0,

    # PIR1 / PIE1 bits
    "PSPIF": 7, "ADIF": 6, "RCIF": 5, "TXIF": 4, "SSPIF": 3, "CCP1IF": 2, "TMR2IF": 1, "TMR1IF": 0,
    "PSPIE": 7, "ADIE": 6, "RCIE": 5, "TXIE": 4, "SSPIE": 3, "CCP1IE": 2, "TMR2IE": 1, "TMR1IE": 0,

    # PIR2 / PIE2 bits
    "CMIF": 6, "EEIF": 4, "BCLIF": 3, "CCP2IF": 0,
    "CMIE": 6, "EEIE": 4, "BCLIE": 3, "CCP2IE": 0,

    # T1CON / T2CON bits
    "T1CKPS1": 5, "T1CKPS0": 4, "T1OSCEN": 3, "T1SYNC": 2, "TMR1CS": 1, "TMR1ON": 0,
    "TMR2ON": 2, "T2CKPS1": 1, "T2CKPS0": 0,

    # ADCON0 / ADCON1 bits
    "ADCS1": 7, "ADCS0": 6, "CHS2": 5, "CHS1": 4, "CHS0": 3, "GO": 2, "GO_DONE": 2, "NOT_DONE": 2, "ADON": 0,
    "ADFM": 7, "ADCS2": 6, "PCFG3": 3, "PCFG2": 2, "PCFG1": 1, "PCFG0": 0,

    # TXSTA / RCSTA bits
    "CSRC": 7, "TX9": 6, "TXEN": 5, "SYNC": 4, "BRGH": 2, "TRMT": 1, "TX9D": 0,
    "SPEN": 7, "RX9": 6, "SREN": 5, "CREN": 4, "ADDEN": 3, "FERR": 2, "OERR": 1, "RX9D": 0,

    # EECON1 bits
    "EEPGD": 7, "WRERR": 3, "WREN": 2, "WR": 1, "RD": 0,

    # Configuration Word 2007h masks (Register 14-1, p. 144)
    "_CP_ALL": 0x1FFF, "_CP_OFF": 0x3FFF,
    "_DEBUG_ON": 0x37FF, "_DEBUG_OFF": 0x3FFF,
    "_WRT_OFF": 0x3FFF, "_WRT_256": 0x3DFF, "_WRT_1FOURTH": 0x3BFF, "_WRT_HALF": 0x39FF,
    "_CPD_ON": 0x3EFF, "_CPD_OFF": 0x3FFF,
    "_LVP_ON": 0x3FFF, "_LVP_OFF": 0x3F7F,
    "_BODEN_ON": 0x3FFF, "_BODEN_OFF": 0x3FBF,
    "_PWRTE_OFF": 0x3FFF, "_PWRTE_ON": 0x3FF7,
    "_WDT_ON": 0x3FFF, "_WDT_OFF": 0x3FFB,
    "_RC_OSC": 0x3FFF, "_HS_OSC": 0x3FFE, "_XT_OSC": 0x3FFD, "_LP_OSC": 0x3FFC,
}
