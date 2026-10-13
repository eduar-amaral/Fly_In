from __future__ import annotations

from pydantic import BaseModel


class Drone(BaseModel):
    """Represent one drone moving through a precomputed route."""

    drone_id: int
    path: list[str]
    position_index: int = 0
    wait_turns: int = 0

    @property
    def current_zone(self) -> str:
        """Return the zone in which the drone currently stands."""
        return self.path[self.position_index]

    @property
    def finished(self) -> bool:
        """Return whether the drone already reached the last zone."""
        return self.position_index >= len(self.path) - 1

    def next_zone(self) -> str | None:
        """Return the next target zone in the planned route, if any."""
        if self.finished:
            return None

        return self.path[self.position_index + 1]

    def move(self) -> None:
        """Advance the drone to the next zone when it is not finished."""
        if not self.finished:
            self.position_index += 1

    def wait(self, turns: int = 1) -> None:
        """Add or extend the drone's waiting time.

        Args:
            turns: Number of turns to wait before moving again.
        """
        self.wait_turns = max(self.wait_turns, turns)

    def consume_wait(self) -> bool:
        """Consume one wait turn and report whether the drone was delayed.

        Returns:
            True if a wait turn was consumed; otherwise False.
        """
        if self.wait_turns <= 0:
            return False

        self.wait_turns -= 1
        return True
