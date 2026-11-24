# TÀI LIỆU NGHIÊN CỨU KỸ THUẬT VI ĐIỀU KHIỂN PIC16F877A (BẢN NỘI DUNG THÔ 100%)
**Đích xuất bản:** `MCU_Study_Document.pdf` (Component 1 — Mục 5, ~10–15 trang PDF)  
**Nguồn kỹ thuật chính:** Microchip *PIC16F87XA Data Sheet* (`DS39582C`, 2013), *PICmicro Mid-Range MCU Family Reference Manual* (`DS33023A`), Atmel/Microchip *ATmega32(L) Data Sheet* (`2503Q–AVR–02/11`).

> **Hướng dẫn trình bày sang Word/LaTeX → PDF:** Các vị trí ghi `[CHÈN HÌNH: ...]` chỉ rõ số Figure và số trang trong file PDF gốc ở thư mục `docs/` để nhóm cắt dán đúng sơ đồ và trích dẫn chuẩn theo yêu cầu Mục 5.10.

---

## 5.1. Giới thiệu chung (Introduction)

### 5.1.1. Hãng sản xuất và họ vi điều khiển
- **Vi điều khiển lựa chọn:** **PIC16F877A** (thuộc dòng `PIC16F87XA`: `873A`, `874A`, `876A`, `877A`).
- **Hãng sản xuất:** **Microchip Technology Inc.** (Hoa Kỳ).
- **Họ kiến trúc:** **PICmicro Mid-Range 8-bit CMOS Enhanced Flash Microcontroller** — kiến trúc Harvard cải tiến với bus lệnh 14-bit và bus dữ liệu 8-bit (`DS39582C`, p. 1, 5).
- **Công nghệ chế tạo:** CMOS công suất thấp, tốc độ cao, thiết kế tĩnh hoàn toàn (fully static design — hoạt động từ DC đến 20 MHz), tích hợp bộ nhớ Flash/EEPROM bền bỉ (`100,000` chu kỳ ghi/xóa Flash điển hình và `1,000,000` chu kỳ ghi/xóa EEPROM điển hình, lưu dữ liệu > 40 năm, p. 1, 179).

### 5.1.2. Ứng dụng tiêu biểu
Nhờ tích hợp đầy đủ bộ chuyển đổi tương tự–số (ADC 10-bit), 3 bộ định thời, 2 kênh PWM, các chuẩn giao tiếp công nghiệp (USART, SPI, I²C), cổng song song PSP và 2 bộ so sánh tương tự trên cùng một vi mạch 40 chân giá thành hợp lý, `PIC16F877A` được ứng dụng rộng rãi trong:
- **Đo lường và giám sát cảm biến:** Hệ thống đo nhiệt độ/độ ẩm, vôn kế số, bộ ghi dữ liệu (data logger).
- **Điều khiển công nghiệp & tự động hóa:** Điều khiển tốc độ động cơ DC/Servo bằng PWM, điều khiển đèn giao thông, thang máy, tưới tiêu thông minh.
- **Thiết bị điện tử dân dụng & học thuật:** Khóa điện tử, đồng hồ số có báo thức, thiết bị gia dụng, và làm nền tảng giảng dạy kiến trúc vi điều khiển 8-bit trên toàn thế giới.

### 5.1.3. Thông số kỹ thuật chính (Specifications)

| Nhóm thông số | Đặc tính kỹ thuật của PIC16F877A (`DS39582C`, Table 1-1 p. 5, Section 17 pp. 173–179) |
| :--- | :--- |
| **Lõi CPU** | 8-bit RISC, kiến trúc Harvard, pipeline 2 tầng, **35 lệnh đơn từ (14-bit)** |
| **Tần số & Chu kỳ lệnh** | `DC – 20 MHz` (`1 TCY = 4 / FOSC`, tối thiểu `200 ns` @ 20 MHz → tối đa **5 MIPS**) |
| **Điện áp hoạt động (`VDD`)** | `4.0V – 5.5V` (`PIC16F877A`); `2.0V – 5.5V` (`PIC16LF877A`, tối đa 10 MHz) |
| **Bộ nhớ Chương trình (Flash)** | **8K × 14-bit words** (`8,192` từ lệnh ≈ 14.3 KB), hỗ trợ tự lập trình (self-reprogrammable) |
| **Bộ nhớ Dữ liệu (SRAM)** | **368 bytes** (tổ chức thành 4 Bank), kết hợp các thanh ghi chức năng đặc biệt (SFR) |
| **Bộ nhớ EEPROM dữ liệu** | **256 bytes** (`00h – FFh`), giữ dữ liệu > 40 năm |
| **Cổng vào/ra (GPIO)** | **33 chân I/O** trên 5 Port (`PORTA` 6b, `PORTB/C/D` 8b, `PORTE` 3b); dòng tối đa `25 mA/chân` |
| **Bộ định thời (Timers)** | 3 bộ: **Timer0** (8-bit), **Timer1** (16-bit, chạy được khi Sleep), **Timer2** (8-bit có `PR2`) |
| **Capture/Compare/PWM** | 2 module **CCP1, CCP2** (Capture 16-bit `12.5 ns`, Compare 16-bit `200 ns`, **PWM 10-bit**) |
| **ADC 10-bit** | **8 kênh** (`AN0–AN7`), độ phân giải 10-bit, điện áp tham chiếu cấu hình được |
| **Giao tiếp nối tiếp & song song** | **1 USART** (đồng bộ/bất đồng bộ), **1 MSSP** (SPI Master/Slave hoặc I²C 7/10-bit), **1 PSP** (8-bit) |
| **Ngoại vi tương tự khác** | **2 Analog Comparators** + bộ tạo áp tham chiếu nội **CVREF** 16 bậc |
| **Hệ thống Ngắt & Stack** | **15 nguồn ngắt** (1 vector `0004h`), Hardware Stack **8 mức × 13-bit** |
| **Tính năng đặc biệt** | WDT (RC nội độc lập), BOR, POR, PWRT (72 ms), OST (1024 TOSC), Sleep, ICSP/ICD 2 dây |
| **Đóng gói (Packages)** | 40-pin PDIP (phổ biến nhất cho học tập/mô phỏng), 44-pin PLCC, TQFP, QFN |

### 5.1.4. Lý do lựa chọn PIC16F877A cho dự án
1. **Khác biệt rõ rệt về kiến trúc so với ATmega32:** PIC16F877A đại diện tiêu biểu cho trường phái kiến trúc **Accumulator đơn (`W`) + RAM phân Bank + 1 vector ngắt + Stack phần cứng cố định**, tạo nên sự đối chiếu kiến trúc rất sâu sắc với AVR ATmega32 (32 thanh ghi đa dụng `R0–R31`, SRAM tuyến tính, 21 vector ngắt).
2. **Tập lệnh cực gọn (35 lệnh 14-bit) — lý tưởng cho Component 3 & 4:** Toàn bộ tập lệnh chỉ có 35 lệnh độ dài cố định 14-bit chia thành 3 định dạng bit liền mạch, giúp sinh viên hiểu bản chất dịch mã máy và xây dựng **Python GUI Mini Assembler** đạt độ chính xác 100% mà không bị rối bởi các mã hóa độ dài biến thiên.
3. **Tài liệu chính hãng đầy đủ & công cụ phổ biến:** Có datasheet `DS39582C`, sổ tay họ `DS33023A`, trình biên dịch **MPASM / `gpasm`**, và được hỗ trợ trực tiếp rất ổn định trên **Proteus** và **SimulIDE** (nằm ngay đầu danh sách khuyến nghị Mục 3.1.A của đề bài).
4. **Ngoại vi đa dạng:** Đáp ứng dư dả yêu cầu ứng dụng dùng tối thiểu 3 ngoại vi (ADC, Timer, PWM, Interrupt, USART, GPIO/LCD).

---

## 5.2. Kiến trúc CPU (CPU Architecture)

`[CHÈN HÌNH: Figure 1-2 – PIC16F874A/877A Block Diagram, DS39582C, trang 7]`

### 5.2.1. Kiến trúc Harvard và các Bus nội bộ
PIC16F877A áp dụng **kiến trúc Harvard** tách biệt hoàn toàn hai đường bus (`DS39582C`, Figure 1-2, p. 7):
- **Bus Chương trình (Program Bus — 14-bit):** Kết nối Flash Program Memory với thanh ghi lệnh (`Instruction Register`), cho phép đọc trọn vẹn một lệnh 14-bit (gồm cả opcode và toán hạng) trong một chu kỳ truy xuất.
- **Bus Dữ liệu (Data Bus — 8-bit):** Kết nối RAM/SFR, thanh ghi `W`, ALU, các cổng I/O và ngoại vi.
- **Bus Địa chỉ RAM (9-bit):** Hình thành từ 7-bit địa chỉ trực tiếp trong lệnh ghép với `RP1:RP0` (hoặc 8-bit `FSR` ghép với `IRP`), định địa chỉ tối đa `512` byte (`000h–1FFh`).
- **Bus Địa chỉ Chương trình (13-bit):** Nối từ Program Counter (`PC<12:0>`) tới Flash Memory và Hardware Stack 8 mức, định địa chỉ `8K` từ lệnh (`0000h–1FFFh`).

### 5.2.2. ALU 8-bit, Khối Điều khiển và Thanh ghi CPU
- **ALU (Arithmetic Logic Unit — 8-bit):** Thực hiện mọi phép toán cộng, trừ (bù 2), dịch/quay bit, logic (`AND`, `OR`, `XOR`, đảo bit) giữa thanh ghi làm việc `W` và bất kỳ thanh ghi tệp `f` nào hoặc hằng số `k`. Kết quả có thể ghi lại vào `W` (`d = 0`) hoặc vào chính thanh ghi `f` (`d = 1`).
- **Thanh ghi `W` (Working Register — 8-bit):** Thanh ghi tích lũy (Accumulator) duy nhất của CPU, không có địa chỉ trong bản đồ RAM, đóng vai trò toán hạng đầu vào mặc định cho ALU và trung gian truyền dữ liệu giữa các ô nhớ.
- **Khối Giải mã & Điều khiển (Instruction Decode & Control + Timing Generation):** Nhận lệnh 14-bit từ Instruction Register, chia xung clock đầu vào `OSC1` thành 4 pha không chồng lấn `Q1, Q2, Q3, Q4` tạo thành một chu kỳ lệnh (`TCY = 4 × TOSC`).
- **Thanh ghi `STATUS` (`03h, 83h, 103h, 183h` — truy cập từ mọi Bank, `Register 2-1`, p. 22):**

