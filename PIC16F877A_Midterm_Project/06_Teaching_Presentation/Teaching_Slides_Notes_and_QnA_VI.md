# NỘI DUNG THÔ SLIDE THUYẾT TRÌNH, HƯỚNG DẪN MINI ASSEMBLER, MẪU KIỂM THỬ, NGÂN HÀNG Q&A & DANH MỤC TÀI LIỆU THAM KHẢO
**Phạm vi phủ:** Component 4 (`MiniAssembler_User_Guide.pdf`), Component 5 (`Test_Results.pdf`), Component 6 (`Teaching_Slides.pdf`), Component 7 (`References.pdf`) và chuẩn bị Vấn đáp (Oral Examination — 5đ Q&A + 5đ đóng góp cá nhân).

---

## PHẦN A: KỊCH BẢN & NỘI DUNG CHI TIẾT 18 SLIDE GIẢNG DẠY (`Teaching_Slides.pdf`)

- **Yêu cầu đề bài (Mục 10):** 15–20 slides, giảng dạy cho cả lớp hiểu và dùng được `PIC16F877A`.
- **Phân bổ thời gian chuẩn (Mục 10.1 — Tổng 28 phút):**
  - Kiến trúc MCU & Datasheet: **8 phút** *(Thành viên 1 — Slides 1–8)*
  - Giải thích Code Assembly: **5 phút** *(Thành viên 2 — Slides 9–11)*
  - Thiết kế Ứng dụng & Mạch: **4 phút** *(Thành viên 3 — Slides 12–13)*
  - Demo Python Mini Assembler: **3 phút** *(Thành viên 2 — Slide 14 + Demo live)*
  - Demo Mô phỏng Proteus: **3 phút** *(Thành viên 3 — Slide 15 + Demo live)*
  - So sánh ATmega32 & Kết luận: *(gộp gọn trong phần cuối trước Q&A — Slides 16–18)*
  - Hỏi đáp & Thảo luận (Q&A): **5 phút** *(Cả 3 thành viên)*

