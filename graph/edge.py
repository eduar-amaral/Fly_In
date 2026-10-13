from __future__ import annotations

from models import MapModel


class Edge(MapModel):
    """Represent a directed connection between two zones in the graph."""

    target: str
    cost: int
    capacity: int
    is_priority: bool = False
