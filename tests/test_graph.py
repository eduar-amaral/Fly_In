import pytest

from graph import GraphError

from tests.helpers import make_graph


def test_graph_adds_bidirectional_edge():
    graph = make_graph()

    a_neighbours = graph.get_neighbours("A")
    end_neighbours = graph.get_neighbours("END")

    assert any(edge.target == "END" for edge in a_neighbours)
    assert any(edge.target == "A" for edge in end_neighbours)


def test_graph_get_edge():
    graph = make_graph()

    edge = graph.get_edge("START", "A")

    assert edge.target == "A"


def test_graph_get_edge_raises_for_unknown_connection():
    graph = make_graph()

    with pytest.raises(GraphError):
        graph.get_edge("START", "END")
