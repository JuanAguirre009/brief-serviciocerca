from django.db.models import QuerySet
from .models import (
   Connection,
   CoverageNode,
   Technician,
)

def node_list(
   *,
   node_type: str | None = None,
) -> QuerySet[CoverageNode]:
   """
   Return coverage nodes.
   Optionally filter the network by node type:
   BASE or ZONE.
   """
   queryset = CoverageNode.objects.all()
   if node_type:
       queryset = queryset.filter(
           type=node_type.strip().upper(),
       )
   return queryset.order_by(
       "code",
   )

def technician_list(
   *,
   base_id: int | None = None,
   is_available: bool | None = None,
) -> QuerySet[Technician]:
   """
   Return technicians.
   Optional filters:
   - operational base;
   - availability.
   """
   queryset = (
       Technician.objects
       .select_related("base")
       .all()
   )
   if base_id is not None:
       queryset = queryset.filter(
           base_id=base_id,
       )
   if is_available is not None:
       queryset = queryset.filter(
           is_available=is_available,
       )
   return queryset.order_by(
       "code",
   )

def connection_list() -> QuerySet[Connection]:
   """
   Return graph edges with origin and destination already loaded.
   select_related avoids unnecessary queries when the API needs
   information about both nodes.
   """
   return (
       Connection.objects
       .select_related(
           "origin",
           "destination",
       )
       .order_by(
           "origin__code",
           "destination__code",
       )
   )

def network_get() -> dict:
   """
   Return the complete configured coverage network.
   This selector intentionally returns domain/queryset objects.
   Serialization belongs to the API layer and will be implemented
   separately.
   """
   return {
       "nodes": node_list(),
       "technicians": technician_list(),
       "connections": connection_list(),
   }