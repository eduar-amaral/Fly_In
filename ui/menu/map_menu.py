from __future__ import annotations

from pathlib import Path

import pygame


class MapMenu:
    """Display a list of maps for the chosen difficulty."""

    def __init__(
        self,
        screen: pygame.Surface,
        difficulty: str,
    ) -> None:
        """Initialize the menu with the available map
        files for a difficulty.
        """
        self._screen = screen
        self._difficulty = difficulty

        self._maps = self._load_maps()
        self._selected = 0

        self._font = pygame.font.Font(None, 42)
        self._title_font = pygame.font.Font(None, 72)

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        """Handle input for map selection and navigation."""
        if event.type != pygame.KEYDOWN:
            return None

        if event.key == pygame.K_UP:
            self._move_up()

        elif event.key == pygame.K_DOWN:
            self._move_down()

        elif event.key == pygame.K_LEFT:
            return "BACK"

        elif event.key in (pygame.K_RETURN, pygame.K_RIGHT):
            if not self._maps:
                return None

            return self._maps[self._selected]

        elif event.key == pygame.K_ESCAPE:
            return "BACK"

        return None

    def render(self) -> None:
        """Render the list of existing map files."""
        self._screen.fill((15, 18, 24))

        self._render_title()
        self._render_maps()

        pygame.display.flip()

    def _load_maps(self) -> list[str]:
        """Load all map file names for the selected difficulty directory."""
        directory = Path("maps") / self._difficulty.lower()

        return sorted(
            path.name
            for path in directory.glob("*.txt")
        )

    def _move_up(self) -> None:
        """Move the selection up one item."""
        if not self._maps:
            return

        self._selected = (
            self._selected - 1
        ) % len(self._maps)

    def _move_down(self) -> None:
        """Move the selection down one item."""
        if not self._maps:
            return

        self._selected = (
            self._selected + 1
        ) % len(self._maps)

    def _render_title(self) -> None:
        """Render the difficulty title shown at the top of the menu."""
        title = self._title_font.render(
            f"{self._difficulty} MAPS",
            True,
            (240, 240, 240),
        )

        title_rect = title.get_rect(
            center=(640, 150)
        )

        self._screen.blit(title, title_rect)

    def _render_maps(self) -> None:
        """Render every available map option or a fallback message."""
        if not self._maps:
            text = self._font.render(
                "No maps available",
                True,
                (180, 180, 180),
            )

            rect = text.get_rect(
                center=(640, 350)
            )

            self._screen.blit(text, rect)
            return

        for index, map_name in enumerate(self._maps):
            color = (
                (240, 240, 240)
                if index == self._selected
                else (120, 120, 120)
            )

            text = self._font.render(
                map_name,
                True,
                color,
            )

            rect = text.get_rect(
                center=(640, 280 + index * 55)
            )

            self._screen.blit(text, rect)