| Bit | Tên | Quyền / Reset | Chức năng chi tiết |
| :---: | :---: | :---: | :--- |
| 7 | `IRP` | R/W-0 | Chọn Bank cho định địa chỉ gián tiếp: `0` = Bank 0–1 (`00h–FFh`), `1` = Bank 2–3 (`100h–1FFh`) |
| 6–5 | `RP1:RP0` | R/W-00 | Chọn Bank cho định địa chỉ trực tiếp: `00`=Bank 0, `01`=Bank 1, `10`=Bank 2, `11`=Bank 3 |
| 4 | `~TO` | R-1 | Time-out bit: `1` sau POR/`CLRWDT`/`SLEEP`, `0` khi xảy ra WDT time-out |
| 3 | `~PD` | R-1 | Power-down bit: `1` sau POR/`CLRWDT`, `0` khi thực thi lệnh `SLEEP` |
| 2 | `Z` | R/W-x | Zero bit: `1` nếu kết quả phép toán ALU bằng `0`, ngược lại `0` |
| 1 | `DC` | R/W-x | Digit Carry / `~Borrow` (nhớ từ bit 3 sang bit 4); **đảo cực tính trong phép trừ** |
| 0 | `C` | R/W-x | Carry / `~Borrow` (nhớ từ bit 7); **đảo cực tính trong phép trừ** (`C=1` không mượn, `C=0` có mượn) |

- **Program Counter (`PC<12:0>`, `Figure 2-5`, p. 30):** Gồm `PCL` (8 bit thấp, địa chỉ `02h`, đọc/ghi trực tiếp) và `PCH` (5 bit cao, không đọc trực tiếp mà ghi gián tiếp thông qua thanh ghi giữ `PCLATH` tại `0Ah`).
- **Hardware Stack (8 mức × 13-bit, Mục 2.3.2, p. 30):** Tách biệt hoàn toàn khỏi RAM/Flash, con trỏ stack ẩn, hoạt động dạng **vòng tròn (circular buffer)** — nếu gọi lồng quá 8 mức (tính cả ngắt), lần `PUSH` thứ 9 sẽ ghi đè mức 1 mà **không có cờ báo tràn**. Không có lệnh `PUSH`/`POP` cho người dùng; chỉ tự động thực hiện bởi `CALL`, `RETURN`, `RETLW`, `RETFIE` và ngắt.

### 5.2.3. Cơ chế Pipeline 2 tầng và Chu kỳ thực thi lệnh (`Q1–Q4`)
Nhờ bus Harvard tách biệt, PIC16F877A thực hiện **pipeline 2 tầng** (nạp lệnh kế tiếp song song với thực thi lệnh hiện tại):
- Mỗi chu kỳ máy `TCY = 4 × TOSC` chia thành 4 pha (`DS39582C`, Figure 17-4, p. 182; `DS33023A`):
  - **Q1 (Decode):** Giải mã lệnh đang có trong Instruction Register; tăng `PC`.
  - **Q2 (Read):** Đọc dữ liệu từ thanh ghi `f` hoặc chân ngoại vi (pha *Read* của RMW).
  - **Q3 (Process):** ALU xử lý dữ liệu.
  - **Q4 (Write):** Ghi kết quả vào `W` hoặc `f` (pha *Write* của RMW), đồng thời hoàn tất nạp (Fetch) lệnh tiếp theo từ Flash.
- **Ảnh hưởng của rẽ nhánh:** Lệnh thông thường tốn **1 `TCY`**. Khi có lệnh làm thay đổi `PC` (`GOTO`, `CALL`, `RETURN`, `RETFIE`, `RETLW`, ghi `PCL`) hoặc lệnh bỏ qua có điều kiện thỏa mãn (`BTFSC`, `BTFSS`, `DECFSZ`, `INCFSZ`), lệnh đã nạp sẵn trong pipeline bị hủy (thay bằng một chu kỳ `NOP` ẩn) nên tổng thời gian thực thi là **2 `TCY`**.

```text
Chu kỳ máy:  |---- TCY 1 ----|---- TCY 2 ----|---- TCY 3 ----|---- TCY 4 ----|
Pha xung:    | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   | Q1 Q2 Q3 Q4   |
Fetch:       | Fetch Lệnh 1  | Fetch Lệnh 2  | Fetch Lệnh 3  | Fetch Target  |
Execute:     |               | Exec Lệnh 1   | Exec GOTO     | Flush (NOP)   | -> Exec Target
```

---

## 5.3. Tổ chức Bộ nhớ (Memory Organization)

PIC16F877A có 3 khối bộ nhớ độc lập: **Flash Program Memory**, **SRAM Data Memory (Register File)** và **Data EEPROM**.

### 5.3.1. Bộ nhớ Chương trình (Flash Program Memory — `Figure 2-1`, p. 15)
`[CHÈN HÌNH: Figure 2-1 – PIC16F876A/877A Program Memory Map and Stack, DS39582C, trang 15]`
- **Dung lượng:** `8,192 × 14-bit words` (`0000h – 1FFFh`).
- **Vector đặc biệt:**
  - **Reset Vector:** `0000h` (thường đặt lệnh `GOTO MAIN`).
  - **Interrupt Vector (duy nhất):** `0004h` (mọi nguồn ngắt đều nhảy về đây).
  - **Vùng cấu hình ngoài không gian người dùng:** ID Locations (`2000h–2003h`), Configuration Word (`2007h`).
- **Phân trang (Program Memory Paging — Mục 2.4, p. 30):** Do từ lệnh `CALL`/`GOTO` chỉ chứa **11-bit địa chỉ** (`2^11 = 2,048 words = 2K`), bộ nhớ `8K` được chia thành **4 Page**:
  - **Page 0:** `0000h – 07FFh` (`PCLATH<4:3> = 00`)
  - **Page 1:** `0800h – 0FFFh` (`PCLATH<4:3> = 01`)
  - **Page 2:** `1000h – 17FFh` (`PCLATH<4:3> = 10`)
  - **Page 3:** `1800h – 1FFFh` (`PCLATH<4:3> = 11`)
  - Khi gọi hàm hoặc nhảy sang trang khác, phải cập nhật `PCLATH<4:3>` (hoặc dùng chỉ thị `PAGESEL`). Lệnh `RETURN`/`RETFIE` khôi phục đủ 13-bit `PC` từ Stack nhưng **không** tự đổi lại `PCLATH`.

### 5.3.2. Bộ nhớ Dữ liệu RAM (Data Memory / Register File — `Figure 2-3`, p. 17)
`[CHÈN HÌNH: Figure 2-3 – PIC16F876A/877A Register File Map, DS39582C, trang 17]`
- **Cơ chế phân Bank:** Từ lệnh trực tiếp chỉ chứa 7-bit địa chỉ (`00h–7Fh` = 128 bytes/Bank), nên không gian 512 bytes (`000h–1FFh`) được chia thành **4 Bank**, chọn bằng `RP1:RP0` (`STATUS<6:5>`):

| Bank | `RP1:RP0` | Dải địa chỉ | Vùng SFR | Vùng GPR (RAM người dùng) | Vùng Shared RAM |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **Bank 0** | `00` | `000h–07Fh` | `00h–1Fh` (32B) | `20h–6Fh` (80B) + `70h–7Fh` (16B) = **96B** | `70h–7Fh` (16B gốc) |
| **Bank 1** | `01` | `080h–0FFh` | `80h–9Fh` (32B) | `A0h–EFh` (**80B**) | `F0h–FFh` → gương `70h–7Fh` |
| **Bank 2** | `10` | `100h–17Fh` | `100h–10Fh` (16B) | `110h–16Fh` (**96B**: 16B + 80B) | `170h–17Fh` → gương `70h–7Fh` |
| **Bank 3** | `11` | `180h–1FFh` | `180h–18Fh` (16B) | `190h–1EFh` (**96B**: 16B + 80B) | `1F0h–1FFh` → gương `70h–7Fh` |
| **Tổng GPR** | — | — | — | **96 + 80 + 96 + 96 = 368 bytes** | 16B dùng chung cả 4 Bank |

- **Các SFR quan trọng ánh xạ trên cả 4 Bank:** `INDF` (`00h`), `PCL` (`02h`), `STATUS` (`03h`), `FSR` (`04h`), `PCLATH` (`0Ah`), `INTCON` (`0Bh`) — truy cập được ở bất kỳ Bank nào mà không cần đổi `RP1:RP0`.
- **Phân bố các SFR ngoại vi tiêu biểu (`Table 2-1`, pp. 19–21):**
  - **Bank 0:** `TMR0 (01h)`, `PORTA–PORTE (05h–09h)`, `PIR1–PIR2 (0Ch–0Dh)`, `TMR1L/H (0Eh–0Fh)`, `T1CON (10h)`, `TMR2 (11h)`, `T2CON (12h)`, `SSPBUF/SSPCON (13h–14h)`, `CCPR1L/H, CCP1CON (15h–17h)`, `RCSTA/TXREG/RCREG (18h–1Ah)`, `CCPR2L/H, CCP2CON (1Bh–1Dh)`, `ADRESH (1Eh)`, `ADCON0 (1Fh)`.
  - **Bank 1:** `OPTION_REG (81h)`, `TRISA–TRISE (85h–89h)`, `PIE1–PIE2 (8Ch–8Dh)`, `PCON (8Eh)`, `SSPCON2/PR2/SSPADD/SSPSTAT (91h–94h)`, `TXSTA/SPBRG (98h–99h)`, `CMCON/CVRCON (9Ch–9Dh)`, `ADRESL (9Eh)`, `ADCON1 (9Fh)`.
  - **Bank 2:** `EEDATA (10Ch)`, `EEADR (10Dh)`, `EEDATH (10Eh)`, `EEADRH (10Fh)`.
  - **Bank 3:** `EECON1 (18Ch)`, `EECON2 (18Dh)` (thanh ghi ảo dùng mở khóa ghi EEPROM/Flash).

