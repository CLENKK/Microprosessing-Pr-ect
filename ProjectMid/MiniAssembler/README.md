# PIC16F877A Educational Mini Assembler (Component 4)

A Python 3 + Tkinter GUI educational assembler that translates **Microchip PIC16F877A** assembly programs into **14-bit binary and hexadecimal machine code** and exports **Proteus/SimulIDE-ready Intel HEX (`INHX32M`)** firmware.

## 1. Key Features
- **Full 35/35 PIC16F877A Instruction Set Support** (`DS39582C`, Table 15-2, p. 160), covering all five required categories (Data Transfer, Arithmetic, Logical, Bit/Register, Branch/Control).
- **Two-Pass Assembler Engine:** Resolves both forward and backward branch/call labels (`GOTO`, `CALL`), supporting `ORG`, `EQU`, `CBLOCK`/`ENDC`, `__CONFIG`, `BANKSEL`, `PAGESEL`, `DT`, `DW`, and `END`.
- **Built-in PIC16F877A Symbol Library:** Preloaded SFR addresses across Banks 0–3 (`PORTA–E`, `TRISA–E`, `STATUS`, `INTCON`, `ADCON0/1`, `TMR0/1/2`, `T1CON`, `EECON1/2`, bit constants, and `__CONFIG` masks).
- **Interactive Tkinter GUI (Sections 8.1 & 8.4):**
  - Assembly source editor with synchronized line numbers and syntax highlighting.
  - Machine-Code Translation Table (`Address`, `Assembly Line`, `Binary (14-bit)`, `Hex`, `Size`, `Cycles`).
  - Live **Intel HEX (`.hex`)** and **Symbol Table** tabs.
  - Searchable **35-Instruction Opcode Table Viewer**.
  - Line-numbered error diagnostics with red-highlighted offending lines.
  - Export listing/table (`.lst`, `.csv`, `.txt`) and Intel HEX firmware (`.hex`).

## 2. Project Structure
```text
MiniAssembler/
├── main.py                # Tkinter GUI application
├── parser.py              # MPASM-compatible lexical & syntax parser
├── instruction_set.py     # All 35 14-bit instruction definitions & SFR constants
├── encoder.py             # 2-pass encoder, listing & Intel HEX generator
├── error_handler.py       # Operand range validators & structured error reporting
├── test_assembler.py      # Automated unit test suite verifying all 35 instructions
├── examples/
│   ├── sample.asm         # Multi-category verification sample program
│   ├── sample.hex         # Verified Intel HEX output
│   └── sample.lst         # Verified listing output
└── README.md              # Documentation (PDF version included as README.pdf)
```

## 3. Running & Verification
- **Requirements:** Python 3.8+ (uses standard-library `tkinter` only).
- **Launch GUI:**
  ```bash
  python main.py
  ```
- **Run Automated Verification Suite (35 instructions + 2-Pass + Intel HEX + Error Detection):**
  ```bash
  python -m unittest discover -s . -p "test_*.py" -v
  ```
