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
