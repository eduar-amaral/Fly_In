from __future__ import annotations

from models import Zone, ZoneType, Connection, ParsedMap

from .edge import Edge


class GraphError(Exception):
    """Raised when the graph is used with an invalid zone or edge."""


class Graph:
    """Represent a map as a graph of connected zones.

    Each zone has a name and each connection is stored as a bidirectional edge.
    This class also gives access to the start and end hubs of the map.
    """

    def __init__(self) -> None:
        """Create an empty graph."""
        self._nodes: dict[str, Zone] = {}
        self._edges: dict[str, list[Edge]] = {}

    @classmethod
    def from_map(cls, parsed: ParsedMap) -> Graph:
        """Build a graph from a parsed map.

        Args:
            parsed: Parsed map data with zones and connections.

        Returns:
            A graph filled with all zones and links from the map.
        """
        graph = cls()

        for zone in parsed.zones:
            graph.add_node(zone)

        for conn in parsed.connections:
            graph.add_edge(conn)

        return graph

    def add_node(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: Zone instance to register.

        Raises:
            GraphError: If the zone name is already in the graph.
        """
        if zone.name in self._nodes:
            raise GraphError(
                f"Duplicate zone: {zone.name!r}. "
                "add_node was called twice for the same zone"
            )

        self._nodes[zone.name] = zone
        self._edges[zone.name] = []

    def add_edge(self, conn: Connection) -> None:
        """Add a connection between two zones.

        Args:
            conn: Connection data to add to the graph.

        Raises:
            GraphError: If one of the zones does not exist.
        """
        from_name = conn.from_zone
        to_name = conn.to_zone

        if from_name not in self._nodes:
            raise GraphError(f"Unknown zone {from_name!r} in connection.")

        if to_name not in self._nodes:
            raise GraphError(f"Unknown zone {to_name!r} in connection.")

        from_zone = self._nodes[from_name]
        to_zone = self._nodes[to_name]
        capacity = conn.max_link_capacity

        if not from_zone.zone_type.is_passable:
            return
        if not to_zone.zone_type.is_passable:
            return

        cost_a_to_b = to_zone.zone_type.movement_cost
        cost_b_to_a = from_zone.zone_type.movement_cost

        self._edges[from_name].append(Edge(
            target=to_name,
            cost=cost_a_to_b,
            capacity=capacity,
            is_priority=to_zone.zone_type == ZoneType.PRIORITY
        ))

        self._edges[to_name].append(Edge(
            target=from_name,
            cost=cost_b_to_a,
            capacity=capacity,
            is_priority=from_zone.zone_type == ZoneType.PRIORITY
        ))

    def get_zone(self, name: str) -> Zone:
        if name not in self._nodes:
            raise GraphError(f"Zone not found: {name!r}")
        return self._nodes[name]

    def get_neighbours(self, name: str) -> list[Edge]:
        if name not in self._edges:
            raise GraphError(f"Zone not found: {name!r}")
        return self._edges[name]

    def get_edge(self, source: str, target: str) -> Edge:
        for edge in self._edges[source]:
            if edge.target == target:
                return edge

        raise GraphError(f"No edge from {source!r} to {target!r}")

    def has_zone(self, name: str) -> bool:
        return name in self._nodes

    def start_zone(self) -> Zone:
        for zone in self._nodes.values():
            if zone.is_start:
                return zone
        raise GraphError("No start zone in graph.")

    def end_zone(self) -> Zone:
        for zone in self._nodes.values():
            if zone.is_end:
                return zone
        raise GraphError("No end zone in graph.")

    def all_zones(self) -> list[Zone]:
        return list(self._nodes.values())

    def passable_zones(self) -> list[Zone]:
        return [z for z in self._nodes.values() if z.zone_type.is_passable]

    def node_count(self) -> int:
        return len(self._nodes)

    def edge_count(self) -> int:
        return sum(len(nbrs) for nbrs in self._edges.values())

    def __repr__(self) -> str:
        return (
            f"Graph("
            f"zones={self.node_count()}, "
            f"edges={self.edge_count() // 2} bidirectional"
            f")"
        )

    def debug_print(self) -> None:
        print(repr(self))
        for name, nbrs in self._edges.items():
            zone = self._nodes[name]
            marker = ""
            if zone.is_start:
                marker = " [START]"
            elif zone.is_end:
                marker = " [END]"
            elif not zone.zone_type.is_passable:
                marker = " [BLOCKED]"

            print(f" {name}{marker}:")

            if not nbrs:
                print(" (no edges)")

            for edge in nbrs:
                print(
                    f" -> {edge.target} "
                    f"cost={edge.cost} "
                    f"cap={edge.capacity}"
                )
