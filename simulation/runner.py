from __future__ import annotations

from pathlib import Path

from graph import Graph
from parser import MapParser

from .simulation import Simulation


class TerminalRunner:
    """Run a map in the terminal-only execution mode."""

    @staticmethod
    def load_simulation_from_map(map_path: str | Path) -> Simulation:
        """Load a map file and build its simulation object."""
        parsed_map = MapParser(map_path).load()
        graph = Graph.from_map(parsed_map)
        return Simulation(graph=graph, nb_drones=parsed_map.nb_drones)

    def __init__(self, map_path: str | Path) -> None:
        """Create a runner for a given map file."""
        self._map_path = Path(map_path)

    def run(self) -> None:
        """Load and execute the chosen map as a terminal simulation."""
        simulation = self.load_simulation_from_map(self._map_path)
        simulation.run()
