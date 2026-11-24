# Tài liệu Tổng hợp Dự án Giữa kỳ (MPS Midterm Project) – Vi điều khiển PIC16F877A

Tài liệu này tổng hợp đầy đủ các thông số kỹ thuật từ datasheet chính thức của Microchip (**DS39582C**, **DS33023A**) và đối chiếu chi tiết theo từng yêu cầu sau khi chọn IC trong file `MPS_MIDTERM PROJECT ASSIGNMENT.docx`.

---

## 1. Tài liệu đã tải về trong workspace

- **Datasheet chính thức PIC16F87XA (Microchip DS39582C, 234 trang):** `docs/PIC16F87XA_Datasheet_DS39582C.pdf`
- **Tài liệu tham khảo họ vi điều khiển tầm trung (PICmicro Mid-Range MCU Family Reference Manual, DS33023A):** `docs/PICmicro_MidRange_RefManual_DS33023A.pdf`

---

## 2. Xác nhận điều kiện chọn IC (Mục 3) & Định hướng Đề tài Ứng dụng (Mục 4)

### 2.1. Kiểm tra điều kiện chọn IC (Mục 3)
`PIC16F877A` đáp ứng hoàn toàn 4 tiêu chí bắt buộc của bài assignment:
1. **Khác họ với ATmega32:** `PIC16F877A` thuộc họ **PIC16 Mid-Range (8-bit)** của Microchip (kiến trúc Harvard, từ lệnh 14-bit, tập lệnh RISC 35 lệnh), khác biệt rõ rệt với AVR ATmega32.
2. **Có Datasheet và Tài liệu tập lệnh chính thức:** Đã tải đầy đủ `DS39582C` (gồm Section 15.0 Instruction Set Summary, trang 159–165) và `DS33023A`.
3. **Có toolchain lập trình Assembly:** Hỗ trợ chính thức bởi **MPASM** (trong **MPLAB IDE**) hoặc trình biên dịch mã nguồn mở **gpasm** (gputils), xuất ra file `.hex`, `.lst`, `.map`, `.cof`.
4. **Được hỗ trợ mô phỏng:** Được hỗ trợ trực tiếp trong **Proteus** (và SimulIDE), đồng thời được liệt kê khuyến nghị ngay trong Bảng 3.1.A của đề bài (*"particularly suitable for introductory projects"*).

### 2.2. Định hướng chọn Đề tài Ứng dụng (Mục 4)
Bài toán ứng dụng bắt buộc phải sử dụng **tối thiểu 3 ngoại vi / tính năng phần cứng** của MCU. Trong 17 chủ đề gợi ý ở Mục 4, các đề tài phù hợp nhất với thế mạnh của `PIC16F877A` gồm:
- **Đề tài 5 – Temperature Monitoring System (Hệ thống giám sát nhiệt độ):** Kết hợp **ADC 10-bit** (đọc cảm biến nhiệt độ analog như LM35 qua `RA0/AN0`), **GPIO** (xuất LCD 16x2 hoặc LED 7 đoạn + LED cảnh báo/còi), **Timer0/Timer1 + Ngắt** (lấy mẫu định kỳ) và tùy chọn **USART** (gửi log nhiệt độ lên máy tính).
- **Đề tài 7 – PWM Motor Speed Controller (Điều khiển tốc độ động cơ bằng PWM):** Kết hợp **ADC 10-bit** (đọc biến trở đặt tốc độ), **CCP1/Timer2 PWM** (tạo xung PWM 10-bit trên chân `RC2/CCP1`), **GPIO + External Interrupt `RB0/INT`** (nút nhấn đảo chiều/dừng khẩn cấp, hiển thị LCD/LED).
- **Đề tài 1 & 4 – Digital Clock with Alarm / Digital Stopwatch:** Kết hợp **Timer1** (định thời 16-bit chính xác), **Ngắt (Interrupts)**, **GPIO** (quét LED 7 đoạn/LCD + nút nhấn) và **EEPROM** (lưu thời gian báo thức).

