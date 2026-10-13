from __future__ import annotations

import math

import pygame

from graph import Graph
from models import Drone

from ...camera import Camera
from simulation.step_result import Movement


class DroneRenderer:
    """Render drone entities on the map and during transitions."""

    def __init__(self, graph: Graph, camera: Camera) -> None:
        """Create a drone renderer bound to a graph and camera."""
        self._graph = graph
        self._camera = camera

    @staticmethod
    def offset_for_group(count: int, index: int) -> tuple[int, int]:
        """Return the offset used when many drones share one zone."""
        if count <= 1:
            return (0, 0)

        angle = (2.0 * math.pi * index) / count
        radius = 10 + (count - 1) * 3
        x = int(round(radius * math.cos(angle)))
        y = int(round(radius * math.sin(angle)))
        return (x, y)

    def render(self, screen: pygame.Surface, drones: list[Drone]) -> None:
        """Render drones that are stationary in their current zones."""
        grouped: dict[str, list[Drone]] = {}
        for drone in drones:
            grouped.setdefault(drone.current_zone, []).append(drone)

        for zone_name, zone_drones in grouped.items():
            zone = self._graph.get_zone(zone_name)
            base_position = self._camera.map_to_screen(zone.x, zone.y)
            count = len(zone_drones)

            for index, drone in enumerate(zone_drones):
                offset = self.offset_for_group(count, index)
                position = (
                    base_position[0] + offset[0],
                    base_position[1] + offset[1],
                )
                self._draw_drone(screen, position, drone.drone_id)

    def render_movement(
        self,
        screen: pygame.Surface,
        movement: Movement,
        progress: float,
        offset: tuple[int, int] = (0, 0),
    ) -> None:
        """Render one drone while it is transitioning between two zones."""
        start_zone = self._graph.get_zone(movement.from_zone)
        end_zone = self._graph.get_zone(movement.to_zone)

        start_position = self._camera.map_to_screen(
            start_zone.x,
            start_zone.y,
        )

        end_position = self._camera.map_to_screen(
            end_zone.x,
            end_zone.y,
        )

        x = start_position[0] + (
            end_position[0] - start_position[0]
        ) * progress

        y = start_position[1] + (
            end_position[1] - start_position[1]
        ) * progress

        self._draw_drone(
            screen,
            (int(x) + offset[0], int(y) + offset[1]),
            movement.drone_id,
        )

    def _draw_drone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        drone_id: int,
    ) -> None:
        """Draw the circular drone marker and its numeric label."""
        pygame.draw.circle(
            screen,
            (240, 240, 240),
            position,
            8,
        )

        label = str(drone_id)
        label_surface = pygame.font.SysFont("consolas", 9).render(
            label,
            True,
            (10, 12, 18),
        )
        label_rect = label_surface.get_rect(center=position)
        screen.blit(label_surface, label_rect)
