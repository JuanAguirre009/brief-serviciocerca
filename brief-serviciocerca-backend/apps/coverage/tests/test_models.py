from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from apps.coverage.models import (
    Connection,
    CoverageNode,
    Technician,
)


class CoverageNodeTests(TestCase):

    def test_create_base_node(self):
        node = CoverageNode.objects.create(
            code="BASE-NORTE",
            name="Base Norte",
            type=CoverageNode.NodeType.BASE,
        )

        self.assertEqual(
            node.type,
            CoverageNode.NodeType.BASE,
        )

    def test_create_zone_node(self):
        node = CoverageNode.objects.create(
            code="ZONA-001",
            name="Laureles",
            type=CoverageNode.NodeType.ZONE,
        )

        self.assertEqual(
            node.type,
            CoverageNode.NodeType.ZONE,
        )

    def test_reject_invalid_identifier(self):
        node = CoverageNode(
            code="base norte!",
            name="Base Norte",
            type=CoverageNode.NodeType.BASE,
        )

        with self.assertRaises(ValidationError):
            node.full_clean()

    def test_reject_duplicate_node_code(self):
        CoverageNode.objects.create(
            code="BASE-NORTE",
            name="Base Norte",
            type=CoverageNode.NodeType.BASE,
        )

        duplicate = CoverageNode(
            code="BASE-NORTE",
            name="Otra Base",
            type=CoverageNode.NodeType.BASE,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()


class TechnicianTests(TestCase):

    def setUp(self):
        self.base = CoverageNode.objects.create(
            code="BASE-NORTE",
            name="Base Norte",
            type=CoverageNode.NodeType.BASE,
        )

        self.zone = CoverageNode.objects.create(
            code="ZONA-001",
            name="Laureles",
            type=CoverageNode.NodeType.ZONE,
        )

    def test_create_technician_assigned_to_base(self):
        technician = Technician(
            code="TEC-001",
            name="Carlos Pérez",
            base=self.base,
        )

        technician.full_clean()
        technician.save()

        self.assertEqual(
            technician.base,
            self.base,
        )

    def test_reject_technician_assigned_to_zone(self):
        technician = Technician(
            code="TEC-001",
            name="Carlos Pérez",
            base=self.zone,
        )

        with self.assertRaises(ValidationError):
            technician.full_clean()


class ConnectionTests(TestCase):

    def setUp(self):
        self.base = CoverageNode.objects.create(
            code="BASE-NORTE",
            name="Base Norte",
            type=CoverageNode.NodeType.BASE,
        )

        self.zone_1 = CoverageNode.objects.create(
            code="ZONA-001",
            name="Laureles",
            type=CoverageNode.NodeType.ZONE,
        )

        self.zone_2 = CoverageNode.objects.create(
            code="ZONA-002",
            name="Belén",
            type=CoverageNode.NodeType.ZONE,
        )

    def test_create_valid_connection(self):
        connection = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=15,
        )

        connection.full_clean()
        connection.save()

        self.assertEqual(
            connection.estimated_minutes,
            15,
        )

    def test_create_bidirectional_connection(self):
        connection = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=15,
            is_bidirectional=True,
        )

        connection.full_clean()
        connection.save()

        self.assertTrue(
            connection.is_bidirectional
        )

    def test_reject_zero_weight(self):
        connection = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=0,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_reject_negative_weight(self):
        connection = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=-5,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_reject_same_origin_and_destination(self):
        connection = Connection(
            origin=self.base,
            destination=self.base,
            estimated_minutes=10,
        )

        with self.assertRaises(ValidationError):
            connection.full_clean()

    def test_reject_duplicate_connection(self):
        Connection.objects.create(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=10,
        )

        duplicate = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=20,
        )

        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_reject_reverse_when_existing_connection_is_bidirectional(
        self,
    ):
        Connection.objects.create(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=10,
            is_bidirectional=True,
        )

        reverse = Connection(
            origin=self.zone_1,
            destination=self.base,
            estimated_minutes=10,
        )

        with self.assertRaises(ValidationError):
            reverse.full_clean()

    def test_allow_two_unidirectional_connections(self):
        first = Connection(
            origin=self.base,
            destination=self.zone_1,
            estimated_minutes=10,
            is_bidirectional=False,
        )

        first.full_clean()
        first.save()

        reverse = Connection(
            origin=self.zone_1,
            destination=self.base,
            estimated_minutes=15,
            is_bidirectional=False,
        )

        reverse.full_clean()
        reverse.save()

        self.assertEqual(
            Connection.objects.count(),
            2,
        )