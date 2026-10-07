"""HTTP views / controllers for the ServicioCerca API.

This module exposes endpoints that receive HTTP requests, delegate work to
services/selectors, and return JSON responses.
"""
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import status
from rest_framework.exceptions import ValidationError as DRFValidationError
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
 
 
class CoverageNodeListCreateAPIView(APIView):
 
    def get(self, request):
        nodes = node_list()
 
        serializer = CoverageNodeSerializer(
            nodes,
            many=True,
        )
 
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request):
        input_serializer = CoverageNodeCreateSerializer(
            data=request.data,
        )
 
        input_serializer.is_valid(
            raise_exception=True,
        )
 
        data = input_serializer.validated_data
 
        try:
            node = node_create(
                code=data["code"],
                name=data["name"],
                node_type=data["type"],
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)
 
        output_serializer = CoverageNodeSerializer(
            node
        )
 
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
 
 
class TechnicianListCreateAPIView(APIView):
 
    def get(self, request):
        technicians = technician_list()
 
        serializer = TechnicianSerializer(
            technicians,
            many=True,
        )
 
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request):
        input_serializer = TechnicianCreateSerializer(
            data=request.data,
        )
 
        input_serializer.is_valid(
            raise_exception=True,
        )
 
        data = input_serializer.validated_data
 
        try:
            technician = technician_create(
                code=data["code"],
                name=data["name"],
                base_id=data["base_id"],
                is_available=data["is_available"],
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)
 
        output_serializer = TechnicianSerializer(
            technician
        )
 
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
 
 
class ConnectionListCreateAPIView(APIView):
 
    def get(self, request):
        connections = connection_list()
 
        serializer = ConnectionSerializer(
            connections,
            many=True,
        )
 
        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
 
    def post(self, request):
        input_serializer = ConnectionCreateSerializer(
            data=request.data,
        )
 
        input_serializer.is_valid(
            raise_exception=True,
        )
 
        data = input_serializer.validated_data
 
        try:
            connection = connection_create(
                origin_id=data["origin_id"],
                destination_id=data["destination_id"],
                estimated_minutes=data["estimated_minutes"],
                is_bidirectional=data["is_bidirectional"],
            )
        except DjangoValidationError as exc:
            _raise_drf_validation_error(exc)
 
        output_serializer = ConnectionSerializer(
            connection
        )
 
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )
 
 
class CoverageNetworkAPIView(APIView):
 
    def get(self, request):
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