### 5.3.3. Bộ nhớ EEPROM Dữ liệu (256 bytes) & Tự ghi Flash (`Section 3.0`, pp. 33–39)
- Không ánh xạ trực tiếp vào RAM mà truy cập gián tiếp qua 6 thanh ghi SFR ở Bank 2–3 (`EEADR/H`, `EEDATA/H`, `EECON1`, `EECON2`).
- **Đọc EEPROM (`Example 3-1`, p. 35):** Ghi địa chỉ vào `EEADR` → `BCF EECON1, EEPGD` → `BSF EECON1, RD` → đọc dữ liệu ngay từ `EEDATA`.
- **Ghi EEPROM (`Example 3-2`, p. 35):** Đợi `EECON1.WR == 0` → ghi `EEADR`, `EEDATA` → `EEPGD = 0`, `WREN = 1` → **tắt ngắt `GIE = 0`** → thực hiện đúng chuỗi mở khóa bắt buộc 5 lệnh (`MOVLW 0x55 → MOVWF EECON2 → MOVLW 0xAA → MOVWF EECON2 → BSF EECON1, WR`) → bật lại `GIE`, xóa `WREN`. Thời gian ghi điển hình `4 ms` (tối đa `8 ms`, p. 179).
- **Ghi Flash (`Section 3.6`, p. 37):** Thực hiện theo **khối 4 words** (tự xóa trước khi ghi) với 2 lệnh `NOP` bắt buộc sau `BSF EECON1, WR`.

### 5.3.4. Các chế độ định địa chỉ (Addressing Modes — `Figure 2-6`, p. 31)
`[CHÈN HÌNH: Figure 2-6 – Direct/Indirect Addressing, DS39582C, trang 31]`
1. **Định địa chỉ Trực tiếp (Direct Addressing):** Ghép 2-bit `RP1:RP0` (`STATUS<6:5>`) với 7-bit `f` trong từ lệnh → địa chỉ 9-bit (`000h–1FFh`). Ví dụ: `MOVWF 0x20`.
2. **Định địa chỉ Gián tiếp (Indirect Addressing):** Ghi địa chỉ 8-bit vào `FSR` (`04h`), chọn nửa Bank bằng bit `IRP` (`STATUS<7>`), sau đó đọc/ghi thông qua thanh ghi ảo `INDF` (`00h`). Rất hữu ích khi duyệt mảng/chuỗi trong RAM.
3. **Định địa chỉ Tức thời (Immediate / Literal Addressing):** Giá trị hằng số 8-bit `k` nằm trực tiếp trong từ lệnh. Ví dụ: `MOVLW 0x55`, `ADDLW d'10'`.
4. **Định địa chỉ Nhảy / Gọi hàm (Program Branch Addressing):** 11-bit địa chỉ `k` trong lệnh `GOTO`/`CALL` ghép với `PCLATH<4:3>` tạo thành 13-bit `PC`; hoặc **Computed GOTO** (`ADDWF PCL, F`) để tra bảng hằng `RETLW`.

---

## 5.4. Cấu hình Chân (Pin Configuration — 40-pin PDIP)

`[CHÈN HÌNH: Pin Diagrams – 40-Pin PDIP PIC16F874A/877A, DS39582C, trang 3]`

### 5.4.1. Bảng đầy đủ 40 chân PIC16F877A (40-pin PDIP — `Table 1-3`, pp. 10–13)

| Chân | Tên chân | Loại | Đệm | Chức năng chính & Chức năng thay thế (Alternate Functions) |
| :---: | :--- | :---: | :---: | :--- |
| 1 | `~MCLR/VPP` | I/P | ST | Reset tích cực thấp (`~MCLR`) / Điện áp nạp cao áp `VPP` |
| 2 | `RA0/AN0` | I/O | TTL | Digital I/O hoặc Ngõ vào tương tự `AN0` *(mặc định Analog sau Reset)* |
| 3 | `RA1/AN1` | I/O | TTL | Digital I/O hoặc `AN1` *(mặc định Analog)* |
| 4 | `RA2/AN2/VREF-/CVREF` | I/O | TTL | Digital I/O, `AN2`, áp tham chiếu thấp `VREF-`, ngõ ra `CVREF` |
| 5 | `RA3/AN3/VREF+` | I/O | TTL | Digital I/O, `AN3`, áp tham chiếu cao `VREF+` |
| 6 | `RA4/T0CKI/C1OUT` | I/O | ST | Digital I/O (**ngõ ra Open-Drain**, cần điện trở kéo lên ngoài), xung `TMR0`, ngõ ra `C1OUT` |
| 7 | `RA5/AN4/~SS/C2OUT` | I/O | TTL | Digital I/O, `AN4`, chọn Slave SPI `~SS`, ngõ ra `C2OUT` |
| 8 | `RE0/~RD/AN5` | I/O | ST/TTL | Digital I/O, tín hiệu đọc PSP `~RD`, `AN5` *(mặc định Analog)* |
| 9 | `RE1/~WR/AN6` | I/O | ST/TTL | Digital I/O, tín hiệu ghi PSP `~WR`, `AN6` *(mặc định Analog)* |
| 10 | `RE2/~CS/AN7` | I/O | ST/TTL | Digital I/O, chọn chip PSP `~CS`, `AN7` *(mặc định Analog)* |
| 11 | `VDD` | P | — | Nguồn dương `+5V` (`4.0V – 5.5V`, cần tụ lọc `0.1 µF` sát chân) |
| 12 | `VSS` | P | — | Mass (`GND`, nối chung với chân 31) |
| 13 | `OSC1/CLKI` | I | ST/CMOS | Ngõ vào thạch anh / nguồn xung clock ngoài |
| 14 | `OSC2/CLKO` | O | — | Ngõ ra thạch anh (hoặc xuất `FOSC/4` ở chế độ RC) |
| 15 | `RC0/T1OSO/T1CKI` | I/O | ST | Digital I/O, ngõ ra dao động Timer1, ngõ vào xung đếm Timer1 |
| 16 | `RC1/T1OSI/CCP2` | I/O | ST | Digital I/O, ngõ vào dao động Timer1, **Capture2 / Compare2 / PWM2** |
| 17 | `RC2/CCP1` | I/O | ST | Digital I/O, **Capture1 / Compare1 / PWM1** |
| 18 | `RC3/SCK/SCL` | I/O | ST | Digital I/O, xung clock **SPI (`SCK`)** hoặc **I²C (`SCL`)** |
| 19–22 | `RD0/PSP0 – RD3/PSP3` | I/O | ST/TTL | Digital I/O (PORTD bit 0–3) hoặc Bus dữ liệu PSP bit 0–3 |
| 23 | `RC4/SDI/SDA` | I/O | ST | Digital I/O, **SPI Data In (`SDI`)** hoặc **I²C Data (`SDA`)** |
| 24 | `RC5/SDO` | I/O | ST | Digital I/O, **SPI Data Out (`SDO`)** |
| 25 | `RC6/TX/CK` | I/O | ST | Digital I/O, **USART Asynchronous TX** hoặc Synchronous Clock `CK` |
| 26 | `RC7/RX/DT` | I/O | ST | Digital I/O, **USART Asynchronous RX** hoặc Synchronous Data `DT` |
| 27–30 | `RD4/PSP4 – RD7/PSP7` | I/O | ST/TTL | Digital I/O (PORTD bit 4–7) hoặc Bus dữ liệu PSP bit 4–7 |
| 31 | `VSS` | P | — | Mass (`GND`) |
| 32 | `VDD` | P | — | Nguồn dương `+5V` |
| 33 | `RB0/INT` | I/O | TTL/ST | Digital I/O (có weak pull-up), **Ngắt ngoài `INT`** |
| 34–35 | `RB1, RB2` | I/O | TTL | Digital I/O (có weak pull-up) |
| 36 | `RB3/PGM` | I/O | TTL | Digital I/O hoặc chân kích hoạt **LVP** *(tắt bằng `_LVP_OFF` để dùng làm I/O)* |
| 37–38 | `RB4, RB5` | I/O | TTL | Digital I/O (weak pull-up + **Interrupt-on-Change**) |
| 39 | `RB6/PGC` | I/O | TTL/ST | Digital I/O (IOC + pull-up) hoặc **ICSP/ICD Clock (`PGC`)** |
| 40 | `RB7/PGD` | I/O | TTL/ST | Digital I/O (IOC + pull-up) hoặc **ICSP/ICD Data (`PGD`)** |

### 5.4.2. Hoạt động GPIO và các lưu ý thiết kế phần cứng quan trọng
- **Điều khiển chiều qua `TRISx`:** `1 = Input` (tổng trở cao, nhớ mẹo `1` giống chữ `I` = Input), `0 = Output` (giống chữ `O` = Output). Sau Reset, tất cả `TRISx` mặc định là `1` (Input) để an toàn mạch.
- **Hiện tượng Read-Modify-Write (RMW — Mục 4.1 p. 41, Mục 15.1 p. 159):** Do không có thanh ghi `LATx` riêng như PIC18, lệnh `BSF/BCF PORTx, b` sẽ đọc điện áp thực trên 8 chân vật lý, sửa 1 bit rồi ghi lại cả 8 bit. Nếu có chân khác cùng Port đang chịu tải dung lớn (chưa kịp lên mức 1) hoặc vừa chuyển mạch ở lệnh ngay trước đó, trạng thái bit đó có thể bị ghi đè sai. *Giải pháp:* dùng biến đệm `SHADOW_PORT` trong RAM rồi `MOVWF PORTx`, hoặc chèn `NOP`.
- **3 "bẫy" mặc định sau Reset trên PIC16F877A:**
  1. `PORTA` và `PORTE` mặc định là **Analog Input** (đọc số luôn ra `0`) → phải ghi `ADCON1 = 0x06` (Bank 1) nếu dùng làm Digital I/O.
  2. `RA4` có tầng ra **Open-Drain** → khi cấu hình làm Output phải gắn điện trở kéo lên ngoài (VD `4.7 kΩ – 10 kΩ`) lên `VDD`.
  3. `RB3/PGM` mặc định bật chế độ **Low-Voltage Programming (`LVP = 1`)** → phải khai báo `_LVP_OFF` trong `__CONFIG` (hoặc kéo xuống GND) để dùng `RB3` như chân I/O bình thường.