| Slide | Tiêu đề Slide | Nội dung chính trình bày trên Slide | Hình ảnh / Minh họa gợi ý | Người nói & Thời lượng |
| :---: | :--- | :--- | :--- | :---: |
| **1** | **Trang bìa (Title Slide)** | Tên đề tài: *Nghiên cứu Kiến trúc, Lập trình Assembly, Dịch Mã máy & Ứng dụng Vi điều khiển PIC16F877A*; Mã lớp, Số nhóm, Họ tên 3 thành viên & vai trò. | Ảnh chip `PIC16F877A` 40-pin PDIP + logo trường. | TV1 (0.5p) |
| **2** | **Giới thiệu & Thông số nổi bật** | Microchip PIC16 Mid-Range 8-bit; 35 lệnh 14-bit; `DC–20 MHz` (`5 MIPS`); 8K Flash, 368B SRAM, 256B EEPROM; 33 I/O, 3 Timers, 2 PWM, 8-ch ADC 10-bit; 4 lý do chọn IC. | Bảng tóm tắt thông số (trích Table 1-1, `DS39582C` p. 5). | TV1 (1p) |
| **3** | **Kiến trúc CPU Harvard & Pipeline** | Bus Program 14-bit vs Bus Data 8-bit; ALU 8-bit + thanh ghi `W` duy nhất; thanh ghi `STATUS`; `1 TCY = 4 TOSC` (`Q1–Q4`); Pipeline 2 tầng (1 TCY thường, 2 TCY khi rẽ nhánh). | `Figure 1-2` (p. 7) + sơ đồ pipeline `Q1–Q4`. | TV1 (1.5p) |
| **4** | **Tổ chức Bộ nhớ & Stack** | Flash `8K×14-bit` (4 Page × 2K, Reset `0000h`, ISR `0004h`); SRAM 368B chia **4 Bank** (`RP1:RP0`), Shared RAM `70h–7Fh`; Hardware Stack vòng **8 mức** (không có `PUSH/POP`). | `Figure 2-1` (p. 15) & `Figure 2-3` (p. 17). | TV1 (1.5p) |
| **5** | **Sơ đồ chân 40-pin PDIP & 3 "Bẫy" GPIO** | 5 Port (`A–E`), `TRISx` (`1=In, 0=Out`), lỗi RMW. **Nhấn mạnh 3 lưu ý sống còn:** `ADCON1=0x06` tắt Analog `PORTA/E`, `RA4` open-drain, `_LVP_OFF` giải phóng `RB3`. | Pinout 40-pin PDIP (p. 3) khoanh đỏ các chân đặc biệt. | TV1 (1p) |
| **6** | **Tập lệnh 35 lệnh & Chế độ định địa chỉ** | 3 nhóm (18 Byte, 4 Bit, 13 Literal/Control); 3 định dạng 14-bit; Direct vs Indirect (`FSR`/`INDF`/`IRP`) vs Literal; lưu ý cờ `C` đảo cực tính trong `SUBWF/SUBLW`. | `Figure 15-1` (p. 159) + `Figure 2-6` (p. 31). | TV1 (1p) |
| **7** | **Ngoại vi cốt lõi: Timers & Hệ thống Ngắt** | So sánh nhanh `TMR0` (8b, chung prescaler WDT), `TMR1` (16b), `TMR2` (8b + `PR2`); 15 nguồn ngắt chung **1 vector `0004h`** + polling cờ + lưu ngữ cảnh bằng `SWAPF`. | `Figure 14-10` Interrupt Logic (p. 153). | TV1 (1p) |
| **8** | **Ngoại vi cốt lõi: ADC 10-bit & Truyền thông** | ADC 8 kênh (`ADCON0/1`, `TACQ ~ 20 µs`, `ADRESH` Bank 0 vs `ADRESL` Bank 1); USART (`SPBRG` 9600 bps); MSSP (SPI hoặc I²C); CCP/PWM 10-bit. | `Figure 11-4` A/D Justification (p. 132). | TV1 (0.5p) |
| **9** | **Dịch Assembly sang Mã máy 14-bit** | 3 khung bit mã hóa; ví dụ dịch tay trực tiếp 3 lệnh tiêu biểu: `MOVLW 0x55 → 0x3055`, `ADDWF 0x20, 1 → 0x07A0`, `BSF 0x03, 5 → 0x1683`, `GOTO LOOP → 0x2805`; giải thích Intel HEX Little-Endian. | Sơ đồ tách bit màu từng trường `opcode | d/b | f/k`. | TV2 (2p) |
| **10** | **Môi trường Lập trình Assembly (MPASM / `gpasm`)** | Cấu trúc file `.asm`, các chỉ thị chính (`__CONFIG`, `CBLOCK`, `ORG`, `BANKSEL`), quy trình `.asm → .hex/.lst` và cách nạp vào Proteus. | Lưu đồ biên dịch + ảnh trích đoạn file `.lst`. | TV2 (1p) |
| **11** | **Giải thích Mã nguồn Ứng dụng (`smart_irrigation.asm`)** | Khởi tạo (Bank 1/0, `ADCON1=0x0E`, `Timer1=0xCF2C`, đọc EEPROM); ISR `0004h` xử lý đồng thời `TMR1IF` & `INTF` với `SWAPF`; phép nhân 8×8 tính `%` độ ẩm; logic Hysteresis 10% dùng cờ mượn `STATUS.C`; xuất `PORTC_IMG` chống RMW. | Flowchart + đoạn code ISR & Hysteresis có highlight. | TV2 (2p) |
| **12** | **Đề tài #15: Smart Irrigation Controller & Sơ đồ khối** | Mục tiêu tưới cây tự động/thủ công; **5 ngoại vi** (ADC `AN0`, Timer1 100ms, Ngắt ngoài `RB0/INT`, GPIO/LCD 4-bit + Relay/Buzzer, EEPROM lưu ngưỡng); sơ đồ khối & phân công chân. | Sơ đồ khối + bảng pinout `PIC16F877A`. | TV3 (2p) |
| **13** | **Thiết kế Mạch Nguyên lý (Circuit Schematic)** | Mạch nguồn 5V, thạch anh `4 MHz` + 2 tụ `22 pF`, mạch `~MCLR`, biến trở mô phỏng cảm biến độ ẩm đất (`AN0`), mạch lái Relay bơm (`2N2222 + 1N4007`), LCD 16×2 (`LM016L`), 3 nút nhấn & LED/Buzzer. | Ảnh Schematic Proteus rõ nét, chú thích từng khối. | TV3 (2p) |
| **14** | **Python GUI Mini Assembler (Kiến trúc & Live Demo)** | Kiến trúc 5 module (`main`, `parser`, `instruction_set`, `encoder`, `error_handler`), cơ chế 2-Pass xử lý nhãn, hỗ trợ **trọn bộ 35 lệnh**; **Demo trực tiếp (3 phút)** dịch `sample.asm` & `smart_irrigation.asm`, báo lỗi cú pháp và kiểm chứng mã máy. | Ảnh chụp GUI + kết quả `test_assembler.py` 100% PASS. | TV2 (3p) |
| **15** | **Mô phỏng Proteus & Kết quả Kiểm thử (Live Demo)** | Bảng 8 Test Cases (`TC01–TC08`: Auto ON/OFF, Hysteresis 10%, cảnh báo `<20%`, Manual `RB0/INT`, lưu EEPROM sau Reset); **Demo trực tiếp Proteus (3 phút)**. | Ảnh chụp LCD & bơm chạy trên Proteus + bảng Pass/Fail. | TV3 (3p) |
| **16** | **So sánh PIC16F877A vs. ATmega32 (Phần cứng)** | Bảng đối chiếu 10 tiêu chí bắt buộc (CPU/MIPS, thanh ghi `W` vs `R0–R31`, Bank RAM, Stack, GPIO, Timers, 1 vs 21 Interrupts, ADC, Serial, Tools). | Bảng so sánh 2 cột dùng màu nhấn điểm khác biệt. | TV1 (1p) |
| **17** | **So sánh PIC16F877A vs. ATmega32 (Code Assembly)** | So sánh song song 1 đoạn code thực tế (VD: cấu hình GPIO hoặc ISR `SWAPF` vs `PUSH/POP` + cờ mượn `C`) → rút ra khi nào chọn PIC vs AVR. | Code 2 cột side-by-side (trích từ file so sánh). | TV2 (1p) |
| **18** | **Kết luận, Tài liệu tham khảo & Q&A** | Tổng kết 4 bài học chính; danh mục tài liệu trích dẫn chính (DS39582C, DS33023A, doc2503, DS33014); mở màn phần **Hỏi đáp 5 phút**. | QR / danh sách gói tài liệu nộp Blackboard. | TV3 + Cả nhóm (5p Q&A) |

