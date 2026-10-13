from __future__ import annotations

import pygame


class ResultMenu:
    """Display the final summary after the simulation completes."""

    def __init__(self, screen: pygame.Surface) -> None:
        """Initialize the final result menu."""
        self._screen = screen

        self._font = pygame.font.Font(None, 48)
        self._title_font = pygame.font.Font(None, 72)

    MENU = "MENU"

    def handle_event(
        self,
        event: pygame.event.Event,
    ) -> str | None:
        """Handle confirmation input to return to the main menu."""
        if event.type != pygame.KEYDOWN:
            return None

        if (
            event.key in (pygame.K_RETURN, pygame.K_KP_ENTER)
            and not getattr(event, "repeat", False)
        ):
            return self.MENU

        return None

    def render(self) -> None:
        """Render the completion screen."""
        self._screen.fill((15, 18, 24))

        self._render_title()
        self._render_message()

        pygame.display.flip()

    def _render_title(self) -> None:
        """Render the title indicating the simulation ended."""
        title = self._title_font.render(
            "SIMULATION COMPLETE",
            True,
            (240, 240, 240),
        )

        title_rect = title.get_rect(
            center=(640, 220),
        )

        self._screen.blit(title, title_rect)

    def _render_message(self) -> None:
        """Render the instruction for returning to the menu."""
        message = self._font.render(
            "Press ENTER to return to menu",
            True,
            (180, 180, 180),
        )

        message_rect = message.get_rect(
            center=(640, 350),
        )

        self._screen.blit(message, message_rect)
