from __future__ import annotations

from pydantic import field_validator
from pydantic_core import PydanticCustomError as Pce

from .base import MapModel
from .zone_type import ZoneType
from .zone_kind import ZoneKind


class Zone(MapModel):
    """A node in the map that can be a hub or a normal zone.

    A zone stores its position, type, and capacity. It is the basic building
    block of the graph used in routes and simulation.
    """

    name: str
    x: int
    y: int

    kind: ZoneKind = ZoneKind.NORMAL
    zone_type: ZoneType = ZoneType.NORMAL

    color: str | None = None
    max_drones: int = 1

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if value == "":
            raise Pce(
                "empty_zone_name_error",
                "Zone name cannot be empty",
                {},
            )

        if "-" in value or " " in value:
            raise Pce(
                "invalid_zone_name_error",
                "Zone name '{name}' must not contain dashes or spaces",
                {"name": value},
            )
        return value

    @field_validator("max_drones")
    @classmethod
    def validate_max_drones(cls, value: int) -> int:
        if value <= 0:
            raise Pce(
                "invalid_capacity_error",
                "max_drones must be a positive integer, got {value}",
                {"value": value},
            )
        return value

    @property
    def is_start(self) -> bool:
        return self.kind is ZoneKind.START

    @property
    def is_end(self) -> bool:
        return self.kind is ZoneKind.END

    @property
    def is_passable(self) -> bool:
        return self.zone_type.is_passable

    @property
    def movement_cost(self) -> int:
        return self.zone_type.movement_cost

    @property
    def priority_discount(self) -> float:
        return self.zone_type.priority_discount

    @property
    def palette_color(self) -> tuple[int, int, int]:
        palette = {
            "black": (44, 44, 48),
            "blue": (79, 154, 255),
            "green": (76, 175, 80),
            "red": (239, 83, 80),
            "yellow": (255, 193, 7),
            "orange": (255, 152, 0),
            "purple": (156, 99, 255),
            "magenta": (233, 30, 99),
            "violet": (133, 94, 255),
            "crimson": (220, 53, 69),
            "gold": (255, 215, 0),
            "rainbow": (255, 120, 180),
            "white": (240, 240, 240),
        }

        if self.color is None:
            return (180, 180, 180)

        return palette.get(self.color.lower(), (180, 180, 180))
