from __future__ import annotations

from simulation.log_history import SimulationLog
from simulation.simulation_state import SimulationState
from simulation.step_result import StepResult

from .base import Renderer


class TerminalRenderer(Renderer):
    """Render turn info in the terminal view."""

    def __init__(self, logger: SimulationLog | None = None) -> None:
        """Initialize the terminal renderer with an optional shared log."""
        self._logger = logger

    def render_turn(
        self,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        """Render the current turn movement summary to the terminal."""
        if self._logger is not None:
            return

        parts: list[str] = []

        for movement in result.movements:
            parts.append(f"D{movement.drone_id}-{movement.to_zone}")

        if not parts:
            return

        print(" ".join(parts))

    def is_open(self) -> bool:
        """Return whether the terminal renderer is active."""
        return True

    def close(self) -> None:
        """Close the terminal renderer without performing
        additional actions.
        """
        pass