---

## PHẦN B: ĐẶC TẢ & NỘI DUNG THÔ HƯỚNG DẪN PYTHON MINI ASSEMBLER (`MiniAssembler_User_Guide.pdf`)

### B.1. Cấu trúc Dự án (`Python_MiniAssembler.zip`)
```text
MiniAssembler/
├── main.py                # Giao diện Tkinter GUI, điều phối Load/Assemble/Clear/Save
├── parser.py              # Chuẩn hóa dòng lệnh, xóa comment ';', tách label, directive, mnemonic, operands
├── instruction_set.py     # Từ điển 35 lệnh PIC16F877A (định dạng, base opcode, chu kỳ) + bảng SFR chuẩn
├── encoder.py             # Bộ dịch 2-Pass (Pass 1: Symbol Table; Pass 2: mã hóa 14-bit Binary/Hex & Intel HEX)
├── error_handler.py       # Lớp ngoại lệ AssemblyError(line_no, message), kiểm tra phạm vi f/b/k/d và nhãn trùng/thiếu
├── examples/
│   └── sample.asm         # File ASM mẫu chứa đủ 5 nhóm lệnh (dùng demo và đối chiếu gpasm/MPASM)
└── README.pdf             # (hoặc MiniAssembler_User_Guide.pdf)
```

