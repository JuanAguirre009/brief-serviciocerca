"""Dijkstra's shortest-path algorithm for coverage networks.

This module finds the minimum-total-time route between two nodes in a
directed graph whose edge weights are strictly positive integers
(representing estimated_minutes).

It is intentionally independent of Django and the database. It operates
only on the weighted adjacency list produced by weighted_graph.py.
"""

from heapq import heappop, heappush
from typing import Optional

from .weighted_graph import validate_positive_minutes


INFINITY = float("inf")


def _validate_graph_weights(
    adjacency: dict[int, list[tuple[int, int]]],
) -> None:
    """
    Verify that every arc in the graph has a valid positive weight.

    Raises:
        ValueError: If any weight is invalid.
    """
    for neighbors in adjacency.values():
        for _node_id, weight in neighbors:
            validate_positive_minutes(weight)


def _initialize_state(
    origin_id: int,
) -> tuple[dict[int, int], dict[int, int], list[tuple[int, int]]]:
    """
    Create the initial Dijkstra state.

    Returns:
        - distances: best known cost to reach each node.
        - parents: parent map for path reconstruction.
        - pending: priority queue seeded with the origin.
    """
    distances: dict[int, int] = {origin_id: 0}
    parents: dict[int, int] = {}
    pending: list[tuple[int, int]] = [(0, origin_id)]

    return distances, parents, pending


def _relax_edge(
    current_id: int,
    current_cost: int,
    neighbor_id: int,
    weight: int,
    distances: dict[int, int],
    parents: dict[int, int],
    pending: list[tuple[int, int]],
) -> None:
    """
    Try to improve the known distance to a neighbor.

    If a cheaper path is found, update the distance, record the parent,
    and push the new candidate into the priority queue.
    """
    candidate_cost = current_cost + weight
    previous_cost = distances.get(neighbor_id, INFINITY)

    if candidate_cost < previous_cost:
        distances[neighbor_id] = candidate_cost
        parents[neighbor_id] = current_id
        heappush(pending, (candidate_cost, neighbor_id))


def _build_path(
    parents: dict[int, int],
    origin_id: int,
    destination_id: int,
) -> list[int]:
    """
    Reconstruct the shortest path from origin to destination.

    Returns an empty list when the destination is not reachable.
    """
    if destination_id == origin_id:
        return [origin_id]

    if destination_id not in parents:
        return []

    path: list[int] = [destination_id]
    current: Optional[int] = destination_id

    while current is not None and current != origin_id:
        current = parents.get(current)
        if current is not None:
            path.append(current)

    path.reverse()
    return path


def dijkstra_shortest_path(
    adjacency: dict[int, list[tuple[int, int]]],
    *,
    origin_id: int,
    destination_id: int,
) -> dict:
    """
    Find the minimum-total-minutes directed path between two nodes.

    Args:
        adjacency: Weighted adjacency list: node_id -> [(neighbor_id, weight)].
        origin_id: Starting node.
        destination_id: Target node.

    Returns:
        {
            "reachable": bool,
            "path": [node_id, ...],
            "total_minutes": int | None,
            "visited": [node_id, ...]
        }

    Notes:
        - All weights must be strictly positive integers.
        - When origin == destination, the path is [origin_id] and
          total_minutes is 0.
        - When the destination is unreachable, reachable is False,
          path is empty, and total_minutes is None.
        - visited contains nodes in the order Dijkstra settles their
          minimum distance, not the order they are first discovered.
    """
    _validate_graph_weights(adjacency)

    if origin_id == destination_id:
        return {
            "reachable": True,
            "path": [origin_id],
            "total_minutes": 0,
            "visited": [origin_id],
        }

    distances, parents, pending = _initialize_state(origin_id)
    settled: set[int] = set()
    visited_order: list[int] = []

    while pending:
        current_cost, current_id = heappop(pending)

        if current_id in settled:
            continue

        if current_cost != distances.get(current_id, INFINITY):
            continue

        settled.add(current_id)
        visited_order.append(current_id)

        if current_id == destination_id:
            break

        for neighbor_id, weight in adjacency.get(current_id, []):
            if neighbor_id in settled:
                continue

            _relax_edge(
                current_id,
                current_cost,
                neighbor_id,
                weight,
                distances,
                parents,
                pending,
            )

    if destination_id not in settled:
        return {
            "reachable": False,
            "path": [],
            "total_minutes": None,
            "visited": visited_order,
        }

    path = _build_path(parents, origin_id, destination_id)

    return {
        "reachable": True,
        "path": path,
        "total_minutes": distances[destination_id],
        "visited": visited_order,
    }
