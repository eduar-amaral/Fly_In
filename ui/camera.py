from __future__ import annotations


class Camera:
    MIN_ZOOM = 0.5
    MAX_ZOOM = 3.0
    ZOOM_STEP = 0.1
    PAN_SPEED = 20

    def __init__(
        self,
        width: int,
        height: int,
        margin: int = 80,
    ) -> None:
        self.width = width
        self.height = height
        self.margin = margin

        self._min_x = 0
        self._max_x = 1
        self._min_y = 0
        self._max_y = 1

        self._zoom = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def fit(
        self,
        min_x: int,
        max_x: int,
        min_y: int,
        max_y: int,
    ) -> None:
        self._min_x = min_x
        self._max_x = max_x
        self._min_y = min_y
        self._max_y = max_y

        self.reset()

    def reset(self) -> None:
        self._zoom = 1.0
        self._offset_x = 0.0
        self._offset_y = 0.0

    def zoom_in(self) -> None:
        self._zoom = min(
            self._zoom + self.ZOOM_STEP,
            self.MAX_ZOOM,
        )

    def zoom_out(self) -> None:
        self._zoom = max(
            self._zoom - self.ZOOM_STEP,
            self.MIN_ZOOM,
        )

    def move(self, dx: float, dy: float) -> None:
        self._offset_x = self._clamp_offset(self._offset_x + dx, axis="x")
        self._offset_y = self._clamp_offset(self._offset_y + dy, axis="y")

    def _clamp_offset(self, value: float, axis: str) -> float:
        map_width = max(self._max_x - self._min_x, 1)
        map_height = max(self._max_y - self._min_y, 1)

        available_width = max(self.width - 2 * self.margin, 1)
        available_height = max(self.height - 2 * self.margin, 1)

        scale = min(
            available_width / map_width,
            available_height / map_height,
        ) * self._zoom

        view_width = map_width * scale
        view_height = map_height * scale

        max_offset_x = max(0.0, (view_width - available_width) / 2.0)
        max_offset_y = max(0.0, (view_height - available_height) / 2.0)

        if axis == "x":
            return max(-max_offset_x, min(max_offset_x, value))

        return max(-max_offset_y, min(max_offset_y, value))

    def map_to_screen(
        self,
        x: int,
        y: int,
    ) -> tuple[int, int]:
        map_width = max(
            self._max_x - self._min_x,
            1,
        )

        map_height = max(
            self._max_y - self._min_y,
            1,
        )

        available_width = (
            self.width - 2 * self.margin
        )

        available_height = (
            self.height - 2 * self.margin
        )

        scale = min(
            available_width / map_width,
            available_height / map_height,
        )

        scale *= self._zoom

        map_center_x = (
            self._min_x + self._max_x
        ) / 2

        map_center_y = (
            self._min_y + self._max_y
        ) / 2

        screen_x = (
            self.width / 2
            + (x - map_center_x) * scale
            + self._offset_x
        )

        screen_y = (
            self.height / 2
            - (y - map_center_y) * scale
            + self._offset_y
        )

        return int(screen_x), int(screen_y)
