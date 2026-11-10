from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.coverage.exceptions import NodeNotFoundError
from apps.coverage.services import (
    node_create,
    connection_create,
)
from apps.coverage.shortest_route import calculate_shortest_route


class ShortestRouteTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.base = node_create(
            code="BASE-F3-NORTE",
            name="Base Norte",
            node_type="BASE",
        )

        cls.other_base = node_create(
            code="BASE-F3-SUR",
            name="Base Sur",
            node_type="BASE",
        )

        cls.zone_a = node_create(
            code="ZONE-F3-A",
            name="Laureles",
            node_type="ZONE",
        )

        cls.zone_b = node_create(
            code="ZONE-F3-B",
            name="Estadio",
            node_type="ZONE",
        )

        cls.target = node_create(
            code="ZONE-F3-TARGET",
            name="Belén",
            node_type="ZONE",
        )

        cls.isolated = node_create(
            code="ZONE-F3-ISOLATED",
            name="Zona Aislada",
            node_type="ZONE",
        )

        cls.reverse_zone = node_create(
            code="ZONE-F3-REVERSE",
            name="Zona Reversa",
            node_type="ZONE",
        )

        cls.bidirectional_zone = node_create(
            code="ZONE-F3-BIDIRECTIONAL",
            name="Zona Bidireccional",
            node_type="ZONE",
        )

        # Direct route: 30 minutes.
        connection_create(
            origin_id=cls.base.id,
            destination_id=cls.target.id,
            estimated_minutes=30,
        )

        # Alternative route: 5 + 7 + 8 = 20 minutes (cheaper).
        connection_create(
            origin_id=cls.base.id,
            destination_id=cls.zone_a.id,
            estimated_minutes=5,
        )

        connection_create(
            origin_id=cls.zone_a.id,
            destination_id=cls.zone_b.id,
            estimated_minutes=7,
        )

        connection_create(
            origin_id=cls.zone_b.id,
            destination_id=cls.target.id,
            estimated_minutes=8,
        )

        # One-way from target to reverse_zone (not from base).
        connection_create(
            origin_id=cls.target.id,
            destination_id=cls.reverse_zone.id,
            estimated_minutes=10,
        )

        # Bidirectional connection from other_base to bidirectional_zone.
        connection_create(
            origin_id=cls.other_base.id,
            destination_id=cls.bidirectional_zone.id,
            estimated_minutes=15,
            is_bidirectional=True,
        )

    # ------------------------------------------------------------------
    # Happy-path tests
    # ------------------------------------------------------------------

    def test_prefers_less_time_over_fewer_hops(self):
        """
        Dijkstra must prefer the 20-minute path (3 hops)
        over the 30-minute direct connection (1 hop).
        """
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["total_minutes"], 20)
        self.assertEqual(
            [node["code"] for node in result["path"]],
            [
                "BASE-F3-NORTE",
                "ZONE-F3-A",
                "ZONE-F3-B",
                "ZONE-F3-TARGET",
            ],
        )

    def test_result_contains_required_keys(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        expected_keys = {
            "mode",
            "reachable",
            "origin",
            "destination",
            "path",
            "segments",
            "total_minutes",
            "traversal_order",
            "visited_count",
            "message",
        }

        self.assertEqual(set(result.keys()), expected_keys)

    def test_mode_is_shortest_route(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertEqual(result["mode"], "shortest_route")

    def test_origin_serialization(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertEqual(result["origin"]["code"], "BASE-F3-NORTE")
        self.assertEqual(result["origin"]["type"], "BASE")
        self.assertIn("id", result["origin"])
        self.assertIn("name", result["origin"])

    def test_destination_serialization(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertEqual(result["destination"]["code"], "ZONE-F3-TARGET")
        self.assertEqual(result["destination"]["type"], "ZONE")

    def test_segments_describe_each_connection(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        segments = result["segments"]

        # 3 hops → 3 segments
        self.assertEqual(len(segments), 3)

        self.assertEqual(segments[0]["origin"]["code"], "BASE-F3-NORTE")
        self.assertEqual(segments[0]["destination"]["code"], "ZONE-F3-A")
        self.assertEqual(segments[0]["estimated_minutes"], 5)

        self.assertEqual(segments[1]["origin"]["code"], "ZONE-F3-A")
        self.assertEqual(segments[1]["destination"]["code"], "ZONE-F3-B")
        self.assertEqual(segments[1]["estimated_minutes"], 7)

        self.assertEqual(segments[2]["origin"]["code"], "ZONE-F3-B")
        self.assertEqual(segments[2]["destination"]["code"], "ZONE-F3-TARGET")
        self.assertEqual(segments[2]["estimated_minutes"], 8)

    def test_segments_total_matches_total_minutes(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        segment_total = sum(
            seg["estimated_minutes"] for seg in result["segments"]
        )

        self.assertEqual(segment_total, result["total_minutes"])

    def test_traversal_order_contains_settled_nodes(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        traversal_codes = [
            node["code"] for node in result["traversal_order"]
        ]

        # Origin must be first settled node
        self.assertEqual(traversal_codes[0], "BASE-F3-NORTE")

        # Target must appear in traversal
        self.assertIn("ZONE-F3-TARGET", traversal_codes)

    def test_visited_count_matches_traversal_order_length(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertEqual(
            result["visited_count"],
            len(result["traversal_order"]),
        )

    def test_message_contains_total_minutes_when_reachable(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertIn("20", result["message"])
        self.assertIn("minuto", result["message"])

    # ------------------------------------------------------------------
    # Unreachable destination
    # ------------------------------------------------------------------

    def test_unreachable_zone_returns_reachable_false(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.isolated.id,
        )

        self.assertFalse(result["reachable"])

    def test_unreachable_zone_returns_empty_path(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.isolated.id,
        )

        self.assertEqual(result["path"], [])

    def test_unreachable_zone_returns_empty_segments(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.isolated.id,
        )

        self.assertEqual(result["segments"], [])

    def test_unreachable_zone_returns_none_total_minutes(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.isolated.id,
        )

        self.assertIsNone(result["total_minutes"])

    def test_unreachable_message_mentions_no_route(self):
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.isolated.id,
        )

        self.assertIn("No existe", result["message"])

    # ------------------------------------------------------------------
    # Directionality
    # ------------------------------------------------------------------

    def test_one_way_link_cannot_be_traversed_in_reverse(self):
        """
        Una conexión ZONE -> BASE no debe permitir
        desplazarse desde BASE hacia ZONE.
        """
    
        connection_create(
            origin_id=self.reverse_zone.id,
            destination_id=self.other_base.id,
            estimated_minutes=4,
            is_bidirectional=False,
        )
    
        result = calculate_shortest_route(
            origin_id=self.other_base.id,
            destination_id=self.reverse_zone.id,
        )
    
        self.assertFalse(result["reachable"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["total_minutes"])

    def test_bidirectional_connection_allows_both_directions(self):
        """
        other_base <-> bidirectional_zone, so both directions work.
        """
        result = calculate_shortest_route(
            origin_id=self.other_base.id,
            destination_id=self.bidirectional_zone.id,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["total_minutes"], 15)

    # ------------------------------------------------------------------
    # Validation errors
    # ------------------------------------------------------------------

    def test_missing_origin_raises_node_not_found(self):
        with self.assertRaises(NodeNotFoundError):
            calculate_shortest_route(
                origin_id=999999,
                destination_id=self.target.id,
            )

    def test_missing_destination_raises_node_not_found(self):
        with self.assertRaises(NodeNotFoundError):
            calculate_shortest_route(
                origin_id=self.base.id,
                destination_id=999999,
            )

    def test_origin_must_be_base(self):
        with self.assertRaises(ValidationError):
            calculate_shortest_route(
                origin_id=self.zone_a.id,
                destination_id=self.target.id,
            )

    def test_destination_must_be_zone(self):
        with self.assertRaises(ValidationError):
            calculate_shortest_route(
                origin_id=self.base.id,
                destination_id=self.other_base.id,
            )

    # ------------------------------------------------------------------
    # Weight independence
    # ------------------------------------------------------------------

    def test_estimated_minutes_not_in_top_level_response(self):
        """estimated_minutes must only appear inside segments, not at top level."""
        result = calculate_shortest_route(
            origin_id=self.base.id,
            destination_id=self.target.id,
        )

        self.assertNotIn("estimated_minutes", result)
