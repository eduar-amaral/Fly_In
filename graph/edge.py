from __future__ import annotations

from models import MapModel


class Edge(MapModel):
    target: str
    cost: int
    capacity: int
    is_priority: bool = False
