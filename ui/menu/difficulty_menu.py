from __future__ import annotations

import pygame


class DifficultyMenu:
    """Let the user choose the campaign difficulty before selecting a map."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Create the difficulty menu and its list of options."""
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
        """Move selection to the previous option."""
        self._selected = (
            self._selected - 1
        ) % len(self._options)

    def move_down(self) -> None:
        """Move selection to the next option."""
        self._selected = (
            self._selected + 1
        ) % len(self._options)

    def selected_option(self) -> str:
        """Return the currently selected difficulty."""
        return self._options[self._selected]

    def render(self) -> None:
        """Render the difficulty menu to the screen."""
        self._screen.fill((15, 18, 24))

        self._render_title()
        self._render_options()

        pygame.display.flip()

    def _render_title(self) -> None:
        """Render the difficulty title at the top of the screen."""
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
        """Render each difficulty option with a highlight
        for the current selection.
        """
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
