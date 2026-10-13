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

    def __init__(self, graph: Graph | None = None) -> None:
        """Create a log attached to an optional graph for zone coloring."""
        self._graph = graph
        self._lines: list[str] = []

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
        return self._plain_entry(0, result)

    def record(self, turn: int, result: StepResult) -> None:
        """Save one turn of simulation output.

        Args:
            turn: Turn number to store.
            result: Step result produced by the scheduler.
        """
        entry = self._plain_entry(turn, result)
        if not entry:
            return

        self._lines.append(entry)
        print(entry)

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
