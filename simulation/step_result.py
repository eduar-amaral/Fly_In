from __future__ import annotations

from pydantic import BaseModel, Field


class Movement(BaseModel):
    drone_id: int
    from_zone: str
    to_zone: str


class Wait(BaseModel):
    drone_id: int
    zone: str
    reason: str


class StepResult(BaseModel):
    movements: list[Movement] = Field(default_factory=list)
    waits: list[Wait] = Field(default_factory=list)
