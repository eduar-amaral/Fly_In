from __future__ import annotations

from enum import Enum

import pygame

from graph import Graph
from parser import MapParser
from simulation import Simulation
from ui.renderer.pygame_renderer import PygameRenderer

from .menu.menu_manager import MenuManager


class ScreenState(str, Enum):
    """Possible states of the main application screen."""

    MENU = "menu"
    SIMULATION = "simulation"
    RESULT = "result"


class Application:
    """Main game loop and menu manager for the Fly In application.

    This class controls the pygame window, menu flow, and simulation screen.
    """

    def __init__(self) -> None:
        """Initialize pygame, window, and default app state."""
        pygame.init()

        display_info = pygame.display.Info()

        self._screen = pygame.display.set_mode(
            (
                display_info.current_w,
                display_info.current_h,
            ),
            pygame.FULLSCREEN,
        )

        pygame.display.set_caption("Fly_In")
        pygame.key.set_repeat(30, 30)

        self._clock = pygame.time.Clock()
        self._running = True
        self._result_font = pygame.font.SysFont("consolas", 28)

        self._menu_manager = MenuManager(self._screen)

        self._simulation: Simulation | None = None
        self._renderer: PygameRenderer | None = None

        self._current_screen = ScreenState.MENU

    def run(self) -> None:
        """Run the main app loop until the user exits the program."""
        while self._running:
            self._handle_events()
            self._update()
            self._render()

            self._clock.tick(60)

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._running = False
                continue

            if self._current_screen == ScreenState.RESULT:
                if (
                    event.type == pygame.KEYDOWN
                    and not getattr(event, "repeat", False)
                    and event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
                ):
                    self._current_screen = ScreenState.MENU
                    self._simulation = None
                    self._renderer = None
                    continue

                if (
                    event.type == pygame.KEYDOWN
                    and not getattr(event, "repeat", False)
                    and event.key == pygame.K_ESCAPE
                ):
                    self._current_screen = ScreenState.MENU
                    self._simulation = None
                    self._renderer = None
                    continue

                continue

            if self._current_screen == ScreenState.SIMULATION:
                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                ):
                    self._current_screen = ScreenState.MENU
                    self._simulation = None
                    self._renderer = None
                    continue

                if self._renderer is not None:
                    self._renderer.handle_event(event)

                if (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_SPACE
                    and self._renderer is not None
                ):
                    self._renderer.toggle_pause()

                continue

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                self._running = False
                continue

            if self._current_screen != ScreenState.MENU:
                continue

            action = self._menu_manager.handle_event(event)

            if action == "EXIT":
                self._running = False

            elif action is not None:
                self._start_simulation(action)

    def _start_simulation(self, map_name: str) -> None:
        difficulty = self._menu_manager.difficulty

        if difficulty is None:
            return

        map_path = f"maps/{difficulty.lower()}/{map_name}"

        parsed = MapParser(map_path).load()
        graph = Graph.from_map(parsed)

        self._simulation = Simulation(
            graph=graph,
            nb_drones=parsed.nb_drones,
            logger=None,
        )

        self._renderer = PygameRenderer(graph, logger=self._simulation.logger)
        self._current_screen = ScreenState.SIMULATION

    def _update(self) -> None:
        if self._current_screen != ScreenState.SIMULATION:
            return

        if self._simulation is None:
            return

        if self._renderer is None:
            return

        self._renderer.update()

        if self._renderer.animation_active:
            return

        if all(
            drone.finished
            for drone in self._simulation.state.drones
        ):
            self._current_screen = ScreenState.RESULT
            return

        result = self._simulation.step()

        self._renderer.render_turn(
            state=self._simulation.state,
            result=result,
        )

    def _render(self) -> None:
        if self._current_screen == ScreenState.MENU:
            self._menu_manager.render()

        elif self._current_screen == ScreenState.RESULT:
            if self._renderer is not None:
                self._renderer.render()

            text = self._result_font.render(
                "Press Enter to continue",
                True,
                (255, 255, 255),
            )
            self._screen.blit(
                text,
                (
                    self._screen.get_width() // 2 - text.get_width() // 2,
                    self._screen.get_height() - 80,
                ),
            )
            pygame.display.flip()

        elif self._current_screen == ScreenState.SIMULATION:
            if self._renderer is not None:
                self._renderer.render()