### B.2. Bố cục Giao diện Người dùng (Tkinter GUI — Đáp ứng 100% Mục 8.1)
```text
+-----------------------------------------------------------------------------------+
| PIC16F877A Educational Mini Assembler  |  Target MCU: PIC16F877A (14-bit Mid-Range)|
+-----------------------------------------------------------------------------------+
| [Load .asm]  [Assemble / Translate]  [Clear]  [Save Table (.txt/.csv)] [Export .hex]
+------------------------------------+----------------------------------------------+
| Assembly Source Code Editor        | Machine-Code Translation Results (Treeview)  |
| (Text widget + Line numbers)       | Addr   | Assembly Line | Binary(14b) | Hex|Sz|
| 1: ORG 0x0000                      | 0x0000 | BSF 0x03, 5   | 01011010000011|1683|1|
| 2: BSF STATUS, 5                   | 0x0001 | CLRF 0x06     | 00000110000110|0186|1|
| ...                                | ...                                          |
+------------------------------------+----------------------------------------------+
| Console / Error Messages (Hiển thị lỗi chi tiết kèm số dòng hoặc "Assemble OK!")  |
+-----------------------------------------------------------------------------------+
```

### B.3. Các nhóm lỗi bắt buộc phát hiện (`error_handler.py`)
1. **Lệnh không hỗ trợ / sai chính tả:** VD `MOV R16, 5` → `Line 3: Unsupported instruction 'MOV'`.
2. **Sai số lượng toán hạng:** VD `BSF PORTB` (thiếu `b`) → `Line 4: 'BSF' expects 2 operands (f, b), got 1`.
3. **Toán hạng vượt phạm vi bit:** `f > 0x7F` (nhắc dùng địa chỉ 7-bit hoặc tên SFR), `b ∉ [0..7]`, `d ∉ {0, 1, W, F}`, `k > 0xFF` (Literal 8-bit) hoặc `k > 0x7FF` (`GOTO`/`CALL`).
4. **Lỗi nhãn (Labels):** Nhãn không tồn tại (`Undefined label 'END_LP'`) hoặc khai báo trùng tên (`Duplicate label 'LOOP'`).
5. **Lỗi cú pháp số:** Số hex/binary/decimal không hợp lệ (`0xGG`, `b'102'`).

### B.4. Hướng dẫn cài đặt & sử dụng (dán trực tiếp vào `MiniAssembler_User_Guide.pdf`)
- **Yêu cầu hệ thống:** Python 3.8 trở lên (không cần cài thư viện bên thứ ba vì dùng `tkinter` chuẩn).
- **Cách chạy:** `python main.py`.
- **Các bước thao tác:** (1) Nhập code vào khung trái hoặc bấm **Load `.asm`** chọn `examples/sample.asm` → (2) Bấm **Assemble / Translate** → (3) Xem bảng địa chỉ, mã nhị phân 14-bit, mã Hex 4 ký tự và kích thước bên khung phải → (4) Bấm **Save Results** để lưu báo cáo hoặc xuất file `.hex` chuẩn Intel HEX.

---

## PHẦN C: MẪU BÁO CÁO KẾT QUẢ MÔ PHỎNG & KIỂM THỬ (`Test_Results.pdf`)

### C.1. Cấu hình môi trường mô phỏng
- **Phần mềm:** Proteus ISIS (hoặc SimulIDE) — phiên bản: `[Điền phiên bản]`.
- **Thiết lập IC `PIC16F877A`:** Tần số `Processor Clock Frequency = 4 MHz` (hoặc `20 MHz`), `Configuration Word = 0x3F31` (hoặc `0x3F32`), nạp file `.hex` biên dịch từ MPASM/`gpasm`.

### C.2. Bảng Ca kiểm thử chuẩn (Test Cases Matrix — điền ảnh & trạng thái khi chạy)

