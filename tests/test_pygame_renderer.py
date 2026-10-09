import pygame

from graph import Graph
from parser import MapParser
from simulation.simulation_state import SimulationState
from simulation.step_result import StepResult
from ui.renderer.pygame_renderer import PygameRenderer


def test_pygame_renderer_draws_and_closes() -> None:
    pygame.init()

    try:
        pygame.display.set_mode((800, 600))

        parsed = MapParser("maps/simple.map").load()
        graph = Graph.from_map(parsed)

        renderer = PygameRenderer(graph)

        state = SimulationState(drones=[])
        result = StepResult()

        renderer.render_turn(
            state=state,
            result=result,
        )
        renderer.render()

        assert renderer.is_open()

        renderer.close()

        assert not renderer.is_open()
    finally:
        pygame.quit()
