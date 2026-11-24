# PIC16F877A Midterm Project — Thư Mục Tổng Hợp Các Mục Chính

Thư mục này đóng gói đầy đủ, gọn gàng toàn bộ **các mục chính của Midterm Project** theo đúng cấu trúc yêu cầu trong đề bài `MPS_MIDTERM PROJECT ASSIGNMENT.docx` (loại bỏ các file tạm/cache).

## Cấu trúc thư mục theo từng mục của đề bài

| Thư mục con | Ánh xạ mục đề bài | Nội dung chính bên trong |
| :--- | :--- | :--- |
| `00_Overview_and_Datasheets/` | Đề bài, Báo cáo tổng hợp & Datasheet gốc | Đề bài gốc `.docx`, file mô tả chi tiết ATmega32 – PIC16F877A – Rubric (`.docx`), ma trận truy vết yêu cầu và 3 file Datasheet chính thức (`ATmega32`, `PIC16F87XA`, `PICmicro Mid-Range Ref Manual`). |
| `01_MCU_Study_Document/` | **Required Component 1** (Section 5 — 15đ + 10đ) | Tài liệu nghiên cứu kiến trúc PIC16F877A (`MCU_Study_Document.pdf`, bản Word `.docx` VI/EN), đối chiếu 10 tiêu chí với ATmega32 và tài liệu tham khảo (`References.pdf`). |
| `02_Assembly_Source_Code/` | **Required Component 2** (Section 6 — 15đ) | Ứng dụng *Smart Irrigation Controller* viết bằng Assembly thuần (`smart_irrigation.asm`, firmware `.hex`, bảng `.lst` và tài liệu giải thuật `Assembly_Documentation.md`). |
| `03_Instruction_Set_and_Machine_Code/` | **Required Component 3** (Section 7 — 10đ) | Bảng giải mã 35 lệnh 14-bit PIC16F877A sang mã nhị phân/hex (`Instruction_Set_Opcode_Table.pdf` + bản `.md` VI/EN). |
| `04_Python_GUI_MiniAssembler/` | **Required Component 4** (Section 8 — 20đ) | Mã nguồn ứng dụng `MiniAssembler/` (Tkinter GUI + 2-Pass Assembler + Unit Tests + ví dụ `sample.asm`) và hướng dẫn sử dụng `MiniAssembler_User_Guide.pdf`. |
| `05_Circuit_Design_and_Simulation/` | **Required Component 5** (Section 9 — 10đ + 10đ) | Hướng dẫn thiết kế mạch & mô phỏng Proteus/SimulIDE (`README_Simulation_Guide.md`), firmware nạp mô phỏng (`.hex`/`.asm`) và báo cáo kiểm thử (`Test_Results.pdf`). |
| `06_Teaching_Presentation/` | **Required Component 6** (Section 10 — 10đ + 5đ) | Bộ slide giảng dạy trên lớp (`Teaching_Slides.pdf`) kèm kịch bản thuyết trình và bộ câu hỏi vấn đáp Q&A (VI/EN). |
| `07_Blackboard_Submission_Package/` | **Required Component 7** (Section 11 — Nộp Blackboard) | Gói thư viện chuẩn định dạng nộp lên *Midterm MCU Self-Study Library* (`GroupXX_PIC16F877A/` gồm các file `.pdf` và `.zip` đóng gói sẵn). |

## Hướng dẫn chạy nhanh Python GUI Mini Assembler

```powershell
cd 04_Python_GUI_MiniAssembler/MiniAssembler
python main.py
```

Chạy kiểm thử tự động bộ mã hóa mã máy 14-bit:

```powershell
cd 04_Python_GUI_MiniAssembler/MiniAssembler
python -m unittest test_assembler.py
```
