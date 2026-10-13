from __future__ import annotations

from pydantic import BaseModel, Field


class Movement(BaseModel):
    """Describe a drone move from one zone to another."""

    drone_id: int
    from_zone: str
    to_zone: str


class Wait(BaseModel):
    """Describe a drone that had to wait during the turn."""

    drone_id: int
    zone: str
    reason: str


class StepResult(BaseModel):
    """Container for all movement and waiting actions produced by a turn."""

    movements: list[Movement] = Field(default_factory=list)
    waits: list[Wait] = Field(default_factory=list)
