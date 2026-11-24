# So sánh Chi tiết Datasheet ATmega32(L) và PIC16F87XA (PIC16F877A)

Tài liệu đối chiếu trực tiếp từ hai datasheet chính thức đã lưu trong thư mục `docs/`:
- **ATmega32(L):** Atmel/Microchip Document `2503Q–AVR–02/11` (346 trang) — `docs/ATmega32_Datasheet_doc2503.pdf`
- **PIC16F87XA:** Microchip Document `DS39582C` (234 trang) — `docs/PIC16F87XA_Datasheet_DS39582C.pdf`

*(Ghi chú: Họ `PIC16F87XA` gồm 4 mã `PIC16F873A`, `874A`, `876A`, `877A`. Trong bảng so sánh dưới đây lấy đại diện cùng phân khúc 40-pin là **`PIC16F877A`** để đối chiếu ngang hàng với **`ATmega32`**, đồng thời ghi chú rõ khác biệt của các mã còn lại khi cần thiết.)*

---

## 1. Bảng Tổng hợp So sánh Thông số Kỹ thuật (từ Datasheet)

| Hạng mục | ATmega32(L) (`doc2503.pdf`) | PIC16F877A / PIC16F87XA (`DS39582C`) |
| :--- | :--- | :--- |
| **Kiến trúc lõi** | 8-bit AVR Enhanced RISC, Harvard, pipeline 2 tầng (p. 8) | 8-bit PIC Mid-Range RISC, Harvard, pipeline 2 tầng (p. 1, 6–7) |
| **Thanh ghi làm việc (CPU)** | **32 thanh ghi đa dụng 8-bit (`R0–R31`)** nối thẳng ALU; 3 cặp con trỏ 16-bit `X(R27:R26)`, `Y(R29:R28)`, `Z(R31:R30)` (p. 11–12) | **1 thanh ghi `W` (Working Register / Accumulator)** duy nhất (p. 6–7, 159) |
| **Bộ nhân phần cứng** | **Có** (2-cycle hardware multiplier: `MUL`, `MULS`, `MULSU`, `FMUL`, kết quả 16-bit vào `R1:R0`, p. 1, 329) | **Không có** (phải lập trình nhân bằng phần mềm) |
| **Tần số & Thông lượng** | `0–16 MHz` (`ATmega32`, 4.5–5.5V) / `0–8 MHz` (`ATmega32L`, 2.7–5.5V). **1 clock/lệnh** → tối đa **16 MIPS** (62.5 ns/lệnh, p. 1, 13) | `DC–20 MHz` (`16F87XA`, 4.0–5.5V) / `DC–10 MHz` (`16LF87XA`, 2.0–5.5V). **`1 TCY = 4 clock`** (`Q1–Q4`) → tối đa **5 MIPS** (200 ns/lệnh, p. 1, 175, 182) |
| **Dao động nội (Internal RC)** | **Có** (Calibrated RC 1 / 2 / 4 / 8 MHz; xuất xưởng mặc định 1 MHz, p. 25, 29) | **Không có** cho CPU (chỉ có RC nội riêng cho WDT, PWRT và ADC; CPU bắt buộc gắn thạch anh/resonator/RC ngoài, p. 145–146) |
| **Bộ nhớ Chương trình (Flash)** | **32 KB** (`16K × 16-bit words`), PC 14-bit (`$0000–$3FFF`), tuyến tính, có Boot Loader RWW. Độ bền: `10,000` E/W (p. 1, 16, 244) | **8K × 14-bit words** (~14.3 KB, `876A/877A`; `4K` cho `873A/874A`), PC 13-bit (`0000h–1FFFh`), chia **4 Page × 2K** (`PCLATH<4:3>`). Độ bền: `100,000` E/W typ (p. 1, 15, 30, 179) |
| **Bộ nhớ Dữ liệu (SRAM)** | **2048 bytes (2 KB)** tuyến tính (`$0060–$085F`), dùng chung không gian địa chỉ với `R0–R31` (`$00–$1F`) & 64 I/O Reg (`$20–$5F`). **Không phân Bank** (p. 17) | **368 bytes** GPR (`876A/877A`; `192B` cho `873A/874A`), **chia 4 Bank × 128 bytes** chọn qua `STATUS<RP1:RP0>`; vùng chung 16B `70h–7Fh` (p. 16–18) |
| **EEPROM dữ liệu** | **1024 bytes** (`100,000` chu kỳ E/W, p. 1, 18) | **256 bytes** (`876A/877A`; `128B` cho `873A/874A`, `1,000,000` chu kỳ E/W typ, p. 1, 179) |
| **Stack** | Nằm trong **SRAM**, con trỏ 16-bit `SPH:SPL` đọc/ghi được (tùy biến theo RAM), có lệnh `PUSH`/`POP` (p. 12) | **Hardware Stack 8 mức × 13-bit**, tách khỏi RAM, dạng vòng (tràn sẽ ghi đè âm thầm), **không có `PUSH`/`POP`** (p. 15, 30) |
| **Tập lệnh (Instruction Set)** | **131 lệnh**, độ dài **16-bit** (đa số) và **32-bit** (`JMP`, `CALL`, `LDS`, `STS`) (p. 1, 8, 329–331) | **35 lệnh**, độ dài cố định **14-bit** (1 word) (p. 1, 159–165) |
| **Thanh ghi Trạng thái** | `SREG` (`$3F`): `I, T, H, S, V, N, Z, C` — đủ cờ toán học có dấu (`N, V, S`), chứa bit ngắt `I` (p. 10) | `STATUS` (`03h`): `IRP, RP1, RP0, TO, PD, Z, DC, C` — chứa bit chọn Bank & Reset; không có `N, V, S`; cờ `C` trong phép trừ bị **đảo cực tính** (p. 22) |
| **I/O Ports (GPIO)** | **32 chân** (4 Port 8-bit `PORTA–PORTD`), mỗi Port gồm **3 thanh ghi**: `DDRx` (`1`=Out, `0`=In), `PORTx`, `PINx`. Pull-up nội từng chân trên cả 4 Port. Dòng 20 mA (max 40 mA) (p. 49–65, 287) | **33 chân** trên 5 Port (`PORTA` 6b, `B/C/D` 8b, `E` 3b; 28-pin có 22 chân). Mỗi Port chỉ có **2 thanh ghi**: `TRISx` (**`1`=In, `0`=Out**), `PORTx` (dễ dính lỗi RMW). Chỉ `PORTB` có pull-up chung (`RBPU`). Dòng max 25 mA (p. 41–50, 173) |
| **Hệ thống Ngắt** | **21 vector riêng biệt** (`$000` Reset + 20 ngắt tới `$028`), ưu tiên cố định theo địa chỉ; **phần cứng tự xóa hầu hết cờ ngắt** khi vào ISR (p. 13–15, 44–45) | **15 nguồn ngắt** (`14` trên bản 28-pin) nhưng chỉ **1 vector duy nhất (`0004h`)**; ISR tự polling cờ để phân biệt và **tự xóa cờ bằng phần mềm** (p. 15, 24–28, 153–154) |
| **Timers & PWM** | `T0` (8b), `T1` (16b, Input Capture + Noise Canceler), `T2` (8b, RTC 32 kHz bất đồng bộ). **4 kênh PWM** (`OC0`, `OC1A`, `OC1B`, `OC2`), tối đa **16-bit** trên T1 (p. 69–131) | `TMR0` (8b, chung prescaler với WDT), `TMR1` (16b, RTC 32 kHz bất đồng bộ), `TMR2` (8b, `PR2` + postscaler). 2 module **CCP1/CCP2** → **2 kênh PWM tối đa 10-bit** (dùng chung TMR2) (p. 53–69) |
| **ADC 10-bit (8 kênh)** | 8 kênh đơn + **kênh vi sai (gain 1x/10x/200x)**, có **VREF nội 2.56V**, Auto-Trigger, Free Running, chân `AVCC` riêng, `ADLAR=1` canh trái (p. 201–218) | 8 kênh đơn (`5` trên 28-pin), **không vi sai, không VREF nội** cho ADC, phải chờ `TACQ` (~19.7 µs) bằng phần mềm, `ADFM=1` canh phải; `ADRESH` (Bank 0) & `ADRESL` (Bank 1) nằm khác Bank! (p. 127–133) |
| **Truyền thông nối tiếp** | **3 bộ độc lập chạy song song**: USART (hardware parity, 5–9 bit, baud 12-bit `UBRR`), SPI, TWI (I²C 7-bit) (p. 132–197) | **1 USART** (8/9 bit, không hardware parity, baud 8-bit `SPBRG`) + **1 MSSP dùng chung SPI / I²C** (chỉ chọn 1 tại một thời điểm, I²C hỗ trợ 7-bit & **10-bit**). Có thêm **PSP** 8-bit (p. 71–125, 51) |
| **Analog Comparator** | **1 bộ** (`AIN0/AIN1`, có thể mượn MUX của ADC, kích hoạt Input Capture T1, p. 198–200) | **2 bộ** + **CVREF** (mạch chia áp 16 bậc nội, p. 135–142) |
| **Chế độ Tiết kiệm năng lượng** | **6 chế độ Sleep** (Idle, ADC Noise Reduction, Power-down, Power-save, Standby, Extended Standby, p. 32–34) | **1 chế độ Sleep** (Power-down, p. 156) |
| **Nạp code, Debug & Cấu hình** | SPI ISP, JTAG (4 dây: OCD + Boundary-scan), Parallel HV, Bootloader. Cấu hình qua **2 Fuse Bytes** (p. 219, 257–258) | **ICSP / ICD 2 dây** (`RB6/PGC`, `RB7/PGD`), hỗ trợ LVP (`RB3/PGM`). Cấu hình qua **1 Configuration Word 14-bit** (`2007h`, khai báo `__CONFIG` ngay trong ASM, p. 143–144, 158) |
| **Toolchain lập trình Assembly** | **Microchip Studio (Atmel Studio) + AVRASM2**, mã nguồn mở `avra` / `avr-as`; file `.hex` (Intel HEX 16-bit word), không nhúng Fuse Bytes mặc định trong `.asm` | **MPLAB IDE v8.92 / MPLAB X (≤ v5.35) + MPASM**, mã nguồn mở **`gpasm` (`gputils`)** (`DS39582C`, Sec. 16.0, p. 167–168); nhúng `__CONFIG` trực tiếp vào `.hex` |

