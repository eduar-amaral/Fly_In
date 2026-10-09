from __future__ import annotations

from math import inf

from graph import Graph
from algorithms import Dijkstra


class PathfinderError(Exception):
    """Raised when the pathfinder receives an invalid zone name."""


class Pathfinder:
    """Find paths in a graph using Dijkstra-based search.

    This class exposes the most common path queries for the simulation.
    """

    def __init__(self, graph: Graph) -> None:
        """Create a pathfinder for a graph.

        Args:
            graph: Graph that contains the zones and links.
        """
        self._graph = graph
        self._algorithm = Dijkstra(graph)

    def shortest_path(self, start: str, end: str) -> list[str]:
        """Return the shortest path between two zones.

        Args:
            start: Name of the start zone.
            end: Name of the end zone.

        Returns:
            List of zone names from start to end.
        """
        self._validate_zones(start, end)

        result = self._algorithm.search(start)

        return result.build_path(start, end)

    def shortest_cost(self, start: str, end: str) -> int:
        """Return the cost of the shortest path.

        Args:
            start: Name of the start zone.
            end: Name of the end zone.

        Returns:
            The total path cost, or -1 if no path exists.
        """
        self._validate_zones(start, end)

        result = self._algorithm.search(start)

        cost = result.distance_to(end)

        return -1 if cost == inf else int(cost)

    def all_shortest_paths(
        self,
        start: str,
        end: str,
    ) -> list[list[str]]:
        self._validate_zones(start, end)

        result = self._algorithm.search(
            start,
            multiple_paths=True,
        )

        return result.all_paths(start, end)

    def reachable(self, start: str, end: str) -> bool:
        self._validate_zones(start, end)

        result = self._algorithm.search(start)

        return result.has_path_to(end)

    def _validate_zones(
        self,
        start: str,
        end: str,
    ) -> None:
        for zone_name in (start, end):
            if not self._graph.has_zone(zone_name):
                raise PathfinderError(
                    f"Unknown zone {zone_name!r}"
                )