---

## 3. Component 1 – Nghiên cứu Kiến trúc & Datasheet PIC16F877A (Mục 5, 10–15 trang PDF)

Dưới đây là toàn bộ khung nội dung kỹ thuật chuẩn xác để nhóm biên soạn `MCU_Study_Document.pdf` theo đúng 10 tiểu mục (5.1 – 5.10):

### 5.1. Giới thiệu chung (Introduction)
- **Hãng sản xuất:** Microchip Technology Inc.
- **Họ vi điều khiển:** PICmicro Mid-Range 8-bit CMOS Flash Microcontroller.
- **Mức điện áp hoạt động:** `4.0V – 5.5V` đối với `PIC16F877A` (bản `PIC16LF877A` hỗ trợ `2.0V – 5.5V`).
- **Tần số hoạt động:** `DC – 20 MHz`. Chu kỳ lệnh `TCY = 4 / FOSC` (tối thiểu `200 ns` tại 20 MHz, hoặc `1 µs` tại 4 MHz).
- **Đóng gói phổ biến:** 40-pin PDIP (phù hợp cắm breadboard và mô phỏng Proteus), ngoài ra có 44-pin PLCC, TQFP, QFN.
- **Ứng dụng thực tế:** Điều khiển công nghiệp, đo lường cảm biến, tự động hóa, thiết bị nhúng học thuật.

### 5.2. Kiến trúc CPU (CPU Architecture)
- **Kiến trúc Harvard:** Tách biệt hoàn toàn bus bộ nhớ chương trình (**14-bit**) và bus dữ liệu (**8-bit**), cho phép nạp lệnh và thực thi song song (pipeline 2 tầng: Fetch & Execute).
- **Thanh ghi làm việc `W` (Working Register):** Đóng vai trò Accumulator 8-bit duy nhất cho các phép toán ALU.
- **ALU 8-bit và thanh ghi `STATUS` (`03h`):** Lưu các cờ trạng thái `C` (Carry), `DC` (Digit Carry), `Z` (Zero), các bit chọn Bank `RP1:RP0` (`STATUS<6:5>`) và bit chọn Bank gián tiếp `IRP` (`STATUS<7>`).
- **Program Counter (PC) 13-bit:** Gồm `PCL` (`02h`, 8-bit thấp) và `PCLATH` (`0Ah`, 5-bit cao) cho phép định địa chỉ tới `8K` từ lệnh (`0000h – 1FFFh`).
- **Hardware Stack:** **8 mức x 13-bit**, hoạt động dạng vòng (circular stack), chuyên dùng cho lệnh `CALL` / `RETURN` / `RETFIE` / `RETLW` và phục vụ ngắt; **không có lệnh `PUSH`/`POP`** cho lập trình viên.

### 5.3. Tổ chức Bộ nhớ (Memory Organization)
1. **Bộ nhớ chương trình (Flash Program Memory):**
   - Dung lượng: **8K x 14-bit words** (`0000h – 1FFFh`, tương đương ~14.3 KB).
   - **Reset Vector:** `0000h`.
   - **Interrupt Vector (duy nhất):** `0004h`.
   - Chia làm **4 trang (Program Pages)**, mỗi trang **2K words**:
     - Page 0: `0000h – 07FFh`
     - Page 1: `0800h – 0FFFh`
     - Page 2: `1000h – 17FFh`
     - Page 3: `1800h – 1FFFh`
     *(Khi nhảy `GOTO`/`CALL` sang trang khác phải thiết lập `PCLATH<4:3>`).*
