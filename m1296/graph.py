from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from collections import deque

NODE_COUNT = 36
SLOT_COUNT = NODE_COUNT * NODE_COUNT  # 1296

class EdgeType(str, Enum):
    INFLUENCE = "influence"
    DATA_FLOW = "data_flow"
    CONTROL_FLOW = "control_flow"
    DEPENDENCY_FLOW = "dependency_flow"
    RESOURCE_FLOW = "resource_flow"
    FEEDBACK_FLOW = "feedback_flow"

@dataclass(frozen=True)
class Edge:
    source: int
    target: int
    edge_type: EdgeType
    weight: float = 1.0
    confidence: float = 1.0
    active: bool = True

    def __post_init__(self):
        if not (0 <= self.source < NODE_COUNT and 0 <= self.target < NODE_COUNT):
            raise ValueError("node indices must be in [0, 35]")
        if not (-1.0 <= self.weight <= 1.0):
            raise ValueError("weight must be between -1 and 1")
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError("confidence must be between 0 and 1")

def edge_index(source: int, target: int) -> int:
    if not (0 <= source < NODE_COUNT and 0 <= target < NODE_COUNT):
        raise ValueError("node indices must be in [0, 35]")
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
        self._edges[edge_index(edge.source, edge.target)] = edge

    def get_edge(self, source: int, target: int) -> Edge | None:
        return self._edges.get(edge_index(source, target))

    def remove_edge(self, source: int, target: int) -> bool:
        return self._edges.pop(edge_index(source, target), None) is not None

    def outgoing(self, source: int, active_only: bool = True) -> tuple[Edge, ...]:
        if not 0 <= source < NODE_COUNT:
            raise ValueError("source must be in [0, 35]")
        return tuple(e for e in self._edges.values() if e.source == source and (e.active or not active_only))

    def impacted_nodes(self, source: int, max_depth: int | None = None) -> tuple[int, ...]:
        """Return nodes reachable downstream, excluding the source itself."""
        if not 0 <= source < NODE_COUNT:
            raise ValueError("source must be in [0, 35]")
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

    def cycles(self) -> tuple[tuple[int, ...], ...]:
        """Return directed simple cycles, canonicalized to avoid duplicate rotations."""
        adjacency = {i: [e.target for e in self.outgoing(i)] for i in range(NODE_COUNT)}
        found: set[tuple[int, ...]] = set()
        for start in range(NODE_COUNT):
            stack: list[tuple[int, list[int]]] = [(start, [start])]
            while stack:
                node, path = stack.pop()
                for nxt in adjacency[node]:
                    if nxt == start and len(path) > 1:
                        cycle = path[:]
                        rotations = [tuple(cycle[i:] + cycle[:i]) for i in range(len(cycle))]
                        found.add(min(rotations))
                    elif nxt > start and nxt not in path:
                        stack.append((nxt, path + [nxt]))
        return tuple(sorted(found))

    def validate(self) -> None:
        if len(self._edges) > SLOT_COUNT:
            raise ValueError("M1296 capacity exceeded")
        for key, edge in self._edges.items():
            if key != edge_index(edge.source, edge.target):
                raise ValueError("edge stored at incorrect directed slot")