---

## 2. Những Điểm Khác biệt Cốt lõi Ảnh hưởng Trực tiếp đến Lập trình Assembly

### 2.1. Thanh ghi Đa dụng (`R0–R31`) vs. Kiến trúc 1 Thanh ghi `W` + Chuyển Bank
- **ATmega32:** Mọi phép toán ALU diễn ra giữa 2 thanh ghi CPU (`ADD R16, R17`) chỉ mất **1 clock**. Không cần đổi Bank khi truy cập SRAM hay thanh ghi ngoại vi I/O (`$00–$3F` dùng `IN`/`OUT`; `$00–$1F` dùng trực tiếp `SBI`/`CBI`/`SBIS`/`SBIC`). Tuy nhiên cần nhớ: các lệnh hằng số (`LDI`, `ANDI`, `ORI`, `SUBI`, `CPI`) **chỉ dùng được với `R16–R31`**, không dùng được với `R0–R15`.
- **PIC16F87XA:** Mọi dữ liệu di chuyển giữa các thanh ghi/RAM/SFR đều phải "trung chuyển" qua `W` (`MOVF A, W` → `MOVWF B`). Ngoài ra, địa chỉ trực tiếp trong từ lệnh 14-bit chỉ có **7 bit (`00h–7Fh`)**, nên để truy cập 4 Bank phải liên tục bật/tắt `RP1:RP0` trong `STATUS` (hoặc dùng chỉ thị `BANKSEL`). Quên chuyển Bank là lỗi phổ biến nhất khi viết ASM trên PIC.

