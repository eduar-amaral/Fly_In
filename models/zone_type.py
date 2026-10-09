from __future__ import annotations

from enum import Enum


class ZoneType(str, Enum):
    """Describe how a zone behaves in the simulation.

    The type defines movement cost, passability, and priority behavior.
    """

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

    @property
    def movement_cost(self) -> int:
        return {
            ZoneType.NORMAL: 1,
            ZoneType.BLOCKED: 999,
            ZoneType.RESTRICTED: 2,
            ZoneType.PRIORITY: 1,
        }[self]

    @property
    def priority_discount(self) -> float:
        if self is ZoneType.PRIORITY:
            return 0.001

        return 0.0

    @property
    def is_passable(self) -> bool:
        return self != ZoneType.BLOCKED

    @classmethod
    def valid_values(cls) -> tuple[str, ...]:
        return tuple(zone.value for zone in cls)
