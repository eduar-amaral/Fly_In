from __future__ import annotations

import pygame

from .difficulty_menu import DifficultyMenu
from .main_menu import MainMenu
from .map_menu import MapMenu
from .result_menu import ResultMenu


class MenuManager:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

        self._main_menu = MainMenu(screen)
        self._difficulty_menu = DifficultyMenu(screen)

        self._map_menu: MapMenu | None = None

        self._current_menu = "main"
        self._difficulty: str | None = None
        self._result_menu = ResultMenu(screen)

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        if self._current_menu == "main":
            return self._handle_main_menu(event)

        if self._current_menu == "difficulty":
            return self._handle_difficulty_menu(event)

        if self._current_menu == "map":
            return self._handle_map_menu(event)

        if self._current_menu == "result":
            return self._handle_result_menu(event)

        return None

    def render(self) -> None:
        if self._current_menu == "main":
            self._main_menu.render()

        elif self._current_menu == "difficulty":
            self._difficulty_menu.render()

        elif self._current_menu == "map":
            if self._map_menu is not None:
                self._map_menu.render()

        elif self._current_menu == "result":
            self._result_menu.render()

    def _handle_main_menu(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        choice = self._main_menu.handle_event(event)

        if choice == "Start Simulation":
            self._current_menu = "difficulty"

        elif choice == "Exit":
            return "EXIT"

        return None

    def _handle_difficulty_menu(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        if event.key == pygame.K_UP:
            self._difficulty_menu.move_up()

        elif event.key == pygame.K_DOWN:
            self._difficulty_menu.move_down()

        elif event.key == pygame.K_LEFT:
            self._current_menu = "main"
            self._difficulty = None

        elif event.key in (pygame.K_RETURN, pygame.K_RIGHT):
            self._difficulty = (
                self._difficulty_menu.selected_option()
            )

            self._map_menu = MapMenu(
                self._screen,
                self._difficulty,
            )

            self._current_menu = "map"

        return None

    def _handle_map_menu(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        if self._map_menu is None:
            return None

        choice = self._map_menu.handle_event(event)

        if choice == "BACK":
            self._map_menu = None
            self._current_menu = "difficulty"
            return None

        if choice is not None:
            return choice

        return None

    def _handle_result_menu(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        choice = self._result_menu.handle_event(event)

        if choice == "MENU":
            self._current_menu = "main"

        return None

    @property
    def difficulty(self) -> str | None:
        return self._difficulty

    def show_result(self) -> None:
        self._current_menu = "result"
