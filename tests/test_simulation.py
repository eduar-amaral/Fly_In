from parser import MapParser
from graph import Graph
from models import Connection, Zone, ZoneKind, ZoneType
from simulation import Simulation


def make_split_graph() -> Graph:
    graph = Graph()

    for name, x, y, kind, zone_type in (
        ("START", 0, 0, ZoneKind.START, ZoneType.NORMAL),
        ("A", 1, 0, ZoneKind.NORMAL, ZoneType.NORMAL),
        ("B", 1, 1, ZoneKind.NORMAL, ZoneType.NORMAL),
        ("END", 2, 0, ZoneKind.END, ZoneType.NORMAL),
    ):
        graph.add_node(
            Zone(
                name=name,
                x=x,
                y=y,
                kind=kind,
                zone_type=zone_type,
            )
        )

    graph.add_edge(Connection(from_zone="START", to_zone="A"))
    graph.add_edge(Connection(from_zone="A", to_zone="END"))
    graph.add_edge(Connection(from_zone="START", to_zone="B"))
    graph.add_edge(Connection(from_zone="B", to_zone="END"))

    return graph


def test_simulation_runs_simple_map():
    parsed = MapParser("maps/simple.map").load()

    graph = Graph.from_map(parsed)

    sim = Simulation(graph, parsed.nb_drones)

    sim.run()

    assert all(drone.finished for drone in sim.state.drones)


def test_simulation_distributes_equal_shortest_paths_among_drones():
    graph = make_split_graph()

    sim = Simulation(graph=graph, nb_drones=2)

    assert {tuple(drone.path) for drone in sim.state.drones} == {
        ("START", "A", "END"),
        ("START", "B", "END"),
    }


def test_simulation_keeps_single_shortest_path_when_no_alternative_exists():
    graph = Graph()

    for name, x, y, kind, zone_type in (
        ("START", 0, 0, ZoneKind.START, ZoneType.NORMAL),
        ("MID", 1, 0, ZoneKind.NORMAL, ZoneType.NORMAL),
        ("END", 2, 0, ZoneKind.END, ZoneType.NORMAL),
    ):
        graph.add_node(
            Zone(
                name=name,
                x=x,
                y=y,
                kind=kind,
                zone_type=zone_type,
            )
        )

    graph.add_edge(Connection(from_zone="START", to_zone="MID"))
    graph.add_edge(Connection(from_zone="MID", to_zone="END"))

    sim = Simulation(graph=graph, nb_drones=3)

    assert all(
        drone.path == ["START", "MID", "END"]
        for drone in sim.state.drones
    )
