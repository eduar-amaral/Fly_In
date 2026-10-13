from __future__ import annotations

from enum import Enum


class ZoneKind(str, Enum):
    """Describe the semantic role of each zone in the map."""

    NORMAL = "normal"
    START = "start"
    END = "end"

    @classmethod
    def valid_values(cls) -> tuple[str, ...]:
        """Return the serialized values accepted by the enum."""
        return tuple(kind.value for kind in cls)