| Mã Test | Hạng mục kiểm thử | Đầu vào / Thao tác | Kết quả Kỳ vọng (Expected) | Kết quả Thực tế (Actual) | Đánh giá |
| :---: | :--- | :--- | :--- | :--- | :---: |
| `TC01` | Khởi động & Reset | Cấp nguồn 5V / Nhấn nút `~MCLR` | Hệ thống reset sạch, LCD hiện thông điệp khởi tạo, đèn trạng thái mặc định | `[Điền kết quả + Ảnh 1]` | PASS/FAIL |
| `TC02` | Đọc ngoại vi chính (ADC / Nút nhấn) | Đặt giá trị cảm biến ở mức thấp / bình thường | Giá trị đo & hiển thị đúng công thức (sai số ≤ 1 đơn vị) | `[Điền kết quả + Ảnh 2]` | PASS/FAIL |
| `TC03` | Ngưỡng cảnh báo / Điều khiển đầu ra | Tăng tín hiệu vượt ngưỡng đặt | Kích hoạt LED đỏ / Còi / Thay đổi Duty Cycle PWM đúng yêu cầu | `[Điền kết quả + Ảnh 3]` | PASS/FAIL |
| `TC04` | Ngắt phần cứng (Timer / `RB0/INT`) | Nhấn nút ngắt ngoài hoặc đo chu kỳ ngắt trên Oscilloscope | Đáp ứng tức thì, không treo vòng lặp chính, đúng chu kỳ định thời | `[Điền kết quả + Ảnh 4]` | PASS/FAIL |
| `TC05` | Trường hợp biên (Boundary Cases) | Đầu vào min (`0V`), max (`5V`), nhấn giữ nút liên tục | Không tràn biến 8-bit/10-bit, không nhiễu hiển thị | `[Điền kết quả + Ảnh 5]` | PASS/FAIL |
| `TC06` | Kiểm chứng Mini Assembler (Mục 8.5) | Dịch `sample.asm` trên Python GUI và `gpasm`/MPASM | 100% mã Hex & Binary từng dòng khớp hoàn toàn với `.lst`/`.hex` chuẩn | `[Điền kết quả + Ảnh 6]` | PASS/FAIL |
| `TC07` | Kiểm thử báo lỗi Mini Assembler | Nhập lệnh sai opcode, thiếu toán hạng, `b = 9`, nhãn sai | Báo đúng thông điệp lỗi kèm số dòng, không crash GUI | `[Điền kết quả + Ảnh 7]` | PASS/FAIL |

---

## PHẦN D: NGÂN HÀNG 15 CÂU HỎI VẤN ĐÁP (ORAL EXAM Q&A BANK — 5đ Q&A)

1. **Hỏi:** *Tại sao PIC16F877A chạy thạch anh 20 MHz nhưng chỉ đạt 5 MIPS, trong khi ATmega32 chạy 16 MHz lại đạt 16 MIPS?*  
   **Đáp:** Vì mỗi chu kỳ lệnh của PIC16F877A cần **4 chu kỳ xung clock** (`Q1–Q4`, `TCY = 4/FOSC = 200 ns` @ 20 MHz → `5 MIPS`), còn ATmega32 thực thi phần lớn lệnh trong **1 chu kỳ xung clock** (`62.5 ns` @ 16 MHz → `16 MIPS`).

2. **Hỏi:** *Tại sao RAM của PIC16F877A lại phải chia làm 4 Bank? Thanh ghi nào quyết định Bank?*  
   **Đáp:** Vì từ lệnh 14-bit chỉ dành **7 bit** cho địa chỉ thanh ghi trực tiếp (`f`), tối đa truy cập được `2^7 = 128` ô nhớ (`00h–7Fh`). Để mở rộng lên `512` ô (`000h–1FFh`), CPU ghép thêm 2 bit `RP1:RP0` (`STATUS<6:5>`) tạo thành địa chỉ 9-bit.

3. **Hỏi:** *Tại sao trên PIC16F877A đọc tín hiệu số ở `PORTA` sau khi reset lại luôn ra `0`?*  
   **Đáp:** Vì theo `DS39582C` (p. 41, 128), sau Reset mọi chân ghép kênh với ADC (`RA0–RA3`, `RA5`, `RE0–RE2`) mặc định ở chế độ **Analog Input** (bộ đệm số bị ngắt nên đọc luôn ra `0`). Phải ghi `ADCON1 = 0x06` (Bank 1) để chuyển sang Digital I/O.

