from __future__ import annotations

from simulation.log_history import SimulationLog
from simulation.simulation_state import SimulationState
from simulation.step_result import StepResult

from .base import Renderer


class TerminalRenderer(Renderer):
    """Render turn info in the terminal view."""

    def __init__(self, logger: SimulationLog | None = None) -> None:
        self._logger = logger

    def render_turn(
        self,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        if self._logger is not None:
            return

        parts: list[str] = []

        for movement in result.movements:
            parts.append(f"D{movement.drone_id}-{movement.to_zone}")

        if not parts:
            return

        print(" ".join(parts))

    def is_open(self) -> bool:
        return True

    def close(self) -> None:
        pass