### 2.2. Cực tính Cờ `C` (Carry/Borrow) và Thiếu Cờ Số có dấu (`N, V`) trên PIC
- **ATmega32 (`SREG`):** Phép trừ `SUB Rd, Rr` / `CP Rd, Rr` đặt `C = 1` nếu `Rd < Rr` (có mượn), và có sẵn bộ lệnh rẽ nhánh trực quan (`BREQ`, `BRNE`, `BRLO`, `BRSH`, `BRLT`, `BRGE`).
- **PIC16F87XA (`STATUS`):** Phép trừ `SUBWF f, d` tính `(f) - (W)` và `SUBLW k` tính `k - (W)` (chú ý chiều trừ của `SUBLW` là `k - W` chứ không phải `W - k`!). Quan trọng hơn, cờ `C` bị **đảo cực tính** (p. 22):
  - `C = 1` → **Không mượn** (tức `f >= W` hoặc `k >= W`).
  - `C = 0` → **Có mượn** (tức `f < W` hoặc `k < W`).
  - PIC cũng không có lệnh rẽ nhánh theo cờ mà phải dùng `BTFSC`/`BTFSS STATUS, C` hoặc `Z` kết hợp `GOTO`.

### 2.3. Chiều GPIO, Lỗi Read-Modify-Write (RMW) & Bẫy Mặc định khi Reset
| Đặc điểm | ATmega32 | PIC16F877A |
| :--- | :--- | :--- |
| **Bit điều hướng** | `DDRx`: **`1` = Output**, **`0` = Input** | `TRISx`: **`1` = Input**, **`0` = Output** |
| **Đọc chân vật lý vs. Ghi ngõ ra** | Tách làm 2 thanh ghi: ghi `PORTx`, đọc chân dùng `PINx` → **không bị lỗi RMW** (nhưng đọc lại ngay chân vừa ghi cần 1 `NOP` do synchronizer, p. 52) | Dùng chung 1 thanh ghi `PORTx` → lệnh `BSF`/`BCF PORTx, b` đọc trạng thái chân thực tế rồi ghi đè cả 8 bit → **dễ bị lỗi RMW** nếu tải dung lớn hoặc chuyển mạch nhanh (p. 41, 159) |
| **Bẫy mặc định sau Reset** | `PC2–PC5` bị **JTAG** chiếm (`JTAGEN = 0` mặc định, p. 257); phải tắt fuse `JTAGEN` hoặc ghi `JTD = 1` hai lần trong 4 clock (p. 228) | `PORTA` & `PORTE` mặc định là **Analog Input** (đọc số luôn ra `0`, phải ghi `ADCON1 = 0x06`, p. 41); `RA4` là **open-drain** (p. 42); `RB3/PGM` bị **LVP** chiếm nếu không cấu hình `_LVP_OFF` (p. 45, 158) |

