import pytest

from ui.animation_manager import AnimationManager


def test_animation_manager_starts_and_tracks_progress(monkeypatch) -> None:
    manager = AnimationManager(duration=0.1)
    current_time = {"value": 100.0}

    def fake_perf_counter() -> float:
        value = current_time["value"]
        current_time["value"] += 0.04
        return value

    monkeypatch.setattr("time.perf_counter", fake_perf_counter)

    manager.start()
    manager.update()

    assert manager.active is True
    assert manager.progress == pytest.approx(0.4)


def test_animation_manager_ends_at_one(monkeypatch) -> None:
    manager = AnimationManager(duration=0.05)
    current_time = {"value": 99.95}

    def fake_perf_counter() -> float:
        value = current_time["value"]
        current_time["value"] += 0.05
        return value

    monkeypatch.setattr("time.perf_counter", fake_perf_counter)

    manager.start()
    manager.update()

    assert manager.progress == pytest.approx(1.0)
    assert manager.active is False


def test_animation_manager_can_pause_and_resume(monkeypatch) -> None:
    manager = AnimationManager(duration=0.2)
    current_time = {"value": 100.0}

    def fake_perf_counter() -> float:
        value = current_time["value"]
        current_time["value"] += 0.05
        return value

    monkeypatch.setattr("time.perf_counter", fake_perf_counter)

    manager.start()
    manager.update()

    assert manager.progress == pytest.approx(0.25)

    manager.toggle_pause()
    manager.update()

    assert manager.paused is True
    assert manager.progress == pytest.approx(0.25)

    manager.toggle_pause()
    manager.update()

    assert manager.paused is False
    assert manager.progress == pytest.approx(0.75)
