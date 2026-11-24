# PROJECT REQUIREMENTS TRACEABILITY MATRIX (PIC16F877A — TOPIC #15: SMART IRRIGATION CONTROLLER)

This matrix maps **every single requirement** from `MPS_MIDTERM PROJECT ASSIGNMENT.docx` to its exact corresponding deliverable(s) in the workspace and Blackboard package (`GroupXX_PIC16F877A/`). **All submission deliverables are 100% in English.**

---

## 1. Master Requirement-to-Deliverable Mapping Table

| Assignment Section | Project Requirement | Marks | Corresponding Deliverable(s) | Exact Workspace / Submission Path | Status |
| :--- | :--- | :---: | :--- | :--- | :---: |
| **Sec. 3** | MCU Selection (different from ATmega32, datasheet + toolchain + simulator verified) | *(Prereq)* | Official Datasheets + Selection Verification (Sec. 5.1.4) | `docs/PIC16F87XA_Datasheet_DS39582C.pdf`<br>`docs/PICmicro_MidRange_RefManual_DS33023A.pdf`<br>`docs/ATmega32_Datasheet_doc2503.pdf` | **100% Done** |
| **Sec. 4** | Application Project Topic (≥ 3 MCU peripherals) — **Topic #15: Smart Irrigation Controller** (uses **5 peripherals**: ADC, Timer1, `RB0/INT`, GPIO/LCD, EEPROM) | *(Prereq)* | Section 5.8 + Full ASM Firmware + Proteus Guide | `GroupXX_PIC16F877A/MCU_Study_Document.pdf` (Sec. 5.8)<br>`GroupXX_PIC16F877A/Assembly_Source_Code.zip` | **100% Done** |
| **Sec. 5 (Comp. 1)** | **MCU Architecture & Datasheet Study** (~10–15 pages PDF covering all 10 subsections `5.1 – 5.10`) | **15** *(+10 shared w/ Slides)* | `MCU_Study_Document.pdf` *(English)*<br>Editable Word copy for inserting figures | `GroupXX_PIC16F877A/MCU_Study_Document.pdf`<br>`raw_content_en/MCU_Study_Document_Editable_EN.docx`<br>`raw_content_en/01_MCU_Study_Document_EN.md` | **Ready** *(optional: insert cropped datasheet/Proteus images in `.docx`)* |
| **Sec. 5.1 – 5.4** | Intro, CPU Architecture (Harvard, ALU, `W`, `STATUS`, Pipeline, Stack), Memory Map (Flash/4 Banks/EEPROM), 40-Pin PDIP Pinout & GPIO | *(in Comp. 1)* | Sections 5.1–5.4 of `MCU_Study_Document.pdf` | `GroupXX_PIC16F877A/MCU_Study_Document.pdf` | **100% Done** |
| **Sec. 5.5 – 5.7** | 35-Instruction Set, Peripheral Modules (GPIO, Timers, Interrupts, ADC, USART/MSSP, PWM), Assembly Environment (MPASM/`gpasm`, directives, Intel HEX) | *(in Comp. 1)* | Sections 5.5–5.7 of `MCU_Study_Document.pdf` | `GroupXX_PIC16F877A/MCU_Study_Document.pdf` | **100% Done** |
| **Sec. 5.8** | Application Project (Objectives, Block Diagram, Pinout, Calculations, Flowchart, Testing) | *(in Comp. 1)* | Section 5.8 of `MCU_Study_Document.pdf` | `GroupXX_PIC16F877A/MCU_Study_Document.pdf` | **100% Done** *(add Proteus screenshot)* |
| **Sec. 5.9** | Comparison with ATmega32 (**all 10 criteria**: CPU, Regs, Memory, ISA, GPIO, Timers, Interrupts, ADC, Serial, Assembly Tools) | *(in Comp. 1)* | Section 5.9 of `MCU_Study_Document.pdf` + Detailed Comparison | `GroupXX_PIC16F877A/MCU_Study_Document.pdf` (Sec. 5.9)<br>`ATmega32_vs_PIC16F87XA_Comparison.md` | **100% Done** |
| **Sec. 5.10** | References & Technical Diagram Citations | *(in Comp. 1)* | Section 5.10 + Standalone `References.pdf` | `GroupXX_PIC16F877A/References.pdf` | **100% Done** |
| **Sec. 6 (Comp. 2)** | **Assembly Language Programming** (commented `.asm`, compiled `.hex`/`.lst`, flowchart, init/ISR/hardware docs) | **15** | `Assembly_Source_Code.zip` (`smart_irrigation.asm`, `.hex`, `.lst`, `Assembly_Documentation.md`) | `GroupXX_PIC16F877A/Assembly_Source_Code.zip`<br>`Assembly_Source_Code/smart_irrigation.asm` | **100% Done** *(417 words, verified)* |
| **Sec. 7 (Comp. 3)** | **Assembly-to-Machine-Code Translation** (10 topics, full opcode table, hand-encoding examples, Intel HEX) | **10** | `Instruction_Set_Opcode_Table.pdf` *(all 35/35 instructions)* | `GroupXX_PIC16F877A/Instruction_Set_Opcode_Table.pdf`<br>`raw_content_en/02_Instruction_Set_Opcode_Table_EN.md` | **100% Done** *(verified)* |
| **Sec. 8 (Comp. 4)** | **Python GUI Mini Assembler** (≥ 10–15 instructions, Tkinter GUI, 5 modules, error checking, save/export, verification) | **20** | `Python_MiniAssembler.zip` *(supports all 35/35 instructions)*<br>`MiniAssembler_User_Guide.pdf` | `GroupXX_PIC16F877A/Python_MiniAssembler.zip`<br>`GroupXX_PIC16F877A/MiniAssembler_User_Guide.pdf`<br>`MiniAssembler/main.py` (+ 4 modules + `test_assembler.py`) | **100% Done** *(4/4 unit tests PASS)* |
| **Sec. 9 (Comp. 5)** | **Circuit Design & Simulation** (Proteus/SimulIDE schematic, clock/config, `.hex`, screenshots, test cases, troubleshooting) | **10** *(+10 Demo & Testing)* | `Simulation_Project.zip` (BOM, Netlist, `.hex`, `.asm`)<br>`Test_Results.pdf` (automated checks + `TC01–TC06`) | `GroupXX_PIC16F877A/Simulation_Project.zip`<br>`GroupXX_PIC16F877A/Test_Results.pdf`<br>`Simulation_Project/README_Simulation_Guide.md` | **Firmware & Guide Done** *(draw `.pdsprj` & capture screenshots in Proteus)* |
| **Sec. 10 (Comp. 6)** | **Teaching Presentation** (15–20 slides, 28-minute schedule, 15 topics + Q&A prep) | *(shared 10 + 5 Q&A)* | `Teaching_Slides.pdf` *(18 widescreen 16:9 English slides)*<br>Oral Exam 15-Question Q&A Bank | `GroupXX_PIC16F877A/Teaching_Slides.pdf`<br>`raw_content_en/03_Teaching_Slides_QnA_References_EN.md` | **100% Done** *(optional: insert Proteus screenshot on Slide 13)* |
| **Sec. 11 (Comp. 7)** | **Blackboard Learning Library** (`Group##_MCU_Name/` with all 9 required files + optional video) | *(Required)* | Complete `GroupXX_PIC16F877A/` folder ready for Blackboard upload | `GroupXX_PIC16F877A/` (9 files; rename `XX` to your Group #) | **Ready** *(add `.pdsprj` + optional `.mp4`)* |
| **Sec. 12 – 13** | **Group Roles & Oral Examination** (3 students, 100-mark rubric) | **5 + 5** | Role split & 15-question Oral Exam Q&A Bank | `raw_content_en/03_Teaching_Slides_QnA_References_EN.md` | **100% Done** |

---

## 2. Blackboard Submission Checklist (`Group##_PIC16F877A/`)

| # | Required Blackboard File (Section 11) | Language | Present in `GroupXX_PIC16F877A/` | Action Needed Before Upload |
| :-: | :--- | :---: | :---: | :--- |
| 1 | `MCU_Study_Document.pdf` | English | Yes | Optional: insert datasheet & Proteus images in `.docx` and re-export PDF |
| 2 | `Teaching_Slides.pdf` | English | Yes (18 slides) | Optional: add Proteus screenshot on Slide 13 |
| 3 | `Assembly_Source_Code.zip` | English | Yes | None — complete & verified |
| 4 | `Simulation_Project.zip` | English | Yes | Draw circuit in Proteus (per guide) and add `.pdsprj` file into zip |
| 5 | `Python_MiniAssembler.zip` | English | Yes | None — complete & verified (`4/4` tests PASS) |
| 6 | `MiniAssembler_User_Guide.pdf` | English | Yes | None — includes full verification table |
| 7 | `Instruction_Set_Opcode_Table.pdf` | English | Yes | None — all 35 instructions verified |
| 8 | `Test_Results.pdf` | English | Yes | Add Proteus simulation screenshots for `TC01–TC06` |
| 9 | `References.pdf` | English | Yes | None — IEEE citations + Figure index complete |
| 10 | `Demonstration_Video.mp4` | — | Optional | Only required if not performing live demonstration |