2. **Bộ nhớ dữ liệu RAM (Data Memory):**
   - Tổng dung lượng GPR (RAM người dùng): **368 bytes**, kết hợp với các thanh ghi chức năng đặc biệt **SFR** (Special Function Registers).
   - Tổ chức thành **4 Bank**, mỗi Bank dài 128 bytes, chọn thông qua `STATUS<6:5>` (`RP1:RP0`):
     - **Bank 0** (`00h – 7Fh`): GPR tại `20h – 7Fh` (96 bytes).
     - **Bank 1** (`80h – FFh`): GPR tại `A0h – EFh` (80 bytes).
     - **Bank 2** (`100h – 17Fh`): GPR tại `110h – 16Fh` (80 bytes).
     - **Bank 3** (`180h – 1FFh`): GPR tại `190h – 1EFh` (80 bytes).
   - **Vùng RAM dùng chung (Shared/Mirrored RAM):** 16 bytes từ `70h – 7Fh` được ánh xạ sang cả 4 Bank (`F0h–FFh`, `170h–17Fh`, `1F0h–1FFh`) — cực kỳ quan trọng để lưu ngữ cảnh (`W_TEMP`, `STATUS_TEMP`, `PCLATH_TEMP`) khi xảy ra ngắt mà không phụ thuộc Bank hiện tại.
   - **Định địa chỉ gián tiếp:** Thông qua thanh ghi ảo `INDF` (`00h`) và thanh ghi con trỏ `FSR` (`04h`) kết hợp bit `IRP` (`STATUS<7>`).
3. **Bộ nhớ EEPROM dữ liệu:** **256 bytes** (`00h – FFh`), đọc/ghi thông qua `EECON1`, `EECON2`, `EEDATA`, `EEADR`.

### 5.4. Cấu hình Chân (Pin Configuration – 40-pin PDIP)
- **33 chân I/O** phân bố trên **5 Port**:
  - **PORTA (`RA0–RA5`, 6 bit):** Thanh ghi điều hướng `TRISA`. **Lưu ý quan trọng:** Khi Reset (POR), `RA0–RA3`, `RA5` và `RE0–RE2` mặc định ở chế độ **Analog Input**; phải ghi `ADCON1 = 0x06` (hoặc `0x07`) nếu muốn dùng làm Digital I/O. Chân `RA4/T0CKI` là ngõ ra cực máng hở (open-drain).
  - **PORTB (`RB0–RB7`, 8 bit):** Thanh ghi `TRISB`. Có điện trở kéo lên nội (weak pull-up) điều khiển bởi `OPTION_REG<7>` (`RBPU`). Hỗ trợ ngắt ngoài `RB0/INT` và ngắt thay đổi trạng thái `RB4–RB7`. Chân `RB3/PGM` mặc định bật Low-Voltage Programming (LVP) trừ khi tắt bằng bit cấu hình `LVP_OFF`.
  - **PORTC (`RC0–RC7`, 8 bit):** Thanh ghi `TRISC`. Ghép kênh với các ngoại vi truyền thông và PWM: `CCP1` (`RC2`), `CCP2` (`RC1`), `SPI/I²C` (`RC3/SCK/SCL`, `RC4/SDI/SDA`, `RC5/SDO`), `USART` (`RC6/TX`, `RC7/RX`).
  - **PORTD (`RD0–RD7`, 8 bit):** Thanh ghi `TRISD`. Có thể cấu hình làm Parallel Slave Port (PSP).
  - **PORTE (`RE0–RE2`, 3 bit):** Thanh ghi `TRISE` (cũng chứa bit điều khiển `PSPMODE`).
- **Chân nguồn & xung nhịp & reset:** `VDD`, `VSS`, `OSC1/CLKI`, `OSC2/CLKO`, `MCLR/VPP` (khuyến nghị mạch RC trên `MCLR` với `R1 < 40kΩ`, `R2 > 1kΩ`).

