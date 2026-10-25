"""HTTP views / controllers for the ServicioCerca API.

This module exposes endpoints that receive HTTP requests, delegate work to
services/selectors, and return JSON responses.
"""
from typing import Callable

from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .selectors import (
    connection_list,
    network_get,
    node_list,
    technician_list,
)
from .serializers import (
    ConnectionCreateSerializer,
    ConnectionSerializer,
    CoverageNodeCreateSerializer,
    CoverageNodeSerializer,
    TechnicianCreateSerializer,
    TechnicianSerializer,
)
from .services import (
    connection_create,
    node_create,
    technician_create,
)


def _raise_drf_validation_error(
    exc: DjangoValidationError,
) -> None:
    """
    Translate Django/domain validation errors into
    HTTP-friendly DRF validation responses.
    """

    if hasattr(exc, "message_dict"):
        raise DRFValidationError(
            exc.message_dict
        ) from exc

    raise DRFValidationError(
        exc.messages
    ) from exc


class CreateResourceMixin:
    """
    Mixin for list/create API views.

    Reduces repetition by encapsulating the common pattern:
    validate input -> call service -> serialize output.
    """

    input_serializer_class: type
    output_serializer_class: type
    create_service: Callable
    success_status: int = status.HTTP_201_CREATED

    def perform_create(self, validated_data: dict):
        """Delegate creation to the configured service."""
        return self.create_service(**validated_data)

    def create(self, request: Request):
        input_serializer = self.input_serializer_class(
            data=request.data,
        )

        input_serializer.is_valid(
            raise_exception=True,
        )

        try:
            instance = self.perform_create(
                input_serializer.validated_data,
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)

        output_serializer = self.output_serializer_class(
            instance,
        )

        return Response(
            output_serializer.data,
            status=self.success_status,
        )


class CoverageNodeListCreateAPIView(CreateResourceMixin, APIView):

    input_serializer_class = CoverageNodeCreateSerializer
    output_serializer_class = CoverageNodeSerializer
    create_service = staticmethod(node_create)

    def perform_create(self, validated_data: dict):
        return self.create_service(
            code=validated_data["code"],
            name=validated_data["name"],
            node_type=validated_data["type"],
        )

    def get(self, request: Request):
        node_type = request.query_params.get("node_type")
        nodes = node_list(
            node_type=node_type,
        )

        serializer = CoverageNodeSerializer(
            nodes,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request):
        return self.create(request)


class TechnicianListCreateAPIView(CreateResourceMixin, APIView):

    input_serializer_class = TechnicianCreateSerializer
    output_serializer_class = TechnicianSerializer
    create_service = staticmethod(technician_create)

    def perform_create(self, validated_data: dict):
        return self.create_service(
            code=validated_data["code"],
            name=validated_data["name"],
            base_id=validated_data["base_id"],
            is_available=validated_data["is_available"],
        )

    def get(self, request: Request):
        base_id = request.query_params.get("base_id")
        is_available = request.query_params.get("is_available")

        filters = {}
        if base_id is not None:
            filters["base_id"] = int(base_id)
        if is_available is not None:
            filters["is_available"] = is_available.lower() in ("true", "1", "yes")

        technicians = technician_list(
            **filters,
        )

        serializer = TechnicianSerializer(
            technicians,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request):
        return self.create(request)


class ConnectionListCreateAPIView(CreateResourceMixin, APIView):

    input_serializer_class = ConnectionCreateSerializer
    output_serializer_class = ConnectionSerializer
    create_service = staticmethod(connection_create)

    def perform_create(self, validated_data: dict):
        return self.create_service(
            origin_id=validated_data["origin_id"],
            destination_id=validated_data["destination_id"],
            estimated_minutes=validated_data["estimated_minutes"],
            is_bidirectional=validated_data["is_bidirectional"],
        )

    def get(self, request: Request):
        connections = connection_list()

        serializer = ConnectionSerializer(
            connections,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def post(self, request: Request):
        return self.create(request)


class CoverageNetworkAPIView(APIView):

    def get(self, request: Request):
        network = network_get()

        return Response(
            {
                "nodes": CoverageNodeSerializer(
                    network["nodes"],
                    many=True,
                ).data,
                "technicians": TechnicianSerializer(
                    network["technicians"],
                    many=True,
                ).data,
                "connections": ConnectionSerializer(
                    network["connections"],
                    many=True,
                ).data,
            },
            status=status.HTTP_200_OK,
        )
