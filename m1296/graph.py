from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from collections import deque
import math

NODE_COUNT = 36
SLOT_COUNT = NODE_COUNT * NODE_COUNT  # 1296


class EdgeType(str, Enum):
    INFLUENCE = "influence"
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"
    DEPENDENCY_FLOW = "dependency_flow"
    RESOURCE_FLOW = "resource_flow"
    FEEDBACK_FLOW = "feedback_flow"


def _require_node(value: int, field: str) -> None:
    if type(value) is not int or not 0 <= value < NODE_COUNT:
        raise ValueError(f"{field} must be an integer in [0, 35]")


def _require_finite_number(value: float, field: str, lower: float, upper: float) -> None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    if not lower <= value <= upper:
        raise ValueError(f"{field} must be between {lower} and {upper}")


@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    edge_type: EdgeType
    weight: float = 1.0
    confidence: float = 1.0
    active: bool = True

    def __post_init__(self):
        _require_node(self.source, "source")
        _require_node(self.target, "target")
        if not isinstance(self.edge_type, EdgeType):
            raise ValueError("edge_type must be an EdgeType")
        _require_finite_number(self.weight, "weight", -1.0, 1.0)
        _require_finite_number(self.confidence, "confidence", 0.0, 1.0)
        if type(self.active) is not bool:
            raise ValueError("active must be a boolean")


def edge_index(source: int, target: int) -> int:
    _require_node(source, "source")
    _require_node(target, "target")
    return source * NODE_COUNT + target


class M1296Graph:
    """Sparse directed graph; reverse edges are independent and need not exist."""

    def __init__(self):
        self._edges: dict[int, Edge] = {}

    @property
    def capacity(self) -> int:
        return SLOT_COUNT

    @property
    def active_count(self) -> int:
        return sum(1 for e in self._edges.values() if e.active)

    def set_edge(self, edge: Edge) -> None:
        if not isinstance(edge, Edge):
            raise TypeError("edge must be an Edge")
        self._edges[edge_index(edge.source, edge.target)] = edge

    def get_edge(self, source: int, target: int) -> Edge | None:
        return self._edges.get(edge_index(source, target))

    def remove_edge(self, source: int, target: int) -> bool:
        return self._edges.pop(edge_index(source, target), None) is not None

    def outgoing(self, source: int, active_only: bool = True) -> tuple[Edge, ...]:
        _require_node(source, "source")
        if type(active_only) is not bool:
            raise ValueError("active_only must be a boolean")
        return tuple(e for e in self._edges.values() if e.source == source and (e.active or not active_only))

    def impacted_nodes(self, source: int, max_depth: int | None = None) -> tuple[int, ...]:
        """Return nodes reachable downstream, excluding the source itself."""
        _require_node(source, "source")
        if max_depth is not None and (type(max_depth) is not int or max_depth < 0):
            raise ValueError("max_depth must be a non-negative integer or None")
        visited = {source}
        queue = deque([(source, 0)])
        result: list[int] = []
        while queue:
            node, depth = queue.popleft()
            if max_depth is not None and depth >= max_depth:
                continue
            for edge in self.outgoing(node):
                if edge.target not in visited:
                    visited.add(edge.target)
                    result.append(edge.target)
                    queue.append((edge.target, depth + 1))
        return tuple(result)

    def cyclic_components(self) -> tuple[tuple[int, ...], ...]:
        """Return strongly connected components containing a directed cycle (Tarjan O(V+E))."""
        adjacency = {i: [e.target for e in self.outgoing(i) if e.active] for i in range(NODE_COUNT)}
        index = 0
        indices: dict[int, int] = {}
        lowlink: dict[int, int] = {}
        stack: list[int] = []
        on_stack: set[int] = set()
        components: list[tuple[int, ...]] = []

        def visit(node: int) -> None:
            nonlocal index
            indices[node] = lowlink[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            for target in adjacency[node]:
                if target not in indices:
                    visit(target)
                    lowlink[node] = min(lowlink[node], lowlink[target])
                elif target in on_stack:
                    lowlink[node] = min(lowlink[node], indices[target])
            if lowlink[node] == indices[node]:
                component: list[int] = []
                while True:
                    member = stack.pop()
                    on_stack.remove(member)
                    component.append(member)
                    if member == node:
                        break
                component.sort()
                if len(component) > 1 or node in adjacency[node]:
                    components.append(tuple(component))

        for node in range(NODE_COUNT):
            if node not in indices:
                visit(node)
        return tuple(sorted(components))

    def cycles(self) -> tuple[tuple[int, ...], ...]:
        """Backward-compatible alias returning cyclic strongly connected components."""
        return self.cyclic_components()

    def validate(self) -> None:
        if len(self._edges) > SLOT_COUNT:
            raise ValueError("M1296 capacity exceeded")
        for key, edge in self._edges.items():
            if not isinstance(edge, Edge):
                raise ValueError("graph contains a non-Edge value")
            if key != edge_index(edge.source, edge.target):
                raise ValueError("edge stored at incorrect directed slot")
