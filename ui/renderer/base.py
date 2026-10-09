from __future__ import annotations

from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from simulation.simulation_state import SimulationState
    from simulation.step_result import StepResult


class Renderer(ABC):

    @abstractmethod
    def render_turn(
        self,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        pass

    @abstractmethod
    def is_open(self) -> bool:
        pass

    @abstractmethod
    def close(self) -> None:
        pass
