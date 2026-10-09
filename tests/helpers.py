from graph import Graph
from models import (
    Connection,
    Drone,
    Zone,
    ZoneKind,
    ZoneType,
)


def make_zone(
    name: str,
    *,
    x: int = 0,
    y: int = 0,
    kind: ZoneKind = ZoneKind.NORMAL,
    zone_type: ZoneType = ZoneType.NORMAL,
    max_drones: int = 1,
) -> Zone:
    return Zone(
        name=name,
        x=x,
        y=y,
        kind=kind,
        zone_type=zone_type,
        max_drones=max_drones
    )


def make_graph(
    *,
    zone_capacity: int = 1,
    link_capacity: int = 1,
) -> Graph:
    graph = Graph()

    graph.add_node(make_zone(
        "START",
        x=0,
        kind=ZoneKind.START
    ))

    graph.add_node(make_zone(
        "A",
        x=1,
        max_drones=zone_capacity
    ))

    graph.add_node(make_zone(
        "END",
        x=2,
        kind=ZoneKind.END
    ))

    graph.add_edge(Connection(
        from_zone="START",
        to_zone="A",
        max_link_capacity=link_capacity
    ))

    graph.add_edge(Connection(
        from_zone="A",
        to_zone="END",
    ))

    return graph


def make_drones(
    count: int,
    path: list[str] | None = None,
) -> list[Drone]:
    if path is None:
        path = ["START", "A", "END"]

    return [
        Drone(
            drone_id=i + 1,
            path=path.copy(),
        )
        for i in range(count)
    ]
