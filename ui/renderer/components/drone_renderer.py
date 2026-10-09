from __future__ import annotations

import pygame

from graph import Graph
from models import Drone

from ...camera import Camera
from simulation.step_result import Movement


class DroneRenderer:
    def __init__(self, graph: Graph, camera: Camera) -> None:
        self._graph = graph
        self._camera = camera

    def render(self, screen: pygame.Surface, drones: list[Drone]) -> None:
        for drone in drones:
            self._render_drone(screen, drone)

    def render_movement(
        self,
        screen: pygame.Surface,
        movement: Movement,
        progress: float,
    ) -> None:
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

        self._draw_drone(screen, (int(x), int(y)))

    def _render_drone(self, screen: pygame.Surface, drone: Drone) -> None:
        zone = self._graph.get_zone(drone.current_zone)

        position = self._camera.map_to_screen(zone.x, zone.y)

        self._draw_drone(screen, position)

    def _draw_drone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
    ) -> None:
        pygame.draw.circle(
            screen,
            (240, 240, 240),
            position,
            8,
        )
