"""Business logic for Feature 3 minimum-time routes."""

from django.core.exceptions import ValidationError

from .algorithms.dijkstra import dijkstra_shortest_path
from .algorithms.weighted_graph import build_weighted_adjacency
from .exceptions import NodeNotFoundError
from .models import Connection, CoverageNode


def _get_node(*, node_id: int, field_name: str) -> CoverageNode:
    try:
        return CoverageNode.objects.get(pk=node_id)
    except CoverageNode.DoesNotExist as exc:
        raise NodeNotFoundError(
            node_id=node_id,
            field_name=field_name,
        ) from exc


def _validate_nodes(
    origin: CoverageNode,
    destination: CoverageNode,
) -> None:
    if origin.type != CoverageNode.NodeType.BASE:
        raise ValidationError({
            "origin": "El origen debe ser un nodo de tipo BASE."
        })

    if destination.type != CoverageNode.NodeType.ZONE:
        raise ValidationError({
            "destination": "El destino debe ser un nodo de tipo ZONE."
        })


def _serialize_node(node: CoverageNode) -> dict:
    return {
        "id": node.id,
        "code": node.code,
        "name": node.name,
        "type": node.type,
    }


def _serialize_ids(
    node_ids: list[int],
    nodes_by_id: dict[int, CoverageNode],
) -> list[dict]:
    return [
        _serialize_node(nodes_by_id[node_id])
        for node_id in node_ids
    ]


def _build_segments(
    path_ids: list[int],
    adjacency: dict[int, list[tuple[int, int]]],
    nodes_by_id: dict[int, CoverageNode],
) -> list[dict]:
    """Describe each directed connection in the selected route."""
    segments = []

    for origin_id, destination_id in zip(
        path_ids,
        path_ids[1:],
    ):
        minutes = min(
            weight
            for neighbor_id, weight in adjacency.get(origin_id, [])
            if neighbor_id == destination_id
        )

        segments.append({
            "origin": _serialize_node(nodes_by_id[origin_id]),
            "destination": _serialize_node(nodes_by_id[destination_id]),
            "estimated_minutes": minutes,
        })

    return segments


def calculate_shortest_route(
    *,
    origin_id: int,
    destination_id: int,
) -> dict:
    """
    Calculate the minimum-total-minutes route from BASE to ZONE.

    The algorithm is implemented separately in dijkstra.py.
    This function handles persistence, business validation and
    serialization.
    """
    origin = _get_node(
        node_id=origin_id,
        field_name="origin",
    )

    destination = _get_node(
        node_id=destination_id,
        field_name="destination",
    )

    _validate_nodes(origin, destination)

    connections = Connection.objects.only(
        "origin_id",
        "destination_id",
        "estimated_minutes",
        "is_bidirectional",
    ).order_by("pk")

    adjacency = build_weighted_adjacency(connections)

    algorithm_result = dijkstra_shortest_path(
        adjacency,
        origin_id=origin.id,
        destination_id=destination.id,
    )

    path_ids = algorithm_result["path"]
    visited_ids = algorithm_result["visited"]

    required_ids = list(dict.fromkeys(
        visited_ids + path_ids
    ))

    nodes_by_id = CoverageNode.objects.in_bulk(required_ids)

    path = _serialize_ids(path_ids, nodes_by_id)
    traversal_order = _serialize_ids(visited_ids, nodes_by_id)

    reachable = algorithm_result["reachable"]
    total_minutes = algorithm_result["total_minutes"]

    segments = (
        _build_segments(path_ids, adjacency, nodes_by_id)
        if reachable
        else []
    )

    if reachable:
        message = (
            f"La ruta de menor tiempo desde {origin.name} "
            f"hasta {destination.name} tarda "
            f"{total_minutes} minuto(s)."
        )
    else:
        message = (
            f"No existe una ruta disponible desde "
            f"{origin.name} hasta {destination.name}."
        )

    return {
        "mode": "shortest_route",
        "reachable": reachable,
        "origin": _serialize_node(origin),
        "destination": _serialize_node(destination),
        "path": path,
        "segments": segments,
        "total_minutes": total_minutes,
        "traversal_order": traversal_order,
        "visited_count": len(visited_ids),
        "message": message,
    }
