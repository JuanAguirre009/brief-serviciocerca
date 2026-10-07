from rest_framework import serializers
 
from .models import (
    Connection,
    CoverageNode,
    Technician,
)
class CoverageNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoverageNode
        fields = (
            "id",
            "code",
            "name",
            "type",
            "created_at",
            "updated_at",
        )
 
 
class TechnicianSerializer(serializers.ModelSerializer):
    base = CoverageNodeSerializer(
        read_only=True,
    )
 
    class Meta:
        model = Technician
        fields = (
            "id",
            "code",
            "name",
            "base",
            "is_available",
            "created_at",
            "updated_at",
        )
 
 
class ConnectionSerializer(serializers.ModelSerializer):
    origin = CoverageNodeSerializer(
        read_only=True,
    )
 
    destination = CoverageNodeSerializer(
        read_only=True,
    )
 
    class Meta:
        model = Connection
        fields = (
            "id",
            "origin",
            "destination",
            "estimated_minutes",
            "is_bidirectional",
            "created_at",
            "updated_at",
        )

class CoverageNodeCreateSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=50,
    )
 
    name = serializers.CharField(
        max_length=150,
    )
 
    type = serializers.ChoiceField(
        choices=CoverageNode.NodeType.choices,
    )
 
 
class TechnicianCreateSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=50,
    )
 
    name = serializers.CharField(
        max_length=150,
    )
 
    base_id = serializers.IntegerField()
 
    is_available = serializers.BooleanField(
        default=True,
    )
 
 
class ConnectionCreateSerializer(serializers.Serializer):
    origin_id = serializers.IntegerField()
 
    destination_id = serializers.IntegerField()
 
    estimated_minutes = serializers.IntegerField(
        min_value=1,
    )
 
    is_bidirectional = serializers.BooleanField(
        default=False,
    )