from __future__ import annotations

import pygame


class MainMenu:
    START_SIMULATION = "Start Simulation"
    EXIT = "Exit"

    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

        self._options = [
            self.START_SIMULATION,
            self.EXIT,
        ]

        self._selected = 0

        self._font = pygame.font.Font(None, 48)
        self._title_font = pygame.font.Font(None, 96)

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self._selected = (
                self._selected - 1
            ) % len(self._options)

        elif event.key == pygame.K_DOWN:
            self._selected = (
                self._selected + 1
            ) % len(self._options)

        elif event.key in (pygame.K_RETURN, pygame.K_RIGHT):
            return self._options[self._selected]

        return None

    def render(self) -> None:
        self._screen.fill((15, 18, 24))

        self._render_title()
        self._render_options()

        pygame.display.flip()

    def _render_title(self) -> None:
        title = self._title_font.render(
            "FLY-IN",
            True,
            (240, 240, 240),
        )

        title_rect = title.get_rect(
            center=(640, 180)
        )

        self._screen.blit(title, title_rect)

    def _render_options(self) -> None:
        for index, option in enumerate(self._options):
            color = (
                (240, 240, 240)
                if index == self._selected
                else (120, 120, 120)
            )

            text = self._font.render(
                option,
                True,
                color,
            )

            rect = text.get_rect(
                center=(640, 340 + index * 70)
            )

            self._screen.blit(text, rect)
