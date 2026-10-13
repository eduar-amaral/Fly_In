from __future__ import annotations

import time


class AnimationManager:
    """Control the time progress of a visual animation.

    This class keeps the animation state, supports pause/resume, and exposes
    the current progress value to the renderer.

    Args:
        duration: Total time of the animation in seconds.
    """

    def __init__(self, duration: float = 0.5) -> None:
        """Initialize the animation state.

        Args:
            duration: Total time of the animation in seconds.
        """
        self._duration = duration

        self._active = False
        self._paused = False

        self._start_time = 0.0
        self._paused_time = 0.0
        self._progress = 0.0

    def start(self) -> None:
        """Start or restart the animation from the beginning."""
        self._start_time = time.perf_counter()
        self._paused_time = 0.0
        self._progress = 0.0

        self._active = True
        self._paused = False

    def update(self) -> None:
        """Refresh the animation progress using the current time."""
        if not self._active or self._paused:
            return

        elapsed = time.perf_counter() - self._start_time

        self._progress = min(
            elapsed / self._duration,
            1.0,
        )

        if self._progress >= 1.0 - 1e-9:
            self._progress = 1.0
            self._active = False

    def toggle_pause(self) -> None:
        """Pause the animation if it is running, or resume it if paused."""
        if not self._active:
            return

        if self._paused:
            self._resume()
        else:
            self._pause()

    def _pause(self) -> None:
        """Suspend the animation and record the moment it was paused."""
        self._paused_time = time.perf_counter()
        self._paused = True

    def _resume(self) -> None:
        """Resume the animation by compensating for the paused duration."""
        paused_duration = (
            time.perf_counter() - self._paused_time
        )

        self._start_time += paused_duration
        self._paused = False

    @staticmethod
    def ease_in_out_cubic(value: float) -> float:
        """Apply a smooth easing curve used for animation interpolation."""
        value = max(0.0, min(1.0, value))

        if value < 0.5:
            return 4.0 * value * value * value

        return 1.0 - ((-2.0 * value + 2.0) ** 3) / 2.0

    @property
    def progress(self) -> float:
        """Return the raw normalized animation progress in the range [0, 1]."""
        return self._progress

    @property
    def eased_progress(self) -> float:
        """Return the eased progress value used for smoother motion."""
        return self.ease_in_out_cubic(self._progress)

    @property
    def active(self) -> bool:
        """Return whether the animation is still running."""
        return self._active

    @property
    def paused(self) -> bool:
        """Return whether the animation is currently paused."""
        return self._paused
