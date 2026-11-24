"""
Two-Pass PIC16F877A 14-bit Machine-Code Encoder, Listing Generator, and Intel HEX Exporter.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from error_handler import (
    AssemblyError,
    AssemblyErrorCollector,
    validate_address_11,
    validate_bit_index,
    validate_destination,
    validate_file_register,
    validate_literal_8,
)
from instruction_set import INSTRUCTION_SET, PREDEFINED_SYMBOLS
from parser import ParsedLine, parse_number, parse_source


@dataclass
class EncodedInstruction:
    line_no: int
    address: int            # 13-bit Program Memory word address (0x0000..0x1FFF)
    assembly_line: str      # Clean assembly line shown in GUI table
    machine_word: int       # 14-bit machine code integer (0x0000..0x3FFF)
    binary_str: str         # Formatted 14-bit binary (e.g. "11 0000 0101 0101")
    binary_raw: str         # Contiguous 14-bit binary (e.g. "11000001010101")
    hex_str: str            # 4-digit hex (e.g. "3055")
    size_words: int = 1
    cycles: str = "1"
    label: Optional[str] = None


@dataclass
class AssemblyResult:
    instructions: List[EncodedInstruction] = field(default_factory=list)
    symbols: Dict[str, int] = field(default_factory=dict)
    user_symbols: Dict[str, int] = field(default_factory=dict)
    config_word: Optional[int] = None
    errors: List[AssemblyError] = field(default_factory=list)
    intel_hex: str = ""
    listing_text: str = ""

    @property
    def success(self) -> bool:
        return len(self.errors) == 0


def format_14bit_binary(word: int) -> Tuple[str, str]:
    """Return (raw_14bit, grouped_14bit) strings for a 14-bit machine word."""
    raw = f"{word & 0x3FFF:014b}"
    grouped = f"{raw[0:2]} {raw[2:6]} {raw[6:10]} {raw[10:14]}"
    return raw, grouped


def expand_dt_operands(operands: List[str], symbols: Dict[str, int], line_no: int, raw_line: str) -> List[int]:
    """Expand MPASM DT directive (strings and numeric bytes) into a list of 8-bit values."""
    values: List[int] = []
    for op in operands:
        op = op.strip()
        if (op.startswith('"') and op.endswith('"')) or (op.startswith("'") and op.endswith("'") and len(op) > 3):
            for ch in op[1:-1]:
                values.append(ord(ch) & 0xFF)
        else:
            val = parse_number(op, symbols, line_no, raw_line)
            values.append(validate_literal_8(val, line_no, raw_line))
    return values


def generate_intel_hex(instructions: List[EncodedInstruction], config_word: Optional[int] = None) -> str:
    """
    Generate standard INHX32M Intel HEX compatible with Proteus, SimulIDE, MPASM, and gpasm.
    Each 14-bit word is stored as 2 bytes (Little-Endian) at Byte Address = 2 * Word Address.
    """
    mem: Dict[int, int] = {inst.address: inst.machine_word & 0x3FFF for inst in instructions}
    lines: List[str] = [":020000040000FA"]  # Extended linear address = 0x0000

    def emit_chunk(start_word_addr: int, words: List[int]) -> None:
        byte_addr = start_word_addr * 2
        data_bytes: List[int] = []
        for w in words:
            data_bytes.append(w & 0xFF)         # Low byte first (Little-Endian)
            data_bytes.append((w >> 8) & 0x3F)  # High byte (upper 6 bits)
        record = [len(data_bytes), (byte_addr >> 8) & 0xFF, byte_addr & 0xFF, 0x00] + data_bytes
        checksum = (-sum(record)) & 0xFF
        lines.append(":" + "".join(f"{b:02X}" for b in record + [checksum]))

    sorted_addrs = sorted(mem.keys())
    idx = 0
    while idx < len(sorted_addrs):
        start_addr = sorted_addrs[idx]
        chunk: List[int] = [mem[start_addr]]
        curr = start_addr
        idx += 1
        # Max 8 words (16 bytes) per Intel HEX record, must be contiguous
        while idx < len(sorted_addrs) and sorted_addrs[idx] == curr + 1 and len(chunk) < 8:
            curr = sorted_addrs[idx]
            chunk.append(mem[curr])
            idx += 1
        emit_chunk(start_addr, chunk)

    # Configuration word at 0x2007 (byte address 0x400E)
    if config_word is not None:
        emit_chunk(0x2007, [config_word & 0x3FFF])

    lines.append(":00000001FF")  # End Of File record
    return "\n".join(lines) + "\n"


def generate_listing(instructions: List[EncodedInstruction], config_word: Optional[int] = None) -> str:
    """Generate MPASM/gpasm-style listing output for side-by-side verification."""
    out = [
        "PIC16F877A Mini Assembler Listing File",
        "=" * 78,
        f"{'ADDR':<8}{'HEX':<8}{'BINARY (14-BIT)':<20}{'SIZE':<6}{'CYCLES':<8}ASSEMBLY LINE",
        "-" * 78,
    ]
    for inst in instructions:
        lbl = f"{inst.label}: " if inst.label else ""
        out.append(
            f"0x{inst.address:04X}  0x{inst.hex_str}  {inst.binary_str:<20}{inst.size_words:<6}{inst.cycles:<8}{lbl}{inst.assembly_line}"
        )
    if config_word is not None:
        _, cfg_bin = format_14bit_binary(config_word)
        out.append("-" * 78)
        out.append(f"0x2007  0x{config_word:04X}  {cfg_bin:<20}1     -       __CONFIG 0x{config_word:04X}")
    out.append("=" * 78)
    out.append(f"Total instructions: {len(instructions)} word(s) ({len(instructions) * 2} bytes)")
    return "\n".join(out) + "\n"


def assemble(source_text: str) -> AssemblyResult:
    """
    Assemble PIC16F877A assembly source using a 2-Pass algorithm:
      Pass 1: Process ORG, EQU, CBLOCK, labels -> build complete Symbol Table.
      Pass 2: Encode every instruction to 14-bit Binary/Hex & generate Intel HEX + Listing.
    """
    result = AssemblyResult()
    err_col = AssemblyErrorCollector()
    symbols: Dict[str, int] = dict(PREDEFINED_SYMBOLS)
    user_symbols: Dict[str, int] = {}

    parsed = parse_source(source_text)

    # ========================== PASS 1: SYMBOL TABLE ==========================
    pc = 0
    cblock_addr = 0x20
    for pl in parsed:
        try:
            if pl.mnemonic == "END":
                break

            if pl.mnemonic == "CBLOCK":
                if not pl.operands:
                    raise AssemblyError(pl.line_no, "CBLOCK requires a starting RAM address (e.g. CBLOCK 0x20).", pl.raw_line)
                cblock_addr = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                continue

            if pl.mnemonic == "CBLOCK_ITEM":
                if pl.label:
                    key = pl.label.upper()
                    symbols[key] = cblock_addr
                    user_symbols[pl.label] = cblock_addr
                    cblock_addr += 1
                continue

            if pl.mnemonic == "ENDC":
                continue

            if pl.mnemonic == "EQU":
                if not pl.label or not pl.operands:
                    raise AssemblyError(pl.line_no, "EQU requires '<NAME> EQU <VALUE>'.", pl.raw_line)
                val = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                symbols[pl.label.upper()] = val
                user_symbols[pl.label] = val
                continue

            if pl.mnemonic == "ORG":
                if not pl.operands:
                    raise AssemblyError(pl.line_no, "ORG requires a program memory address.", pl.raw_line)
                pc = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                if pc < 0 or pc > 0x1FFF:
                    raise AssemblyError(pl.line_no, f"ORG address 0x{pc:X} out of Flash range (0x0000–0x1FFF).", pl.raw_line)
                continue

            if pl.mnemonic in ("__CONFIG", "CONFIG"):
                if pl.operands:
                    result.config_word = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc) & 0x3FFF
                continue

            if pl.mnemonic in ("LIST", "PROCESSOR", "INCLUDE", "#INCLUDE", "ERRORLEVEL", "RADIX"):
                continue

            # Record program label at current PC
            if pl.label:
                key = pl.label.upper()
                if key in user_symbols or (key in symbols and key not in PREDEFINED_SYMBOLS):
                    raise AssemblyError(pl.line_no, f"Duplicate label '{pl.label}'.", pl.raw_line)
                symbols[key] = pc
                user_symbols[pl.label] = pc

            # Advance PC based on instruction / directive size
            if pl.mnemonic is None:
                continue
            elif pl.mnemonic == "BANKSEL":
                pc += 2  # Expands to BCF/BSF STATUS, RP0 and RP1
            elif pl.mnemonic == "PAGESEL":
                pc += 2  # Expands to BCF/BSF PCLATH, 3 and 4
            elif pl.mnemonic == "DT":
                vals = expand_dt_operands(pl.operands, symbols, pl.line_no, pl.raw_line)
                pc += len(vals)
            elif pl.mnemonic == "DW":
                pc += len(pl.operands)
            else:
                pc += 1
        except AssemblyError as exc:
            err_col.add(exc.line_no, exc.message, exc.source_line)

    # ========================== PASS 2: CODE ENCODING ==========================
    pc = 0
    for pl in parsed:
        if pl.mnemonic == "END":
            break
        if pl.mnemonic in (
            None, "EQU", "CBLOCK", "CBLOCK_ITEM", "ENDC",
            "__CONFIG", "CONFIG", "LIST", "PROCESSOR", "INCLUDE", "#INCLUDE", "ERRORLEVEL", "RADIX",
        ):
            continue

        try:
            if pl.mnemonic == "ORG":
                pc = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                continue

            # Pseudo-directive: BANKSEL <reg> -> 2 bit operations on STATUS RP0 (5) & RP1 (6)
            if pl.mnemonic == "BANKSEL":
                if len(pl.operands) != 1:
                    raise AssemblyError(pl.line_no, "BANKSEL expects 1 register operand.", pl.raw_line)
                reg_addr = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                bank = (reg_addr >> 7) & 0x03
                rp0_op = ("BSF", 0x1400) if (bank & 1) else ("BCF", 0x1000)
                rp1_op = ("BSF", 0x1400) if (bank & 2) else ("BCF", 0x1000)
                for idx_b, (op_name, base, bit_idx) in enumerate([(rp0_op[0], rp0_op[1], 5), (rp1_op[0], rp1_op[1], 6)]):
                    word = base | (bit_idx << 7) | 0x03
                    b_raw, b_grp = format_14bit_binary(word)
                    result.instructions.append(
                        EncodedInstruction(
                            line_no=pl.line_no,
                            address=pc,
                            assembly_line=f"{op_name} STATUS, {'RP0' if bit_idx == 5 else 'RP1'}  ; BANKSEL {pl.operands[0]}",
                            machine_word=word,
                            binary_str=b_grp,
                            binary_raw=b_raw,
                            hex_str=f"{word:04X}",
                            cycles="1",
                            label=pl.label if idx_b == 0 else None,
                        )
                    )
                    pc += 1
                continue

            # Pseudo-directive: PAGESEL <label> -> 2 bit operations on PCLATH bit 3 & 4
            if pl.mnemonic == "PAGESEL":
                if len(pl.operands) != 1:
                    raise AssemblyError(pl.line_no, "PAGESEL expects 1 label/address operand.", pl.raw_line)
                target = parse_number(pl.operands[0], symbols, pl.line_no, pl.raw_line, pc)
                page = (target >> 11) & 0x03
                p3_op = ("BSF", 0x1400) if (page & 1) else ("BCF", 0x1000)
                p4_op = ("BSF", 0x1400) if (page & 2) else ("BCF", 0x1000)
                for idx_b, (op_name, base, bit_idx) in enumerate([(p3_op[0], p3_op[1], 3), (p4_op[0], p4_op[1], 4)]):
                    word = base | (bit_idx << 7) | 0x0A
                    b_raw, b_grp = format_14bit_binary(word)
                    result.instructions.append(
                        EncodedInstruction(
                            line_no=pl.line_no,
                            address=pc,
                            assembly_line=f"{op_name} PCLATH, {bit_idx}  ; PAGESEL {pl.operands[0]}",
                            machine_word=word,
                            binary_str=b_grp,
                            binary_raw=b_raw,
                            hex_str=f"{word:04X}",
                            cycles="1",
                            label=pl.label if idx_b == 0 else None,
                        )
                    )
                    pc += 1
                continue

            # Directive: DT (Define Table -> sequence of RETLW k)
            if pl.mnemonic == "DT":
                vals = expand_dt_operands(pl.operands, symbols, pl.line_no, pl.raw_line)
                for idx_v, val in enumerate(vals):
                    word = 0x3400 | val
                    b_raw, b_grp = format_14bit_binary(word)
                    ch_disp = f"'{chr(val)}'" if 32 <= val <= 126 else f"0x{val:02X}"
                    result.instructions.append(
                        EncodedInstruction(
                            line_no=pl.line_no,
                            address=pc,
                            assembly_line=f"RETLW 0x{val:02X}  ; DT {ch_disp}",
                            machine_word=word,
                            binary_str=b_grp,
                            binary_raw=b_raw,
                            hex_str=f"{word:04X}",
                            cycles="2",
                            label=pl.label if idx_v == 0 else None,
                        )
                    )
                    pc += 1
                continue

            # Directive: DW (raw 14-bit words)
            if pl.mnemonic == "DW":
                for idx_v, op in enumerate(pl.operands):
                    val = parse_number(op, symbols, pl.line_no, pl.raw_line, pc) & 0x3FFF
                    b_raw, b_grp = format_14bit_binary(val)
                    result.instructions.append(
                        EncodedInstruction(
                            line_no=pl.line_no,
                            address=pc,
                            assembly_line=f"DW 0x{val:04X}",
                            machine_word=val,
                            binary_str=b_grp,
                            binary_raw=b_raw,
                            hex_str=f"{val:04X}",
                            cycles="-",
                            label=pl.label if idx_v == 0 else None,
                        )
                    )
                    pc += 1
                continue

            # Standard PIC16F877A Instruction Lookup
            if pl.mnemonic not in INSTRUCTION_SET:
                raise AssemblyError(pl.line_no, f"Unsupported or unknown instruction '{pl.mnemonic}'.", pl.raw_line)

            idef = INSTRUCTION_SET[pl.mnemonic]
            ops = pl.operands
            word = 0

            if idef.fmt == "FIXED":
                if len(ops) != 0:
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' takes no operands, got {len(ops)}.", pl.raw_line)
                word = idef.base_opcode
                asm_clean = idef.mnemonic

            elif idef.fmt == "BYTE_F":
                if len(ops) != 1:
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' expects 1 operand (f), got {len(ops)}.", pl.raw_line)
                f_val = validate_file_register(parse_number(ops[0], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                word = idef.base_opcode | f_val
                asm_clean = f"{idef.mnemonic} {ops[0]}"

            elif idef.fmt == "BYTE_FD":
                if len(ops) not in (1, 2):
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' expects 2 operands (f, d), got {len(ops)}.", pl.raw_line)
                f_val = validate_file_register(parse_number(ops[0], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                if len(ops) == 2:
                    d_val = validate_destination(parse_number(ops[1], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                    asm_clean = f"{idef.mnemonic} {ops[0]}, {ops[1]}"
                else:
                    d_val = 1  # MPASM default d = 1 (F)
                    asm_clean = f"{idef.mnemonic} {ops[0]}, F"
                word = idef.base_opcode | (d_val << 7) | f_val

            elif idef.fmt == "BIT_FB":
                if len(ops) != 2:
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' expects 2 operands (f, b), got {len(ops)}.", pl.raw_line)
                f_val = validate_file_register(parse_number(ops[0], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                b_val = validate_bit_index(parse_number(ops[1], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                word = idef.base_opcode | (b_val << 7) | f_val
                asm_clean = f"{idef.mnemonic} {ops[0]}, {ops[1]}"

            elif idef.fmt == "LIT_8":
                if len(ops) != 1:
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' expects 1 operand (8-bit k), got {len(ops)}.", pl.raw_line)
                k_val = validate_literal_8(parse_number(ops[0], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                word = idef.base_opcode | k_val
                asm_clean = f"{idef.mnemonic} {ops[0]}"

            elif idef.fmt == "ADDR_11":
                if len(ops) != 1:
                    raise AssemblyError(pl.line_no, f"'{idef.mnemonic}' expects 1 operand (label or 11-bit address), got {len(ops)}.", pl.raw_line)
                k_val = validate_address_11(parse_number(ops[0], symbols, pl.line_no, pl.raw_line, pc), pl.line_no, pl.raw_line)
                word = idef.base_opcode | k_val
                asm_clean = f"{idef.mnemonic} {ops[0]}"

            b_raw, b_grp = format_14bit_binary(word)
            result.instructions.append(
                EncodedInstruction(
                    line_no=pl.line_no,
                    address=pc,
                    assembly_line=asm_clean,
                    machine_word=word,
                    binary_str=b_grp,
                    binary_raw=b_raw,
                    hex_str=f"{word:04X}",
                    cycles=idef.cycles,
                    label=pl.label,
                )
            )
            pc += 1

        except AssemblyError as exc:
            err_col.add(exc.line_no, exc.message, exc.source_line)
            pc += 1

    result.symbols = symbols
    result.user_symbols = user_symbols
    result.errors = err_col.errors
    if result.success:
        result.intel_hex = generate_intel_hex(result.instructions, result.config_word)
        result.listing_text = generate_listing(result.instructions, result.config_word)
    return result
