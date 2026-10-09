from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class MapModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        use_enum_values=False,
        str_strip_whitespace=True,
    )
