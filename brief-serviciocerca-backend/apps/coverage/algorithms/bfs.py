"""Breadth-first search algorithm for coverage reachability.

This module implements BFS manually to answer coverage questions:
- Can node X reach node Y?
- Which nodes are reachable from node X?

Weights (estimated_minutes) are intentionally ignored because Feature 2
defines coverage as the existence of a valid path, not as a cost
optimization problem.
"""

from collections import deque
from typing import Optional


def _traverse_bfs(
    adjacency: dict[int, list[int]],
    origin_id: int,
    destination_id: Optional[int] = None,
) -> tuple[list[int], dict[int, int]]:
    visited: set[int] = {origin_id}
    visited_order: list[int] = [origin_id]
    parents: dict[int, int] = {}

    queue: deque[int] = deque([origin_id])

    if destination_id == origin_id:
        return visited_order, parents

    while queue:
        current = queue.popleft()

        for neighbor in adjacency.get(current, []):
            if neighbor in visited:
                continue

            visited.add(neighbor)
            visited_order.append(neighbor)
            parents[neighbor] = current

            if neighbor == destination_id:
                return visited_order, parents

            queue.append(neighbor)

    return visited_order, parents

def _reconstruct_path(
    parents: dict[int, int],
    origin_id: int,
    destination_id: int,
) -> list[int]:
    """
    Reconstruct the shortest path (in number of edges) from origin to
    destination using the parent map produced by BFS.

    Returns an empty list when no path exists.
    """
    if destination_id == origin_id:
        return [origin_id]

    if destination_id not in parents:
        return []

    path: list[int] = []
    current: Optional[int] = destination_id

    while current is not None:
        path.append(current)
        current = parents.get(current)

    path.reverse()
    return path


def bfs_reachability(
    adjacency: dict[int, list[int]],
    origin_id: int,
    destination_id: Optional[int] = None,
) -> dict:
    """
    Determine reachability inside the coverage graph using BFS.

    Args:
        adjacency: Mapping node_id -> list of neighbor ids.
        origin_id: Node from which the search starts.
        destination_id: Optional node to reach. When provided, the
            function stops early as soon as the destination is found.

    Returns:
        {
            "reachable": bool,
            "visited": [id, ...],
            "path": [id, ...]
        }

    Behavior:
        - When origin == destination:
          reachable=True, path=[origin_id].
        - When destination is None:
          reachable is always True (the origin is trivially reachable
          from itself), path is empty, and visited contains all reachable
          nodes.
        - When destination is provided and reachable:
          reachable=True and path contains the shortest path in edges.
        - When destination is provided and not reachable:
          reachable=False and path is empty. visited contains all nodes
          explored before giving up.
    """
    visited_order, parents = _traverse_bfs(
        adjacency,
        origin_id,
        destination_id,
    )
    if destination_id is None:
        return {
            "reachable": True,
            "visited": visited_order,
            "path": [],
        }

    if destination_id == origin_id:
        return {
            "reachable": True,
            "visited": visited_order,
            "path": [origin_id],
        }

    path = _reconstruct_path(
        parents,
        origin_id,
        destination_id,
    )

    return {
        "reachable": len(path) > 0,
        "visited": visited_order,
        "path": path,
    }
