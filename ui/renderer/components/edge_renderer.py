from __future__ import annotations

import math

import pygame

from graph import Graph

from ...camera import Camera
from .zone_renderer import ZoneRenderer


class EdgeRenderer:
    """Draw the connections between zones on the map surface."""

    WIDTH = 2
    COLOR = (70, 80, 95)

    def __init__(self, graph: Graph, camera: Camera) -> None:
        """Create an edge renderer tied to a graph and camera."""
        self._graph = graph
        self._camera = camera

    def render(self, screen: pygame.Surface) -> None:
        """Render each undirected edge once to avoid duplicate lines."""
        draw_edges: set[frozenset[str]] = set()

        for zone in self._graph.all_zones():
            source = self._camera.map_to_screen(
                zone.x,
                zone.y,
            )

            for edge in self._graph.get_neighbours(zone.name):
                key = frozenset({
                    zone.name,
                    edge.target,
                })

                if key in draw_edges:
                    continue

                draw_edges.add(key)

                target_zone = self._graph.get_zone(edge.target)

                target = self._camera.map_to_screen(
                    target_zone.x,
                    target_zone.y,
                )

                start, end = self._shorten_line(
                    source,
                    target,
                    ZoneRenderer.RADIUS,
                )

                pygame.draw.line(
                    screen,
                    self.COLOR,
                    start,
                    end,
                    self.WIDTH,
                )

    def _shorten_line(
        self,
        start: tuple[int, int],
        end: tuple[int, int],
        distance: int,
    ) -> tuple[
        tuple[int, int],
        tuple[int, int],
    ]:
        """Shorten the line segment to avoid drawing under zone circles."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]

        length = math.hypot(dx, dy)

        if length == 0:
            return start, end

        offset_x = dx / length * distance
        offset_y = dy / length * distance

        new_start = (
            int(start[0] + offset_x),
            int(start[1] + offset_y),
        )

        new_end = (
            int(end[0] - offset_x),
            int(end[1] - offset_y),
        )

        return new_start, new_end