### 5.5. Tập lệnh (Instruction Set – Section 15.0, pp. 159–165)
- Gồm **35 lệnh đơn từ (single-word)**, mỗi lệnh dài cố định **14-bit**, chia thành 3 nhóm:
  1. **Byte-oriented (18 lệnh):** `ADDWF`, `ANDWF`, `CLRF`, `CLRW`, `COMF`, `DECF`, `DECFSZ`, `INCF`, `INCFSZ`, `IORWF`, `MOVF`, `MOVWF`, `NOP`, `RLF`, `RRF`, `SUBWF`, `SWAPF`, `XORWF`.
  2. **Bit-oriented (4 lệnh):** `BCF`, `BSF`, `BTFSC`, `BTFSS`.
  3. **Literal & Control (13 lệnh):** `ADDLW`, `ANDLW`, `CALL`, `CLRWDT`, `GOTO`, `IORLW`, `MOVLW`, `RETFIE`, `RETLW`, `RETURN`, `SLEEP`, `SUBLW`, `XORLW`.
- **Thời gian thực thi:** Hầu hết thực thi trong **1 chu kỳ lệnh (`TCY`)**; các lệnh rẽ nhánh (`GOTO`, `CALL`, `RETURN`, `RETFIE`, `RETLW`), lệnh nhảy có điều kiện (`BTFSC`, `BTFSS`, `DECFSZ`, `INCFSZ`) khi thỏa điều kiện, hoặc lệnh ghi vào `PCL` mất **2 chu kỳ lệnh**.
- **Lưu ý Read-Modify-Write (RMW):** Các lệnh thao tác trực tiếp lên Port (`BSF PORTB, 0`, `BCF PORTC, 1`) đọc trạng thái chân vật lý tại thời điểm thực thi, sửa bit rồi ghi lại toàn bộ 8-bit Port.

### 5.6. Các Module Ngoại vi (Peripheral Modules)
- **GPIO:** 5 Port (`PORTA–PORTE`) điều khiển chiều qua `TRISA–TRISE` (`1` = Input, `0` = Output).
- **Timers (3 bộ định thời):**
  - **Timer0 (`TMR0`, `OPTION_REG`):** 8-bit Timer/Counter, chia bộ chia tần (Prescaler) dùng chung với Watchdog Timer (WDT).
  - **Timer1 (`TMR1H:TMR1L`, `T1CON`):** 16-bit Timer/Counter, có thể chạy bất đồng bộ với thạch anh ngoài 32.768 kHz.
  - **Timer2 (`TMR2`, `PR2`, `T2CON`):** 8-bit Timer có thanh ghi chu kỳ `PR2`, Prescaler và Postscaler, là nguồn tạo xung chuẩn cho **PWM**.
- **Hệ thống Ngắt (15 nguồn ngắt, 1 vector `0004h`):** Quản lý qua `INTCON`, `PIE1/PIR1`, `PIE2/PIR2`. Khi có ngắt, phần cứng tự động tắt `GIE` (`INTCON<7>`), đẩy PC vào Stack và nhảy tới `0004h`; chương trình ISR tự kiểm tra cờ nào đang bật và xóa cờ bằng phần mềm trước khi `RETFIE`.
- **ADC 10-bit (8 kênh `AN0–AN7`):** Điều khiển qua `ADCON0`, `ADCON1`; kết quả 10-bit lưu trong `ADRESH:ADRESL` (canh trái hoặc canh phải qua `ADFM`). Thời gian chuyển đổi tối thiểu `TAD = 1.6 µs`, thời gian lấy mẫu `TACQ ~ 19.72 µs`.
- **USART:** Truyền thông nối tiếp đồng bộ/bất đồng bộ qua `TXSTA`, `RCSTA`, `SPBRG` (tạo baud rate), `TXREG`, `RCREG`.
- **MSSP (Master Synchronous Serial Port):** Hỗ trợ **SPI** và **I²C** (Master/Slave) qua `SSPCON`, `SSPCON2`, `SSPSTAT`, `SSPBUF`, `SSPADD`.
- **CCP1 & CCP2 (Capture/Compare/PWM):** Tạo **PWM 10-bit** (độ phân giải tối đa 10-bit) dựa trên `PR2` (tần số) và `CCPRxL:CCPxCON<5:4>` (duty cycle).
- **2 Bộ so sánh tương tự (Analog Comparators):** Điều khiển qua `CMCON`, `CVRCON`.

