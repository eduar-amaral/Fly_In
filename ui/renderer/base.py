from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.simulation_state import SimulationState
    from simulation.step_result import StepResult


class Renderer(ABC):
    """Abstract contract for all simulation renderers."""

    @abstractmethod
    def render_turn(
        self,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        """Queue a simulation turn to be rendered."""
        pass

    @abstractmethod
    def is_open(self) -> bool:
        """Return whether the renderer is still active."""
        pass

    @abstractmethod
    def close(self) -> None:
        """Close the renderer and stop future drawing."""
        pass
