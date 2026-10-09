from parser import MapParser
from graph import Graph
from simulation import Simulation


def test_simulation_runs_simple_map():
    parsed = MapParser("maps/simple.map").load()

    graph = Graph.from_map(parsed)

    sim = Simulation(graph, parsed.nb_drones)

    sim.run()

    assert all(drone.finished for drone in sim.state.drones)
