# BẢNG TẬP LỆNH, MÃ OPCODE 14-BIT & HƯỚNG DẪN DỊCH MÃ MÁY PIC16F877A (NỘI DUNG THÔ 100%)
**Đích xuất bản:** `Instruction_Set_Opcode_Table.pdf` (Component 3 — Mục 7, **10 điểm** riêng trong Rubric; là đặc tả chuẩn cho Component 4 `instruction_set.py` & `encoder.py`)  
**Nguồn xác thực:** Microchip *PIC16F87XA Data Sheet* (`DS39582C`, Section 15.0, Table 15-1, Figure 15-1, Table 15-2, pp. 159–165).

---

## 1. Kiến thức Nền tảng về Dịch Assembly sang Mã máy (Đủ 10 chủ đề Mục 7.1)

1. **Biểu diễn Mã máy (Machine-Code Representation):** CPU `PIC16F877A` không hiểu chữ gợi nhớ (mnemonic) như `MOVLW`, `BSF`, mà chỉ đọc các từ nhị phân cố định **14-bit (1 word)** từ bộ nhớ chương trình Flash (`0000h–1FFFh`). Để con người dễ đọc và đối chiếu với file `.lst`/`.hex`, từ 14-bit này được viết dưới dạng **4 ký tự thập lục phân (Hex)** trong phạm vi `0x0000 – 0x3FFF` (hai bit cao nhất 15–14 luôn đệm bằng `0`).
2. **Trường Opcode và Trường Toán hạng (Opcode & Operand Fields — `Table 15-1`, p. 159):**
   - `OPCODE`: Các bit cao xác định loại phép toán CPU cần thực hiện.
   - `f` (**7 bit**, `0x00 – 0x7F`): Địa chỉ offset của thanh ghi tệp (File Register) trong Bank hiện tại. *(Lưu ý quan trọng: Khi viết `TRISB = 0x86`, chỉ 7 bit thấp `0x86 & 0x7F = 0x06` được nhúng vào mã lệnh; 2 bit cao chọn Bank nằm ở `STATUS<RP1:RP0>`!)*
   - `d` (**1 bit**, `0` hoặc `1`): Chọn nơi lưu kết quả (`d = 0` hoặc `, W` lưu vào thanh ghi `W`; `d = 1` hoặc `, F` lưu lại vào thanh ghi `f`; mặc định của MPASM nếu bỏ trống là `d = 1`).
   - `b` (**3 bit**, `0 – 7`): Vị trí bit cần thao tác trong thanh ghi 8-bit `f`.
   - `k` (**8 bit**, `0x00 – 0xFF` hoặc **11 bit**, `0x000 – 0x7FF`): Hằng số tức thời (Literal) hoặc địa chỉ nhảy/gọi hàm (Branch/Call Target).
   - `x` (**Don't care**): Bit không quan tâm trong giải mã phần cứng; theo khuyến cáo của Microchip (`Table 15-1`, p. 159), **Assembler luôn sinh mã với `x = 0`** để đảm bảo tương thích với mọi công cụ chính hãng.
3. **3 Định dạng Từ lệnh 14-bit (`Figure 15-1`, p. 159):**
   ```text
   (A) Byte-oriented File Register:
       Bit:  13 12 11 10  9  8 |  7  |  6  5  4  3  2  1  0
            [   OPCODE (6b)    |  d  |       f (7-bit)      ]

   (B) Bit-oriented File Register:
       Bit:  13 12 11 10 |  9  8  7 |  6  5  4  3  2  1  0
            [ OPCODE(4b) |  b (3b)  |       f (7-bit)      ]

   (C1) Literal & Control (hằng số 8-bit):
       Bit:  13 12 11 10  9  8 |  7  6  5  4  3  2  1  0
            [   OPCODE (6b)    |        k (8-bit)        ]

   (C2) Branch / Call (CALL & GOTO, địa chỉ 11-bit):
       Bit:  13 12 11 | 10  9  8  7  6  5  4  3  2  1  0
            [ OP (3b) |            k (11-bit)            ]
   ```
4. **Độ dài Lệnh (Instruction Length):** Mọi lệnh của PIC16F877A đều dài cố định **1 word (14-bit)** → mỗi lệnh làm bộ đếm địa chỉ chương trình `PC` tăng đúng **+1** (rất đơn giản so với AVR 16/32-bit hay 8051 1/2/3-byte).
5. **Chế độ Định địa chỉ (Addressing Modes):** Direct (`RP1:RP0` + 7-bit `f`), Indirect (`IRP:FSR` qua `INDF`), Immediate/Literal (`k` 8-bit), Absolute/Paged Branch (`PCLATH<4:3>` + 11-bit `k`).
6. **Quy tắc Chuyển đổi Nhị phân ↔ Thập lục phân (Binary ↔ Hex):** Đệm thêm `00` vào trước 14 bit để đủ 16 bit, chia thành 4 nhóm 4-bit (nibble) từ trái sang phải rồi đổi từng nhóm sang `0–F`. Ví dụ: `11 0000 0101 0101` → `0011 0000 0101 0101` → **`3055h`** (`0x3055`).
7. **Quy tắc Mã hóa Lệnh (Encoding Rules):** Thực hiện bằng phép dịch bit (`<<`) và phép hợp bit (`|`) giữa mã nền (base opcode) với các toán hạng đã kiểm tra phạm vi hợp lệ (`0 ≤ f ≤ 0x7F`, `d ∈ {0,1}`, `0 ≤ b ≤ 7`, `0 ≤ k ≤ 0xFF` hoặc `0x7FF`).
8. **Nhãn (Labels) & Tính Địa chỉ Nhảy (2-Pass Assembly):**
   - **Pass 1 (Quét bảng ký hiệu — Symbol Table):** Duyệt từ trên xuống bắt đầu từ `addr = 0` (hoặc giá trị sau chỉ thị `ORG`), ghi nhận cặp `Label → addr` cho mọi nhãn, chỉ tăng `addr += 1` khi gặp dòng có lệnh thực thi (bỏ qua dòng trống, comment `;`, `EQU`).
   - **Pass 2 (Sinh mã máy):** Với `GOTO label` hoặc `CALL label`, tra `target = symbol_table[label]`, lấy 11 bit thấp `k = target & 0x7FF` rồi mã hóa `0x2800 | k` (`GOTO`) hoặc `0x2000 | k` (`CALL`). *(Nhờ 2-Pass nên giải quyết được cả nhảy lùi lẫn nhảy tiến tới nhãn khai báo phía dưới.)*
9. **Quan hệ giữa Mã máy, Bộ nhớ Chương trình và File Intel HEX:**
   - Trong Flash: lệnh thứ $n$ nằm tại địa chỉ từ `Word_Addr = n` (`0x0000, 0x0001, ...`).
   - Trong file Intel HEX: mỗi từ 14-bit được tách thành **2 byte theo thứ tự Little-Endian** (`Low_Byte = word & 0xFF`, `High_Byte = (word >> 8) & 0x3F`), và **địa chỉ byte trong file HEX bằng `2 × Word_Addr`**.

---

## 2. Bảng Toàn bộ 35 Lệnh & Mã Opcode 14-bit của PIC16F877A (`Table 15-2`, p. 160)

> **Quy ước cho Python Mini Assembler (`x = 0`):** Cột **Công thức Mã hóa (Python)** là biểu thức bit chuẩn có thể dùng trực tiếp trong `instruction_set.py` và `encoder.py`. Các dấu `f`, `d`, `b`, `k` đã được che mặt nạ đúng số bit (`f & 0x7F`, `d & 1`, `b & 7`, `k & 0xFF` hoặc `k & 0x7FF`).

### 2.1. Nhóm Byte-Oriented File Register Operations (18 lệnh)

| STT | Lệnh & Toán hạng | Mô tả ngắn | Chu kỳ | Mã Nhị phân 14-bit (`MSb → LSb`) | Mã nền Hex (`x=0`) | Công thức Mã hóa (Python) | Cờ `STATUS` |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 1 | `ADDWF f, d` | Cộng `W` và `f` (`W + f → dest`) | 1 | `00 0111 dfff ffff` | `0x0700` | `0x0700 \| (d << 7) \| (f & 0x7F)` | `C, DC, Z` |
| 2 | `ANDWF f, d` | AND `W` với `f` (`W & f → dest`) | 1 | `00 0101 dfff ffff` | `0x0500` | `0x0500 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 3 | `CLRF f` | Xóa thanh ghi `f` (`0 → f`) | 1 | `00 0001 1fff ffff` | `0x0180` | `0x0180 \| (f & 0x7F)` | `Z` |
| 4 | `CLRW` | Xóa thanh ghi `W` (`0 → W`) | 1 | `00 0001 0xxx xxxx` | `0x0100` | `0x0100` | `Z` |
| 5 | `COMF f, d` | Đảo bit `f` (`~f → dest`) | 1 | `00 1001 dfff ffff` | `0x0900` | `0x0900 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 6 | `DECF f, d` | Giảm `f` đi 1 (`f - 1 → dest`) | 1 | `00 0011 dfff ffff` | `0x0300` | `0x0300 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 7 | `DECFSZ f, d` | Giảm `f`, bỏ qua lệnh kế nếu `= 0` | 1(2) | `00 1011 dfff ffff` | `0x0B00` | `0x0B00 \| (d << 7) \| (f & 0x7F)` | Không |
| 8 | `INCF f, d` | Tăng `f` thêm 1 (`f + 1 → dest`) | 1 | `00 1010 dfff ffff` | `0x0A00` | `0x0A00 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 9 | `INCFSZ f, d` | Tăng `f`, bỏ qua lệnh kế nếu `= 0` | 1(2) | `00 1111 dfff ffff` | `0x0F00` | `0x0F00 \| (d << 7) \| (f & 0x7F)` | Không |
| 10 | `IORWF f, d` | OR `W` với `f` (`W \| f → dest`) | 1 | `00 0100 dfff ffff` | `0x0400` | `0x0400 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 11 | `MOVF f, d` | Di chuyển `f` (`f → dest`, cập nhật `Z`) | 1 | `00 1000 dfff ffff` | `0x0800` | `0x0800 \| (d << 7) \| (f & 0x7F)` | `Z` |
| 12 | `MOVWF f` | Ghi `W` vào `f` (`W → f`) | 1 | `00 0000 1fff ffff` | `0x0080` | `0x0080 \| (f & 0x7F)` | Không |
| 13 | `NOP` | Không thao tác (trễ 1 chu kỳ) | 1 | `00 0000 0xx0 0000` | `0x0000` | `0x0000` | Không |
| 14 | `RLF f, d` | Quay trái `f` qua cờ `C` | 1 | `00 1101 dfff ffff` | `0x0D00` | `0x0D00 \| (d << 7) \| (f & 0x7F)` | `C` |
| 15 | `RRF f, d` | Quay phải `f` qua cờ `C` | 1 | `00 1100 dfff ffff` | `0x0C00` | `0x0C00 \| (d << 7) \| (f & 0x7F)` | `C` |
| 16 | `SUBWF f, d` | Trừ `W` khỏi `f` (`f - W → dest`) | 1 | `00 0010 dfff ffff` | `0x0200` | `0x0200 \| (d << 7) \| (f & 0x7F)` | `C, DC, Z` |
| 17 | `SWAPF f, d` | Hoán đổi 2 nibble của `f` | 1 | `00 1110 dfff ffff` | `0x0E00` | `0x0E00 \| (d << 7) \| (f & 0x7F)` | Không |
| 18 | `XORWF f, d` | XOR `W` với `f` (`W ^ f → dest`) | 1 | `00 0110 dfff ffff` | `0x0600` | `0x0600 \| (d << 7) \| (f & 0x7F)` | `Z` |

### 2.2. Nhóm Bit-Oriented File Register Operations (4 lệnh)

| STT | Lệnh & Toán hạng | Mô tả ngắn | Chu kỳ | Mã Nhị phân 14-bit (`MSb → LSb`) | Mã nền Hex | Công thức Mã hóa (Python) | Cờ `STATUS` |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 19 | `BCF f, b` | Xóa bit `b` trong `f` (`0 → f<b>`) | 1 | `01 00bb bfff ffff` | `0x1000` | `0x1000 \| ((b & 7) << 7) \| (f & 0x7F)` | Không |
| 20 | `BSF f, b` | Đặt bit `b` trong `f` (`1 → f<b>`) | 1 | `01 01bb bfff ffff` | `0x1400` | `0x1400 \| ((b & 7) << 7) \| (f & 0x7F)` | Không |
| 21 | `BTFSC f, b` | Kiểm tra bit `b`, bỏ qua nếu `= 0` | 1(2) | `01 10bb bfff ffff` | `0x1800` | `0x1800 \| ((b & 7) << 7) \| (f & 0x7F)` | Không |
| 22 | `BTFSS f, b` | Kiểm tra bit `b`, bỏ qua nếu `= 1` | 1(2) | `01 11bb bfff ffff` | `0x1C00` | `0x1C00 \| ((b & 7) << 7) \| (f & 0x7F)` | Không |

### 2.3. Nhóm Literal and Control Operations (13 lệnh)

| STT | Lệnh & Toán hạng | Mô tả ngắn | Chu kỳ | Mã Nhị phân 14-bit (`MSb → LSb`) | Mã nền Hex (`x=0`) | Công thức Mã hóa (Python) | Cờ `STATUS` |
| :---: | :--- | :--- | :---: | :---: | :---: | :--- | :---: |
| 23 | `ADDLW k` | Cộng hằng số `k` với `W` (`W + k → W`) | 1 | `11 111x kkkk kkkk` | `0x3E00` | `0x3E00 \| (k & 0xFF)` | `C, DC, Z` |
| 24 | `ANDLW k` | AND hằng số `k` với `W` (`W & k → W`) | 1 | `11 1001 kkkk kkkk` | `0x3900` | `0x3900 \| (k & 0xFF)` | `Z` |
| 25 | `CALL k` | Gọi chương trình con tại địa chỉ `k` | 2 | `10 0kkk kkkk kkkk` | `0x2000` | `0x2000 \| (k & 0x7FF)` | Không |
| 26 | `CLRWDT` | Xóa Watchdog Timer & prescaler | 1 | `00 0000 0110 0100` | `0x0064` | `0x0064` | `~TO, ~PD` |
| 27 | `GOTO k` | Nhảy không điều kiện tới địa chỉ `k` | 2 | `10 1kkk kkkk kkkk` | `0x2800` | `0x2800 \| (k & 0x7FF)` | Không |
| 28 | `IORLW k` | OR hằng số `k` với `W` (`W \| k → W`) | 1 | `11 1000 kkkk kkkk` | `0x3800` | `0x3800 \| (k & 0xFF)` | `Z` |
| 29 | `MOVLW k` | Nạp hằng số `k` vào `W` (`k → W`) | 1 | `11 00xx kkkk kkkk` | `0x3000` | `0x3000 \| (k & 0xFF)` | Không |
| 30 | `RETFIE` | Trở về từ ngắt (`TOS→PC`, `1→GIE`) | 2 | `00 0000 0000 1001` | `0x0009` | `0x0009` | Không |
| 31 | `RETLW k` | Trở về từ hàm con kèm `k → W` | 2 | `11 01xx kkkk kkkk` | `0x3400` | `0x3400 \| (k & 0xFF)` | Không |
| 32 | `RETURN` | Trở về từ chương trình con (`TOS→PC`) | 2 | `00 0000 0000 1000` | `0x0008` | `0x0008` | Không |
| 33 | `SLEEP` | Vào chế độ ngủ tiết kiệm điện | 1 | `00 0000 0110 0011` | `0x0063` | `0x0063` | `~TO, ~PD` |
| 34 | `SUBLW k` | Trừ `W` khỏi hằng số `k` (`k - W → W`) | 1 | `11 110x kkkk kkkk` | `0x3C00` | `0x3C00 \| (k & 0xFF)` | `C, DC, Z` |
| 35 | `XORLW k` | XOR hằng số `k` với `W` (`W ^ k → W`) | 1 | `11 1010 kkkk kkkk` | `0x3A00` | `0x3A00 \| (k & 0xFF)` | `Z` |

---

## 3. Ví dụ Dịch tay Chi tiết Từng bước (Worked Hand-Encoding Examples)

### Ví dụ A — Lệnh Literal (`MOVLW 0x55`)
1. Tra bảng: `MOVLW k` → `11 00xx kkkk kkkk` (với `x = 0` → `11 0000 kkkk kkkk`).
2. Đổi hằng số `k = 0x55` sang 8-bit nhị phân: `0101 0101`.
3. Ghép 14 bit: `11 0000 0101 0101`.
4. Đệm `00` thành 16 bit: `0011 0000 0101 0101` → Hex: **`0x3055`**.

### Ví dụ B — Lệnh Byte-oriented có bit `d` (`ADDWF 0x20, 1` tức `ADDWF 0x20, F`)
1. Tra bảng: `ADDWF f, d` → `00 0111 dfff ffff`.
2. Toán hạng: `d = 1`, `f = 0x20` (`010 0000`, 7-bit).
3. Ghép 14 bit: `00 0111 1010 0000`.
4. Đổi sang Hex (`0000 0111 1010 0000`): **`0x07A0`**. *(Nếu đích là `W` tức `d = 0` thì ra `0x0720`.)*

### Ví dụ C — Lệnh Bit-oriented (`BSF STATUS, RP0` tức `BSF 0x03, 5`)
1. Tra bảng: `BSF f, b` → `01 01bb bfff ffff`.
2. Toán hạng: `b = 5` (`101`, 3-bit), `f = 0x03` (`000 0011`, 7-bit).
3. Ghép 14 bit: `01 01 101 0000011` = `01 0110 1000 0011`.
4. Đổi sang Hex (`0001 0110 1000 0011`): **`0x1683`**.

### Ví dụ D — Lệnh Nhảy có Nhãn (`GOTO LOOP` với `LOOP` nằm tại địa chỉ `0x0005`)
1. Tra bảng: `GOTO k` → `10 1kkk kkkk kkkk`.
2. Địa chỉ 11-bit của nhãn `LOOP`: `k = 0x005` = `000 0000 0101`.
3. Ghép 14 bit: `10 1000 0000 0101`.
4. Đổi sang Hex (`0010 1000 0000 0101`): **`0x2805`**.

### Ví dụ E — Xử lý Thanh ghi Bank 1 (`CLRF TRISB` với `TRISB = 0x86`)
1. Địa chỉ đầy đủ của `TRISB` là `0x86` (`1000 0110`), nhưng trường `f` trong lệnh chỉ dài **7 bit** → lấy `f = 0x86 & 0x7F = 0x06` (`000 0110`).
2. Tra bảng: `CLRF f` → `00 0001 1fff ffff` → `00 0001 1000 0110` → Hex: **`0x0186`**.
3. CPU hiểu được là `TRISB` (chứ không phải `PORTB` ở `0x06`) nhờ lệnh `BSF STATUS, RP0` ngay trước đó đã đặt `RP0 = 1`.

---

## 4. Dịch trọn vẹn một Chương trình Mẫu sang Mã máy & File Intel HEX

Xét chương trình Assembly mẫu (8 lệnh, cấu hình `PORTB` làm Output rồi tăng `PORTB` 5 lần trong vòng lặp):

```asm
        ORG     0x0000
        BSF     STATUS, 5       ; Chọn Bank 1 (STATUS = 0x03, RP0 = bit 5)
        CLRF    TRISB           ; PORTB = Output (TRISB = 0x86 -> 7-bit f = 0x06)
        BCF     STATUS, 5       ; Quay về Bank 0
        MOVLW   0x05            ; Nạp số lần lặp = 5 vào W
        MOVWF   0x20            ; Lưu vào biến COUNT (0x20)
LOOP:   INCF    PORTB, F        ; Tăng PORTB thêm 1 (PORTB = 0x06, d = 1)
        DECFSZ  0x20, F         ; Giảm COUNT, bỏ qua lệnh kế nếu = 0
        GOTO    LOOP            ; Nhảy về nhãn LOOP (địa chỉ 0x0005)
        END
```

### Bảng kết quả dịch (tương ứng đúng cột bảng đầu ra của Python GUI Mini Assembler — Mục 8.1)

| Address (Word) | Assembly Line | Binary (14-bit) | Hex (4 ký tự) | Size | Little-Endian Bytes (Intel HEX) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| `0x0000` | `BSF 0x03, 5` | `01 0110 1000 0011` | `0x1683` | 1 word | `83 16` |
| `0x0001` | `CLRF 0x06` | `00 0001 1000 0110` | `0x0186` | 1 word | `86 01` |
| `0x0002` | `BCF 0x03, 5` | `01 0010 1000 0011` | `0x1283` | 1 word | `83 12` |
| `0x0003` | `MOVLW 0x05` | `11 0000 0000 0101` | `0x3005` | 1 word | `05 30` |
| `0x0004` | `MOVWF 0x20` | `00 0000 1010 0000` | `0x00A0` | 1 word | `A0 00` |
| `0x0005` | `INCF 0x06, 1` *(LOOP)* | `00 1010 1000 0110` | `0x0A86` | 1 word | `86 0A` |
| `0x0006` | `DECFSZ 0x20, 1` | `00 1011 1010 0000` | `0x0BA0` | 1 word | `A0 0B` |
| `0x0007` | `GOTO 0x005` *(LOOP)* | `10 1000 0000 0101` | `0x2805` | 1 word | `05 28` |

### Chuỗi Intel HEX tương ứng (kiểm chứng Checksum 8-bit)
- **Số byte dữ liệu:** `8 words × 2 = 16 bytes = 0x10`
- **Địa chỉ byte bắt đầu:** `2 × 0x0000 = 0x0000`
- **Loại bản ghi:** `00` (Data)
- **16 byte dữ liệu (Little-Endian):** `83 16 86 01 83 12 05 30 A0 00 86 0A A0 0B 05 28`
- **Tính Checksum:** Tổng tất cả các byte (`0x10 + 0x00 + 0x00 + 0x00 + 0x83 + ... + 0x28`) = `1026 = 0x0402` → lấy bù 2 của byte thấp `0x02`: `(0x100 - 0x02) & 0xFF = 0xFE`.
- **File `.hex` hoàn chỉnh:**
  ```text
  :100000008316860183120530A000860AA00B0528FE
  :00000001FF
  ```

---

## 5. Quy trình Kiểm chứng Độ chính xác Mã máy (Verification — Mục 8.5)
Để đạt trọn vẹn **10 điểm** phần *Machine-code encoding correctness* trong Rubric:
1. Lưu đoạn mã mẫu (chứa đủ toàn bộ các lệnh mà Python Mini Assembler hỗ trợ) thành `examples/sample.asm`.
2. Biên dịch bằng trình hợp dịch chính hãng **`gpasm -p p16f877a sample.asm`** (hoặc MPASM trong MPLAB IDE) để sinh ra `sample.lst` và `sample.hex`.
3. Dịch cùng file `sample.asm` bằng **Python GUI Mini Assembler** của nhóm.
4. Chụp màn hình đặt cạnh nhau (side-by-side) bảng kết quả của Python Mini Assembler và cột mã Hex trong `sample.lst` (kèm bảng đối chiếu 100% khớp từng địa chỉ) đưa vào `MiniAssembler_User_Guide.pdf` và `Test_Results.pdf`.