### 5.4.3. Mạch Xung nhịp, Reset (`~MCLR`) và Nguồn điện
- **Xung nhịp (`Section 14.2`, pp. 145–146 — `[CHÈN HÌNH: Figure 14-1, p. 145]`):** Hỗ trợ 4 chế độ cấu hình qua `FOSC1:FOSC0`:
  - `LP` (Low-Power Crystal, `32 kHz – 200 kHz`, `C1 = C2 = 15–33 pF`)
  - `XT` (Crystal/Resonator, `≤ 4 MHz`, `C1 = C2 = 15–33 pF` — phổ biến nhất cho `4 MHz`, cho `1 TCY = 1 µs`)
  - `HS` (High-Speed Crystal, `4 – 20 MHz`, `C1 = C2 = 15–33 pF` — phổ biến cho `20 MHz`, cho `1 TCY = 200 ns`)
  - `RC` (Mạch R–C ngoài, `3 kΩ ≤ REXT ≤ 100 kΩ`, `CEXT > 20 pF`, giá rẻ nhưng sai số cao).
- **Mạch Reset `~MCLR` (`Figure 14-5`, p. 148):** Microchip khuyến cáo không nối thẳng `~MCLR` vào `VDD` mà qua mạch RCR (`R1 = 10 kΩ < 40 kΩ`, `R2 = 1 kΩ – 10 kΩ` hạn dòng ESD, tụ `C1 = 0.1 µF`, kèm nút nhấn Reset nối xuống `VSS`). Khi bật nguồn có sẵn `POR` + `PWRT` (`72 ms`) + `OST` (`1024 TOSC`) giúp mạch khởi động ổn định.
- **Yêu cầu nguồn (`Section 17.0`, pp. 173–176):** Cấp đủ cả 2 cặp nguồn (`VDD` chân 11 & 32, `VSS` chân 12 & 31), gắn tụ gốm lọc nhiễu `0.1 µF` sát mỗi cặp chân. Dòng tiêu thụ điển hình: `1.6 mA` @ `4 MHz / 5.5V`, `7 mA` @ `20 MHz / 5.5V`; ở chế độ `SLEEP` (tắt WDT) chỉ còn `1.5 µA` điển hình. Dòng sink/source tối đa `25 mA/chân`, tổng `200 mA` cho cụm `PORTA+B+E` và `200 mA` cho cụm `PORTC+D`.

---

## 5.5. Tập lệnh (Instruction Set — `Section 15.0`, pp. 159–165)

`[CHÈN HÌNH: Figure 15-1 – General Format for Instructions, DS39582C, trang 159]`

- PIC16F877A có tổng cộng **35 lệnh đơn từ**, độ dài cố định **14-bit (1 word)**, chia làm 3 nhóm chính:
  1. **Byte-oriented File Register Operations (18 lệnh):** `ADDWF`, `ANDWF`, `CLRF`, `CLRW`, `COMF`, `DECF`, `DECFSZ`, `INCF`, `INCFSZ`, `IORWF`, `MOVF`, `MOVWF`, `NOP`, `RLF`, `RRF`, `SUBWF`, `SWAPF`, `XORWF`.
     - Cấu trúc 14-bit: `[13:8 OPCODE (6b)] | [7 d (1b)] | [6:0 f (7b)]` (`d = 0` lưu `W`, `d = 1` lưu `f`).
  2. **Bit-oriented File Register Operations (4 lệnh):** `BCF`, `BSF`, `BTFSC`, `BTFSS`.
     - Cấu trúc 14-bit: `[13:10 OPCODE (4b)] | [9:7 b (3b)] | [6:0 f (7b)]`.
  3. **Literal and Control Operations (13 lệnh):** `ADDLW`, `ANDLW`, `CALL`, `CLRWDT`, `GOTO`, `IORLW`, `MOVLW`, `RETFIE`, `RETLW`, `RETURN`, `SLEEP`, `SUBLW`, `XORLW`.
     - Cấu trúc hằng số 8-bit: `[13:8 OPCODE (6b)] | [7:0 k (8b)]`.
     - Cấu trúc nhảy/gọi 11-bit (`CALL`/`GOTO`): `[13:11 OPCODE (3b)] | [10:0 k (11b)]`.
- **Ví dụ một số lệnh quan trọng và lưu ý đặc biệt:**
  - `MOVLW 0x35` (`11 0000 0011 0101` = `0x3035`): Nạp hằng số `0x35` vào `W` (1 `TCY`, không đổi cờ).
  - `MOVWF 0x20` (`00 0000 1010 0000` = `0x00A0`): Ghi `W` vào thanh ghi `0x20` (1 `TCY`).
  - `SUBWF f, d` (`(f) - (W) → dest`) và `SUBLW k` (`k - (W) → W`): Phép trừ cộng bù 2, **cờ `C` đảo cực tính** (`C = 1` nếu kết quả ≥ 0 / không mượn; `C = 0` nếu kết quả < 0 / có mượn).
  - `DECFSZ COUNT, F`: Giảm `COUNT` đi 1, nếu bằng `0` thì bỏ qua lệnh ngay sau (thường là `GOTO LOOP`) — cực kỳ hiệu quả cho vòng lặp trễ.
  - `SWAPF STATUS, W`: Đảo 2 nibble của `STATUS` đưa vào `W` mà **không ảnh hưởng cờ `Z`** — kỹ thuật chuẩn bắt buộc khi lưu ngữ cảnh trong ngắt (`Example 14-1`, p. 154).
  - *(Bảng đầy đủ toàn bộ 35 lệnh, mã máy 14-bit và ví dụ dịch tay được trình bày chi tiết tại tài liệu kèm theo: `Instruction_Set_Opcode_Table.pdf`.)*

---

## 5.6. Các Module Ngoại vi (Peripheral Modules)

### 5.6.1. GPIO (`Section 4.0`, pp. 41–52)
Gồm 5 Port (`PORTA` 6-bit, `PORTB/C/D` 8-bit, `PORTE` 3-bit) với các thanh ghi `PORTx` (Bank 0) và `TRISx` (Bank 1). Riêng `PORTB` có điện trở kéo lên nội bật đồng loạt qua `OPTION_REG<7>` (`~RBPU = 0`) và ngắt thay đổi trạng thái (Interrupt-on-Change) trên `RB7:RB4`.

### 5.6.2. Các Bộ định thời (Timers — `Sections 5.0–7.0`, pp. 53–62)

| Đặc điểm | **Timer0** (`TMR0`, `OPTION_REG`) | **Timer1** (`TMR1H:TMR1L`, `T1CON`) | **Timer2** (`TMR2`, `PR2`, `T2CON`) |
| :--- | :--- | :--- | :--- |
| **Độ rộng** | 8-bit (`00h–FFh`) | **16-bit** (`0000h–FFFFh`) | 8-bit (`00h` đến `PR2`) |
| **Prescaler** | `1:2` đến `1:256` *(dùng chung với WDT!)* | `1:1, 1:2, 1:4, 1:8` (`T1CKPS1:0`) | `1:1, 1:4, 1:16` (`T2CKPS1:0`) |
| **Postscaler** | Không | Không | `1:1` đến `1:16` (`TOUTPS3:0`) |
| **Nguồn xung** | Nội (`FOSC/4`) hoặc ngoài `RA4/T0CKI` | Nội (`FOSC/4`) hoặc thạch anh `32.768 kHz` (`T1OSCEN`) | Chỉ xung nội (`FOSC/4`) |
| **Chạy khi Sleep** | Không | **Có** (chế độ Counter bất đồng bộ) | Không |
| **Cờ / Bật ngắt** | `INTCON.TMR0IF` / `TMR0IE` | `PIR1.TMR1IF` / `TMR1IE` (+ `PEIE`) | `PIR1.TMR2IF` / `TMR2IE` (+ `PEIE`) |
| **Công thức định thời** | $T = (256 - \text{TMR0}) \times \text{PS} \times \frac{4}{F_{\text{OSC}}}$ | $T = (65536 - \text{TMR1}) \times \text{PS} \times \frac{4}{F_{\text{OSC}}}$ | $T = (\text{PR2}+1) \times \text{PS} \times \text{Post} \times \frac{4}{F_{\text{OSC}}}$ |

*(Lưu ý: Ghi vào `TMR0` sẽ xóa bộ đếm prescaler và tạm dừng tăng `TMR0` trong 2 chu kỳ lệnh `TCY`.)*

### 5.6.3. Hệ thống Ngắt (Interrupt System — `Section 14.11–14.12`, pp. 153–154)
`[CHÈN HÌNH: Figure 14-10 – Interrupt Logic, DS39582C, trang 153]`
- **15 nguồn ngắt** nhưng **chỉ có 1 vector ngắt duy nhất tại `0004h`**, phân làm 2 nhóm:
  - **Nhóm Core (`INTCON` `0Bh` — chỉ cần `GIE = 1` + bit enable riêng):** `TMR0IF/TMR0IE` (tràn Timer0), `INTF/INTE` (ngắt ngoài cạnh lên/xuống trên `RB0/INT` chọn bởi `OPTION_REG.INTEDG`), `RBIF/RBIE` (thay đổi trạng thái `RB7:RB4` — phải đọc `PORTB` trước khi xóa `RBIF`).
  - **Nhóm Ngoại vi (`PIE1/PIR1` `8Ch/0Ch` & `PIE2/PIR2` `8Dh/0Dh` — bắt buộc bật cả `GIE = 1` và `PEIE = 1`):** `PSPIF`, `ADIF` (ADC xong), `RCIF`/`TXIF` (USART), `SSPIF` (SPI/I²C), `CCP1IF`, `TMR2IF`, `TMR1IF`, `CMIF` (Comparator), `EEIF` (ghi EEPROM xong), `BCLIF` (va chạm bus I²C), `CCP2IF`.
