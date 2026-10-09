from __future__ import annotations

import pygame

from graph import Graph
from models import Zone, ZoneType

from ...camera import Camera


class ZoneRenderer:
    RADIUS = 18
    BORDER_WIDTH = 2

    def __init__(self, graph: Graph, camera: Camera) -> None:
        self._graph = graph
        self._camera = camera
        self._font = pygame.font.Font(None, 20)

    def render(self, screen: pygame.Surface) -> None:
        for zone in self._graph.all_zones():
            position = self._get_position(
                zone.x,
                zone.y,
            )

            self._draw_zone(
                screen,
                position,
                zone,
            )

            self._draw_name(
                screen,
                zone.name,
                position,
            )

    def _get_position(self, x: int, y: int) -> tuple[int, int]:
        return self._camera.map_to_screen(x, y)

    def _draw_zone(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        zone: Zone,
    ) -> None:
        color = self._get_color(zone)

        pygame.draw.circle(
            screen,
            (230, 230, 230),
            position,
            self.RADIUS + self.BORDER_WIDTH,
        )

        pygame.draw.circle(
            screen,
            color,
            position,
            self.RADIUS,
        )

    def _draw_name(
        self,
        screen: pygame.Surface,
        name: str,
        position: tuple[int, int],
    ) -> None:
        text = self._font.render(
            name,
            True,
            (240, 240, 240),
        )

        text_rect = text.get_rect(
            centerx=position[0],
            bottom=position[1] - self.RADIUS - 6,
        )

        background_rect = text_rect.inflate(8, 4)

        pygame.draw.rect(
            screen,
            (15, 18, 24),
            background_rect,
            border_radius=4,
        )

        pygame.draw.rect(
            screen,
            (70, 80, 95),
            background_rect,
            width=1,
            border_radius=4,
        )

        screen.blit(text, text_rect)

    def _get_color(
        self,
        zone: Zone,
    ) -> tuple[int, int, int]:
        if zone.color is not None:
            return zone.palette_color

        if zone.is_start:
            return (80, 220, 120)

        if zone.is_end:
            return (240, 90, 90)

        if zone.zone_type == ZoneType.NORMAL:
            return (100, 180, 255)

        if zone.zone_type == ZoneType.RESTRICTED:
            return (255, 180, 80)

        if zone.zone_type == ZoneType.PRIORITY:
            return (120, 220, 140)

        if zone.zone_type == ZoneType.BLOCKED:
            return (100, 100, 100)

        return (180, 180, 180)