### 2.4. Phân trang Program Memory (`PCLATH`) và Stack
- **ATmega32:** Lệnh `JMP k` / `CALL k` dài 32-bit định địa chỉ trực tiếp toàn bộ 16K words Flash → không bao giờ lo chuyện phân trang. Stack nằm trên SRAM nên có thể `PUSH`/`POP` lưu thanh ghi và lồng hàm sâu tùy ý (miễn khởi tạo `SPH:SPL = RAMEND` ở đầu `RESET`).
- **PIC16F877A:** Lệnh `GOTO k` / `CALL k` chỉ mang 11-bit địa chỉ (`2K words`). Chương trình vượt quá `07FFh` phải chỉnh `PCLATH<4:3>` trước khi `CALL`/`GOTO` sang Page 1–3 (Example 2-1, p. 30). Hardware Stack chỉ có **8 mức** (tính cả ngắt), không thể `PUSH`/`POP` dữ liệu.

---

## 3. So sánh Trực tiếp qua Mã nguồn Assembly (Side-by-Side)

### Ví dụ 1: Cấu hình GPIO, Đọc nút nhấn và Xuất LED
*Yêu cầu: Cấu hình chân `bit 0` của Port A làm Input (nút nhấn), chân `bit 0` của Port B làm Output (LED). Nếu nút nhấn ở mức 0 thì bật LED, ngược lại tắt LED.*

**ATmega32 (AVR Assembly):**
```asm
; Không cần chuyển Bank, không cần tắt Analog trên PORTA
    cbi  DDRA, 0        ; PA0 = Input  (DDR = 0 -> Input)
    sbi  PORTA, 0       ; Bật điện trở kéo lên nội (pull-up) trên PA0
    sbi  DDRB, 0        ; PB0 = Output (DDR = 1 -> Output)

MAIN_LOOP:
    sbis PINA, 0        ; Đọc chân vật lý qua PINA; bỏ qua lệnh sau nếu PA0 = 1
    rjmp LED_ON         ; Nếu PA0 = 0 (nhấn nút) -> bật LED
    cbi  PORTB, 0       ; PA0 = 1 -> tắt LED (PB0 = 0)
    rjmp MAIN_LOOP
LED_ON:
    sbi  PORTB, 0       ; Bật LED (PB0 = 1)
    rjmp MAIN_LOOP
```