- **Cơ chế vào/thoát ISR:** Khi ngắt xảy ra, phần cứng tự động tắt `GIE = 0` (chống ngắt lồng nhau), đẩy `PC` vào Stack và nhảy tới `0004h` (độ trễ 3–4 `TCY`). Trong ISR, phần mềm **phải tự lưu `W`, `STATUS`, `PCLATH`** vào vùng Shared RAM `70h–7Fh` (dùng `SWAPF STATUS, W`), **tự kiểm tra (polling) cờ ngắt**, **tự xóa cờ ngắt bằng phần mềm**, khôi phục ngữ cảnh rồi kết thúc bằng `RETFIE` (tự bật lại `GIE = 1` và POP `PC`).

### 5.6.4. Bộ chuyển đổi ADC 10-bit (`Section 11.0`, pp. 127–133)
`[CHÈN HÌNH: Figure 11-1 – A/D Block Diagram, trang 129 & Figure 11-4 – A/D Result Justification, trang 132]`
- **8 kênh đơn cực (`AN0–AN7`)**, chọn qua `ADCON0<5:3>` (`CHS2:0`), bật bằng `ADCON0.ADON = 1`, khởi động chuyển đổi bằng `ADCON0.GO/DONE = 1`.
- **Cấu hình chân Analog/Digital & `VREF`:** Qua `ADCON1<3:0>` (`PCFG3:0`, `Register 11-2`, p. 128). Một số giá trị hay dùng:
  - `PCFG = 0110` (`ADCON1 = 0x06`): Toàn bộ là Digital I/O.
  - `PCFG = 1110` (`ADCON1 = 0x8E` khi `ADFM = 1`): Chỉ `AN0` là Analog (`VREF+ = VDD`, `VREF- = VSS`), các chân còn lại là Digital.
  - `PCFG = 0000`: Cả 8 kênh `AN0–AN7` là Analog.
- **Định dạng kết quả 10-bit (`ADCON1.ADFM`):**
  - `ADFM = 1` (Canh phải — 10-bit): `ADRESH<1:0>` (Bank 0) chứa 2 bit cao, `ADRESL<7:0>` (Bank 1) chứa 8 bit thấp.
  - `ADFM = 0` (Canh trái — tiện khi chỉ cần 8-bit): đọc trực tiếp 8 bit cao tại `ADRESH` (Bank 0).
- **Thông số thời gian bắt buộc:**
  - **Chu kỳ xung ADC (`TAD` ≥ `1.6 µs`, `Table 11-1`, p. 131):** Tổng thời gian chuyển đổi là `12 TAD`. Với `FOSC = 4 MHz` chọn `FOSC/8` (`TAD = 2.0 µs`); với `FOSC = 20 MHz` chọn `FOSC/32` (`TAD = 1.6 µs`) hoặc `FOSC/64` (`TAD = 3.2 µs`).
  - **Thời gian lấy mẫu (`TACQ`, `Equation 11-1`, p. 130):** Bắt buộc chờ tối thiểu **`19.72 µs`** (thực tế chọn `20–40 µs`) sau khi chọn kênh mới trước khi set `GO/DONE = 1` để tụ giữ mẫu `CHOLD = 120 pF` nạp đầy. Trở kháng nguồn tương tự khuyến nghị `RS ≤ 2.5 kΩ`.
  - **Công thức quy đổi điện áp:** $\text{ADC}_{10\text{bit}} = \left\lfloor \frac{V_{\text{IN}} - V_{\text{REF}-}}{V_{\text{REF}+} - V_{\text{REF}-}} \times 1023 \right\rfloor$ (với `VREF = 5V`, mỗi bậc `1 LSB ≈ 4.887 mV`).

### 5.6.5. Truyền thông nối tiếp: USART và MSSP (SPI / I²C)
1. **USART (`Section 10.0`, pp. 111–125):** Chân `RC6/TX` & `RC7/RX` (lưu ý đặt `TRISC<7:6> = 1` khi bật `RCSTA.SPEN = 1`, p. 111).
   - Thanh ghi điều khiển: `TXSTA` (`98h`, Bank 1), `SPBRG` (`99h`, Bank 1), `RCSTA` (`18h`, Bank 0), `TXREG` (`19h`, Bank 0), `RCREG` (`1Ah`, Bank 0 — FIFO 2 byte).
   - **Công thức Baud Rate bất đồng bộ (`SYNC = 0`, `Table 10-1`, p. 113):**
     - Tốc độ thấp (`BRGH = 0`): $\text{Baud} = \frac{F_{\text{OSC}}}{64(X + 1)}$
     - Tốc độ cao (`BRGH = 1`, sai số nhỏ hơn): $\text{Baud} = \frac{F_{\text{OSC}}}{16(X + 1)}$
     - Ví dụ cấu hình chuẩn **9600 bps** (`Table 10-4`, p. 114): tại `FOSC = 4 MHz` → `BRGH = 1, SPBRG = 25` (sai số `0.16%`); tại `FOSC = 20 MHz` → `BRGH = 1, SPBRG = 129` (sai số `0.16%`).
2. **MSSP (`Section 9.0`, pp. 71–109):** Một phần cứng dùng chung cho **SPI** *hoặc* **I²C** (không chạy đồng thời):
   - **SPI:** Hỗ trợ cả 4 chế độ `(CKP, CKE)`, tốc độ Master `FOSC/4`, `FOSC/16`, `FOSC/64` hoặc `TMR2/2` qua chân `RC3/SCK`, `RC4/SDI`, `RC5/SDO` (và `RA5/~SS` ở chế độ Slave).
   - **I²C:** Hỗ trợ Master/Multi-Master/Slave, địa chỉ **7-bit và 10-bit**, phát hiện va chạm bus (`BCLIF`), clock stretching (`CKP`), tốc độ Master $F_{\text{SCL}} = \frac{F_{\text{OSC}}}{4(\text{SSPADD} + 1)}$ (`100 kHz` / `400 kHz`) trên `RC3/SCL` & `RC4/SDA` (cần điện trở kéo lên ngoài `4.7 kΩ`).

### 5.6.6. Module CCP1/CCP2 (PWM 10-bit) và Các module phụ (`Sections 8.0, 12.0, 13.0`)
- **PWM 10-bit (`Section 8.3`, pp. 67–68):** Xuất xung tại `RC2/CCP1` (`CCP1CON<3:0> = 11xx`) và `RC1/CCP2`, dùng chung nguồn định thời `Timer2`:
  - $\text{PWM Period} = [(\text{PR2}) + 1] \times 4 \times T_{\text{OSC}} \times (\text{TMR2 Prescale})$
  - $\text{PWM Duty Cycle} = (\text{CCPR1L}:\text{CCP1CON}\langle 5:4 \rangle) \times T_{\text{OSC}} \times (\text{TMR2 Prescale})$
  - Độ phân giải tối đa (`Equation 8-1`, p. 67): $\text{Resolution} = \frac{\log(F_{\text{OSC}} / F_{\text{PWM}})}{\log 2}\text{ bits}$ (tối đa 10-bit khi `PR2 = 0xFF`, VD tại `20 MHz`, Prescaler `16` → `1.22 kHz` đạt đủ 10-bit, `Table 8-3`, p. 68).
- **2 Analog Comparators & CVREF (`Sections 12–13`, pp. 135–142):** So sánh tín hiệu tương tự trên `RA0–RA3` với nhau hoặc với điện áp tham chiếu nội 16 bậc `CVREF` (`CVRCON`), kết quả xuất ra `CMCON<7:6>` hoặc trực tiếp ra chân `RA4/RA5`.
- **Parallel Slave Port (`Section 4.6`, pp. 51–52):** Biến `PORTD` thành bus dữ liệu song song 8-bit giao tiếp vi xử lý ngoài điều khiển bằng `RE0/~RD`, `RE1/~WR`, `RE2/~CS` khi bật `TRISE.PSPMODE = 1`.

---

## 5.7. Môi trường Lập trình Assembly (Assembly Programming Environment)

### 5.7.1. Công cụ biên dịch và IDE (`DS39582C`, Section 16.0, pp. 167–168)
1. **MPLAB IDE v8.92 / MPLAB X IDE (phiên bản ≤ v5.35) + MPASM Assembler:**
   - **MPASM** là trình hợp dịch macro chuẩn của Microchip hỗ trợ toàn bộ tập lệnh PIC16, đi kèm bộ mô phỏng phần mềm `MPLAB SIM` và trình liên kết `MPLINK`.
   - *Lưu ý quan trọng về phiên bản:* Từ **MPLAB X v5.40 trở lên**, Microchip đã gỡ bỏ MPASM (32-bit) và thay bằng `XC8 pic-as` (cú pháp chỉ thị khác). Vì vậy khi lập trình theo đúng cú pháp chuẩn trong datasheet `DS39582C`, nhóm sử dụng **MPASM** (MPLAB IDE v8.92 / MPLAB X v5.35) hoặc bộ thay thế tương thích 100% là **`gpasm`**.
2. **`gputils` (`gpasm` / `gplink` / `gpdasm`) — Mã nguồn mở (Windows/Linux):**
   - Tương thích cú pháp MPASM gần như tuyệt đối (cùng file header `p16f877a.inc`), rất nhẹ, chạy trực tiếp qua dòng lệnh (`gpasm -p p16f877a main.asm`), cực kỳ thuận tiện để biên dịch tự động và **đối chiếu kiểm chứng (Verification)** với Python Mini Assembler ở Component 4.

### 5.7.2. Cấu trúc chuẩn của một file mã nguồn Assembly (`.asm`)

