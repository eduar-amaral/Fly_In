from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MapModel(BaseModel):
    """Base model used across the project for validated,
    frozen domain objects.
    """

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )
