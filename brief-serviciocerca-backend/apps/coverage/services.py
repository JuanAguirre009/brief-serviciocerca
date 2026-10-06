from django.core.exceptions import ValidationError
from django.db import transaction
from .models import (
   Connection,
   CoverageNode,
   Technician,
)

def _normalize_code(value: str) -> str:
   """
   Normalize entity identifiers before validation.
   Examples:
       " base-norte " -> "BASE-NORTE"
       "tec-001"      -> "TEC-001"
   """
   return value.strip().upper()

def _normalize_name(value: str) -> str:
   """
   Remove unnecessary whitespace from names.
   """
   return " ".join(value.split())

def _get_node(
   *,
   node_id: int,
   field_name: str,
) -> CoverageNode:
   """
   Retrieve a coverage node and provide a business-friendly
   validation error when it does not exist.
   """
   try:
       return CoverageNode.objects.get(
           pk=node_id,
       )
   except CoverageNode.DoesNotExist as exc:
       raise ValidationError(
           {
               field_name: (
                   f"Coverage node with id {node_id} does not exist."
               )
           }
       ) from exc

@transaction.atomic
def node_create(
   *,
   code: str,
   name: str,
   node_type: str,
) -> CoverageNode:
   """
   Create a BASE or ZONE node in the coverage network.
   Model validation is executed before saving so identifiers,
   choices and uniqueness rules are enforced consistently.
   """
   node = CoverageNode(
       code=_normalize_code(code),
       name=_normalize_name(name),
       type=node_type.strip().upper(),
   )
   node.full_clean()
   node.save()
   return node

@transaction.atomic
def technician_create(
   *,
   code: str,
   name: str,
   base_id: int,
   is_available: bool = True,
) -> Technician:
   """
   Create a technician associated with an operational base.
   Technicians are resources and are not nodes in the graph.
   """
   base = _get_node(
       node_id=base_id,
       field_name="base",
   )
   technician = Technician(
       code=_normalize_code(code),
       name=_normalize_name(name),
       base=base,
       is_available=is_available,
   )
   technician.full_clean()
   technician.save()
   return technician

@transaction.atomic
def connection_create(
   *,
   origin_id: int,
   destination_id: int,
   estimated_minutes: int,
   is_bidirectional: bool = False,
) -> Connection:
   """
   Create an edge between two coverage nodes.
   `estimated_minutes` represents the graph weight.
   A unidirectional connection represents:
       origin -> destination
   A bidirectional connection represents:
       origin <-> destination
   Model validation is responsible for enforcing:
   - different origin and destination;
   - positive weights;
   - duplicate prevention;
   - bidirectional consistency.
   """
   origin = _get_node(
       node_id=origin_id,
       field_name="origin",
   )
   destination = _get_node(
       node_id=destination_id,
       field_name="destination",
   )
   connection = Connection(
       origin=origin,
       destination=destination,
       estimated_minutes=estimated_minutes,
       is_bidirectional=is_bidirectional,
   )
   connection.full_clean()
   connection.save()
   return connection