```asm
;====================================================================
; Tiêu đề dự án, tên tác giả, tần số thạch anh (VD: 4 MHz / 20 MHz)
;====================================================================
    LIST        P=16F877A          ; 1. Khai báo dòng MCU mục tiêu
    #include    <p16f877a.inc>     ; 2. Nạp định nghĩa tên & địa chỉ SFR
    ERRORLEVEL  -302               ;    (Tùy chọn) Tắt cảnh báo nhắc Bank 1

    ; 3. Khai báo Configuration Word tại địa chỉ 2007h (Register 14-1, p. 144)
    __CONFIG _CP_OFF & _DEBUG_OFF & _WRT_OFF & _CPD_OFF & _LVP_OFF & _BODEN_OFF & _PWRTE_ON & _WDT_OFF & _XT_OSC

; 4. Khai báo biến người dùng (RAM Bank 0 & Shared RAM 0x70-0x7F)
    CBLOCK  0x20
        COUNTER1
        COUNTER2
        ADC_LOW
        ADC_HIGH
    ENDC

    CBLOCK  0x70                   ; Vùng Shared RAM cho lưu ngữ cảnh ISR
        W_TEMP
        STATUS_TEMP
        PCLATH_TEMP
    ENDC

; 5. Vector Reset (0x0000) & Vector Ngắt (0x0004)
    ORG     0x0000
    GOTO    MAIN

    ORG     0x0004
ISR:
    ; ... Lưu ngữ cảnh, kiểm tra cờ ngắt, xử lý, xóa cờ, khôi phục ...
    RETFIE

; 6. Chương trình chính & các chương trình con
MAIN:
    ; ... Khởi tạo ADCON1, TRISx, ngoại vi ...
LOOP:
    ; ... Vòng lặp chính ...
    GOTO    LOOP

    END                            ; 7. Kết thúc file nguồn
```

### 5.7.3. Bảng các Chỉ thị Hợp dịch (MPASM Assembler Directives) quan trọng

| Chỉ thị (Directive) | Cú pháp ví dụ | Chức năng |
| :--- | :--- | :--- |
| `LIST` | `LIST P=16F877A, R=DEC` | Thiết lập loại MCU, hệ cơ số mặc định (`DEC`/`HEX`), định dạng file `.lst` |
| `#include` / `INCLUDE` | `#include <p16f877a.inc>` | Chèn tệp tiêu đề chứa hằng số địa chỉ SFR (`PORTB`, `STATUS`, `ADCON1`...) |
| `__CONFIG` | `__CONFIG 0x3F39` *(hoặc macro)* | Ghi giá trị 14-bit vào Configuration Word tại `2007h` (Osc, WDT, PWRT, LVP, CP) |
| `EQU` | `LED_PIN EQU 0x00` | Gán tên biểu tượng cố định cho một hằng số hoặc địa chỉ thanh ghi |
| `CBLOCK` ... `ENDC` | `CBLOCK 0x20 ... ENDC` | Cấp phát liên tiếp địa chỉ RAM cho danh sách nhiều biến |
| `ORG` | `ORG 0x0000` / `ORG 0x0004` | Đặt địa chỉ bộ nhớ chương trình (Program Memory) bắt đầu cho đoạn mã phía sau |
| `BANKSEL` | `BANKSEL TRISB` | Tự động sinh 2 lệnh `BCF/BSF STATUS, RP0/RP1` để chuyển sang đúng Bank của thanh ghi |
| `PAGESEL` | `PAGESEL SUB_P1` | Tự động sinh lệnh chỉnh `PCLATH<4:3>` trước khi `CALL`/`GOTO` sang trang khác |
| `DT` (Define Table) | `DT "TEMP=", 0` | Sinh chuỗi lệnh `RETLW <char>` liên tiếp cho bảng tra cứu ký tự LCD |
| `DW` / `DE` | `DE 0x10, 0x20` | Định nghĩa dữ liệu 14-bit trong Flash (`DW`) hoặc khởi tạo dữ liệu EEPROM (`ORG 0x2100`, `DE`) |
| `#DEFINE` | `#DEFINE LED PORTB, 0` | Thay thế chuỗi văn bản (macro text substitution) giúp code dễ đọc hơn |
| `ERRORLEVEL` | `ERRORLEVEL -302` | Lọc/tắt thông báo nhắc chuyển Bank (`Message [302]`) khi đã quản lý Bank thủ công |
| `END` | `END` | Đánh dấu kết thúc mã nguồn (bắt buộc ở cuối file `.asm`) |

### 5.7.4. Bảng giải mã Configuration Word 14-bit (`2007h` — `Register 14-1`, p. 144)
Giá trị xóa trắng (unprogrammed) là `3FFFh`. Với cấu hình thông dụng cho thạch anh `4 MHz` (`_XT_OSC`, tắt WDT/LVP/CP/BOR, bật PWRT):
- Bit `13 (CP)=1`, `12=1`, `11 (DEBUG)=1`, `10:9 (WRT)=11`, `8 (CPD)=1`, `7 (LVP)=0`, `6 (BOREN)=0`, `5:4=11`, `3 (~PWRTEN)=0`, `2 (WDTEN)=0`, `1:0 (FOSC)=01` → Nhị phân `11 1111 0011 0001` = **`0x3F31`** (với thạch anh `20 MHz` đổi `FOSC=10` → **`0x3F32`**).

### 5.7.5. Quy trình biên dịch và Định dạng đầu ra Intel HEX (`INHX32M`)
1. **Quy trình biên dịch:**
   ```text
   main.asm (+ p16f877a.inc)
        │
        ▼  [MPASM / gpasm]
        ├──► main.hex  (Mã máy dạng Intel HEX — nạp vào Proteus / mạch thật)
        ├──► main.lst  (Listing file: Địa chỉ | Mã Hex 14-bit | Dòng ASM gốc — dùng kiểm chứng!)
        ├──► main.err  (Báo cáo lỗi cú pháp & cảnh báo)
        └──► main.cof  (File debug có symbol cho MPLAB SIM / Proteus debug từng bước)
   ```
2. **Định dạng Intel HEX (`:LLAAAATT[DD...]CC`):**
   - `:` Ký tự bắt đầu bản ghi.
   - `LL`: Số byte dữ liệu trên dòng.
   - `AAAA`: **Địa chỉ byte** (lưu ý đặc thù PIC16: mỗi từ lệnh 14-bit chiếm 2 byte trong file HEX nên **`AAAA = 2 × Word_Address`**).
   - `TT`: Loại bản ghi (`00` = Data, `01` = End of File `:00000001FF`, `04` = Extended Linear Address).
   - `DD...`: Các byte dữ liệu của từ lệnh 14-bit lưu theo thứ tự **Little-Endian (Low Byte trước, High Byte sau)**.
   - `CC`: Checksum 8-bit = bù 2 của tổng tất cả các byte trong dòng (`(0x100 - (sum & 0xFF)) & 0xFF`).
   - *Ví dụ thực tế:* Lệnh tại địa chỉ `0x0000`: `MOVLW 0x55` (`0x3055`) và tại `0x0001`: `MOVWF 0x20` (`0x00A0`):
     - Byte theo Little-Endian: `55 30 A0 00` tại địa chỉ byte `0000`.
     - Tổng byte: `0x04 + 0x00 + 0x00 + 0x00 + 0x55 + 0x30 + 0xA0 + 0x00 = 0x129` → Checksum = `(-0x29) & 0xFF = 0xD7`.
     - Dòng Intel HEX hoàn chỉnh: **`:040000005530A000D7`**.

### 5.7.6. Cách nạp Firmware và cấu hình vào phần mềm mô phỏng
- **Trên Proteus ISIS:**
  1. Đặt linh kiện `PIC16F877A` (cùng thạch anh, mạch Reset `~MCLR` kéo lên `+5V` qua trở `10 kΩ`, ngoại vi).
  2. Double-click vào IC `PIC16F877A` → mục **Program File**: trỏ tới file `.hex` vừa biên dịch.
  3. Mục **Processor Clock Frequency**: nhập chính xác tần số thạch anh khớp với code ASM (VD `4MHz` hoặc `20MHz`) — *Proteus dùng tham số này để tính tốc độ chạy mô phỏng*.
  4. Mục **Configuration Word**: để mặc định đọc từ file `.hex` (hoặc nhập khớp `0x3F31`/`0x3F32`). Nhấn Play để chạy.
- **Trên SimulIDE:**
  1. Kéo thả `PIC16F877A` từ thư mục *Micro → PIC*, gắn nguồn và ngoại vi.
  2. Chuột phải vào IC → **Load Firmware** → chọn file `.hex`; chuột phải → **Properties** chỉnh `Frequency` khớp với code.

---

## 5.8. Dự án Ứng dụng: Đề tài #15 — Hệ thống Tưới cây Thông minh (Smart Irrigation Controller)

### 5.8.1. Mục tiêu và 5 Ngoại vi phần cứng khai thác (Vượt mức tối thiểu ≥ 3 ngoại vi)
Xây dựng hệ thống tưới cây tự động/thủ công thông minh sử dụng vi điều khiển **PIC16F877A (`4 MHz`)** lập trình hoàn toàn bằng **Assembly (`smart_irrigation.asm`, 417 words gọn trong Page 0)**. Hệ thống đo độ ẩm đất thời gian thực (`0%–99%`), điều khiển máy bơm nước có **dải trễ chống bật/tắt liên tục (Hysteresis `10%`)**, cảnh báo khô hạn nặng (`< 20%`), cho phép chuyển chế độ **AUTO / MANUAL** bằng ngắt ngoài và lưu ngưỡng độ ẩm vào **EEPROM nội**.

