from __future__ import annotations

from typing import TYPE_CHECKING

import pygame

from graph import Graph

from simulation.log_history import SimulationLog

from ..animation_manager import AnimationManager
from ..camera import Camera
from .base import Renderer
from .components.drone_renderer import DroneRenderer
from .components.edge_renderer import EdgeRenderer
from .components.hud_renderer import HUDRenderer
from .components.zone_renderer import ZoneRenderer

if TYPE_CHECKING:
    from simulation.simulation_state import SimulationState
    from simulation.step_result import Movement, StepResult


class PygameRenderer(Renderer):
    """Render the map, drones, and log panel for the UI."""

    def __init__(
        self,
        graph: Graph,
        logger: SimulationLog | None = None,
    ) -> None:
        """Create a renderer tied to a graph and optional simulation logger."""
        self._graph = graph
        self._logger = logger or SimulationLog(graph=graph)
        self._log_scroll = 0
        self._history_panel_rect = pygame.Rect(0, 0, 0, 0)

        screen = pygame.display.get_surface()

        if screen is None:
            raise RuntimeError(
                "Pygame display is not initialized"
            )

        self._screen = screen

        self._width = self._screen.get_width()
        self._height = self._screen.get_height()

        self._camera = Camera(
            width=self._width,
            height=self._height,
        )

        self._fit_camera()
        self._create_renderers()

        self._animation_manager = AnimationManager(
            duration=0.3
        )

        self._render_state: SimulationState | None = None
        self._render_result: StepResult | None = None

        self._open = True

    def render_turn(
        self,
        state: SimulationState,
        result: StepResult,
    ) -> None:
        """Queue a simulation turn for animated rendering."""
        if not self._open:
            return

        self._render_state = state
        self._render_result = result

        self._animation_manager.start()

    def update(self) -> None:
        """Advance the current animation frame."""
        self._animation_manager.update()

    @property
    def animation_active(self) -> bool:
        """Return whether the current animation is still in progress."""
        return self._animation_manager.active

    def is_open(self) -> bool:
        """Return whether the renderer still accepts draw operations."""
        return self._open

    def close(self) -> None:
        """Close the renderer and stop future updates."""
        self._open = False

    def render(self) -> None:
        """Render the current simulation frame, map, drones,
        and turning log.
        """
        if self._render_state is None:
            return

        if self._render_result is None:
            return

        if not self._open:
            return

        self._clear_screen()
        self._render_map()

        self._render_drones(
            self._render_state,
            self._render_result,
            self._animation_manager.progress,
        )

        self._hud_renderer.render(
            self._screen,
            self._render_state,
            self._render_result,
        )

        self._render_history_panel()
        self._update_display()

    def _create_renderers(self) -> None:
        """Instantiate the child renderers used to draw the map and HUD."""
        self._edge_renderer = EdgeRenderer(
            graph=self._graph,
            camera=self._camera,
        )

        self._zone_renderer = ZoneRenderer(
            graph=self._graph,
            camera=self._camera,
        )

        self._drone_renderer = DroneRenderer(
            graph=self._graph,
            camera=self._camera,
        )

        self._hud_renderer = HUDRenderer()

    def _render_map(self) -> None:
        """Render the static map structure made of edges and zones."""
        self._edge_renderer.render(self._screen)
        self._zone_renderer.render(self._screen)

    def _render_drones(
        self,
        state: SimulationState,
        result: StepResult,
        progress: float
    ) -> None:
        """Render stationary and moving drones for the current frame."""
        moving_ids = {
            movement.drone_id
            for movement in result.movements
        }

        stationary_drones = [
            drone
            for drone in state.drones
            if drone.drone_id not in moving_ids
        ]

        self._drone_renderer.render(self._screen, stationary_drones)

        moving_groups: dict[tuple[str, str], list[Movement]] = {}
        for movement in result.movements:
            key = (movement.from_zone, movement.to_zone)
            moving_groups.setdefault(key, []).append(movement)

        eased_progress = self._animation_manager.eased_progress

        for movement in result.movements:
            key = (movement.from_zone, movement.to_zone)
            group = moving_groups[key]
            index = group.index(movement)
            offset = self._drone_renderer.offset_for_group(
                len(group),
                index,
            )
            self._drone_renderer.render_movement(
                self._screen,
                movement,
                eased_progress,
                offset,
            )

    def _clear_screen(self) -> None:
        """Clear the rendering surface before drawing the next frame."""
        self._screen.fill((15, 18, 24))

    def _update_display(self) -> None:
        """Refresh the rendered surface on the screen."""
        pygame.display.flip()

    def _wrap_log_line(
        self,
        line: str,
        font: pygame.font.Font,
        max_width: int,
    ) -> list[str]:
        """Wrap a log line so it fits inside the history panel width."""
        if not line.strip():
            return [""]

        wrapped: list[str] = []
        remaining = line.strip()

        while remaining:
            if font.size(remaining)[0] <= max_width:
                wrapped.append(remaining)
                break

            cut_index = 1
            while cut_index <= len(remaining):
                if font.size(remaining[:cut_index])[0] > max_width:
                    break
                cut_index += 1

            if cut_index == 1:
                chunk = remaining[:1]
            else:
                chunk = remaining[: cut_index - 1].rstrip()

            if not chunk:
                chunk = remaining[:1]

            wrapped.append(chunk)
            remaining = remaining[len(chunk):].lstrip()

        return wrapped

    def _scroll_history(self, step: int) -> None:
        """Scroll the visible log history up or down."""
        visible_rows = max(1, self._visible_rows())
        history_lines = self._history_lines()
        max_scroll = max(0, len(history_lines) - visible_rows)
        self._log_scroll = max(
            0,
            min(max_scroll, self._log_scroll + step),
        )

    def _visible_rows(self) -> int:
        """Return how many rows of the log can fit in the panel."""
        if self._history_panel_rect.height <= 0:
            return 10

        return max(1, (self._history_panel_rect.height - 42) // 18)

    def _visible_history_lines(self) -> list[str]:
        """Return the subset of log lines currently visible in the panel."""
        history_lines = self._history_lines()
        visible_rows = max(1, self._visible_rows())
        max_scroll = max(0, len(history_lines) - visible_rows)
        self._log_scroll = min(self._log_scroll, max_scroll)

        start_index = max(
            0,
            len(history_lines) - visible_rows - self._log_scroll,
        )
        return history_lines[start_index: start_index + visible_rows]

    def _history_lines(self) -> list[str]:
        """Return history entries wrapped to the panel width."""
        if self._history_panel_rect.width <= 0:
            return list(self._logger.lines)

        max_chars = max(12, (self._history_panel_rect.width - 30) // 8)
        rendered: list[str] = []

        for line in self._logger.lines:
            chunk = line.strip()
            if not chunk:
                rendered.append("")
                continue

            while len(chunk) > max_chars:
                rendered.append(chunk[:max_chars].rstrip())
                chunk = chunk[max_chars:].lstrip()

            rendered.append(chunk)

        return rendered

    def _render_history_panel(self) -> None:
        """Render the turn history panel anchored to
        the right edge of the screen.
        """
        font = pygame.font.SysFont("consolas", 16)

        panel_x = self._screen.get_width() - 360
        panel_y = 20
        panel_w = 320
        panel_h = 220
        content_x = panel_x + 12
        content_y = panel_y + 28
        content_w = panel_w - 24
        content_h = panel_h - 40

        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        inner_rect = pygame.Rect(content_x, content_y, content_w, content_h)
        self._history_panel_rect = inner_rect

        pygame.draw.rect(
            self._screen,
            (22, 24, 30),
            panel_rect,
            border_radius=10,
        )
        pygame.draw.rect(
            self._screen,
            (60, 72, 92),
            inner_rect,
            border_radius=8,
        )

        title = font.render("Turn log", True, (255, 255, 255))
        self._screen.blit(title, (panel_x + 12, panel_y + 8))

        visible_lines = self._visible_history_lines()
        text_y = content_y + 8

        previous_clip = self._screen.get_clip()
        self._screen.set_clip(inner_rect)
        try:
            for line in visible_lines:
                base_color = (220, 230, 240)
                line_color = self._logger.color_for(line)
                if line_color is not None:
                    base_color = line_color

                text = font.render(line, True, base_color)
                text_rect = text.get_rect(topleft=(content_x + 8, text_y))
                if text_rect.bottom > content_y + content_h:
                    break
                self._screen.blit(text, text_rect.topleft)
                text_y += 18
        finally:
            self._screen.set_clip(previous_clip)

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle camera navigation and log-scrolling controls."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_w, pygame.K_UP):
                self._camera.move(0, Camera.PAN_SPEED)

            elif event.key in (pygame.K_s, pygame.K_DOWN):
                self._camera.move(0, -Camera.PAN_SPEED)

            elif event.key in (pygame.K_a, pygame.K_LEFT):
                self._camera.move(Camera.PAN_SPEED, 0)

            elif event.key in (pygame.K_d, pygame.K_RIGHT):
                self._camera.move(-Camera.PAN_SPEED, 0)

            elif event.key == pygame.K_r:
                self._camera.reset()

            elif event.key == pygame.K_PAGEUP:
                self._scroll_history(1)

            elif event.key == pygame.K_PAGEDOWN:
                self._scroll_history(-1)

        elif event.type == pygame.MOUSEWHEEL:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if self._history_panel_rect.collidepoint(mouse_x, mouse_y):
                if event.y > 0:
                    self._scroll_history(1)
                elif event.y < 0:
                    self._scroll_history(-1)
                return

            if event.y > 0:
                self._camera.zoom_in()
            elif event.y < 0:
                self._camera.zoom_out()

    def _fit_camera(self) -> None:
        """Adjust the camera bounds to encompass all zones in the graph."""
        zones = self._graph.all_zones()

        if not zones:
            return

        min_x = min(zone.x for zone in zones)
        max_x = max(zone.x for zone in zones)
        min_y = min(zone.y for zone in zones)
        max_y = max(zone.y for zone in zones)

        self._camera.fit(
            min_x=min_x,
            max_x=max_x,
            min_y=min_y,
            max_y=max_y,
        )

    def toggle_pause(self) -> None:
        """Pause or resume the animation playback."""
        self._animation_manager.toggle_pause()