**PIC16F877A (MPASM Assembly — đối chiếu Example 4-1, p. 41):**
```asm
; Bắt buộc chuyển sang Bank 1 để cấu hình ADCON1 và TRISx
    BCF   STATUS, RP1   ;
    BSF   STATUS, RP0   ; Chọn Bank 1
    MOVLW 0x06          ; TẮT Analog trên PORTA & PORTE (bắt buộc!)
    MOVWF ADCON1        ;
    BSF   TRISA, 0      ; RA0 = Input  (TRIS = 1 -> Input; cần pull-up ngoài)
    BCF   TRISB, 0      ; RB0 = Output (TRIS = 0 -> Output)
    BCF   STATUS, RP0   ; Quay về Bank 0 để truy cập PORTA, PORTB

MAIN_LOOP:
    BTFSC PORTA, 0      ; Kiểm tra chân RA0; bỏ qua lệnh sau nếu RA0 = 0
    GOTO  LED_OFF       ; Nếu RA0 = 1 -> tắt LED
    BSF   PORTB, 0      ; RA0 = 0 -> bật LED (RB0 = 1)
    GOTO  MAIN_LOOP
LED_OFF:
    BCF   PORTB, 0      ; Tắt LED (RB0 = 0)
    GOTO  MAIN_LOOP
```
> **Điểm khác biệt thấy ngay:** PIC phải đổi Bank (`RP0`), tắt chế độ Analog (`ADCON1 = 0x06`), đảo quy ước bit `TRIS` (`1`=In/`0`=Out), và `PORTA` không có pull-up nội như AVR.

---

### Ví dụ 2: Tính toán, So sánh (`if X < 50`) và Vòng lặp Đếm (`10` lần)
*Yêu cầu: Cộng `A + B`, so sánh kết quả với `50`, sau đó chạy vòng lặp 10 lần.*

**ATmega32 (AVR Assembly):**
```asm
; Cộng trực tiếp 2 thanh ghi đa dụng
    ldi  r16, 20        ; A = 20
    ldi  r17, 15        ; B = 15
    add  r16, r17       ; r16 = r16 + r17 = 35 (1 clock)

; So sánh r16 < 50 (cờ C bình thường: C=1 nếu r16 < 50)
    cpi  r16, 50        ; So sánh trực tiếp không làm mất r16
    brlo IS_LESS        ; Nhảy nếu r16 < 50 (Unsigned Lower)
    rjmp NOT_LESS

; Vòng lặp 10 lần
    ldi  r18, 10
LOOP_10:
    ; ... công việc ...
    dec  r18            ; Giảm r18, tự cập nhật cờ Z
    brne LOOP_10        ; Còn khác 0 thì lặp (1/2 clock)
```

**PIC16F877A (MPASM Assembly):**
```asm
; Cộng 2 biến RAM (VAR_A, VAR_B ở Bank 0) phải đi qua W
    MOVLW d'20'
    MOVWF VAR_A
    MOVLW d'15'
    MOVWF VAR_B
    MOVF  VAR_A, W      ; W = VAR_A
    ADDWF VAR_B, W      ; W = VAR_A + VAR_B = 35
    MOVWF RESULT        ; Lưu kết quả

; So sánh RESULT < 50 bằng SUBLW (k - W = 50 - RESULT) hoặc SUBWF (f - W)
    MOVLW d'50'
    SUBWF RESULT, W     ; W = RESULT - 50 (CHÚ Ý: C=0 là RESULT < 50!)
    BTFSS STATUS, C     ; Nếu C = 1 (RESULT >= 50) thì bỏ qua GOTO
    GOTO  IS_LESS       ; C = 0 -> RESULT < 50
    GOTO  NOT_LESS

; Vòng lặp 10 lần (dùng lệnh đặc sản DECFSZ của PIC)
    MOVLW d'10'
    MOVWF COUNT
LOOP_10:
    ; ... công việc ...
    DECFSZ COUNT, F     ; Giảm COUNT, lưu lại vào COUNT, bỏ qua lệnh kế nếu = 0
    GOTO   LOOP_10
```
> **Điểm khác biệt thấy ngay:** AVR dùng `CPI` + `BRLO` không phá hủy thanh ghi gốc và dùng cờ `C` chuẩn. PIC phải dùng phép trừ phá hủy `W`, chú ý **cờ `C` đảo cực tính**, nhưng bù lại có lệnh `DECFSZ` gộp cả giảm + kiểm tra 0 rất gọn cho vòng lặp.

---

### Ví dụ 3: Vector Ngắt, Lưu Ngữ cảnh (Context Saving) & Xóa Cờ Ngắt (Timer0 Overflow)