5 ngoại vi phần cứng được tích hợp đồng thời:
1. **ADC 10-bit (`RA0/AN0`, canh trái 8-bit tại `ADRESH`):** Đọc tín hiệu điện áp tương tự `0–5V` từ cảm biến độ ẩm đất (mô phỏng bằng biến trở tuyến tính `POT-HG` trong Proteus/SimulIDE).
2. **Timer1 (16-bit) + Ngắt (`PIR1.TMR1IF`):** Tạo xung định thời chính xác `100 ms` (Prescaler `1:8`, nạp trước `TMR1 = 0xCF2C`), chia 5 lần thành chu kỳ lấy mẫu `0.5 giây` không làm treo vòng lặp chính.
3. **Ngắt ngoài (`RB0/INT`, kích cạnh xuống):** Chuyển tức thời giữa chế độ **AUTO** (tự động theo ngưỡng + hysteresis) và **MANUAL** (người dùng tự bật/tắt bơm bằng nút `RB1`).
4. **GPIO (`PORTB`, `PORTC`, `PORTD`):** Giao tiếp **LCD 16×2 chế độ 4-bit**, đọc 3 nút nhấn dùng điện trở kéo lên nội `PORTB`, xuất điều khiển **Relay bơm nước**, **LED Xanh/Đỏ** và **Còi báo động (Buzzer)** qua thanh ghi đệm `PORTC_IMG` chống lỗi RMW.
5. **EEPROM Dữ liệu nội (256 bytes, địa chỉ `0x00`):** Lưu bền vững ngưỡng kích hoạt tưới (`THRESH_PCT`, mặc định `40%`, chỉnh được `15%–85%` theo bước `5%`) theo đúng chuỗi mở khóa `55h → AAh → WR`.

### 5.8.2. Sơ đồ khối hệ thống & Bảng phân công chân (40-pin PDIP)

```text
  [Cảm biến Độ ẩm đất (0..5V)] ──► [RA0/AN0 (ADC)]
                                         │
  [Nút MODE (RB0/INT), +5%/Pump (RB1), -5% (RB2)] ──► [ PIC16F877A (4 MHz) ] ──► [PORTD (RD2-RD7)] ──► [LCD 16x2]
                                                                │                                         Line1: MOIST:XX% TH:YY%
  [Thạch anh 4MHz + ~MCLR] ───────► [Timer1 100ms + EEPROM] ────┴──► [PORTC: RC0 Relay Bơm | RC1 LED Xanh | RC2 LED Đỏ | RC3 Buzzer]
```

| Chân PIC16F877A | Kết nối phần cứng | Chiều (`TRIS`) | Cấu hình đặc biệt |
| :--- | :--- | :---: | :--- |
| `RA0/AN0` (Pin 2) | Cảm biến độ ẩm đất (`0V = 0%`, `5V = 100%`) | Input (`TRISA<0>=1`) | `ADCON1 = 0x0E` (chỉ `AN0` analog, canh trái `ADFM=0`) |
| `RB0/INT` (Pin 33) | Nút nhấn **MODE** (`AUTO ↔ MANUAL`) | Input (`TRISB<0>=1`) | `OPTION_REG = 0x00` (pull-up nội + ngắt cạnh xuống) |
| `RB1` (Pin 34) | Nút **Tăng ngưỡng +5%** (AUTO) / **Bật-Tắt Bơm** (MANUAL) | Input (`TRISB<1>=1`) | Pull-up nội `PORTB`, chống dội `50 ms` |
| `RB2` (Pin 35) | Nút **Giảm ngưỡng -5%** (AUTO) | Input (`TRISB<2>=1`) | Pull-up nội `PORTB`, tự động lưu EEPROM |
| `RC0` (Pin 15) | Tầng lái **Relay + Động cơ Bơm nước** (`2N2222` + `1N4007`) | Output (`TRISC=0x00`) | `1 = Bơm BẬT`, `0 = Bơm TẮT` |
| `RC1`, `RC2` (Pin 16–17) | **LED Xanh** (Đất ẩm / OK) & **LED Đỏ** (Đang tưới) | Output (`TRISC=0x00`) | Trở hạn dòng `330 Ω`, ghi qua `PORTC_IMG` chống RMW |
| `RC3` (Pin 18) | **Còi báo động (Buzzer)** cảnh báo khô hạn nghiêm trọng | Output (`TRISC=0x00`) | Bật khi `MOIST_PCT < 20%` |
| `RD2`, `RD3` (Pin 21–22) | **LCD 16×2** chân `RS`, `EN` (`RW` nối GND) | Output (`TRISD=0x00`) | Giao tiếp 4-bit tiết kiệm chân |
| `RD4–RD7` (Pin 27–30) | **LCD 16×2** bus dữ liệu `D4 – D7` | Output (`TRISD=0x00`) | Gửi nibble cao trước, nibble thấp sau |
| `OSC1/OSC2` (Pin 13–14) | Thạch anh `4 MHz` + 2 tụ `22 pF` | Clock | `__CONFIG = 0x3F31` (`_XT_OSC`, `_WDT_OFF`, `_LVP_OFF`) |

### 5.8.3. Tính toán Thông số Kỹ thuật (Timer1, ADC & Điều khiển Hysteresis)
1. **Tính giá trị nạp Timer1 tạo ngắt đúng `100 ms` tại `FOSC = 4 MHz`:**
   - $F_{\text{CY}} = F_{\text{OSC}}/4 = 1\text{ MHz}$. Chọn Prescaler `1:8` (`T1CON = 0x31`) → tần số đếm $125\text{ kHz}$ ($8\text{ }\mu\text{s}$/nhịp).
   - Số nhịp cho `100 ms`: $N = 100\text{ ms} / 8\text{ }\mu\text{s} = 12,500$.
   - Giá trị nạp trước: $65,536 - 12,500 = 53,036 = \text{0xCF2C}$ (`TMR1H = 0xCF`, `TMR1L = 0x2C`). Đếm 5 lần tràn (`SAMPLE_TICKS = 5`) → chu kỳ lấy mẫu đúng `0.5 s`.
2. **Quy đổi ADC sang phần trăm độ ẩm (`0–99%`) bằng phép nhân 8×8 không cần bộ nhân cứng:**
   - Với `ADFM = 0`, đọc 8 bit cao tại `ADRESH` (`0–255`). Chương trình con `CALC_MOISTURE_PCT` thực hiện vòng lặp dịch–cộng 8 bit tính $\text{MOIST\_PCT} = \lfloor (\text{ADC\_RAW} \times 100) / 256 \rfloor$ (lấy trực tiếp byte cao `MUL_H` của tích 16-bit): `0V → 0%`, `1.5V → 30%`, `2.5V → 50%`, `5.0V → 99%`.
3. **Thuật toán điều khiển Hysteresis `10%` (`CONTROL_IRRIGATION`):**
   - Trong chế độ **AUTO**:
     - Nếu `MOIST_PCT < THRESH_PCT` (kiểm tra bằng `SUBWF`, cờ mượn `STATUS.C == 0`) → **Bật bơm (`F_PUMP_ON = 1`)**.
     - Nếu `MOIST_PCT >= THRESH_PCT + 10%` (`STATUS.C == 1`) → **Tắt bơm (`F_PUMP_ON = 0`)**.
     - Nếu nằm trong vùng trễ `[THRESH_PCT, THRESH_PCT + 10%)` → **Giữ nguyên trạng thái bơm hiện tại** để tránh đóng cắt relay liên tục khi độ ẩm dao động quanh ngưỡng.
   - Cảnh báo khô hạn nặng: Nếu `MOIST_PCT < 20%` → bật còi `RC3`.

### 5.8.4. Lưu đồ giải thuật tổng quát (Flowchart)
```text
[START / RESET 0x0000]
       │
       ▼
[Khởi tạo Bank 1: OPTION_REG=0x00, ADCON1=0x0E, TRISA/B/C/D/E, PIE1.TMR1IE=1]
[Khởi tạo Bank 0: ADCON0=0x41, Đọc ngưỡng EEPROM(0x00), LCD_INIT, Timer1=0xCF2C, Bật GIE/PEIE/INTE]
       │
       ▼
┌─► [Kiểm tra nút RB1 (+5% hoặc Đảo bơm Manual) & nút RB2 (-5% & Lưu EEPROM)]
│      │
│      ▼
│   [Cờ F_SAMPLE == 1 (do ISR Timer1 bật mỗi 0.5s hoặc RB0/INT)?] ──(0)──┐
│      │ (1)                                                             │
│      ▼                                                                 │
│   [Xóa F_SAMPLE → Chờ TACQ 25µs → Đọc ADC (ADRESH) → Tính MOIST_PCT]   │
│      │                                                                 │
│      ▼                                                                 │
│   [Chế độ AUTO?]──(Không/MANUAL)──► Giữ F_PUMP_ON theo nút RB1         │
│      │ (Có/AUTO)                                                       │
│      ├── MOIST < TH       ──► F_PUMP_ON = 1 (Bật Bơm)                  │
│      ├── MOIST >= TH + 10 ──► F_PUMP_ON = 0 (Tắt Bơm)                  │
│      └── Vùng Hysteresis  ──► Giữ nguyên trạng thái bơm                │
│      │                                                                 │
│      ▼                                                                 │
│   [UPDATE_OUTPUTS (qua PORTC_IMG): RC0 Bơm, RC1 Xanh, RC2 Đỏ, RC3 Còi (<20%)]
│      │                                                                 │
│      ▼                                                                 │
│   [UPDATE_LCD: Dòng 1 "MOIST:XX% TH:YY%", Dòng 2 "AUTO/MANUAL PUMP:ON/OFF"]
└────────────────────────────────────────────────────────────────────────┘

[ISR 0x0004]: Lưu W/STATUS/PCLATH (Shared RAM 70h-72h bằng SWAPF)
  ├── Nếu TMR1IF=1: xóa TMR1IF, nạp lại 0xCF2C, đếm 5 lần -> bật F_SAMPLE
  ├── Nếu INTF=1:   xóa INTF, đảo bit F_MANUAL (AUTO <-> MANUAL), bật F_SAMPLE
  └── Khôi phục PCLATH/STATUS/W -> RETFIE
```

