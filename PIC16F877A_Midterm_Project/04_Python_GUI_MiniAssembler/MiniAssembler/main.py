"""
PIC16F877A Educational Mini Assembler — Tkinter GUI Application (Component 4).
Supports all 35 PIC16F877A 14-bit instructions, 2-pass label resolution, syntax highlighting,
live Opcode Table Viewer/Search, Intel HEX export, and listing export.
"""

import csv
import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from typing import Optional

from encoder import AssemblyResult, assemble
from instruction_set import INSTRUCTION_SET
from parser import DIRECTIVES


DEFAULT_SAMPLE = """; PIC16F877A Mini Assembler — Sample Verification Program
; Demonstrates Data Transfer, Arithmetic, Logical, Bit, and Branch instructions
        ORG     0x0000
        BSF     STATUS, RP0     ; Select Bank 1 (STATUS=0x03, RP0=5)
        CLRF    TRISB           ; PORTB as Output (TRISB=0x86 -> 7-bit f=0x06)
        BCF     STATUS, RP0     ; Back to Bank 0
        MOVLW   0x05            ; Load literal 5 into W
        MOVWF   0x20            ; COUNT = 5
LOOP:   INCF    PORTB, F        ; Increment PORTB
        DECFSZ  0x20, F         ; Decrement COUNT, skip GOTO when 0
        GOTO    LOOP            ; Jump back to LOOP (0x0005)
        END
"""


class MiniAssemblerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PIC16F877A Educational Mini Assembler (14-bit Mid-Range RISC)")
        self.root.geometry("1220x760")
        self.root.minsize(980, 620)
        self.last_result: Optional[AssemblyResult] = None
        self.current_file: Optional[str] = None

        self._configure_styles()
        self._build_ui()
        self._load_text(DEFAULT_SAMPLE)
        self.on_assemble()

    def _configure_styles(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#1B365D")
        style.configure("Badge.TLabel", font=("Segoe UI", 10, "bold"), foreground="#FFFFFF", background="#1B365D", padding=(10, 4))
        style.configure("Treeview", font=("Consolas", 10), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"))

    def _build_ui(self) -> None:
        # ---- Top Header Bar ----
        header = ttk.Frame(self.root, padding=(12, 8))
        header.pack(fill=tk.X)

        ttk.Label(header, text="PIC16F877A Educational Mini Assembler", style="Header.TLabel").pack(side=tk.LEFT)
        ttk.Label(
            header,
            text="Target MCU: PIC16F877A  |  14-bit Word  |  35 Instructions",
            style="Badge.TLabel",
        ).pack(side=tk.RIGHT)

        # ---- Toolbar ----
        toolbar = ttk.Frame(self.root, padding=(12, 4))
        toolbar.pack(fill=tk.X)

        ttk.Button(toolbar, text="Load .asm", command=self.on_load_file).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(toolbar, text="Assemble / Translate (F5)", style="Accent.TButton", command=self.on_assemble).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Clear", command=self.on_clear).pack(side=tk.LEFT, padx=6)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(toolbar, text="Save Results (.lst/.csv)", command=self.on_save_results).pack(side=tk.LEFT, padx=6)
        ttk.Button(toolbar, text="Export Intel .hex", command=self.on_export_hex).pack(side=tk.LEFT, padx=6)
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=8)
        ttk.Button(toolbar, text="Opcode Table (35 Instructions)", command=self.open_opcode_viewer).pack(side=tk.LEFT, padx=6)

        self.status_var = tk.StringVar(value="Ready")
        ttk.Label(toolbar, textvariable=self.status_var, font=("Segoe UI", 9, "italic"), foreground="#333333").pack(side=tk.RIGHT)

        # ---- Main Horizontal Split Pane ----
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=12, pady=(4, 6))

        # Left Panel: Editor with Line Numbers
        left_frame = ttk.LabelFrame(paned, text="Assembly Source Code Editor (.asm)", padding=6)
        paned.add(left_frame, weight=42)

        editor_container = ttk.Frame(left_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(
            editor_container,
            width=5,
            padx=4,
            takefocus=0,
            border=0,
            background="#ECEFF4",
            foreground="#4C566A",
            font=("Consolas", 11),
            state=tk.DISABLED,
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.editor = tk.Text(
            editor_container,
            wrap=tk.NONE,
            font=("Consolas", 11),
            undo=True,
            bg="#FFFFFF",
            fg="#1E1E1E",
            insertbackground="#000000",
        )
        y_scroll = ttk.Scrollbar(editor_container, orient=tk.VERTICAL, command=self._on_editor_yscroll)
        x_scroll = ttk.Scrollbar(left_frame, orient=tk.HORIZONTAL, command=self.editor.xview)
        self.editor.configure(yscrollcommand=self._sync_yscroll(y_scroll), xscrollcommand=x_scroll.set)

        y_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        x_scroll.pack(fill=tk.X)

        # Syntax highlight tags
        self.editor.tag_configure("mnemonic", foreground="#005CC5", font=("Consolas", 11, "bold"))
        self.editor.tag_configure("directive", foreground="#6F42C1", font=("Consolas", 11, "bold"))
        self.editor.tag_configure("comment", foreground="#22863A", font=("Consolas", 11, "italic"))
        self.editor.tag_configure("number", foreground="#D73A49")
        self.editor.tag_configure("label", foreground="#B08800", font=("Consolas", 11, "bold"))
        self.editor.tag_configure("error_line", background="#FFE6E6")

        self.editor.bind("<KeyRelease>", lambda _e: self._refresh_editor_decorations())
        self.root.bind("<F5>", lambda _e: self.on_assemble())
        self.root.bind("<Control-Return>", lambda _e: self.on_assemble())

        # Right Panel: Tabs (Translation Table, Intel HEX, Symbol Table)
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=58)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Translation Table
        tab_table = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_table, text="Machine-Code Translation Table")

        cols = ("addr", "asm", "bin", "hex", "size", "cycles")
        self.tree = ttk.Treeview(tab_table, columns=cols, show="headings", selectmode="browse")
        self.tree.heading("addr", text="Address")
        self.tree.heading("asm", text="Assembly Line")
        self.tree.heading("bin", text="Binary (14-bit)")
        self.tree.heading("hex", text="Hex")
        self.tree.heading("size", text="Size")
        self.tree.heading("cycles", text="Cycles")

        self.tree.column("addr", width=78, anchor=tk.CENTER)
        self.tree.column("asm", width=230, anchor=tk.W)
        self.tree.column("bin", width=165, anchor=tk.CENTER)
        self.tree.column("hex", width=75, anchor=tk.CENTER)
        self.tree.column("size", width=65, anchor=tk.CENTER)
        self.tree.column("cycles", width=60, anchor=tk.CENTER)

        tree_y = ttk.Scrollbar(tab_table, orient=tk.VERTICAL, command=self.tree.yview)
        tree_x = ttk.Scrollbar(tab_table, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_y.set, xscrollcommand=tree_x.set)
        tree_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)
        tree_x.pack(fill=tk.X)

        # Tab 2: Intel HEX Output
        tab_hex = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_hex, text="Intel HEX (.hex)")
        self.hex_view = scrolledtext.ScrolledText(tab_hex, font=("Consolas", 11), state=tk.DISABLED, bg="#F8F9FA")
        self.hex_view.pack(fill=tk.BOTH, expand=True)

        # Tab 3: Symbol Table
        tab_sym = ttk.Frame(self.notebook, padding=4)
        self.notebook.add(tab_sym, text="Symbol Table (Labels & EQU)")
        self.sym_tree = ttk.Treeview(tab_sym, columns=("name", "hex_val", "dec_val"), show="headings")
        self.sym_tree.heading("name", text="Symbol / Label")
        self.sym_tree.heading("hex_val", text="Hex Value / Address")
        self.sym_tree.heading("dec_val", text="Decimal")
        self.sym_tree.column("name", width=220, anchor=tk.W)
        self.sym_tree.column("hex_val", width=160, anchor=tk.CENTER)
        self.sym_tree.column("dec_val", width=120, anchor=tk.CENTER)
        self.sym_tree.pack(fill=tk.BOTH, expand=True)

        # ---- Bottom Error / Console Panel ----
        console_frame = ttk.LabelFrame(self.root, text="Assembler Output & Error Console", padding=6)
        console_frame.pack(fill=tk.X, padx=12, pady=(0, 10))
        self.console = scrolledtext.ScrolledText(console_frame, height=6, font=("Consolas", 10), state=tk.DISABLED, bg="#1E1E1E", fg="#D4D4D4")
        self.console.pack(fill=tk.X)

    def _on_editor_yscroll(self, *args) -> None:
        self.editor.yview(*args)
        self.line_numbers.yview(*args)

    def _sync_yscroll(self, scrollbar: ttk.Scrollbar):
        def callback(first, last):
            scrollbar.set(first, last)
            self.line_numbers.yview_moveto(first)
        return callback

    def _refresh_editor_decorations(self) -> None:
        content = self.editor.get("1.0", tk.END)
        total_lines = max(1, content.count("\n"))

        # Update line numbers
        self.line_numbers.configure(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, total_lines + 1)))
        self.line_numbers.configure(state=tk.DISABLED)

        # Syntax highlight
        for tag in ("mnemonic", "directive", "comment", "number", "label"):
            self.editor.tag_remove(tag, "1.0", tk.END)

        for idx, line in enumerate(content.splitlines(), start=1):
            semi = line.find(";")
            code_part = line if semi == -1 else line[:semi]
            if semi != -1:
                self.editor.tag_add("comment", f"{idx}.{semi}", f"{idx}.end")

            for m in re.finditer(r"\b([A-Za-z_#][A-Za-z0-9_]*)\b(:?)", code_part):
                word = m.group(1).upper()
                has_colon = m.group(2) == ":"
                start_idx = f"{idx}.{m.start()}"
                end_idx = f"{idx}.{m.end()}"
                if has_colon:
                    self.editor.tag_add("label", start_idx, end_idx)
                elif word in INSTRUCTION_SET:
                    self.editor.tag_add("mnemonic", start_idx, end_idx)
                elif word in DIRECTIVES:
                    self.editor.tag_add("directive", start_idx, end_idx)

            for m in re.finditer(r"\b(?:0[xXbBoO][0-9A-Fa-f]+|[HhDdBbOo]'[0-9A-Fa-f_]+'|[0-9]+[hH]?)\b", code_part):
                self.editor.tag_add("number", f"{idx}.{m.start()}", f"{idx}.{m.end()}")

    def _load_text(self, text: str) -> None:
        self.editor.delete("1.0", tk.END)
        self.editor.insert("1.0", text)
        self._refresh_editor_decorations()

    def _set_console(self, message: str, is_error: bool = False) -> None:
        self.console.configure(state=tk.NORMAL, fg="#FF8080" if is_error else "#A3BE8C")
        self.console.delete("1.0", tk.END)
        self.console.insert("1.0", message)
        self.console.configure(state=tk.DISABLED)

    def on_load_file(self) -> None:
        default_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "examples")
        path = filedialog.askopenfilename(
            title="Open PIC16F877A Assembly File",
            initialdir=default_dir if os.path.isdir(default_dir) else ".",
            filetypes=[("Assembly Files", "*.asm *.s *.inc"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as fh:
                self._load_text(fh.read())
            self.current_file = path
            self.status_var.set(f"Loaded: {os.path.basename(path)}")
            self.on_assemble()
        except OSError as exc:
            messagebox.showerror("File Error", f"Unable to open file:\n{exc}")

    def on_clear(self) -> None:
        self.editor.delete("1.0", tk.END)
        self.editor.tag_remove("error_line", "1.0", tk.END)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.sym_tree.get_children():
            self.sym_tree.delete(row)
        self.hex_view.configure(state=tk.NORMAL)
        self.hex_view.delete("1.0", tk.END)
        self.hex_view.configure(state=tk.DISABLED)
        self._set_console("Workspace cleared.", is_error=False)
        self.last_result = None
        self.status_var.set("Cleared")
        self._refresh_editor_decorations()

    def on_assemble(self) -> None:
        self.editor.tag_remove("error_line", "1.0", tk.END)
        source = self.editor.get("1.0", tk.END)
        res = assemble(source)
        self.last_result = res

        # Clear previous outputs
        for row in self.tree.get_children():
            self.tree.delete(row)
        for row in self.sym_tree.get_children():
            self.sym_tree.delete(row)

        if not res.success:
            for err in res.errors:
                self.editor.tag_add("error_line", f"{err.line_no}.0", f"{err.line_no}.end")
            err_msg = f"Assembly FAILED ({len(res.errors)} error(s)):\n" + "\n".join(str(e) for e in res.errors)
            self._set_console(err_msg, is_error=True)
            self.status_var.set(f"Error: {len(res.errors)} issue(s) found")
            return

        for inst in res.instructions:
            asm_disp = f"{inst.label}: {inst.assembly_line}" if inst.label else inst.assembly_line
            self.tree.insert(
                "",
                tk.END,
                values=(
                    f"0x{inst.address:04X}",
                    asm_disp,
                    inst.binary_str,
                    f"0x{inst.hex_str}",
                    f"{inst.size_words} word",
                    inst.cycles,
                ),
            )

        for name, val in res.user_symbols.items():
            self.sym_tree.insert("", tk.END, values=(name, f"0x{val:04X}", str(val)))

        self.hex_view.configure(state=tk.NORMAL)
        self.hex_view.delete("1.0", tk.END)
        self.hex_view.insert("1.0", res.intel_hex)
        self.hex_view.configure(state=tk.DISABLED)

        cfg_note = f"  |  __CONFIG = 0x{res.config_word:04X}" if res.config_word is not None else ""
        msg = (
            f"Assembly SUCCEEDED — Target: PIC16F877A (14-bit)\n"
            f"Encoded {len(res.instructions)} instruction word(s) ({len(res.instructions) * 2} bytes)  |  "
            f"{len(res.user_symbols)} user symbol(s){cfg_note}"
        )
        self._set_console(msg, is_error=False)
        self.status_var.set(f"OK: {len(res.instructions)} words assembled")

    def on_save_results(self) -> None:
        if not self.last_result or not self.last_result.success:
            messagebox.showwarning("No Valid Output", "Please assemble valid code before saving results.")
            return
        path = filedialog.asksaveasfilename(
            title="Save Translation Results",
            defaultextension=".lst",
            filetypes=[("Listing File (.lst)", "*.lst"), ("CSV Table (.csv)", "*.csv"), ("Text File (.txt)", "*.txt")],
        )
        if not path:
            return
        try:
            if path.lower().endswith(".csv"):
                with open(path, "w", newline="", encoding="utf-8") as fh:
                    writer = csv.writer(fh)
                    writer.writerow(["Address", "Label", "Assembly Line", "Binary (14-bit)", "Hex", "Size (Words)", "Cycles"])
                    for inst in self.last_result.instructions:
                        writer.writerow([
                            f"0x{inst.address:04X}",
                            inst.label or "",
                            inst.assembly_line,
                            inst.binary_str,
                            f"0x{inst.hex_str}",
                            inst.size_words,
                            inst.cycles,
                        ])
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(self.last_result.listing_text)
            self.status_var.set(f"Saved: {os.path.basename(path)}")
            messagebox.showinfo("Saved", f"Translation results saved to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Save Error", f"Unable to save file:\n{exc}")

    def on_export_hex(self) -> None:
        if not self.last_result or not self.last_result.success:
            messagebox.showwarning("No Valid Output", "Please assemble valid code before exporting Intel HEX.")
            return
        path = filedialog.asksaveasfilename(
            title="Export Intel HEX Firmware",
            defaultextension=".hex",
            filetypes=[("Intel HEX Files", "*.hex"), ("All Files", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(self.last_result.intel_hex)
            self.status_var.set(f"Exported HEX: {os.path.basename(path)}")
            messagebox.showinfo("Exported", f"Intel HEX firmware exported to:\n{path}")
        except OSError as exc:
            messagebox.showerror("Export Error", f"Unable to export HEX:\n{exc}")

    def open_opcode_viewer(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("PIC16F877A Complete 35-Instruction Opcode Reference (DS39582C Table 15-2)")
        win.geometry("920x520")

        search_frame = ttk.Frame(win, padding=8)
        search_frame.pack(fill=tk.X)
        ttk.Label(search_frame, text="Search Mnemonic / Category / Description:").pack(side=tk.LEFT)
        query_var = tk.StringVar()
        entry = ttk.Entry(search_frame, textvariable=query_var, width=36)
        entry.pack(side=tk.LEFT, padx=8)

        cols = ("mnem", "cat", "syntax", "pattern", "base", "cycles", "flags", "desc")
        tv = ttk.Treeview(win, columns=cols, show="headings")
        headers = {
            "mnem": ("Mnemonic", 80), "cat": ("Category", 105), "syntax": ("Syntax", 110),
            "pattern": ("14-bit Opcode Pattern", 160), "base": ("Base Hex", 75),
            "cycles": ("Cycles", 55), "flags": ("Flags", 75), "desc": ("Description", 220),
        }
        for col, (title, w) in headers.items():
            tv.heading(col, text=title)
            tv.column(col, width=w, anchor=tk.CENTER if col in ("mnem", "pattern", "base", "cycles", "flags") else tk.W)

        ybar = ttk.Scrollbar(win, orient=tk.VERTICAL, command=tv.yview)
        tv.configure(yscrollcommand=ybar.set)
        ybar.pack(side=tk.RIGHT, fill=tk.Y)
        tv.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        def populate(*_args):
            q = query_var.get().strip().upper()
            for r in tv.get_children():
                tv.delete(r)
            for mnem in sorted(INSTRUCTION_SET.keys()):
                d = INSTRUCTION_SET[mnem]
                hay = f"{d.mnemonic} {d.category} {d.description} {d.syntax}".upper()
                if not q or q in hay:
                    tv.insert("", tk.END, values=(d.mnemonic, d.category, d.syntax, d.pattern, f"0x{d.base_opcode:04X}", d.cycles, d.flags, d.description))

        query_var.trace_add("write", populate)
        populate()
        entry.focus_set()


def main() -> None:
    root = tk.Tk()
    MiniAssemblerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
