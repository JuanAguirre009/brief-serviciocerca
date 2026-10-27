from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.coverage.exceptions import NodeNotFoundError
from apps.coverage.reachability import (
    check_coverage,
    list_reachable_nodes,
)
from apps.coverage.services import (
    connection_create,
    node_create,
)


class CoverageReachabilityTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.base_north = node_create(
            code="BASE-NORTE",
            name="Base Norte",
            node_type="BASE",
        )

        cls.base_south = node_create(
            code="BASE-SUR",
            name="Base Sur",
            node_type="BASE",
        )

        cls.zone_laureles = node_create(
            code="ZONA-LAURELES",
            name="Laureles",
            node_type="ZONE",
        )

        cls.zone_estadio = node_create(
            code="ZONA-ESTADIO",
            name="Estadio",
            node_type="ZONE",
        )

        cls.zone_belen = node_create(
            code="ZONA-BELEN",
            name="Belén",
            node_type="ZONE",
        )

        cls.zone_isolated = node_create(
            code="ZONA-AISLADA",
            name="Zona Aislada",
            node_type="ZONE",
        )

        connection_create(
            origin_id=cls.base_north.id,
            destination_id=cls.zone_laureles.id,
            estimated_minutes=15,
            is_bidirectional=False,
        )

        connection_create(
            origin_id=cls.zone_laureles.id,
            destination_id=cls.zone_estadio.id,
            estimated_minutes=8,
            is_bidirectional=False,
        )

        connection_create(
            origin_id=cls.zone_estadio.id,
            destination_id=cls.zone_belen.id,
            estimated_minutes=12,
            is_bidirectional=False,
        )

        connection_create(
            origin_id=cls.zone_belen.id,
            destination_id=cls.base_south.id,
            estimated_minutes=20,
            is_bidirectional=False,
        )

    def test_check_coverage_returns_true_when_path_exists(self):
        result = check_coverage(
            origin_id=self.base_north.id,
            destination_id=self.zone_belen.id,
        )

        self.assertTrue(
            result["covered"]
        )

        self.assertEqual(
            result["origin"]["code"],
            "BASE-NORTE",
        )

        self.assertEqual(
            result["destination"]["code"],
            "ZONA-BELEN",
        )

        self.assertEqual(
            [
                node["code"]
                for node in result["path"]
            ],
            [
                "BASE-NORTE",
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
                "ZONA-BELEN",
            ],
        )

    def test_check_coverage_returns_false_for_disconnected_zone(self):
        result = check_coverage(
            origin_id=self.base_north.id,
            destination_id=self.zone_isolated.id,
        )

        self.assertFalse(
            result["covered"]
        )

        self.assertEqual(
            result["path"],
            [],
        )

        self.assertIn(
            "no es alcanzable",
            result["message"],
        )

    def test_check_coverage_respects_directionality(self):
        result = check_coverage(
            origin_id=self.base_south.id,
            destination_id=self.zone_belen.id,
        )

        self.assertFalse(
            result["covered"]
        )

        self.assertEqual(
            result["path"],
            [],
        )

    def test_check_coverage_returns_bfs_trace(self):
        result = check_coverage(
            origin_id=self.base_north.id,
            destination_id=self.zone_belen.id,
        )

        trace_codes = [
            node["code"]
            for node in result["traversal_order"]
        ]

        self.assertEqual(
            trace_codes,
            [
                "BASE-NORTE",
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
                "ZONA-BELEN",
            ],
        )

    def test_list_reachable_nodes_returns_service_zones(self):
        result = list_reachable_nodes(
            origin_id=self.base_north.id,
        )

        zone_codes = [
            node["code"]
            for node in result["reachable_nodes"]
        ]

        self.assertEqual(
            zone_codes,
            [
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
                "ZONA-BELEN",
            ],
        )

        self.assertEqual(
            result["reachable_count"],
            3,
        )

    def test_list_reachable_nodes_for_isolated_base(self):
        isolated_base = node_create(
            code="BASE-AISLADA",
            name="Base Aislada",
            node_type="BASE",
        )

        result = list_reachable_nodes(
            origin_id=isolated_base.id,
        )

        self.assertEqual(
            result["reachable_count"],
            0,
        )

        self.assertEqual(
            result["reachable_nodes"],
            [],
        )

        self.assertEqual(
            [
                node["code"]
                for node in result["traversal_order"]
            ],
            [
                "BASE-AISLADA",
            ],
        )

    def test_missing_origin_raises_node_not_found(self):
        with self.assertRaises(
            NodeNotFoundError
        ):
            check_coverage(
                origin_id=999999,
                destination_id=self.zone_belen.id,
            )

    def test_missing_destination_raises_node_not_found(self):
        with self.assertRaises(
            NodeNotFoundError
        ):
            check_coverage(
                origin_id=self.base_north.id,
                destination_id=999999,
            )

    def test_origin_must_be_base(self):
        with self.assertRaises(
            ValidationError
        ):
            check_coverage(
                origin_id=self.zone_laureles.id,
                destination_id=self.zone_belen.id,
            )

    def test_destination_must_be_zone(self):
        with self.assertRaises(
            ValidationError
        ):
            check_coverage(
                origin_id=self.base_north.id,
                destination_id=self.base_south.id,
            )

    def test_reachable_nodes_does_not_include_bases(self):
        result = list_reachable_nodes(
            origin_id=self.base_north.id,
        )

        self.assertTrue(
            all(
                node["type"] == "ZONE"
                for node in result["reachable_nodes"]
            )
        )

    def test_connection_weight_does_not_change_coverage(self):
        result = check_coverage(
            origin_id=self.base_north.id,
            destination_id=self.zone_laureles.id,
        )

        self.assertTrue(
            result["covered"]
        )

        self.assertNotIn(
            "estimated_minutes",
            result,
        )

    def test_check_coverage_respects_bidirectional_connection(self):
        connection_create(
            origin_id=self.zone_isolated.id,
            destination_id=self.base_south.id,
            estimated_minutes=10,
            is_bidirectional=True,
        )

        result = check_coverage(
            origin_id=self.base_south.id,
            destination_id=self.zone_isolated.id,
        )

        self.assertTrue(
            result["covered"]
        )

        self.assertEqual(
            [
                node["code"]
                for node in result["path"]
            ],
            [
                "BASE-SUR",
                "ZONA-AISLADA",
            ],
        )
        
    def test_list_reachable_nodes_respects_incoming_direction(self):
        result = list_reachable_nodes(
            origin_id=self.base_south.id,
        )

        self.assertEqual(
            result["reachable_count"],
            0,
        )

        self.assertEqual(
            result["reachable_nodes"],
            [],
        )
    
    def test_list_reachable_nodes_missing_origin(self):
        with self.assertRaises(
            NodeNotFoundError
        ):
            list_reachable_nodes(
                origin_id=999999,
            )