### 5.8.5. Ca kiểm thử & Khắc phục sự cố (Chi tiết tại `Test_Results.pdf`)
- **TC01 (Khởi động):** Nguồn 5V, cảm biến `50%`, EEPROM trắng (`0xFF`) → nạp ngưỡng mặc định `40%`, LCD hiện `MOIST:50% TH:40%` / `AUTO   PUMP:OFF`, LED Xanh sáng.
- **TC02 (Tưới tự động):** Giảm độ ẩm xuống `35%` (`< 40%`) → Relay bơm `RC0` bật, LED Đỏ sáng, LCD hiện `AUTO   PUMP:ON`.
- **TC03 (Vùng trễ Hysteresis):** Tăng độ ẩm lên `45%` (vẫn `< 40 + 10 = 50%`) → Bơm **vẫn tiếp tục tưới** (không ngắt sớm). Tăng lên `51%` (`>= 50%`) → Bơm tự động tắt, LED Xanh sáng.
- **TC04 (Cảnh báo khô hạn nặng):** Giảm độ ẩm xuống `15%` (`< 20%`) → Bơm bật + Còi `RC3` kêu cảnh báo.
- **TC05 (Ngắt ngoài MANUAL):** Nhấn `RB0/INT` → chuyển ngay sang `MANUAL PUMP:...`, nhấn `RB1` bật/tắt bơm cưỡng bức bất kể cảm biến.
- **TC06 (Chỉnh ngưỡng & EEPROM):** Chế độ AUTO nhấn `RB1`/`RB2` chỉnh `TH` lên `50%` → nhấn Reset `~MCLR` → hệ thống vẫn khôi phục đúng `TH:50%` từ EEPROM!
- **Các lỗi thường gặp (Troubleshooting):** Quên `ADCON1 = 0x0E` làm sai chân Analog; quên tắt `_LVP_OFF` làm treo chip khi `RB3` thả nổi; đặt sai `Processor Clock Frequency` trong Proteus khác `4 MHz` làm sai nhịp `0.5 s` và lỗi hiển thị LCD; quên dùng `PORTC_IMG` dễ gây nháy sai LED do RMW.

---

## 5.9. So sánh PIC16F877A với ATmega32 (Đủ 10 Tiêu chí bắt buộc Mục 5.9)

| STT | Tiêu chí (Mục 5.9) | **PIC16F877A** (`DS39582C`) | **ATmega32(L)** (`doc2503.pdf`) |
| :---: | :--- | :--- | :--- |
| 1 | **Kiến trúc CPU** | 8-bit Harvard RISC, pipeline 2 tầng; **1 thanh ghi tích lũy `W`**; **không có bộ nhân cứng**; `1 TCY = 4 clock` → tối đa **5 MIPS @ 20 MHz** (`200 ns`); không có RC nội cho CPU. | 8-bit Harvard Enhanced RISC, pipeline 2 tầng; **32 thanh ghi đa dụng** nối thẳng ALU; có **bộ nhân cứng 2 chu kỳ (`MUL`)**; `1 clock/lệnh` → tối đa **16 MIPS @ 16 MHz** (`62.5 ns`); có **RC nội 1/2/4/8 MHz**. |
| 2 | **Tổ chức Thanh ghi** | 1 thanh ghi `W` + thanh ghi tệp chia **4 Bank** (`STATUS<RP1:RP0>`); `STATUS` thiếu cờ số có dấu (`N, V, S`) và **đảo cực tính cờ mượn `C`**; 1 con trỏ gián tiếp 9-bit (`IRP:FSR`). | **32 thanh ghi `R0–R31`** (`R16–R31` nhận hằng số `LDI`), 3 con trỏ 16-bit (`X, Y, Z`) hỗ trợ tự tăng/giảm (`X+`); `SREG` đủ cờ toán học có dấu (`I, T, H, S, V, N, Z, C`), cờ mượn chuẩn. |
| 3 | **Bộ nhớ Chương trình & Dữ liệu** | Flash **8K × 14-bit** (~14.3 KB, **4 Page × 2K**, `PCLATH<4:3>`, bền `100K` E/W); SRAM **368 B** (4 Bank, 16B chung `70h–7Fh`); EEPROM **256 B** (bền `1M` E/W); **Hardware Stack 8 mức** (không có `PUSH/POP`). | Flash **32 KB** (`16K × 16-bit`, tuyến tính, Bootloader RWW, bền `10K` E/W); SRAM **2 KB tuyến tính** (không phân Bank); EEPROM **1 KB** (`100K` E/W); **Stack trên SRAM** (`SPH:SPL`, có `PUSH/POP`). |
| 4 | **Tập lệnh (Instruction Set)** | **35 lệnh**, độ dài cố định **14-bit**, 3 định dạng bit liền mạch → dễ học, viết Assembler/Encoder rất gọn. | **131 lệnh**, độ dài **16-bit / 32-bit**, các bit toán hạng tách rời (VD `LDI`: `1110 KKKK dddd KKKK`) → phong phú nhưng mã máy phức tạp hơn. |
| 5 | **GPIO** | **33 chân** (5 Port `A–E`); 2 thanh ghi/Port (`TRISx`: **`1`=In, `0`=Out**; `PORTx`); dễ lỗi **RMW**; chỉ `PORTB` có pull-up nội; bẫy: `PORTA/E` mặc định Analog (`ADCON1`), `RA4` open-drain, `RB3` LVP. | **32 chân** (4 Port `A–D`); 3 thanh ghi/Port (`DDRx`: **`1`=Out, `0`=In**; `PORTx`; `PINx`); **không bị lỗi RMW**; pull-up từng chân trên cả 4 Port; bẫy: `PC2–PC5` mặc định bật JTAG (`JTAGEN`). |
| 6 | **Timers & PWM** | 3 Timer (`TMR0` 8b chung prescaler với WDT, `TMR1` 16b RTC, `TMR2` 8b có `PR2`); 2 module CCP → **2 kênh PWM tối đa 10-bit** (chung TMR2). | 3 Timer (`T0` 8b, `T1` 16b có Input Capture + Noise Canceler, `T2` 8b RTC); **4 kênh PWM** (`OC0`, `OC1A/B`, `OC2`), tối đa **16-bit** trên T1. |
| 7 | **Hệ thống Ngắt (Interrupts)** | **15 nguồn ngắt** dùng chung **1 vector duy nhất (`0004h`)**; phần mềm tự polling cờ, tự xóa cờ, tự lưu ngữ cảnh bằng `SWAPF` vào Shared RAM `70h–7Fh`. | **21 vector riêng biệt** (`$000–$028`), ưu tiên phần cứng; phần cứng tự xóa phần lớn cờ; lưu ngữ cảnh nhanh bằng `PUSH/POP` trên SRAM Stack. |
| 8 | **ADC** | 10-bit, **8 kênh đơn cực**, không có VREF nội, không có kênh vi sai/gain, phải chờ `TACQ` (~20 µs) bằng phần mềm; `ADRESH` (Bank 0) & `ADRESL` (Bank 1) khác Bank. | 10-bit, 8 kênh đơn + **kênh vi sai (gain 1x/10x/200x)**, có **VREF nội 2.56V**, Auto-Trigger, `ADCL`/`ADCH` cùng không gian I/O (đọc `ADCL` trước). |
| 9 | **Truyền thông nối tiếp** | 1 USART (không hardware parity, baud 8-bit) + **1 MSSP dùng chung SPI / I²C** (chỉ chọn 1 tại một thời điểm; I²C hỗ trợ 7/10-bit); có thêm **PSP** 8-bit và **2 Comparators + CVREF**. | **3 bộ độc lập chạy đồng thời**: USART (hardware parity, baud 12-bit `UBRR`), SPI, TWI (I²C 7-bit); 1 Analog Comparator; không có PSP. |
| 10 | **Công cụ Lập trình Assembly** | **MPLAB IDE v8.92 / MPLAB X (≤ v5.35) + MPASM**, mã nguồn mở **`gputils` (`gpasm`)**; nạp/debug 2 dây **ICSP/ICD** (`PICkit 2/3`); cấu hình ngay trong code bằng `__CONFIG`; mô phỏng mạnh trên Proteus & SimulIDE. | **Microchip Studio (Atmel Studio) + AVRASM2**, mã nguồn mở **`avra` / `avr-as`**; nạp **SPI ISP (6 chân)** hoặc debug **JTAG (4 dây)**; cấu hình qua **2 Fuse Bytes** ngoài file `.hex`; mô phỏng trên Proteus & SimulIDE. |

*(Xem thêm 6 cặp ví dụ mã nguồn Assembly đối chiếu trực tiếp từng dòng giữa ATmega32 và PIC16F877A trong file `ATmega32_vs_PIC16F87XA_Comparison.md`.)*

---

## 5.10. Tài liệu Tham khảo (References)

1. Microchip Technology Inc., *PIC16F87XA Data Sheet: 28/40/44-Pin Enhanced Flash Microcontrollers*, Document No. **DS39582C**, Jan. 2013. (Nguồn trích dẫn cho `Figure 1-2` p. 7, `Pin Diagrams` p. 3, `Table 1-3` pp. 10–13, `Figure 2-1` p. 15, `Figure 2-3` p. 17, `Table 2-1` pp. 19–21, `Figure 2-5` p. 30, `Figure 2-6` p. 31, `Figure 11-1/11-4` pp. 129/132, `Figure 14-1/14-5/14-10` pp. 145/148/153, `Figure 15-1` p. 159, `Table 15-2` p. 160).
2. Microchip Technology Inc., *PICmicro™ Mid-Range MCU Family Reference Manual*, Document No. **DS33023A**, Dec. 1997.
3. Atmel Corporation / Microchip Technology Inc., *ATmega32 / ATmega32L 8-bit AVR Microcontroller with 32K Bytes In-System Programmable Flash Data Sheet*, Document No. **2503Q–AVR–02/11**, Feb. 2011.
4. Microchip Technology Inc., *MPASM™ Assembler, MPLINK™ Object Linker, MPLIB™ Object Librarian User's Guide*, Document No. **DS33014L**, 2013.
5. GNU PIC Utilities (`gputils`) Documentation — *gpasm / gplink / gpdasm Manual*, https://gputils.sourceforge.io/.
6. M. A. Mazidi, R. D. McKinlay, and D. Causey, *PIC Microcontroller and Embedded Systems: Using Assembly and C for PIC18* (và các nguyên lý kiến trúc PIC Mid-Range), Pearson Education.
7. Labcenter Electronics, *Proteus Design Suite – PIC16 Microcontroller Simulation Support*, https://www.labcenter.com/microprocessors/.
