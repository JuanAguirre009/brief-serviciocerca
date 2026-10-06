from django.contrib import admin

from .models import (
    Connection,
    CoverageNode,
    Technician,
)


@admin.register(CoverageNode)
class CoverageNodeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "type",
        "created_at",
    )

    list_filter = (
        "type",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = (
        "code",
    )


@admin.register(Technician)
class TechnicianAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "base",
        "is_available",
    )

    list_filter = (
        "is_available",
        "base",
    )

    search_fields = (
        "code",
        "name",
    )


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = (
        "origin",
        "destination",
        "estimated_minutes",
        "is_bidirectional",
    )

    list_filter = (
        "is_bidirectional",
    )

    search_fields = (
        "origin__code",
        "origin__name",
        "destination__code",
        "destination__name",
    )