from graph import Graph
from models import Connection, Zone, ZoneKind, ZoneType
from pathfinding import Pathfinder


def make_graph() -> Graph:
    graph = Graph()

    graph.add_node(Zone(
        name="START",
        x=0,
        y=0,
        kind=ZoneKind.START,
        zone_type=ZoneType.NORMAL,
    ))

    graph.add_node(Zone(
        name="A",
        x=1,
        y=0,
        zone_type=ZoneType.NORMAL,
    ))

    graph.add_node(Zone(
        name="END",
        x=2,
        y=0,
        kind=ZoneKind.END,
        zone_type=ZoneType.NORMAL,
    ))

    graph.add_edge(Connection(
        from_zone="START",
        to_zone="A",
    ))

    graph.add_edge(Connection(
        from_zone="A",
        to_zone="END",
    ))

    return graph


def test_pathfinder_finds_shortest_path():
    graph = make_graph()

    pathfinder = Pathfinder(graph)

    path = pathfinder.shortest_path("START", "END")

    assert path == ["START", "A", "END"]


def test_pathfinder_returns_cost():
    graph = make_graph()

    pathfinder = Pathfinder(graph)

    cost = pathfinder.shortest_cost("START", "END")

    assert cost == 2
