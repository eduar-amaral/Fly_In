from __future__ import annotations

from math import inf

from graph import Graph, MinHeap, HeapNode
from pathfinding.search_result import SearchResult


class DijkstraError(Exception):
    """Raised when the Dijkstra search receives an invalid starting zone."""


class Dijkstra:
    """Compute shortest paths across the graph with a priority queue."""

    def __init__(self, graph: Graph) -> None:
        """Create a Dijkstra solver bound to a specific graph."""
        self._graph = graph

    def search(
        self,
        start: str,
        multiple_paths: bool = False,
    ) -> SearchResult:
        """Search the shortest distances from a starting zone.

        Args:
            start: Name of the source zone.
            multiple_paths: Whether equal-cost paths should be kept.

        Returns:
            A search result object containing distances and predecessors.

        Raises:
            DijkstraError: If the start zone does not exist in the graph.
        """
        if not self._graph.has_zone(start):
            raise DijkstraError(f"Unknown start zone {start!r}")

        distances: dict[str, float] = {
            zone.name: inf
            for zone in self._graph.all_zones()
        }

        predecessors: dict[str, list[str]] = {
            zone.name: []
            for zone in self._graph.all_zones()
        }

        visited: set[str] = set()

        distances[start] = 0.0

        heap = MinHeap()
        heap.push(HeapNode(priority=(0.0, False), value=start))

        while not heap.is_empty():
            node = heap.pop()

            cost, _ = node.priority
            zone_name = node.value

            if zone_name in visited:
                continue

            visited.add(zone_name)

            for edge in self._graph.get_neighbours(zone_name):
                neighbour = edge.target

                if neighbour in visited:
                    continue

                new_cost = cost + edge.cost

                if new_cost < distances[neighbour]:
                    distances[neighbour] = new_cost
                    predecessors[neighbour] = [zone_name]

                    heap.push(HeapNode(
                        priority=(new_cost, not edge.is_priority),
                        value=neighbour,
                    ))

                elif (
                    multiple_paths
                    and abs(new_cost - distances[neighbour]) < 1e-9
                ):
                    predecessors[neighbour].append(zone_name)

        return SearchResult(
            distances=distances,
            predecessors=predecessors,
        )