4. **Hỏi:** *Tại sao khi lưu thanh ghi `STATUS` trong ngắt (ISR) lại phải dùng `SWAPF STATUS, W` thay vì `MOVF STATUS, W`?*  
   **Đáp:** Vì lệnh `MOVF` có làm thay đổi cờ **`Z`** trong `STATUS` (nếu `STATUS == 0` thì `Z` bị bật lên `1`), làm sai lệch cờ gốc của chương trình chính trước khi kịp lưu. Còn `SWAPF` không tác động đến bất kỳ cờ trạng thái nào (`Table 15-2`, p. 160), nên ta đảo nibble để lưu vào `STATUS_TEMP` rồi `SWAPF` lần nữa khi khôi phục.

5. **Hỏi:** *Tại sao biến `W_TEMP` trong ISR nên đặt ở vùng địa chỉ `0x70–0x7F`?*  
   **Đáp:** Vì ngắt có thể xảy ra khi chương trình chính đang ở bất kỳ Bank nào (0, 1, 2 hoặc 3). Vùng `0x70–0x7F` là **Shared/Mirrored RAM** ánh xạ vào cả 4 Bank (`F0h–FFh`, `170h–17Fh`, `1F0h–1FFh`), nên lệnh đầu tiên `MOVWF W_TEMP` luôn lưu đúng chỗ mà không cần đổi Bank trước (vì đổi Bank sẽ làm thay đổi `STATUS` trước khi kịp lưu!).

6. **Hỏi:** *Lỗi Read-Modify-Write (RMW) trên GPIO của PIC16F877A là gì? Tại sao ATmega32 không bị?*  
   **Đáp:** Khi thực thi `BSF PORTB, 0`, PIC đọc mức điện áp thực trên 8 chân `PORTB` (pha Q2), sửa bit 0 rồi ghi lại cả 8 bit (pha Q4). Nếu một chân khác (VD `RB1`) vừa được set `1` ở lệnh trước nhưng mang tải tụ lớn chưa kịp lên mức cao, CPU sẽ đọc nhầm là `0` và ghi đè `0` vào `RB1`. ATmega32 tách thanh ghi ngõ ra `PORTx` khỏi thanh ghi đọc chân `PINx` nên không dính lỗi này.

7. **Hỏi:** *Cờ `C` (Carry/Borrow) trong phép trừ `SUBWF f, W` hoạt động như thế nào?*  
   **Đáp:** PIC thực hiện phép trừ bằng cách cộng với số bù 2 của `W`, nên cờ `C` bị **đảo cực tính**: `C = 1` nghĩa là **không có mượn** (`f ≥ W`), còn `C = 0` nghĩa là **có mượn** (`f < W`). Ngược hoàn toàn với lệnh `SUB`/`CP` trên ATmega32.

8. **Hỏi:** *Điều gì xảy ra nếu chương trình gọi lồng nhau 9 chương trình con (`CALL`) trên PIC16F877A?*  
   **Đáp:** Hardware Stack chỉ có **8 mức** và hoạt động kiểu **vòng tròn (circular buffer)** không có cờ báo tràn (`DS39582C`, p. 30). Lần `CALL` thứ 9 sẽ ghi đè mất địa chỉ trở về của lần gọi thứ 1, khiến chương trình nhảy sai địa chỉ (crash) khi `RETURN`.

9. **Hỏi:** *Chân `RA4` và chân `RB3` trên PIC16F877A có điểm gì đặc biệt dễ gây lỗi mạch?*  
   **Đáp:** `RA4/T0CKI` là ngõ ra **Open-Drain** (chỉ kéo xuống GND được, muốn xuất mức 1 phải gắn điện trở kéo lên ngoài). `RB3/PGM` mặc định bật chế độ nạp điện áp thấp **LVP** (`LVP = 1`), nếu không khai báo `_LVP_OFF` trong `__CONFIG` thì không thể dùng `RB3` làm I/O bình thường và nếu chân thả nổi IC có thể tự nhảy vào chế độ nạp!

