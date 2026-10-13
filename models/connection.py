from __future__ import annotations

from pydantic import field_validator, model_validator
from pydantic_core import PydanticCustomError as Pce

from .base import MapModel


class Connection(MapModel):
    """Represent a link between two map zones.

    A connection defines the two zones involved and the maximum capacity of the
    link between them.
    """

    from_zone: str
    to_zone: str
    max_link_capacity: int = 1
    used_capacity: int = 0

    @field_validator("from_zone", "to_zone")
    @classmethod
    def validate_zone_name(cls, value: str) -> str:
        """Validate the zone names used in a connection.

        Args:
            value: Zone identifier declared in the map file.

        Returns:
            The validated zone name.

        Raises:
            Pce: If the zone name is empty.
        """
        if value == "":
            raise Pce(
                "empty_zone_name_error",
                "Zone name cannot be empty",
                {},
            )

        return value

    def register_usage(self, count: int = 1) -> int:
        """Register that one or more movements are
        currently using this link.
        """
        next_count = self.used_capacity + max(0, count)
        object.__setattr__(self, "used_capacity", next_count)
        return self.used_capacity

    def release_usage(self, count: int = 1) -> int:
        """Release part of the link usage recorded for this connection."""
        next_count = max(0, self.used_capacity - max(0, count))
        object.__setattr__(self, "used_capacity", next_count)
        return self.used_capacity

    @property
    def available_capacity(self) -> int:
        """Return remaining capacity on the link."""
        return max(0, self.max_link_capacity - self.used_capacity)

    @field_validator("max_link_capacity")
    @classmethod
    def validate_capacity(cls, value: int) -> int:
        """Ensure the connection capacity remains strictly positive.

        Args:
            value: Capacity declared for the edge.

        Returns:
            The validated capacity.

        Raises:
            Pce: If the capacity is zero or negative.
        """
        if value <= 0:
            raise Pce(
                "invalid_capacity_error",
                "max_link_capacity must be a positive integer, got {value}",
                {"value": value},
            )

        return value

    @model_validator(mode="after")
    def validate_self_loop(self) -> Connection:
        """Reject invalid links that connect a zone to itself."""
        if self.from_zone == self.to_zone:
            raise Pce(
                "self_loop_connection",
                "Connection cannot link zone '{name}' to itself",
                {"name": self.from_zone},
            )
        return self