### 5.7. Môi trường lập trình Assembly (Assembly Programming Environment)
- **IDE & Assembler:** MPLAB IDE + **MPASM** (hoặc **gpasm** trong bộ `gputils` trên Windows/Linux).
- **Cấu hình phần cứng (`__CONFIG` tại địa chỉ `2007h`):** Khai báo dao động (`_HS_OSC` cho >4 MHz, `_XT_OSC` cho ≤4 MHz, `_LP_OSC`, `_RC_OSC`), `_WDT_OFF`, `_PWRTE_ON`, `_BOREN_OFF`/`_ON`, `_LVP_OFF` (quan trọng để dùng `RB3` làm I/O bình thường), `_CP_OFF`.
- **Output:** File `.hex` (Intel HEX 32-bit/16-bit) nạp vào Proteus hoặc mạch thật.

### 5.8. Định hướng Application Project
- Trình bày sơ đồ khối phần cứng, phân công chân trên `PIC16F877A`, lý do chọn ≥3 ngoại vi (ví dụ: ADC + Timer/Interrupt + GPIO/LCD hoặc PWM + ADC + GPIO).

### 5.9. Bảng So sánh PIC16F877A và ATmega32 (10 Tiêu chí bắt buộc)

| STT | Tiêu chí | PIC16F877A (Microchip) | ATmega32 (Microchip / Atmel AVR) |
| :--- | :--- | :--- | :--- |
| 1 | **Kiến trúc CPU** | 8-bit Harvard RISC, dùng 1 thanh ghi `W` (Accumulator), 4 RAM Bank | 8-bit Harvard RISC, **32 thanh ghi đa dụng (`R0–R31`)**, không phân Bank RAM |
| 2 | **Tốc độ & Chu kỳ lệnh** | Tối đa `20 MHz`, `1 TCY = 4 clock` (tối đa **5 MIPS**, 200 ns/lệnh) | Tối đa `16 MHz`, đa số lệnh `1 clock` (tối đa **16 MIPS**) |
| 3 | **Bộ nhớ Chương trình (Flash)** | **8K x 14-bit words** (~14.3 KB), chia 4 Page 2K | **32 KB** (16K x 16-bit words) |
| 4 | **Bộ nhớ Dữ liệu (SRAM)** | **368 bytes** (chia 4 Bank qua `RP1:RP0`, vùng chung `70h–7Fh`) | **2 KB** (tuyến tính, không cần chuyển Bank) |
| 5 | **EEPROM nội** | **256 bytes** | **1 KB** (1024 bytes) |
| 6 | **Tập lệnh (Instruction Set)** | **35 lệnh**, độ dài cố định **14-bit** (dễ học, ít lệnh) | **131 lệnh**, độ dài 16-bit / 32-bit |
| 7 | **Số chân I/O (GPIO)** | **33 chân** (5 Port: `PORTA–PORTE`, thanh ghi `TRISx`/`PORTx`) | **32 chân** (4 Port: `PORTA–PORTD`, thanh ghi `DDRx`/`PORTx`/`PINx`) |
| 8 | **Hệ thống Ngắt & Stack** | **15 nguồn ngắt**, **1 vector duy nhất (`0004h`)**; Stack phần cứng **8 mức** | **21 vector ngắt riêng biệt**; Stack nằm trên SRAM (linh hoạt theo RAM) |
| 9 | **Ngoại vi tích hợp** | 3 Timers (T0 8b, T1 16b, T2 8b), 2 CCP/PWM, 8-ch 10-bit ADC, USART, MSSP (SPI/I²C), PSP, 2 Comparators | 3 Timers (T0 8b, T1 16b, T2 8b), 4 kênh PWM, 8-ch 10-bit ADC, USART, SPI, TWI (I²C) |
| 10 | **Độ phức tạp lập trình Assembly** | Tập lệnh rất gọn (35 lệnh), nhưng phải quản lý chuyển Bank (`RP1:RP0`), Page (`PCLATH`) và chỉ có 1 thanh ghi `W` | Tập lệnh phong phú (131 lệnh), có nhiều thanh ghi `R0–R31` và bảng vector ngắt riêng nên viết logic lớn thuận tiện hơn |

