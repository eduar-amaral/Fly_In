from __future__ import annotations

from models import Drone
from pydantic import BaseModel


class SimulationState(BaseModel):
    """Store the mutable state of the simulation for one turn."""

    turn: int = 0
    drones: list[Drone]
