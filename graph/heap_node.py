from __future__ import annotations

from models import MapModel


class HeapNode(MapModel):
    priority: tuple[float, bool]
    value: str
