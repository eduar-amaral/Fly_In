from pathlib import Path

import pygame
import pytest

from graph import Graph
from models import Zone, ZoneKind
from parser import MapParser
from parser.errors import ParseError
from simulation import Simulation
from simulation.log_history import SimulationLog
from simulation.step_result import Movement, StepResult
from ui.camera import Camera
from ui.menu.map_menu import MapMenu
from ui.menu.menu_manager import MenuManager
from ui.renderer.components.zone_renderer import ZoneRenderer
from ui.renderer.pygame_renderer import PygameRenderer


def test_parser_loads_easy_map():
    parsed = MapParser("maps/easy/01_linear_path.txt").load()

    assert parsed.nb_drones == 2
    assert len(parsed.zones) == 4
    assert len(parsed.connections) == 3


def test_zone_renderer_uses_map_color_metadata():
    pygame.init()
    pygame.display.init()
    pygame.display.set_mode((1280, 720))

    graph = Graph()
    zone = Zone(
        name="start",
        x=0,
        y=0,
        kind=ZoneKind.START,
        color="green",
    )
    graph.add_node(zone)

    renderer = ZoneRenderer(graph, Camera(width=1280, height=720))

    assert renderer._get_color(zone) == (76, 175, 80)
    pygame.quit()


def test_simulation_log_respects_zone_palette():
    graph = Graph()
    graph.add_node(
        Zone(name="start", x=0, y=0, kind=ZoneKind.START, color="green")
    )
    graph.add_node(
        Zone(name="goal", x=1, y=0, kind=ZoneKind.END, color="red")
    )

    logger = SimulationLog(graph=graph)
    logger.record(
        1,
        StepResult(
            movements=[
                Movement(drone_id=1, from_zone="start", to_zone="goal")
            ]
        ),
    )

    assert logger.color_for("start") == (76, 175, 80)
    assert logger.color_for("goal") == (239, 83, 80)
    assert logger.lines[0].startswith("D1-goal")
    assert "goal" in logger.lines[0]


def test_map_menu_can_go_back_to_difficulty():
    pygame.init()
    pygame.display.init()
    screen = pygame.display.set_mode((1280, 720))

    menu = MenuManager(screen)
    menu._current_menu = "map"
    menu._map_menu = MapMenu(screen, "EASY")

    event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)
    assert menu.handle_event(event) is None
    assert menu._current_menu == "difficulty"
    assert menu._map_menu is None

    pygame.quit()


def test_pygame_renderer_scrolls_history_within_panel():
    pygame.init()
    pygame.display.init()
    pygame.display.set_mode((1280, 720))

    graph = Graph()
    graph.add_node(Zone(name="start", x=0, y=0, kind=ZoneKind.START))
    graph.add_node(Zone(name="goal", x=1, y=0, kind=ZoneKind.END))

    logger = SimulationLog(graph=graph)
    logger.record(
        1,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="start", to_zone="goal")]
        ),
    )
    logger.record(
        2,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="goal", to_zone="start")]
        ),
    )
    logger.record(
        3,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="start", to_zone="goal")]
        ),
    )
    logger.record(
        4,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="goal", to_zone="start")]
        ),
    )
    logger.record(
        5,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="start", to_zone="goal")]
        ),
    )
    logger.record(
        6,
        StepResult(
            movements=[Movement(drone_id=1, from_zone="goal", to_zone="start")]
        ),
    )

    renderer = PygameRenderer(graph=graph, logger=logger)
    renderer._history_panel_rect = pygame.Rect(0, 0, 1000, 100)
    renderer._log_scroll = 0

    visible_lines = renderer._visible_history_lines()
    assert len(visible_lines) == 3
    assert visible_lines[0].startswith("D1-")
    assert visible_lines[-1].startswith("D1-")

    renderer._log_scroll = 2
    scrolled_lines = renderer._visible_history_lines()
    assert len(scrolled_lines) == 3
    assert scrolled_lines[0].startswith("D1-")
    assert scrolled_lines[-1].startswith("D1-")

    pygame.quit()


