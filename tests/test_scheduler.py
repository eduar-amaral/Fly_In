from graph import Graph
from models import Connection, Zone, ZoneKind, ZoneType
from tests.helpers import make_graph, make_drones

from simulation import Scheduler, SimulationState


def test_scheduler_moves_drone_one_step():
    graph = make_graph()

    drones = make_drones(1)

    state = SimulationState(drones=drones)

    scheduler = Scheduler(graph)

    step = scheduler.step(state)

    assert state.turn == 1
    assert drones[0].current_zone == "A"
    movement = step.movements[0]
    assert movement.drone_id == 1
    assert movement.from_zone == "START"
    assert movement.to_zone == "A"
    assert step.waits == []


def test_scheduler_respects_zone_capacity():
    graph = make_graph(zone_capacity=1)
    drones = make_drones(2)

    state = SimulationState(drones=drones)

    scheduler = Scheduler(graph)

    step = scheduler.step(state)

    assert len(step.movements) == 1
    assert len(step.waits) == 1


def test_scheduler_respects_link_capacity():
    graph = make_graph(
        zone_capacity=2,
        link_capacity=1,
    )

    drones = make_drones(2)

    state = SimulationState(drones=drones)
    scheduler = Scheduler(graph)

    step = scheduler.step(state)

    assert len(step.movements) == 1
    assert len(step.waits) == 1


def test_scheduler_respects_restricted_zone_cost():
    graph = Graph()

    graph.add_node(Zone(
        name="START",
        x=0,
        y=0,
        kind=ZoneKind.START,
    ))
    graph.add_node(Zone(
        name="RESTRICTED",
        x=1,
        y=0,
        zone_type=ZoneType.RESTRICTED,
        max_drones=1,
    ))
    graph.add_node(Zone(
        name="END",
        x=2,
        y=0,
        kind=ZoneKind.END,
    ))

    graph.add_edge(Connection(from_zone="START", to_zone="RESTRICTED"))
    graph.add_edge(Connection(from_zone="RESTRICTED", to_zone="END"))

    drone = next(iter(make_drones(1, ["START", "RESTRICTED", "END"])))
    state = SimulationState(drones=[drone])
    scheduler = Scheduler(graph)

    first_step = scheduler.step(state)
    assert first_step.movements[0].to_zone == "RESTRICTED"
    assert drone.wait_turns == 1

    second_step = scheduler.step(state)
    assert second_step.waits[0].zone == "RESTRICTED"
    assert drone.current_zone == "RESTRICTED"

    third_step = scheduler.step(state)
    assert third_step.movements[0].to_zone == "END"
