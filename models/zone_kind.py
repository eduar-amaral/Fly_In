from __future__ import annotations

from enum import Enum


class ZoneKind(str, Enum):
    NORMAL = "normal"
    START = "start"
    END = "end"

    @classmethod
    def valid_values(cls) -> tuple[str, ...]:
        return tuple(kind.value for kind in cls)
