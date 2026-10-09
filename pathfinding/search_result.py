from __future__ import annotations

from math import inf

from models import MapModel


class SearchResult(MapModel):
    distances: dict[str, float]
    predecessors: dict[str, list[str]]

    def distance_to(self, zone: str) -> float:
        return self.distances.get(zone, inf)

    def has_path_to(self, zone: str) -> bool:
        return self.distance_to(zone) < inf

    def build_path(self, start: str, end: str) -> list[str]:
        if not self.has_path_to(end):
            return []

        path: list[str] = []

        current: str | None = end

        while current is not None:
            path.append(current)

            if current == start:
                break

            previous = self.predecessors.get(current, [])

            if not previous:
                return []

            current = previous[0]

        path.reverse()

        if path[0] != start:
            return []

        return path

    def all_paths(self, start: str, end: str) -> list[list[str]]:
        if start == end:
            return [[start]]

        paths: list[list[str]] = []

        for predecessor in self.predecessors.get(end, []):
            for path in self.all_paths(start, predecessor):
                paths.append(path + [end])

        return paths
