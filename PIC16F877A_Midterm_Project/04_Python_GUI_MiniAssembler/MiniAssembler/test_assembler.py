"""
Automated Verification Test Suite for PIC16F877A Mini Assembler.
Verifies ALL 35 official PIC16F877A instructions against Microchip DS39582C Table 15-2,
2-pass forward/backward labels, Intel HEX checksums, and error handling.
"""

import unittest
from encoder import assemble
from instruction_set import INSTRUCTION_SET


class TestPIC16F877AMiniAssembler(unittest.TestCase):
    def test_instruction_count_is_35(self) -> None:
        self.assertEqual(len(INSTRUCTION_SET), 35)

    def test_all_35_instructions_exact_machine_code(self) -> None:
        """Verify every single one of the 35 instructions against hand-derived DS39582C Table 15-2 values."""
        cases = [
            # 18 Byte-oriented
            ("ADDWF 0x20, 1",  0x07A0),
            ("ADDWF 0x20, 0",  0x0720),
            ("ANDWF 0x21, F",  0x05A1),
            ("CLRF 0x22",      0x01A2),
            ("CLRW",           0x0100),
            ("COMF 0x23, W",   0x0923),
            ("DECF 0x24, F",   0x03A4),
            ("DECFSZ 0x25, F", 0x0BA5),
            ("INCF 0x26, F",   0x0AA6),
            ("INCFSZ 0x27, W", 0x0F27),
            ("IORWF 0x28, F",  0x04A8),
            ("MOVF 0x29, W",   0x0829),
            ("MOVWF 0x2A",     0x00AA),
            ("NOP",            0x0000),
            ("RLF 0x2B, F",    0x0DAB),
            ("RRF 0x2C, W",    0x0C2C),
            ("SUBWF 0x2D, W",  0x022D),
            ("SWAPF STATUS, W",0x0E03),
            ("XORWF 0x2E, F",  0x06AE),
            # 4 Bit-oriented
            ("BCF STATUS, 5",  0x1283),
            ("BSF STATUS, 5",  0x1683),
            ("BTFSC PORTA, 0", 0x1805),
            ("BTFSS PIR1, 0",  0x1C0C),
            # 13 Literal & Control
            ("ADDLW 0x10",     0x3E10),
            ("ANDLW 0x0F",     0x390F),
            ("CALL 0x0123",    0x2123),
            ("CLRWDT",         0x0064),
            ("GOTO 0x0456",    0x2C56),
            ("IORLW 0x80",     0x3880),
            ("MOVLW 0x55",     0x3055),
            ("RETFIE",         0x0009),
            ("RETLW 'A'",      0x3441),
            ("RETURN",         0x0008),
            ("SLEEP",          0x0063),
            ("SUBLW d'50'",    0x3C32),
            ("XORLW b'10101010'", 0x3AAA),
        ]
        src = "\n".join(line for line, _ in cases)
        res = assemble(src)
        self.assertTrue(res.success, msg=f"Errors: {res.errors}")
        self.assertEqual(len(res.instructions), len(cases))
        for (line, expected_word), inst in zip(cases, res.instructions):
            self.assertEqual(
                inst.machine_word,
                expected_word,
                msg=f"{line}: expected 0x{expected_word:04X}, got 0x{inst.hex_str}",
            )

    def test_two_pass_forward_and_backward_labels_and_intel_hex(self) -> None:
        src = """
        ORG 0x0000
        BSF STATUS, 5
        CLRF TRISB
        BCF STATUS, 5
        MOVLW 0x05
        MOVWF 0x20
LOOP:   INCF PORTB, F
        DECFSZ 0x20, F
        GOTO LOOP
        END
        """
        res = assemble(src)
        self.assertTrue(res.success, msg=str(res.errors))
        expected_hex = [0x1683, 0x0186, 0x1283, 0x3005, 0x00A0, 0x0A86, 0x0BA0, 0x2805]
        self.assertEqual([i.machine_word for i in res.instructions], expected_hex)
        self.assertIn(":100000008316860183120530A000860AA00B0528FE", res.intel_hex)

        # Forward jump test
        fwd = "ORG 0x0000\nGOTO TARGET\nNOP\nNOP\nTARGET: RETURN\nEND"
        res_fwd = assemble(fwd)
        self.assertTrue(res_fwd.success)
        self.assertEqual(res_fwd.instructions[0].machine_word, 0x2803)

    def test_error_detection(self) -> None:
        bad_cases = [
            "MOV R16, 5",         # Unknown instruction
            "BSF PORTB",          # Missing operand
            "BSF PORTB, 8",       # Bit > 7
            "MOVLW 0x1FF",        # Literal > 255
            "GOTO NOWHERE",       # Undefined label
            "DUP:\nNOP\nDUP:\nNOP",  # Duplicate label
        ]
        for bad in bad_cases:
            res = assemble(bad)
            self.assertFalse(res.success, msg=f"Expected failure for: {bad}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
