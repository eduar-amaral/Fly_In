from __future__ import annotations

from graph import Graph
from pathfinding import Pathfinder
from models import Drone

from ui.renderer.base import Renderer
from ui.renderer.terminal_renderer import TerminalRenderer

from .log_history import SimulationLog
from .scheduler import Scheduler
from .simulation_state import SimulationState
from .step_result import StepResult


class Simulation:
    """Run a drone simulation over a graph map."""

    def __init__(
        self,
        graph: Graph,
        nb_drones: int,
        renderer: Renderer | None = None,
        logger: SimulationLog | None = None,
    ) -> None:
        """Create a simulation.

        Args:
            graph: Graph used to compute the route.
            nb_drones: Number of drones to simulate.
            renderer: Renderer used during the simulation.
            logger: Shared log used to print turn details.
        """
        start = graph.start_zone().name
        end = graph.end_zone().name

        path = Pathfinder(graph).shortest_path(start, end)

        if not path:
            raise ValueError(
                f"No path found between {start!r} and {end!r}"
            )

        drones = [
            Drone(drone_id=i + 1, path=path)
            for i in range(nb_drones)
        ]

        self._logger = logger or SimulationLog(graph=graph)
        self._state = SimulationState(drones=drones)
        self._scheduler = Scheduler(graph)
        self._renderer = renderer or TerminalRenderer(logger=self._logger)

    def step(self) -> StepResult:
        """Run one simulation step and save the turn to the log."""
        result = self._scheduler.step(self._state)
        self._logger.record(self._state.turn, result)
        return result

    def run(self) -> None:
        """Run the simulation until all drones finish."""
        while (
            not all(drone.finished for drone in self._state.drones)
            and self._renderer.is_open()
        ):
            result = self.step()

            self._renderer.render_turn(
                state=self.state,
                result=result,
            )

        self._renderer.close()

        if all(drone.finished for drone in self._state.drones):
            print("All drones reached the destination.")

    @property
    def state(self) -> SimulationState:
        return self._state

    @property
    def turn(self) -> int:
        return self._state.turn

    @property
    def logger(self) -> SimulationLog:
        return self._logger
