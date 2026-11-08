"""Weighted adjacency list builder for coverage connections.

This module transforms coverage connections into a directed, weighted graph
suitable for shortest-path algorithms such as Dijkstra.

Each connection contributes one or two arcs:
    - A -> B  adds origin -> destination with the connection weight.
    - A <-> B adds origin -> destination AND destination -> origin,
      both with the same weight.

The module is defensive: it validates weights and rejects self-loops
independently of the database layer. This keeps graph algorithms pure,
testable, and reusable outside Django.
"""

from collections import defaultdict
from typing import Any, Iterable


Adjacency = dict[int, list[tuple[int, int]]]
WeightedArc = tuple[int, int]


def validate_positive_minutes(value: Any) -> int:
    """
    Ensure a connection weight is a strictly positive integer.

    The business model only permits strictly positive integer minutes.

    Raises:
        ValueError: If the value is not an integer or is <= 0.
    """
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(
            "estimated_minutes debe ser un entero mayor que cero."
        )

    return value


def _validate_distinct_nodes(origin_id: int, destination_id: int) -> None:
    """
    Reject self-loops because they do not represent useful coverage arcs.

    Raises:
        ValueError: If origin and destination are the same node.
    """
    if origin_id == destination_id:
        raise ValueError(
            "Una conexión no puede conectar un nodo consigo mismo."
        )


def _as_int(value: Any, field_name: str) -> int:
    """
    Coerce a node identifier to an integer with a clear error message.

    Raises:
        ValueError: If the value cannot be converted to an integer.
    """
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"'{field_name}' debe ser un identificador numérico."
        ) from exc


def build_weighted_adjacency(
    connections: Iterable[Any],
) -> Adjacency:
    """
    Build a directed, weighted adjacency list from coverage connections.

    Args:
        connections: Iterable of connection-like objects exposing
            `origin_id`, `destination_id`, `estimated_minutes`,
            and `is_bidirectional`.

    Returns:
        Mapping from node id to a list of (neighbor_id, weight) arcs.
        Isolated nodes do not appear as keys.

    Raises:
        ValueError: If a connection has an invalid weight, connects a node
            to itself, or has non-numeric node identifiers.
    """
    adjacency: Adjacency = defaultdict(list)

    for connection in connections:
        origin_id = _as_int(connection.origin_id, "origin_id")
        destination_id = _as_int(connection.destination_id, "destination_id")
        weight = validate_positive_minutes(connection.estimated_minutes)

        _validate_distinct_nodes(origin_id, destination_id)

        adjacency[origin_id].append((destination_id, weight))

        if connection.is_bidirectional:
            adjacency[destination_id].append((origin_id, weight))

    return dict(adjacency)
