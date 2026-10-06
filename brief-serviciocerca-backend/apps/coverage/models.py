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
        ZONE = "ZONE", "Zone"

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
        verbose_name = "Coverage node"
        verbose_name_plural = "Coverage nodes"

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

    def clean(self):
        super().clean()

        if (
            self.base_id
            and self.base.type != CoverageNode.NodeType.BASE
        ):
            raise ValidationError(
                {
                    "base": (
                        "A technician can only be assigned "
                        "to a BASE node."
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
    )

    destination = models.ForeignKey(
        CoverageNode,
        on_delete=models.CASCADE,
        related_name="incoming_connections",
    )

    estimated_minutes = models.PositiveIntegerField(
        validators=[validate_positive_weight],
    )

    is_bidirectional = models.BooleanField(
        default=False,
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

        constraints = [
            models.CheckConstraint(
                condition=~Q(origin=F("destination")),
                name="coverage_connection_different_nodes",
            ),
            models.CheckConstraint(
                condition=Q(estimated_minutes__gt=0),
                name="coverage_connection_positive_weight",
            ),
            models.UniqueConstraint(
                fields=[
                    "origin",
                    "destination",
                ],
                name="coverage_connection_unique_direction",
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
                        "Origin and destination must be different."
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
                        "Estimated minutes must be greater than zero."
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
                        "A reverse connection already exists. "
                        "A bidirectional connection already "
                        "represents both directions."
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
                        "The reverse connection is already "
                        "bidirectional and therefore already "
                        "represents this direction."
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