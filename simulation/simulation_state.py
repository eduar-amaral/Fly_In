from __future__ import annotations

from models import Drone
from pydantic import BaseModel


class SimulationState(BaseModel):
    turn: int = 0
    drones: list[Drone]
