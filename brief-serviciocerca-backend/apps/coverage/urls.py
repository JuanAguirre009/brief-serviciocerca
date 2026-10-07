from django.urls import path

from .views import (
    ConnectionListCreateAPIView,
    CoverageNetworkAPIView,
    CoverageNodeListCreateAPIView,
    TechnicianListCreateAPIView,
)


app_name = "coverage"


urlpatterns = [
    path(
        "nodes/",
        CoverageNodeListCreateAPIView.as_view(),
        name="node-list-create",
    ),
    path(
        "technicians/",
        TechnicianListCreateAPIView.as_view(),
        name="technician-list-create",
    ),
    path(
        "connections/",
        ConnectionListCreateAPIView.as_view(),
        name="connection-list-create",
    ),
    path(
        "network/",
        CoverageNetworkAPIView.as_view(),
        name="network",
    ),
]