**ATmega32 (AVR Assembly — đối chiếu p. 45, 83):**
```asm
.org 0x0000
    jmp  RESET          ; Vector 1: Reset
.org 0x0016             ; Vector 12: TIMER0 OVF riêng biệt!
    jmp  ISR_TMR0_OVF

RESET:
    ; BẮT BUỘC khởi tạo Stack Pointer lên đỉnh SRAM (RAMEND = 0x085F)
    ldi  r16, high(RAMEND)
    out  SPH, r16
    ldi  r16, low(RAMEND)
    out  SPL, r16
    ; ... cấu hình Timer0 & TIMSK (TOIE0=1) ...
    sei                 ; Bật ngắt toàn cục (SREG.I = 1)
MAIN:
    rjmp MAIN

ISR_TMR0_OVF:
    ; Lưu ngữ cảnh cực gọn bằng PUSH lên SRAM Stack
    push r16
    in   r16, SREG
    push r16

    ; Xử lý ngắt (KHÔNG cần polling nguồn ngắt, KHÔNG cần xóa cờ TOV0
    ; vì phần cứng AVR tự động xóa TOV0 khi nhảy vào vector $016!)
    ; ...

    pop  r16
    out  SREG, r16
    pop  r16
    reti                ; Tự động bật lại SREG.I = 1 và POP PC
```

**PIC16F877A (MPASM Assembly — đối chiếu Example 14-1, p. 154):**
```asm
W_TEMP      EQU 0x70    ; Đặt ở vùng RAM chung 0x70-0x7F (dùng được mọi Bank!)
STATUS_TEMP EQU 0x71
PCLATH_TEMP EQU 0x72

    ORG  0x0000
    GOTO MAIN           ; Reset Vector (Không cần khởi tạo Hardware Stack)

    ORG  0x0004         ; 1 INTERRUPT VECTOR DUY NHẤT cho cả 15 nguồn ngắt!
ISR:
    ; Lưu ngữ cảnh thủ công (không có PUSH/POP, dùng SWAPF để không hỏng cờ Z!)
    MOVWF W_TEMP        ; Lưu W
    SWAPF STATUS, W     ; Đảo nibble STATUS đưa vào W (không đổi cờ Z)
    CLRF  STATUS        ; Về Bank 0 bất kể trước đó đang ở Bank nào
    MOVWF STATUS_TEMP   ; Lưu STATUS
    MOVF  PCLATH, W
    MOVWF PCLATH_TEMP   ; Lưu PCLATH (nếu dùng nhiều Page)
    CLRF  PCLATH        ; Về Page 0

    ; BẮT BUỘC tự polling cờ để kiểm tra nguồn ngắt
    BTFSS INTCON, TMR0IF
    GOTO  EXIT_ISR
    ; ... xử lý ngắt Timer0 ...
    BCF   INTCON, TMR0IF ; BẮT BUỘC xóa cờ ngắt bằng phần mềm!

EXIT_ISR:
    ; Khôi phục ngữ cảnh
    MOVF  PCLATH_TEMP, W
    MOVWF PCLATH
    SWAPF STATUS_TEMP, W ; Đảo ngược lại nibble STATUS
    MOVWF STATUS         ; Khôi phục nguyên trạng thái cờ & Bank cũ
    SWAPF W_TEMP, F      ; Khôi phục W mà không làm ảnh hưởng cờ Z vừa khôi phục
    SWAPF W_TEMP, W
    RETFIE               ; Tự động bật lại INTCON.GIE = 1 và POP PC
```
> **Điểm khác biệt thấy ngay:** Đây là khác biệt kiến trúc lớn nhất giữa hai họ MCU. ATmega32 có bảng 21 vector + `PUSH/POP` + tự xóa cờ; PIC16F877A chỉ có 1 vector `0004h`, không có `PUSH/POP`, phải dùng mẹo `SWAPF` và vùng nhớ gương `70h–7Fh` để tránh làm hỏng cờ `Z` và sai Bank.

---

### Ví dụ 4: Đọc ADC 10-bit (Kênh 0, Canh phải)

**ATmega32 (AVR Assembly — đối chiếu p. 203, 214–217):**
```asm
; Khởi tạo ADC: Vref = AVCC (REFS0=1), kênh ADC0, ADLAR=0 (canh phải)
    ldi  r16, (1<<REFS0)
    out  ADMUX, r16
; Bật ADC (ADEN=1), Prescaler = 128 (ADPS2:0 = 111) cho Fosc = 16 MHz -> 125 kHz
    ldi  r16, (1<<ADEN)|(1<<ADPS2)|(1<<ADPS1)|(1<<ADPS0)
    out  ADCSRA, r16

READ_ADC0:
    sbi  ADCSRA, ADSC       ; Bắt đầu chuyển đổi
WAIT_ADC:
    sbic ADCSRA, ADSC       ; Chờ ADSC tự về 0 khi xong
    rjmp WAIT_ADC
    in   r16, ADCL          ; BẮT BUỘC đọc ADCL trước! (p. 203, 217)
    in   r17, ADCH          ; Rồi mới đọc ADCH (kết quả 10-bit trong r17:r16)
    ret
```

