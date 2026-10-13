from __future__ import annotations

import re

from graph import Graph

from .step_result import StepResult


class SimulationLog:
    """Keep a simple in-memory log of the current simulation turn.

    The same log is used by the terminal output and the pygame history panel so
    both views stay in sync during the run.
    """

    _RESET = "\033[0m"

    def __init__(
        self,
        graph: Graph | None = None,
        print_output: bool = True,
        show_capacity_info: bool = False,
    ) -> None:
        """Create a log attached to an optional graph for zone coloring."""
        self._graph = graph
        self._lines: list[str] = []
        self._print_output = print_output
        self._show_capacity_info = show_capacity_info

    def _zone_color(self, zone_name: str) -> tuple[int, int, int] | None:
        """Return the configured RGB color for a zone when available."""
        if self._graph is None:
            return None

        try:
            zone = self._graph.get_zone(zone_name)
        except Exception:
            return None

        if zone.color is None:
            return None

        return zone.palette_color

    def _ansi_color(self, zone_name: str) -> str:
        """Wrap a zone name with a terminal ANSI color
        sequence when possible.
        """
        color = self._zone_color(zone_name)
        if color is None:
            return zone_name

        red, green, blue = color
        return (
            f"\033[38;2;{red};{green};{blue}m{zone_name}{self._RESET}"
        )

    def _plain_entry(self, turn: int, result: StepResult) -> str:
        """Build the plain-history text describing a turn result."""
        del turn

        parts: list[str] = []

        for movement in result.movements:
            parts.append(f"D{movement.drone_id}-{movement.to_zone}")

        if not parts:
            return ""

        return " ".join(parts)

    def _terminal_entry(self, turn: int, result: StepResult) -> str:
        """Build a terminal-safe representation of a turn record."""
        del turn

        parts: list[str] = []

        for movement in result.movements:
            colored_zone = self._ansi_color(movement.to_zone)
            parts.append(f"D{movement.drone_id}-{colored_zone}")

        if not parts:
            return ""

        return " ".join(parts)

    @property
    def print_output(self) -> bool:
        """Return whether the log should print live terminal output."""
        return self._print_output

    def _capacity_info_line(
        self,
        result: StepResult,
        state: object | None = None,
    ) -> str:
        """Build a capacity summary for the current turn."""
        if self._graph is None:
            return ""

        drone_occupancy: dict[str, int] = {}
        if state is not None:
            for drone in state.drones:
                zone_name = drone.current_zone
                drone_occupancy[zone_name] = (
                    drone_occupancy.get(zone_name, 0) + 1
                )

        zone_parts: list[str] = []
        for zone in self._graph.all_zones():
            current = drone_occupancy.get(zone.name, 0)
            zone_parts.append(
                f"Zone {zone.name}: {current}/{zone.max_drones} drones"
            )

        connection_parts: list[str] = []
        usage: dict[tuple[str, str], int] = {}
        for movement in result.movements:
            edge = (movement.from_zone, movement.to_zone)
            usage[edge] = usage.get(edge, 0) + 1

        for from_zone, to_zone in sorted(usage):
            edge = self._graph.get_edge(from_zone, to_zone)
            connection_parts.append(
                f"Connection {from_zone}-{to_zone}: "
                f"{usage[(from_zone, to_zone)]}/{edge.capacity} capacity used"
            )

        if not zone_parts and not connection_parts:
            return ""

        return ", ".join(zone_parts + connection_parts)

    def record(
        self,
        turn: int,
        result: StepResult,
        state: object | None = None,
    ) -> None:
        """Save one turn of simulation output.

        Args:
            turn: Turn number to store.
            result: Step result produced by the scheduler.
            state: Optional simulation state used for live capacity data.
        """
        entry = self._plain_entry(turn, result)
        if entry:
            self._lines.append(entry)

        if self._show_capacity_info:
            info_line = self._capacity_info_line(result, state)
            if info_line:
                print(info_line)

        if self._print_output and entry:
            print(self._terminal_entry(turn, result))

    @property
    def lines(self) -> list[str]:
        """Return a copy of the stored turn history."""
        return list(self._lines)

    def color_for(self, text: str) -> tuple[int, int, int] | None:
        """Infer the zone color associated with a text log line."""
        if not text or self._graph is None:
            return None

        tokens = re.findall(r"[A-Za-z0-9_]+", text)

        for token in tokens:
            if token.startswith("D") and token[1:].isdigit():
                continue

            if token in {"Turn", "no", "movement", "waits", "at", "and"}:
                continue

            if self._graph.has_zone(token):
                return self._zone_color(token)

        return None
