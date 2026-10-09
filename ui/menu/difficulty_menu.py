from __future__ import annotations

import pygame


class DifficultyMenu:
    def __init__(self, screen: pygame.Surface) -> None:
        self._screen = screen

        self._options = [
            "EASY",
            "MEDIUM",
            "HARD",
            "CHALLENGER",
        ]

        self._selected = 0

        self._font = pygame.font.Font(None, 48)
        self._title_font = pygame.font.Font(None, 72)

    def move_up(self) -> None:
        self._selected = (
            self._selected - 1
        ) % len(self._options)

    def move_down(self) -> None:
        self._selected = (
            self._selected + 1
        ) % len(self._options)

    def selected_option(self) -> str:
        return self._options[self._selected]

    def render(self) -> None:
        self._screen.fill((15, 18, 24))

        self._render_title()
        self._render_options()

        pygame.display.flip()

    def _render_title(self) -> None:
        title = self._title_font.render(
            "DIFFICULTY",
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
                center=(640, 300 + index * 60)
            )

            self._screen.blit(text, rect)
