"""Domain-specific exceptions for the coverage module.

These exceptions inherit from Django's ValidationError so they can be
raised from services and models and still be handled by the existing
validation infrastructure. They add semantic meaning for clearer error
handling in views and tests.
"""

from django.core.exceptions import ValidationError


class CoverageError(ValidationError):
    """Base class for all coverage domain errors."""


class NodeNotFoundError(CoverageError):
    """Raised when a referenced coverage node does not exist."""

    def __init__(self, node_id: int, field_name: str = "node"):
        super().__init__(
            {
                field_name: (
                    f"No existe un nodo de cobertura con id {node_id}."
                )
            }
        )


class InvalidNodeTypeError(CoverageError):
    """Raised when a node is used in a context that requires a different type."""

    def __init__(self, field_name: str = "base"):
        super().__init__(
            {
                field_name: (
                    "Un técnico solo puede asignarse a un nodo de tipo BASE."
                )
            }
        )


class SelfConnectionError(CoverageError):
    """Raised when a connection references the same node as both ends."""

    def __init__(self):
        super().__init__(
            {
                "destination": (
                    "El origen y el destino deben ser diferentes."
                )
            }
        )


class InvalidConnectionWeightError(CoverageError):
    """Raised when a connection weight is not strictly positive."""

    def __init__(self):
        super().__init__(
            {
                "estimated_minutes": (
                    "Los minutos estimados deben ser mayores a cero."
                )
            }
        )


class DuplicateConnectionError(CoverageError):
    """Raised when a connection would duplicate an existing one."""

    def __init__(self):
        super().__init__(
            {
                "destination": (
                    "Ya existe una conexión en esa dirección."
                )
            }
        )


class BidirectionalConflictError(CoverageError):
    """Raised when a connection conflicts with an existing bidirectional link."""

    def __init__(self):
        super().__init__(
            {
                "destination": (
                    "Ya existe una conexión equivalente. "
                    "Una conexión bidireccional representa ambas direcciones."
                )
            }
        )
