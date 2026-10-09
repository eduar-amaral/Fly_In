from __future__ import annotations

import pygame

from simulation.simulation_state import SimulationState
from simulation.step_result import StepResult


class HUDRenderer:
    def __init__(self) -> None:
        self._font = pygame.font.Font(None, 28)
        self._small_font = pygame.font.Font(None, 22)

    def render(
        self,
        screen: pygame.Surface,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        self._render_turn(screen, state)
        self._render_stats(screen, state, result)
        self._render_controls(screen)

    def _render_turn(
        self,
        screen: pygame.Surface,
        state: SimulationState,
    ) -> None:
        text = self._font.render(
            f"Turn: {state.turn}",
            True,
            (240, 240, 240),
        )

        screen.blit(text, (20, 20))

    def _render_stats(
        self,
        screen: pygame.Surface,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        moving = sum(
            1 for drone in state.drones if not drone.finished
        )
        waiting = len(result.waits)

        drones = len(state.drones)

        lines = [
            f"Drones: {drones}",
            f"Moving: {moving}",
            f"Waiting: {waiting}",
        ]

        for index, line in enumerate(lines):
            text = self._small_font.render(
                line,
                True,
                (180, 180, 180),
            )

            screen.blit(
                text,
                (20, 55 + index * 24),
            )

    def _render_controls(
        self,
        screen: pygame.Surface,
    ) -> None:
        text = self._small_font.render(
            "SPACE: Pause / Resume    ESC: Exit",
            True,
            (150, 150, 150),
        )

        screen.blit(
            text,
            (20, screen.get_height() - 35),
        )
