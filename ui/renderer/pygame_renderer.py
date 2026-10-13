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
    """Render the map and drones for the UI."""

    def __init__(
        self,
        graph: Graph,
        logger: SimulationLog | None = None,
    ) -> None:
        """Create a renderer tied to a graph and optional simulation logger."""
        self._graph = graph
        self._logger = logger or SimulationLog(graph=graph)

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
        """Render the current simulation frame, map, and drones."""
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

    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle camera navigation controls for the GUI."""
        if event.type == pygame.KEYDOWN:
            if getattr(event, "repeat", False):
                return

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

        elif event.type == pygame.MOUSEWHEEL:
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
