import pytest
from m1296.graph import M1296Graph, Edge, EdgeType, edge_index, SLOT_COUNT


def test_address_space_is_1296_directed_slots():
    slots = {edge_index(i, j) for i in range(36) for j in range(36)}
    assert len(slots) == SLOT_COUNT == 1296
    assert min(slots) == 0 and max(slots) == 1295


def test_direction_is_not_assumed_symmetric():
    graph = M1296Graph()
    graph.set_edge(Edge(1, 2, EdgeType.INFLUENCE, 0.8))
    assert graph.get_edge(1, 2) is not None
    assert graph.get_edge(2, 1) is None


def test_impact_analysis_follows_directed_edges():
    graph = M1296Graph()
    graph.set_edge(Edge(0, 1, EdgeType.DEPENDENCY_FLOW))
    graph.set_edge(Edge(1, 3, EdgeType.DATA_FLOW))
    graph.set_edge(Edge(3, 4, EdgeType.FEEDBACK_FLOW))
    assert graph.impacted_nodes(0) == (1, 3, 4)
    assert graph.impacted_nodes(0, max_depth=1) == (1,)


def test_cycle_detection_and_inactive_edges():
    graph = M1296Graph()
    graph.set_edge(Edge(0, 1, EdgeType.CONTROL_FLOW))
    graph.set_edge(Edge(1, 0, EdgeType.FEEDBACK_FLOW))
    graph.set_edge(Edge(1, 2, EdgeType.INFLUENCE, active=False))
    assert graph.cycles() == ((0, 1),)
    assert graph.active_count == 2


def test_rejects_invalid_node():
    with pytest.raises(ValueError):
        edge_index(36, 0)


@pytest.mark.parametrize("bad_index", [True, 1.0, "1", -1, 36])
def test_rejects_non_integer_node_indices(bad_index):
    with pytest.raises(ValueError):
        edge_index(bad_index, 2)
    with pytest.raises(ValueError):
        Edge(bad_index, 2, EdgeType.INFLUENCE)


@pytest.mark.parametrize("bad_number", [True, float("nan"), float("inf"), "0.5", 10**400])
def test_rejects_boolean_and_non_finite_edge_numbers(bad_number):
    with pytest.raises(ValueError):
        Edge(1, 2, EdgeType.INFLUENCE, bad_number, 0.9)


def test_rejects_invalid_edge_metadata_and_depth():
    with pytest.raises(ValueError):
        Edge(1, 2, "influence")
    with pytest.raises(ValueError):
        Edge(1, 2, EdgeType.INFLUENCE, active=1)
    with pytest.raises(ValueError):
        M1296Graph().impacted_nodes(1, max_depth=True)
