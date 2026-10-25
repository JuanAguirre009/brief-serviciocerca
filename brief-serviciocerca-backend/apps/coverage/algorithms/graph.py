"""Graph representation utilities for coverage algorithms.

This module builds adjacency lists from Connection records while
respecting directionality and bidirectional flags.
"""

from collections import defaultdict
from typing import Any, Iterable


def build_adjacency(connections: Iterable[Any]) -> dict[int, list[int]]:
    """
    Build an adjacency list from coverage connections.

    Each connection is expected to expose at least:
        - origin_id: int
        - destination_id: int
        - is_bidirectional: bool

    Directionality rules:
        - A -> B  adds A: [..., B]
        - A <-> B adds A: [..., B] and B: [..., A]

    Isolated nodes (nodes without connections) will not appear in the
    adjacency list. This is intentional: the absence of a key means the
    node has no outgoing edges.

    Args:
        connections: Iterable of connection-like objects.

    Returns:
        Dict mapping node id to a list of reachable neighbor ids.
    """
    adjacency: dict[int, list[int]] = defaultdict(list)

    for connection in connections:
        origin_id = int(connection.origin_id)
        destination_id = int(connection.destination_id)
        is_bidirectional = bool(connection.is_bidirectional)

        adjacency[origin_id].append(destination_id)

        if is_bidirectional:
            adjacency[destination_id].append(origin_id)

    return dict(adjacency)