10. **Hỏi:** *Khi đọc kết quả ADC 10-bit canh phải (`ADFM = 1`), có bẫy lập trình nào cần tránh?*  
    **Đáp:** Có 2 bẫy: (1) Phải chờ đủ thời gian nạp tụ giữ mẫu **`TACQ ≥ 19.72 µs`** sau khi chọn kênh trước khi bật `GO/DONE`; (2) `ADRESH` nằm ở **Bank 0 (`1Eh`)** còn `ADRESL` nằm ở **Bank 1 (`9Eh`)**, nên bắt buộc chuyển Bank khi đọc đủ 10 bit.

11. **Hỏi:** *Nếu chương trình lớn hơn 2K từ lệnh (`> 07FFh`) thì `GOTO`/`CALL` gặp vấn đề gì?*  
    **Đáp:** Vì `GOTO`/`CALL` chỉ có 11-bit địa chỉ (`000h–7FFh`), 2 bit cao `PC<12:11>` được lấy từ `PCLATH<4:3>`. Trước khi gọi hàm ở Page 1–3, phải cập nhật `PCLATH<4:3>` (hoặc dùng `PAGESEL`), và lưu ý `RETURN` không tự khôi phục `PCLATH`.

12. **Hỏi:** *Tại sao lệnh `CLRF TRISB` (`TRISB = 0x86`) lại có mã máy là `0x0186` giống hệt `CLRF PORTB` (`PORTB = 0x06`)?*  
    **Đáp:** Vì trường địa chỉ `f` trong từ lệnh 14-bit chỉ lấy **7 bit thấp** (`0x86 & 0x7F = 0x06`). Mã máy 14-bit giống hệt nhau; thanh ghi nào thực sự bị xóa phụ thuộc vào trạng thái của `RP1:RP0` trong `STATUS` tại thời điểm CPU thực thi lệnh đó.

13. **Hỏi:** *Tại sao trong file Intel HEX của PIC16F877A địa chỉ lại gấp đôi địa chỉ từ lệnh và các byte bị đảo ngược?*  
    **Đáp:** Chuẩn Intel HEX đánh địa chỉ theo **byte (8-bit)**, trong khi mỗi từ lệnh PIC16 rộng **14-bit** (phải đóng gói vào **2 byte**). Do đó `Byte_Address = 2 × Word_Address`, và quy ước Microchip lưu theo thứ tự **Little-Endian** (byte thấp trước, byte cao chứa 6 bit cao sau).

14. **Hỏi:** *Python Mini Assembler xử lý nhãn nhảy tiến (Forward Reference — nhãn khai báo sau lệnh `GOTO`) bằng cách nào?*  
    **Đáp:** Dùng kiến trúc **2-Pass Assembler**: **Pass 1** quét toàn bộ file nguồn để xây dựng bảng `symbol_table` ánh xạ tên nhãn sang địa chỉ từ lệnh (tính theo `ORG` và đếm lệnh); **Pass 2** mới mã hóa từng lệnh, lúc này địa chỉ của mọi nhãn phía sau đã có sẵn trong `symbol_table`.

15. **Hỏi:** *Nếu giảng viên yêu cầu đổi tốc độ chớp LED / đổi ngưỡng nhiệt độ / thêm 1 lệnh mới vào Python Mini Assembler ngay tại buổi vấn đáp, bạn sửa ở đâu?*  
    **Đáp:**
    - Đổi ngưỡng/tốc độ trong ASM: sửa hằng số nạp `MOVLW` (ngưỡng hoặc giá trị nạp `TMR0/TMR1`), biên dịch lại `.hex` và chạy lại Proteus.
    - Thêm 1 lệnh mới vào Python Mini Assembler: chỉ cần thêm 1 mục từ điển `(format, base_opcode, operand_count)` vào `instruction_set.py` (không phải sửa logic lõi `parser.py` hay GUI `main.py`).

---

## PHẦN E: DANH MỤC TÀI LIỆU THAM KHẢO & CHỈ MỤC HÌNH ẢNH (`References.pdf`)

