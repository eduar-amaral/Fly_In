from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_core import PydanticCustomError as Pce

from .base import MapModel
from .zone import Zone
from .connection import Connection


class ParsedMap(MapModel):
    """A validated map model with zones, connections, and drone count.

    This object is the result of parsing a map file before the graph is built.
    """

    nb_drones: int
    zones: list[Zone] = Field(default_factory=list)
    connections: list[Connection] = Field(default_factory=list)

    @field_validator("nb_drones")
    @classmethod
    def validate_nb_drones(cls, value: int) -> int:
        """Ensure the map declares at least one drone.

        Args:
            value: Number of drones configured for the map.

        Returns:
            The validated drone count.

        Raises:
            Pce: If the value is zero or negative.
        """
        if value <= 0:
            raise Pce(
                "invalid_drone_count_error",
                "nb_drones must be greater than 0, got {value}",
                {"value": value},
            )
        return value

    @property
    def start_zone(self) -> Zone:
        """Return the starting hub declared in the map."""
        return next(zone for zone in self.zones if zone.is_start)

    @property
    def end_zone(self) -> Zone:
        """Return the destination hub declared in the map."""
        return next(zone for zone in self.zones if zone.is_end)

    @property
    def zone_map(self) -> dict[str, Zone]:
        """Return zones indexed by their names for quick lookup."""
        return {zone.name: zone for zone in self.zones}

    @property
    def zone_names(self) -> frozenset[str]:
        """Return all zone names as an immutable set."""
        return frozenset(zone.name for zone in self.zones)
