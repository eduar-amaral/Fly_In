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

    @field_validator("from_zone", "to_zone")
    @classmethod
    def validate_zone_name(cls, value: str) -> str:
        if value == "":
            raise Pce(
                "empty_zone_name_error",
                "Zone name cannot be empty",
                {},
            )

        return value

    @field_validator("max_link_capacity")
    @classmethod
    def validate_capacity(cls, value: int) -> int:
        if value <= 0:
            raise Pce(
                "invalid_capacity_error",
                "max_link_capacity must be a positive integer, got {value}",
                {"value": value},
            )

        return value

    @model_validator(mode="after")
    def validate_self_loop(self) -> Connection:
        if self.from_zone == self.to_zone:
            raise Pce(
                "self_loop_connection",
                "Connection cannot link zone '{name}' to itself",
                {"name": self.from_zone},
            )
        return self