### E.1. Danh mục Tài liệu Tham khảo chuẩn (IEEE Style)
1. Microchip Technology Inc., *"PIC16F87XA Data Sheet: 28/40/44-Pin Enhanced Flash Microcontrollers,"* Literature Number **DS39582C**, Jan. 2013. [Online]. Available: https://www.microchip.com/
2. Microchip Technology Inc., *"PICmicro™ Mid-Range MCU Family Reference Manual,"* Literature Number **DS33023A**, Dec. 1997. [Online]. Available: https://www.microchip.com/
3. Atmel Corporation / Microchip Technology Inc., *"ATmega32 / ATmega32L 8-bit AVR Microcontroller with 32K Bytes In-System Programmable Flash Data Sheet,"* Document **2503Q–AVR–02/11**, Feb. 2011. [Online]. Available: https://ww1.microchip.com/downloads/en/DeviceDoc/doc2503.pdf
4. Microchip Technology Inc., *"MPASM™ Assembler, MPLINK™ Object Linker, MPLIB™ Object Librarian User's Guide,"* Literature Number **DS33014L**, 2013.
5. GNU PIC Utilities (`gputils`), *"gpasm, gplink, and gpdasm User Documentation,"* Open-Source Project. [Online]. Available: https://gputils.sourceforge.io/
6. Labcenter Electronics, *"Proteus VSM – PIC16 Microcontroller Simulation Support."* [Online]. Available: https://www.labcenter.com/microprocessors/
7. SimulIDE, *"Supported Microcontrollers Documentation."* [Online]. Available: https://simulide.com/p/mcus/
8. M. A. Mazidi, R. D. McKinlay, and D. Causey, *PIC Microcontroller and Embedded Systems: Using Assembly and C*, Pearson Prentice Hall, 2008.
9. Python Software Foundation, *"Python 3 Documentation — `tkinter` Graphical User Interfaces with Tk."* [Online]. Available: https://docs.python.org/3/library/tkinter.html

### E.2. Chỉ mục Trích dẫn Hình ảnh & Bảng biểu Kỹ thuật (Mục 5.10)

| Hình / Bảng sử dụng trong Báo cáo & Slide | Nguồn gốc chính thức | Số Hình / Bảng & Trang gốc |
| :--- | :--- | :--- |
| Sơ đồ chân 40-pin PDIP PIC16F877A | `PIC16F87XA Data Sheet (DS39582C)` | Pin Diagrams, p. 3; Table 1-3, pp. 10–13 |
| Sơ đồ khối kiến trúc CPU PIC16F877A | `PIC16F87XA Data Sheet (DS39582C)` | Figure 1-2, p. 7 |
| Bản đồ bộ nhớ Chương trình & Stack 8 mức | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-1, p. 15 |
| Bản đồ Register File 4 Bank & SFR | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-3, p. 17; Table 2-1, pp. 19–21 |
| Cơ chế nạp PC (`PCL`/`PCLATH`) & Định địa chỉ | `PIC16F87XA Data Sheet (DS39582C)` | Figure 2-5, p. 30; Figure 2-6, p. 31 |
| Sơ đồ khối Timer0 / Timer1 / Timer2 / PWM | `PIC16F87XA Data Sheet (DS39582C)` | Figure 5-1 (p. 53), 6-2 (p. 58), 7-1 (p. 61), 8-3 (p. 67) |
| Sơ đồ khối ADC 10-bit & Canh lề kết quả | `PIC16F87XA Data Sheet (DS39582C)` | Figure 11-1, p. 129; Figure 11-4, p. 132 |
| Mạch Thạch anh, Mạch `~MCLR` & Logic Ngắt | `PIC16F87XA Data Sheet (DS39582C)` | Figure 14-1 (p. 145), 14-5 (p. 148), 14-10 (p. 153) |
| Định dạng Từ lệnh 14-bit & Bảng 35 Opcode | `PIC16F87XA Data Sheet (DS39582C)` | Figure 15-1, p. 159; Table 15-2, p. 160 |
| Biểu đồ xung nhịp `Q1–Q4` (`TCY = 4/FOSC`) | `PIC16F87XA Data Sheet (DS39582C)` | Figure 17-4, p. 182 |
| Kiến trúc & Thông số đối chiếu ATmega32 | `ATmega32(L) Data Sheet (2503Q–AVR–02/11)` | Block Diagram p. 5; SREG p. 10; Memory p. 16–18; Vectors p. 45 |
