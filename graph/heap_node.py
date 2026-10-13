from __future__ import annotations

from models import MapModel


class HeapNode(MapModel):
    """Lightweight heap entry used by the priority queue implementation."""

    priority: tuple[float, bool]
    value: str
