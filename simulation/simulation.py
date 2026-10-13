from __future__ import annotations

from graph import Graph, GraphError
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
        try:
            start = graph.start_zone().name
            end = graph.end_zone().name
        except GraphError as exc:
            raise ValueError(str(exc)) from exc

        pathfinder = Pathfinder(graph)
        shortest_path = pathfinder.shortest_path(start, end)

        if not shortest_path:
            raise ValueError(
                f"No path found between {start!r} and {end!r}"
            )

        routes = self._build_routes(
            pathfinder=pathfinder,
            start=start,
            end=end,
            nb_drones=nb_drones,
        )

        drones = [
            Drone(drone_id=i + 1, path=routes[i])
            for i in range(nb_drones)
        ]

        self._graph = graph
        self._logger = logger or SimulationLog(graph=graph)
        self._state = SimulationState(drones=drones)
        self._scheduler = Scheduler(graph)
        self._renderer = renderer or TerminalRenderer(logger=self._logger)

    @staticmethod
    def _build_routes(
        *,
        pathfinder: Pathfinder,
        start: str,
        end: str,
        nb_drones: int,
    ) -> list[list[str]]:
        """Distribute drones across distinct equal-cost shortest paths.

        Single-path maps keep the previous behavior. When multiple shortest
        routes exist, drones are spread across them in round-robin order so the
        simulation stays realistic without breaking the original project flow.
        """
        shortest_paths = pathfinder.all_shortest_paths(start, end)
        unique_routes: list[list[str]] = []
        seen: set[tuple[str, ...]] = set()

        for route in shortest_paths:
            key = tuple(route)
            if key in seen:
                continue
            seen.add(key)
            unique_routes.append(route)

        if not unique_routes:
            return [pathfinder.shortest_path(start, end)] * nb_drones

        if len(unique_routes) == 1:
            return [unique_routes[0]] * nb_drones

        return [
            unique_routes[i % len(unique_routes)]
            for i in range(nb_drones)
        ]

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
    def graph(self) -> Graph:
        """Return the graph used to build this simulation."""
        return self._graph

    @property
    def state(self) -> SimulationState:
        """Return the live state of the simulation."""
        return self._state

    @property
    def turn(self) -> int:
        """Return the current simulation turn number."""
        return self._state.turn

    @property
    def logger(self) -> SimulationLog:
        """Return the simulation log associated with this run."""
        return self._logger