### 5.10. Tài liệu tham khảo (References)
- Microchip Technology Inc., *PIC16F87XA Data Sheet (28/40/44-Pin Enhanced Flash Microcontrollers)*, DS39582C.
- Microchip Technology Inc., *PICmicro Mid-Range MCU Family Reference Manual*, DS33023A.
- Microchip Technology Inc., *MPASM Assembler, MPLINK Object Linker, MPLIB Object Librarian User's Guide*.

---

## 4. Component 2 – Lập trình Assembly cho PIC16F877A (Mục 6)

### 4.1. Sản phẩm cần nộp
- Mã nguồn `.asm` hoàn chỉnh, chú thích (comment) rõ ràng từng khối.
- Tài liệu giải thích từng lệnh, thanh ghi và cờ trạng thái được sử dụng.
- Lưu đồ giải thuật (Flowchart) hoặc Sơ đồ trạng thái (State Diagram).
- File `.hex` đã biên dịch thành công từ MPASM/`gpasm`.
- Các ca kiểm thử (Test cases) và phần demo chạy thực tế/mô phỏng.

### 4.2. Các lưu ý kỹ thuật đặc thù khi viết Assembly trên PIC16F877A
1. **Chuyển Bank thanh ghi (`RP1:RP0`):**
   - `PORTA–PORTE`, `TMR0`, `TMR1`, `ADCON0` nằm ở **Bank 0** (`RP1=0, RP0=0`).
   - `TRISA–TRISE`, `OPTION_REG`, `ADCON1`, `PR2`, `TXSTA`, `SPBRG`, `PIE1` nằm ở **Bank 1** (`RP1=0, RP0=1`).
   - Có thể dùng chỉ thị `BANKSEL <ten_thanh_ghi>` của MPASM hoặc thao tác trực tiếp `BSF STATUS, RP0` / `BCF STATUS, RP0`.
2. **Tắt Analog trên `PORTA`/`PORTE` khi dùng Digital I/O:**
   - Luôn cấu hình `ADCON1` (ví dụ `0x06` cho toàn bộ Digital, hoặc chọn kênh analog phù hợp nếu dùng ADC).
3. **Lưu và khôi phục ngữ cảnh trong ISR (`ORG 0x0004`):**
   - Dùng các biến ở vùng RAM dùng chung (`0x70–0x7F`) để lưu `W` và `STATUS` (dùng `SWAPF STATUS, W` thay vì `MOVF` để không làm thay đổi cờ `Z`), xử lý ngắt, xóa cờ ngắt, rồi khôi phục trước khi gọi `RETFIE`.

---

## 5. Component 3 – Dịch Assembly sang Mã máy 14-bit (Mục 7)

Đây là phần cốt lõi liên kết trực tiếp với **Component 4 (Python Mini Assembler)** và chiếm **10 điểm** riêng trong Rubric.

### 5.1. Cấu trúc 3 định dạng từ lệnh 14-bit của PIC16F877A (Section 15.0)
Mọi lệnh của `PIC16F877A` đều có độ dài cố định **14 bit (1 word)** trong bộ nhớ chương trình:

1. **Định dạng Byte-oriented (thao tác byte trên thanh ghi `f`):**
   ```text
   Bit:  13 12 | 11 10  9  8 |  7  |  6  5  4  3  2  1  0
        [ 0  0 |   opcode    |  d  |         f (7-bit)    ]
   ```
   - `d = 0` (hoặc `, W`): Kết quả lưu vào thanh ghi `W`.
   - `d = 1` (hoặc `, F`): Kết quả lưu lại vào thanh ghi `f`.
   - `f` (7-bit: `0x00 – 0x7F`): Địa chỉ thanh ghi trong Bank hiện tại.

