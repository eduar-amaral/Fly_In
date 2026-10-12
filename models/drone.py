from __future__ import annotations

from pydantic import BaseModel


class Drone(BaseModel):
    drone_id: int
    path: list[str]
    position_index: int = 0
    wait_turns: int = 0

    @property
    def current_zone(self) -> str:
        return self.path[self.position_index]

    @property
    def finished(self) -> bool:
        return self.position_index >= len(self.path) - 1

    def next_zone(self) -> str | None:
        if self.finished:
            return None

        return self.path[self.position_index + 1]

    def move(self) -> None:
        if not self.finished:
            self.position_index += 1

    def wait(self, turns: int = 1) -> None:
        self.wait_turns = max(self.wait_turns, turns)

    def consume_wait(self) -> bool:
        if self.wait_turns <= 0:
            return False

        self.wait_turns -= 1
        return True