**PIC16F877A (MPASM Assembly — đối chiếu Section 11.0, p. 127–133):**
```asm
; Khởi tạo ADC: ADCON1 nằm ở Bank 1, ADCON0 nằm ở Bank 0!
    BSF   STATUS, RP0       ; Bank 1
    MOVLW b'10001110'       ; ADFM=1 (canh phải), ADCS2=0, PCFG=1110 (chỉ AN0 analog)
    MOVWF ADCON1
    BSF   TRISA, 0          ; RA0/AN0 là Input
    BCF   STATUS, RP0       ; Bank 0
    MOVLW b'10000001'       ; ADCS1:0=10 (Fosc/32), CHS=000 (AN0), ADON=1
    MOVWF ADCON0

READ_ADC0:
    CALL  DELAY_20US        ; BẮT BUỘC chờ thời gian lấy mẫu TACQ (~19.72 us, p. 130)
    BSF   ADCON0, GO        ; Bắt đầu chuyển đổi (GO/DONE = 1)
WAIT_ADC:
    BTFSC ADCON0, GO        ; Chờ GO/DONE tự về 0 khi xong
    GOTO  WAIT_ADC
    MOVF  ADRESH, W         ; Đọc byte cao (ADRESH ở Bank 0)
    MOVWF ADC_H
    BSF   STATUS, RP0       ; Phải chuyển sang Bank 1 để đọc byte thấp ADRESL!
    MOVF  ADRESL, W
    BCF   STATUS, RP0       ; Trở lại Bank 0
    MOVWF ADC_L             ; Kết quả 10-bit trong ADC_H:ADC_L
    RETURN
```
> **Điểm khác biệt thấy ngay:** Trên PIC, `ADRESH` (`1Eh`, Bank 0) và `ADRESL` (`9Eh`, Bank 1) nằm **khác Bank**, ngoài ra phải tự chèn delay `TACQ` trước khi set `GO`. Trên AVR, cả `ADCL`/`ADCH` cùng không gian I/O, chỉ cần nhớ quy tắc **đọc `ADCL` trước, `ADCH` sau** để khóa thanh ghi đồng bộ.

---

### Ví dụ 5: Truyền 1 Byte qua USART (Polling)

**ATmega32 (trích trực tiếp từ Datasheet p. 147):**
```asm
USART_Transmit:
    sbis UCSRA, UDRE        ; Chờ buffer truyền rỗng (UDRE = 1)
    rjmp USART_Transmit
    out  UDR, r16           ; Gửi byte trong r16
    ret
```

**PIC16F877A (đối chiếu Section 10.2.1, p. 115–116):**
```asm
; Giả sử đang ở Bank 0 (PIR1 = 0Ch, TXREG = 19h đều ở Bank 0)
USART_Transmit:
    BTFSS PIR1, TXIF        ; Chờ TXREG rỗng (TXIF = 1)
    GOTO  USART_Transmit
    MOVWF TXREG             ; Gửi byte đang nằm trong thanh ghi W
    RETURN
```
*(Ghi chú: Khi khởi tạo USART trên ATmega32 cần chú ý `UBRRH` và `UCSRC` dùng chung 1 địa chỉ I/O `$20`, phân biệt bằng bit `URSEL`, p. 158; còn trên PIC thì `TXSTA`/`SPBRG` ở Bank 1 còn `RCSTA`/`TXREG`/`RCREG` ở Bank 0.)*

---

### Ví dụ 6: Định địa chỉ Gián tiếp (Xóa 16 byte RAM liên tiếp)

**ATmega32 (dùng con trỏ `X` với tự tăng `X+`, p. 12, 330):**
```asm
    ldi  XH, high(0x0100)   ; Con trỏ X = $0100
    ldi  XL, low(0x0100)
    ldi  r16, 0x00          ; Giá trị cần ghi = 0
    ldi  r17, 16            ; Số byte = 16
CLR_LOOP:
    st   X+, r16            ; Ghi r16 vào (X) và TỰ ĐỘNG tăng X thêm 1 (2 clock)
    dec  r17
    brne CLR_LOOP
```