def test_simulation_output_uses_subject_format(capsys):
    parsed = MapParser("maps/easy/01_linear_path.txt").load()
    graph = Graph.from_map(parsed)

    simulation = Simulation(graph=graph, nb_drones=parsed.nb_drones)
    simulation.run()

    captured = capsys.readouterr()
    assert "D1-" in captured.out
    assert "Turn " not in captured.out
    assert "All drones reached the destination." in captured.out


def test_map_parser_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        MapParser("maps/this_file_does_not_exist.txt").load()


@pytest.mark.parametrize(
    "content, expected",
    [
        (
            "nb_drones: 0\nstart_hub: start 0 0\nend_hub: goal 1 0\n",
            "greater than 0",
        ),
        (
            "nb_drones: nope\nstart_hub: start 0 0\nend_hub: goal 1 0\n",
            "positive integer",
        ),
        (
            "bad_line\nstart_hub: start 0 0\nend_hub: goal 1 0\n",
            "First line must be",
        ),
    ],
)
def test_map_parser_rejects_invalid_nb_drones(tmp_path, content, expected):
    map_file = tmp_path / "bad_map.txt"
    map_file.write_text(content, encoding="utf-8")

    with pytest.raises((ParseError, ValueError), match=expected):
        MapParser(map_file).load()


@pytest.mark.parametrize(
    "content",
    [
        "nb_drones: 2\nstart_hub: start 0 0\n"
        "end_hub: goal 1 0\nstart_hub: start 0 1\n",
        "nb_drones: 2\nstart_hub: start 0 0\n"
        "hub: goal 1 0\nhub: goal 2 0\n",
    ],
)
def test_map_parser_rejects_duplicate_hub_names(tmp_path, content):
    map_file = tmp_path / "duplicate_hub.txt"
    map_file.write_text(content, encoding="utf-8")

    with pytest.raises(
        ParseError,
        match=(
            "Duplicate zone name|"
            "Zone names must be unique"
        ),
    ):
        MapParser(map_file).load()


@pytest.mark.parametrize(
    "content",
    [
        "nb_drones: 1\nstart_hub: start 0 0\n"
        "end_hub: goal 1 0\nconnection: start-missing\n",
        "nb_drones: 1\nstart_hub: start 0 0\n"
        "end_hub: goal 1 0\nconnection: start-goal\n"
        "connection: start-goal\n",
    ],
)
def test_map_parser_rejects_invalid_connections(tmp_path, content):
    map_file = tmp_path / "bad_connection.txt"
    map_file.write_text(content, encoding="utf-8")

    with pytest.raises(ParseError):
        MapParser(map_file).load()


def test_map_parser_rejects_missing_start_and_end_hubs(tmp_path):
    map_file = tmp_path / "missing_hubs.txt"
    map_file.write_text(
        "nb_drones: 2\nhub: waypoint 0 0\nhub: other 1 0\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="no start_hub|no end_hub"):
        MapParser(map_file).load()


def test_map_parser_rejects_invalid_zone_metadata(tmp_path):
    map_file = tmp_path / "invalid_zone.txt"
    map_file.write_text(
        "nb_drones: 1\n"
        "start_hub: start 0 0 [zone=unknown]\n"
        "end_hub: goal 1 0\n",
        encoding="utf-8",
    )

    with pytest.raises(ParseError, match="Invalid zone type"):
        MapParser(map_file).load()


def test_subject_readme_exists_at_root():
    readme = Path("README.md")
    assert readme.exists()


def test_main_handles_keyboard_interrupt(monkeypatch, capsys):
    class DummyApp:
        def __init__(self) -> None:
            self._running = True

        def run(self) -> None:
            raise KeyboardInterrupt

    monkeypatch.setattr("main.Application", lambda: DummyApp())

    from main import main

    main()

    captured = capsys.readouterr()
    assert "Simulation interrupted by user." in captured.out


def test_simulation_prints_final_destination_message(capsys):
    parsed = MapParser("maps/easy/01_linear_path.txt").load()
    graph = Graph.from_map(parsed)

    simulation = Simulation(graph=graph, nb_drones=parsed.nb_drones)
    simulation.run()

    captured = capsys.readouterr()
    assert "All drones reached the destination." in captured.out
