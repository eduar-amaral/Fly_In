from __future__ import annotations

from math import inf

from models import MapModel


class SearchResult(MapModel):
    """Store all distances and predecessor information produced by Dijkstra."""

    distances: dict[str, float]
    predecessors: dict[str, list[str]]

    def distance_to(self, zone: str) -> float:
        """Return the cost from the start to the given zone."""
        return self.distances.get(zone, inf)

    def has_path_to(self, zone: str) -> bool:
        """Return whether the given zone is reachable from the start."""
        return self.distance_to(zone) < inf

    def build_path(self, start: str, end: str) -> list[str]:
        """Reconstruct the first shortest path between two zones.

        Args:
            start: Origin zone.
            end: Destination zone.

        Returns:
            The path from start to end, or an empty list if no path exists.
        """
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
        """Return all shortest paths from the start to the destination."""
        if start == end:
            return [[start]]

        paths: list[list[str]] = []

        for predecessor in self.predecessors.get(end, []):
            for path in self.all_paths(start, predecessor):
                paths.append(path + [end])

        return paths