2. **Định dạng Bit-oriented (thao tác bit `b` trên thanh ghi `f`):**
   ```text
   Bit:  13 12 | 11 10 |  9  8  7 |  6  5  4  3  2  1  0
        [ 0  1 |  op   |  b(3-bit)|         f (7-bit)    ]
   ```
   - `b` (3-bit: `0 – 7`): Vị trí bit cần set/clear/test.

3. **Định dạng Literal & Control (hằng số `k` hoặc địa chỉ nhảy):**
   - **Literal (8-bit `k`):**
     ```text
     Bit:  13 12 | 11 10  9  8 |  7  6  5  4  3  2  1  0
          [ 1  1 |   opcode    |         k (8-bit)        ]
     ```
   - **Branch / Call (`CALL` / `GOTO`, 11-bit địa chỉ `k`):**
     ```text
     Bit:  13 12 | 11 | 10  9  8  7  6  5  4  3  2  1  0
          [ 1  0 | op |           k (11-bit)             ]
     ```
     (`op = 0` cho `CALL`, `op = 1` cho `GOTO`).
   - **Lệnh cố định (Fixed 14-bit):** `NOP`, `RETURN`, `RETFIE`, `SLEEP`, `CLRWDT` có mã 14-bit cố định.

### 5.2. Quy tắc ánh xạ vào Bộ nhớ Chương trình & File Intel HEX
- Mỗi lệnh chiếm **1 word (14-bit)** tại địa chỉ `Addr` (tăng thêm `1` sau mỗi lệnh, bắt đầu từ `ORG 0x0000`).
- Trong file **Intel HEX** do MPASM/`gpasm` xuất ra, mỗi word 14-bit được lưu thành **2 byte theo thứ tự Little-Endian** (byte thấp trước, byte cao sau), và địa chỉ byte trong file HEX bằng `2 * Addr`.

---

## 6. Component 4 – Python GUI Mini Assembler (Mục 8, 20 điểm)

### 6.1. Yêu cầu kiến trúc & chức năng
- **Ngôn ngữ & Thư viện:** Python 3 + **Tkinter** (GUI chuẩn).
- **Cấu trúc module bắt buộc:**
  - `main.py` (giao diện Tkinter + điều phối)
  - `parser.py` (tách nhãn `label`, chỉ thị `ORG`/`EQU`, `opcode`, `operands`, xử lý comment `;`)
  - `instruction_set.py` (bảng định nghĩa opcode 14-bit, định dạng từng lệnh)
  - `encoder.py` (dịch hai lượt — 2-pass assembler để giải quyết nhãn nhảy `GOTO`/`CALL` tiến/lùi, kiểm tra giới hạn bit `f`, `b`, `k`)
  - `error_handler.py` (báo lỗi cú pháp, sai số lượng toán hạng, vượt phạm vi giá trị, nhãn không tồn tại kèm số dòng)
  - `examples/sample.asm` và `README.pdf`
- **Các tính năng GUI bắt buộc:**
  - Khung soạn thảo Assembly + nút **Load `.asm`**
  - Hiển thị tên MCU mục tiêu (`PIC16F877A`)
  - Nút **Assemble / Translate** và **Clear**
  - Bảng kết quả hiển thị: **Address**, **Assembly Line**, **Binary (14-bit)**, **Hex (4 ký tự)**, **Size (1 word)**
  - Vùng hiển thị thông báo lỗi chi tiết và nút **Save Results** (xuất `.hex` / bảng dịch).

### 6.2. Đề xuất bộ 15+ lệnh hỗ trợ tối thiểu (đủ 5 nhóm theo Mục 8.1)
Đề bài yêu cầu tối thiểu **10–15 lệnh** trải đều các nhóm:
1. **Data Transfer:** `MOVLW k`, `MOVWF f`, `MOVF f, d`, `CLRF f`, `CLRW`
2. **Arithmetic:** `ADDLW k`, `ADDWF f, d`, `SUBLW k`, `SUBWF f, d`, `INCF f, d`, `DECF f, d`
3. **Logical:** `ANDLW k`, `ANDWF f, d`, `IORLW k`, `XORLW k`, `COMF f, d`
4. **Register / Bit / Memory:** `BSF f, b`, `BCF f, b`, `BTFSC f, b`, `BTFSS f, b`, `SWAPF f, d`
5. **Branch / Control:** `GOTO label`, `CALL label`, `RETURN`, `RETFIE`, `NOP`