**PIC16F877A (trích từ Example 2-2, p. 31):**
```asm
    BCF   STATUS, IRP       ; Chọn Bank 0-1 cho định địa chỉ gián tiếp
    MOVLW 0x20              ; Con trỏ FSR = 0x20 (xóa 0x20..0x2F)
    MOVWF FSR
NEXT:
    CLRF  INDF              ; Xóa ô nhớ tại địa chỉ FSR trỏ tới
    INCF  FSR, F            ; Phải tự tăng con trỏ FSR bằng lệnh riêng
    BTFSS FSR, 4            ; Đã tới 0x30 (bit 4 đổi trạng thái) chưa?
    GOTO  NEXT
```

---

## 4. So sánh Mã hóa Mã máy (Machine-Code Encoding) — Liên hệ Component 3 & 4

Điểm khác biệt rất đáng chú ý khi làm **Component 3 (Dịch ASM sang Mã máy)** và **Component 4 (Python Mini Assembler)**:

1. **PIC16F87XA (`DS39582C`, Section 15.0, p. 159–160):**
   - **Mọi lệnh đều dài cố định 14-bit (1 word)** — chỉ có **3 định dạng cực kỳ đều đặn**:
     - Byte-oriented: `00 | opcode(4) | d(1) | f(7)` — VD: `ADDWF 0x20, 1` → `00 0111 1 0100000` = `0x07A0`
     - Bit-oriented: `01 | op(2) | b(3) | f(7)` — VD: `BSF 0x06, 0` → `01 01 000 0000110` = `0x1406`
     - Literal/Control: `11 | opcode(4) | k(8)` hoặc `10 | op(1) | k(11)` — VD: `MOVLW 0x55` → `11 0000 01010101` = `0x3055`
   - Các trường bit (`opcode`, `d`, `b`, `f`, `k`) nằm **liền mạch nhau**, không bị xẻ nhỏ → viết bộ mã hóa (`encoder.py`) gọn, rõ ràng, dễ kiểm chứng 100% với MPASM/`gpasm`.

2. **ATmega32 (`AVR Instruction Set`):**
   - Độ dài lệnh **không cố định** (16-bit và 32-bit).
   - Các bit toán hạng thường bị **tách rời (non-contiguous)** để nhồi tối đa thông tin vào 16-bit. Ví dụ lệnh `LDI Rd, K` (`1110 KKKK dddd KKKK`) tách hằng số 8-bit `K` làm 2 mảnh `K[7:4]` và `K[3:0]`; lệnh `ADD Rd, Rr` (`0000 11rd dddd rrrr`) tách `Rr` thành bit 9 (`r`) và 4 bit thấp (`rrrr`).
   - Do đó, bộ giải mã/mã hóa của AVR phức tạp hơn PIC16F877A đáng kể.

---

## 5. Kết luận Tóm tắt (Dùng cho Báo cáo & Q&A)

- **ATmega32 vượt trội về sức mạnh xử lý & tiện nghi lập trình:** nhanh hơn ~3.2 lần ở mức đỉnh (`16 MIPS` vs `5 MIPS`), RAM gấp ~5.5 lần (`2 KB` vs `368 B`), Flash lớn hơn ~2.2 lần (`32 KB` vs `14.3 KB`), không phân Bank/Page, 32 thanh ghi `R0–R31`, có nhân phần cứng, 21 vector ngắt riêng, Stack trên SRAM có `PUSH/POP`, ADC vi sai + VREF nội 2.56V, và chạy được không cần thạch anh ngoài.
- **PIC16F877A vượt trội về tính đơn giản của tập lệnh & một số đặc tính phần cứng chuyên biệt:** chỉ **35 lệnh 14-bit cố định** cực kỳ dễ học và lý tưởng để tự xây dựng Mini Assembler; độ bền Flash/EEPROM cao hơn (`100K/1M` chu kỳ vs `10K/100K`), dải áp thấp hơn ở bản `LF` (`2.0V` vs `2.7V`), có **2 Analog Comparator + CVREF 16 bậc**, **Parallel Slave Port (PSP)**, I²C hỗ trợ **10-bit**, và chỉ tốn **2 chân** cho nạp/debug ICSP/ICD (so với 4 chân JTAG của AVR).
