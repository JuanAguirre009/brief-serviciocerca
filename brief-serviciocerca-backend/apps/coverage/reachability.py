"""Business logic for Feature 2 coverage queries.

This module connects the persisted coverage network with the BFS
algorithm implemented by the team.

Feature 2 defines coverage as reachability: a zone is covered from a
base when at least one valid directed path exists between both nodes.

Connection weights are intentionally ignored here. Cost optimization
belongs to Feature 3.
"""

from django.core.exceptions import ValidationError

from .algorithms.bfs import bfs_reachability
from .algorithms.graph import build_adjacency
from .exceptions import NodeNotFoundError
from .models import Connection, CoverageNode


def _get_node(
    *,
    node_id: int,
    field_name: str,
) -> CoverageNode:
    """Return a coverage node or raise a domain-friendly error."""
    try:
        return CoverageNode.objects.get(
            pk=node_id,
        )
    except CoverageNode.DoesNotExist as exc:
        raise NodeNotFoundError(
            node_id=node_id,
            field_name=field_name,
        ) from exc


def _validate_origin_base(
    node: CoverageNode,
) -> None:
    """Feature 2 coverage queries start from an operational BASE."""
    if node.type != CoverageNode.NodeType.BASE:
        raise ValidationError(
            {
                "origin": (
                    "El origen de la consulta de cobertura "
                    "debe ser un nodo de tipo BASE."
                )
            }
        )


def _validate_destination_zone(
    node: CoverageNode,
) -> None:
    """The requested destination must represent a service ZONE."""
    if node.type != CoverageNode.NodeType.ZONE:
        raise ValidationError(
            {
                "destination": (
                    "El destino de la consulta de cobertura "
                    "debe ser un nodo de tipo ZONE."
                )
            }
        )


def _node_to_dict(
    node: CoverageNode,
) -> dict:
    """Return the node representation required by the API layer."""
    return {
        "id": node.id,
        "code": node.code,
        "name": node.name,
        "type": node.type,
    }


def _nodes_by_id(
    node_ids: list[int],
) -> dict[int, CoverageNode]:
    """
    Load a collection of nodes in one query.

    Returning a mapping avoids querying the database once for every
    node contained in the BFS trace or path.
    """
    if not node_ids:
        return {}

    nodes = CoverageNode.objects.filter(
        id__in=set(node_ids),
    )

    return {
        node.id: node
        for node in nodes
    }


def _serialize_node_ids(
    node_ids: list[int],
    nodes_by_id: dict[int, CoverageNode],
) -> list[dict]:
    """
    Serialize node IDs while preserving the order produced by BFS.
    """
    return [
        _node_to_dict(nodes_by_id[node_id])
        for node_id in node_ids
        if node_id in nodes_by_id
    ]


def _build_current_adjacency() -> dict[int, list[int]]:
    """
    Build the graph representation from the persisted connections.

    estimated_minutes is intentionally not loaded because Feature 2
    only needs graph reachability.
    """
    connections = Connection.objects.only(
        "origin_id",
        "destination_id",
        "is_bidirectional",
    )

    return build_adjacency(
        connections,
    )


def check_coverage(
    *,
    origin_id: int,
    destination_id: int,
) -> dict:
    """
    Determine whether a service zone is reachable from a base.

    Coverage means that at least one valid directed path exists.

    This function does not calculate the lowest-cost route.
    """
    origin = _get_node(
        node_id=origin_id,
        field_name="origin",
    )

    destination = _get_node(
        node_id=destination_id,
        field_name="destination",
    )

    _validate_origin_base(origin)
    _validate_destination_zone(destination)

    adjacency = _build_current_adjacency()

    bfs_result = bfs_reachability(
        adjacency,
        origin_id=origin.id,
        destination_id=destination.id,
    )

    visited_ids = bfs_result["visited"]
    path_ids = bfs_result["path"]

    required_ids = list(
        dict.fromkeys(
            visited_ids + path_ids
        )
    )

    nodes_by_id = _nodes_by_id(
        required_ids,
    )

    covered = bfs_result["reachable"]

    if covered:
        message = (
            f"La zona {destination.name} se encuentra "
            f"dentro de la cobertura de {origin.name}."
        )
    else:
        message = (
            f"La zona {destination.name} no es alcanzable "
            f"desde {origin.name}."
        )

    return {
        "mode": "check",
        "covered": covered,
        "origin": _node_to_dict(origin),
        "destination": _node_to_dict(destination),
        "path": _serialize_node_ids(
            path_ids,
            nodes_by_id,
        ),
        "traversal_order": _serialize_node_ids(
            visited_ids,
            nodes_by_id,
        ),
        "visited_count": len(visited_ids),
        "message": message,
    }


def list_reachable_nodes(
    *,
    origin_id: int,
) -> dict:
    """
    Return all service zones reachable from an operational base.

    The traversal order corresponds to the real BFS discovery order.
    """
    origin = _get_node(
        node_id=origin_id,
        field_name="origin",
    )

    _validate_origin_base(origin)

    adjacency = _build_current_adjacency()

    bfs_result = bfs_reachability(
        adjacency,
        origin_id=origin.id,
        destination_id=None,
    )

    visited_ids = bfs_result["visited"]

    nodes_by_id = _nodes_by_id(
        visited_ids,
    )

    traversal_order = _serialize_node_ids(
        visited_ids,
        nodes_by_id,
    )

    reachable_zones = [
        node_data
        for node_data in traversal_order
        if node_data["type"] == CoverageNode.NodeType.ZONE
    ]

    reachable_count = len(
        reachable_zones
    )

    if reachable_count:
        message = (
            f"{origin.name} puede alcanzar "
            f"{reachable_count} zona(s) de servicio."
        )
    else:
        message = (
            f"{origin.name} no tiene zonas "
            "de servicio alcanzables."
        )

    return {
        "mode": "reachability",
        "origin": _node_to_dict(origin),
        "reachable_count": reachable_count,
        "reachable_nodes": reachable_zones,
        "traversal_order": traversal_order,
        "visited_count": len(visited_ids),
        "message": message,
    }
