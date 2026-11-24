"""
Assembly source parser for PIC16F877A (MPASM-compatible syntax).
Identifies labels, directives (ORG, EQU, CBLOCK/ENDC, __CONFIG, DT, END, LIST, #include, BANKSEL),
instruction mnemonics, operands, literals (0x.., ..h, d'..', b'..', 'A', decimal), and comments (;).
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from error_handler import AssemblyError
from instruction_set import INSTRUCTION_SET


DIRECTIVES = {
    "ORG", "EQU", "CBLOCK", "ENDC", "END", "LIST", "PROCESSOR",
    "__CONFIG", "CONFIG", "INCLUDE", "#INCLUDE", "ERRORLEVEL",
    "DT", "DW", "BANKSEL", "PAGESEL", "RADIX",
}


@dataclass
class ParsedLine:
    line_no: int
    raw_line: str
    label: Optional[str] = None
    mnemonic: Optional[str] = None      # Uppercase mnemonic or directive
    operands: List[str] = field(default_factory=list)
    is_directive: bool = False


def strip_comment(line: str) -> str:
    """Remove ';' comments while preserving ';' inside quoted strings or character literals."""
    in_single = False
    in_double = False
    for idx, ch in enumerate(line):
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == ";" and not in_single and not in_double:
            return line[:idx]
    return line


def split_operands(operand_str: str) -> List[str]:
    """Split comma-separated operands while respecting quoted strings/chars."""
    parts: List[str] = []
    buf: List[str] = []
    in_single = False
    in_double = False
    for ch in operand_str:
        if ch == "'" and not in_double:
            in_single = not in_single
            buf.append(ch)
        elif ch == '"' and not in_single:
            in_double = not in_double
            buf.append(ch)
        elif ch == "," and not in_single and not in_double:
            item = "".join(buf).strip()
            if item:
                parts.append(item)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def parse_number(token: str, symbols: Dict[str, int], line_no: int, raw_line: str = "", current_addr: int = 0) -> int:
    """
    Evaluate a numeric literal, symbol, or simple expression (supports &, |, +, -, $, 'c').
    Supports MPASM formats: 0x1A, 1Ah, h'1A', d'25', b'10101010', o'17', 'A', 25.
    """
    expr = token.strip()
    if not expr:
        raise AssemblyError(line_no, "Empty operand expression.", raw_line)

    # Bitwise AND (commonly used in __CONFIG _CP_OFF & _WDT_OFF & ...)
    if "&" in expr and not (expr.startswith("'") or expr.startswith('"')):
        val = 0x3FFF
        for part in expr.split("&"):
            val &= parse_number(part, symbols, line_no, raw_line, current_addr)
        return val

    # Bitwise OR
    if "|" in expr and not (expr.startswith("'") or expr.startswith('"')):
        val = 0
        for part in expr.split("|"):
            val |= parse_number(part, symbols, line_no, raw_line, current_addr)
        return val

    # Handle $ - N or $ + N (current PC relative expressions like GOTO $-1)
    m_rel = re.match(r"^\$\s*([+-])\s*(.+)$", expr)
    if m_rel:
        op, rhs = m_rel.group(1), m_rel.group(2)
        offset = parse_number(rhs, symbols, line_no, raw_line, current_addr)
        return current_addr + offset if op == "+" else current_addr - offset
    if expr == "$":
        return current_addr

    # Character literal: 'A' or A'A'
    m_char = re.match(r"^[Aa]?'(.)'$", expr)
    if m_char:
        return ord(m_char.group(1))

    # MPASM radix literals: d'20', h'1F', b'10100101', o'17'
    m_mpasm = re.match(r"^([HhDdBbOo])'([0-9A-Fa-f_]+)'$", expr)
    if m_mpasm:
        prefix = m_mpasm.group(1).upper()
        digits = m_mpasm.group(2).replace("_", "")
        base = {"H": 16, "D": 10, "B": 2, "O": 8}[prefix]
        try:
            return int(digits, base)
        except ValueError as exc:
            raise AssemblyError(line_no, f"Invalid base-{base} literal '{expr}'.", raw_line) from exc

    # Standard 0x / 0b / 0o prefixes
    if re.match(r"^0[xX][0-9A-Fa-f]+$", expr):
        return int(expr, 16)
    if re.match(r"^0[bB][01]+$", expr):
        return int(expr, 2)
    if re.match(r"^0[oO][0-7]+$", expr):
        return int(expr, 8)

    # Suffix hex: 20h, 0FFh (must start with a digit)
    if re.match(r"^[0-9][0-9A-Fa-f]*[hH]$", expr):
        return int(expr[:-1], 16)

    # Decimal integer
    if re.match(r"^[0-9]+$", expr):
        return int(expr, 10)

    # Simple + / - arithmetic on symbols or numbers (e.g. RAM_BASE + 1)
    for sep, fn in (("+", lambda a, b: a + b), ("-", lambda a, b: a - b)):
        if sep in expr and not expr.startswith(sep):
            left, right = expr.split(sep, 1)
            if left.strip() and right.strip():
                return fn(
                    parse_number(left, symbols, line_no, raw_line, current_addr),
                    parse_number(right, symbols, line_no, raw_line, current_addr),
                )

    # Symbol lookup (case-insensitive)
    key = expr.upper()
    if key in symbols:
        return symbols[key]

    raise AssemblyError(line_no, f"Undefined symbol or invalid numeric literal '{expr}'.", raw_line)


def parse_source(source_text: str) -> List[ParsedLine]:
    """Parse multi-line PIC16 assembly source into structured ParsedLine objects."""
    parsed_lines: List[ParsedLine] = []
    in_cblock = False

    for line_no, raw_line in enumerate(source_text.splitlines(), start=1):
        clean = strip_comment(raw_line).strip()
        if not clean:
            continue

        # Handle CBLOCK body lines (symbol names allocated sequentially)
        upper_clean = clean.upper()
        if upper_clean.startswith("ENDC"):
            in_cblock = False
            parsed_lines.append(ParsedLine(line_no=line_no, raw_line=raw_line, mnemonic="ENDC", is_directive=True))
            continue

        if in_cblock:
            # Each line inside CBLOCK is a variable name (optionally with :size)
            sym = clean.split()[0].rstrip(":")
            parsed_lines.append(
                ParsedLine(line_no=line_no, raw_line=raw_line, label=sym, mnemonic="CBLOCK_ITEM", is_directive=True)
            )
            continue

        # Check for label with colon: "LOOP: MOVLW 0x05" or "LOOP:"
        label: Optional[str] = None
        rest = clean

        m_colon = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", rest)
        if m_colon:
            label = m_colon.group(1)
            rest = m_colon.group(2).strip()
            if not rest:
                parsed_lines.append(ParsedLine(line_no=line_no, raw_line=raw_line, label=label))
                continue

        # Tokenize first word
        parts = rest.split(None, 1)
        first = parts[0]
        tail = parts[1].strip() if len(parts) > 1 else ""
        first_up = first.upper()

        # Special form: "SYM EQU 0x20" (label without colon before EQU)
        if tail:
            tail_parts = tail.split(None, 1)
            if tail_parts[0].upper() == "EQU":
                label = first
                op_str = tail_parts[1].strip() if len(tail_parts) > 1 else ""
                parsed_lines.append(
                    ParsedLine(
                        line_no=line_no,
                        raw_line=raw_line,
                        label=label,
                        mnemonic="EQU",
                        operands=[op_str] if op_str else [],
                        is_directive=True,
                    )
                )
                continue

        # Check if first word is a known directive or instruction
        if first_up in DIRECTIVES:
            if first_up == "CBLOCK":
                in_cblock = True
            ops = [tail] if first_up in ("__CONFIG", "CONFIG", "LIST", "INCLUDE", "#INCLUDE", "ERRORLEVEL") and tail else split_operands(tail)
            parsed_lines.append(
                ParsedLine(
                    line_no=line_no,
                    raw_line=raw_line,
                    label=label,
                    mnemonic=first_up,
                    operands=ops,
                    is_directive=True,
                )
            )
            continue

        if first_up in INSTRUCTION_SET:
            parsed_lines.append(
                ParsedLine(
                    line_no=line_no,
                    raw_line=raw_line,
                    label=label,
                    mnemonic=first_up,
                    operands=split_operands(tail),
                    is_directive=False,
                )
            )
            continue

        # MPASM allows column-1 labels WITHOUT colons (e.g. "MAIN  MOVLW 0x05" or standalone "MAIN")
        if label is None and not raw_line[0].isspace() and re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", first):
            if not tail:
                parsed_lines.append(ParsedLine(line_no=line_no, raw_line=raw_line, label=first))
                continue
            sub_parts = tail.split(None, 1)
            sub_mnem = sub_parts[0].upper()
            sub_tail = sub_parts[1].strip() if len(sub_parts) > 1 else ""
            if sub_mnem in INSTRUCTION_SET or sub_mnem in DIRECTIVES:
                if sub_mnem == "CBLOCK":
                    in_cblock = True
                parsed_lines.append(
                    ParsedLine(
                        line_no=line_no,
                        raw_line=raw_line,
                        label=first,
                        mnemonic=sub_mnem,
                        operands=split_operands(sub_tail),
                        is_directive=(sub_mnem in DIRECTIVES),
                    )
                )
                continue

        # Otherwise pass unknown mnemonic through so encoder reports a clear error
        parsed_lines.append(
            ParsedLine(
                line_no=line_no,
                raw_line=raw_line,
                label=label,
                mnemonic=first_up,
                operands=split_operands(tail),
                is_directive=False,
            )
        )

    return parsed_lines
