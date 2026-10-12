from __future__ import annotations


class ParseError(Exception):
    """Raised when a map file violates the expected parser syntax."""

    def __init__(self, message: str, line_number: int, raw_line: str) -> None:
        """Store parser details for a clearer error message."""
        self.line_number = line_number
        self.raw_line = raw_line

        super().__init__(
            f"[Line {line_number}] {message}\n"
            f" -> {raw_line!r}"
        )
