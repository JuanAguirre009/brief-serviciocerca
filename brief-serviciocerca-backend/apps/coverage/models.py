from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q

from .validators import (
    validate_identifier,
    validate_positive_weight,
)


class CoverageNode(models.Model):
    """
    Represents a geographical/operational node in the coverage graph.

    A node can represent:
    - BASE: operational base from which technicians operate.
    - ZONE: service zone that may be reached through the network.
    """

    class NodeType(models.TextChoices):
        BASE = "BASE", "Base"
        ZONE = "ZONE", "Zona"

    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_identifier],
    )

    name = models.CharField(
        max_length=150,
    )

    type = models.CharField(
        max_length=10,
        choices=NodeType.choices,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "nodo de cobertura"
        verbose_name_plural = "nodos de cobertura"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Technician(models.Model):
    """
    Represents a technician available from an operational base.

    Technicians are NOT graph nodes.

    They are resources associated with BASE nodes.
    """

    code = models.CharField(
        max_length=50,
        unique=True,
        validators=[validate_identifier],
    )

    name = models.CharField(
        max_length=150,
    )

    base = models.ForeignKey(
        CoverageNode,
        on_delete=models.PROTECT,
        related_name="technicians",
    )

    is_available = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "técnico"
        verbose_name_plural = "técnicos"

    def clean(self):
        super().clean()

        if (
            self.base_id
            and self.base.type != CoverageNode.NodeType.BASE
        ):
            raise ValidationError(
                {
                    "base": (
                        "Un técnico solo puede asignarse a un nodo de tipo BASE."
                    )
                }
            )

    def __str__(self):
        return f"{self.code} - {self.name}"


class Connection(models.Model):
    """
    Represents an edge in the coverage graph.

    `origin` and `destination` define the direction.

    If `is_bidirectional` is True, the connection is considered
    traversable in both directions.

    `estimated_minutes` is the graph weight.
    """

    origin = models.ForeignKey(
        CoverageNode,
        on_delete=models.CASCADE,
        related_name="outgoing_connections",
        verbose_name="origen",
    )

    destination = models.ForeignKey(
        CoverageNode,
        on_delete=models.CASCADE,
        related_name="incoming_connections",
        verbose_name="destino",
    )

    estimated_minutes = models.PositiveIntegerField(
        validators=[validate_positive_weight],
        verbose_name="minutos estimados",
    )

    is_bidirectional = models.BooleanField(
        default=False,
        verbose_name="es bidireccional",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "origin__code",
            "destination__code",
        ]
        verbose_name = "conexión"
        verbose_name_plural = "conexiones"

        constraints = [
            models.CheckConstraint(
                condition=~Q(origin=F("destination")),
                name="coverage_connection_different_nodes",
                violation_error_message=(
                    "El origen y el destino deben ser diferentes."
                ),
            ),
            models.CheckConstraint(
                condition=Q(estimated_minutes__gt=0),
                name="coverage_connection_positive_weight",
                violation_error_message=(
                    "Los minutos estimados deben ser mayores a cero."
                ),
            ),
            models.UniqueConstraint(
                fields=[
                    "origin",
                    "destination",
                ],
                name="coverage_connection_unique_direction",
                violation_error_message=(
                    "Ya existe una conexión en esa dirección."
                ),
            ),
        ]

    def clean(self):
        super().clean()

        if (
            self.origin_id
            and self.destination_id
            and self.origin_id == self.destination_id
        ):
            raise ValidationError(
                {
                    "destination": (
                        "El origen y el destino deben ser diferentes."
                    )
                }
            )

        if (
            self.estimated_minutes is not None
            and self.estimated_minutes <= 0
        ):
            raise ValidationError(
                {
                    "estimated_minutes": (
                        "Los minutos estimados deben ser mayores a cero."
                    )
                }
            )

        if not (
            self.origin_id
            and self.destination_id
        ):
            return

        reverse_connection = Connection.objects.filter(
            origin=self.destination,
            destination=self.origin,
        )

        if self.pk:
            reverse_connection = reverse_connection.exclude(
                pk=self.pk
            )

        if (
            self.is_bidirectional
            and reverse_connection.exists()
        ):
            raise ValidationError(
                {
                    "destination": (
                        "Ya existe una conexión en sentido inverso. "
                        "Una conexión bidireccional ya representa ambas direcciones."
                    )
                }
            )

        reverse_bidirectional = reverse_connection.filter(
            is_bidirectional=True
        )

        if reverse_bidirectional.exists():
            raise ValidationError(
                {
                    "destination": (
                        "La conexión inversa ya es bidireccional, "
                        "por lo que ya representa esta dirección."
                    )
                }
            )

    def __str__(self):
        direction = (
            "↔"
            if self.is_bidirectional
            else "→"
        )

        return (
            f"{self.origin.code} "
            f"{direction} "
            f"{self.destination.code} "
            f"({self.estimated_minutes} min)"
        )