### 6.3. Kiểm chứng (Verification)
- Dịch cùng file `examples/sample.asm` bằng **Mini Assembler** và bằng **MPASM / `gpasm`**, sau đó đối chiếu từng word mã máy (Hex/Binary) trong file `.lst` để chứng minh độ chính xác 100%.

---

## 7. Component 5, 6, 7 – Mô phỏng, Thuyết trình & Cấu trúc Nộp bài (Mục 9–15)

### 7.1. Component 5 – Thiết kế Mạch & Mô phỏng (Mục 9)
- Dùng **Proteus** (khuyến nghị cho PIC16F877A) hoặc SimulIDE.
- Đảm bảo cấp nguồn, mạch Reset `MCLR`, thạch anh `OSC1/OSC2` (ví dụ `4 MHz` hoặc `20 MHz`), thiết lập đúng tần số xung clock trong thuộc tính IC trên Proteus khớp với code Assembly và nạp file `.hex`.
- Lưu kèm: Schematic, file project mô phỏng, ảnh chụp màn hình các test case và giải thích nguyên lý hoạt động.

### 7.2. Component 6 – Slide Thuyết trình Giảng dạy (Mục 10)
- **Số lượng:** 15 – 20 slides (`Teaching_Slides.pdf`).
- **Thời lượng:** Tổng **28 phút** (bao gồm **3 phút Demo** + **5 phút Q&A**, tức phần trình bày nội dung chính khoảng 20 phút).

### 7.3. Component 7 – Cấu trúc Thư mục Nộp Blackboard (Mục 11)
Đặt tên thư mục gốc theo định dạng `Group##_PIC16F877A/` gồm đủ 10 mục:
1. `MCU_Study_Document.pdf`
2. `Teaching_Slides.pdf`
3. `Assembly_Source_Code.zip`
4. `Simulation_Project.zip`
5. `Python_MiniAssembler.zip`
6. `MiniAssembler_User_Guide.pdf`
7. `Instruction_Set_Opcode_Table.pdf`
8. `Test_Results.pdf`
9. `Demonstration_Video.mp4` *(tùy chọn nếu demo trực tiếp)*
10. `References.pdf`

### 7.4. Phân công 3 thành viên (Mục 12) & Thang điểm 100 (Mục 13)
- **Thành viên 1:** Nghiên cứu kiến trúc, datasheet, tập lệnh PIC16F877A, so sánh ATmega32, biên soạn `MCU_Study_Document.pdf` & `Instruction_Set_Opcode_Table.pdf`.
- **Thành viên 2:** Viết code Assembly ứng dụng, phân tích mã hóa lệnh 14-bit, xây dựng **Python GUI Mini Assembler** & `MiniAssembler_User_Guide.pdf`.
- **Thành viên 3:** Thiết kế mạch Proteus, chạy mô phỏng, lập kịch bản test (`Test_Results.pdf`), chuẩn bị Demo và hoàn thiện slide thuyết trình.

**Phân bổ 100 điểm (Rubric):**
- Kiến trúc MCU & phân tích Datasheet: **15đ**
- Tài liệu kỹ thuật & Slide: **10đ**
- Chương trình Assembly & giải thích: **15đ**
- Thiết kế mạch & Mô phỏng: **10đ**
- Demo & Kiểm thử: **10đ**
- Python Mini Assembler & GUI: **20đ**
- Độ chính xác mã hóa lệnh (Machine-Code Encoding): **10đ**
- Kỹ năng giảng dạy & Trả lời Q&A: **5đ**
- Đóng góp cá nhân: **5đ**

