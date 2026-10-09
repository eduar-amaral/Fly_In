from pathlib import Path

import pytest

from graph import Graph
from parser import MapParser
from simulation import Simulation


MAPS_DIR = Path("maps")


BENCHMARK_LIMITS = {
    "maps/easy/01_linear_path.txt": 6,
    "maps/easy/02_simple_fork.txt": 8,
    "maps/easy/03_basic_capacity.txt": 6,
    "maps/medium/01_dead_end_trap.txt": 12,
    "maps/medium/02_circular_loop.txt": 15,
    "maps/medium/03_priority_puzzle.txt": 12,
    "maps/hard/01_maze_nightmare.txt": 30,
    "maps/hard/02_capacity_hell.txt": 35,
    "maps/hard/03_ultimate_challenge.txt": 45,
    "maps/challenger/01_the_impossible_dream.txt": 45,
}


@pytest.mark.parametrize(
    "map_path, max_turns",
    sorted(BENCHMARK_LIMITS.items()),
)
def test_map_performance(map_path: str, max_turns: int):
    parsed = MapParser(map_path).load()
    graph = Graph.from_map(parsed)

    sim = Simulation(graph, parsed.nb_drones)
    sim.run()

    assert all(drone.finished for drone in sim.state.drones)
    assert sim.turn <= max_turns, (
        f"{map_path} took {sim.turn} turns, expected <= {max_turns}"
    )


def test_map_performance_on_all_provided_maps():
    for map_path in sorted(MAPS_DIR.glob("**/*.txt")):
        parsed = MapParser(str(map_path)).load()
        graph = Graph.from_map(parsed)

        sim = Simulation(graph, parsed.nb_drones)
        sim.run()

        assert all(drone.finished for drone in sim.state.drones)
        assert sim.turn >= 1
