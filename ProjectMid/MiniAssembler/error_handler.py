"""
Error handling and operand validation for the PIC16F877A Educational Mini Assembler.
"""

from dataclasses import dataclass
from typing import List


@dataclass
class AssemblyError(Exception):
    """Represents a single syntax, operand, or semantic error in assembly source."""
    line_no: int
    message: str
    source_line: str = ""

    def __str__(self) -> str:
        if self.source_line:
            return f"Line {self.line_no}: {self.message}  |  {self.source_line.strip()}"
        return f"Line {self.line_no}: {self.message}"


class AssemblyErrorCollector:
    """Collects multiple assembly errors so the GUI can report all issues at once."""

    def __init__(self) -> None:
        self.errors: List[AssemblyError] = []

    def add(self, line_no: int, message: str, source_line: str = "") -> None:
        self.errors.append(AssemblyError(line_no=line_no, message=message, source_line=source_line))

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def format_all(self) -> str:
        return "\n".join(str(err) for err in self.errors)


def validate_file_register(value: int, line_no: int, source_line: str = "") -> int:
    """Validate file register address (allows 0x00..0x1FF full banked address; masks to 7-bit f)."""
    if value < 0 or value > 0x1FF:
        raise AssemblyError(
            line_no,
            f"File register address 0x{value:X} out of range (valid: 0x00–0x7F or banked 0x00–0x1FF).",
            source_line,
        )
    return value & 0x7F


def validate_bit_index(value: int, line_no: int, source_line: str = "") -> int:
    """Validate 3-bit index b (0..7)."""
    if value < 0 or value > 7:
        raise AssemblyError(
            line_no,
            f"Bit index '{value}' out of range (valid: 0–7).",
            source_line,
        )
    return value & 0x07


def validate_destination(value: int, line_no: int, source_line: str = "") -> int:
    """Validate destination bit d (0 = W, 1 = F)."""
    if value not in (0, 1):
        raise AssemblyError(
            line_no,
            f"Destination bit '{value}' invalid (expected 0/W or 1/F).",
            source_line,
        )
    return value


def validate_literal_8(value: int, line_no: int, source_line: str = "") -> int:
    """Validate 8-bit literal k (0x00..0xFF)."""
    if value < 0 or value > 0xFF:
        raise AssemblyError(
            line_no,
            f"8-bit literal value {value} (0x{value:X}) out of range (valid: 0–255 / 0x00–0xFF).",
            source_line,
        )
    return value & 0xFF


def validate_address_11(value: int, line_no: int, source_line: str = "") -> int:
    """Validate 11-bit branch/call target address (accepts 13-bit 0..0x1FFF, masks lower 11 bits)."""
    if value < 0 or value > 0x1FFF:
        raise AssemblyError(
            line_no,
            f"Branch/Call address 0x{value:X} out of PIC16F877A Flash range (0x0000–0x1FFF).",
            source_line,
        )
    return value & 0x7FF
