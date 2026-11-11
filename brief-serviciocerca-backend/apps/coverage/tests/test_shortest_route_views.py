"""HTTP contract and regression tests for Feature 3 shortest-route API."""

from rest_framework import status
from rest_framework.test import APITestCase

from apps.coverage.models import Connection, CoverageNode
from apps.coverage.services import connection_create, node_create


class CoverageShortestRouteAPITests(APITestCase):
    url = "/api/coverage/shortest-route/"
    reachability_url = "/api/coverage/reachability/"

    @classmethod
    def setUpTestData(cls):
        cls.base_north = node_create(
            code="F3-BASE-NORTE", name="Base Norte", node_type="BASE"
        )
        cls.base_south = node_create(
            code="F3-BASE-SUR", name="Base Sur", node_type="BASE"
        )
        cls.zone_laureles = node_create(
            code="F3-ZONE-LAURELES", name="Laureles", node_type="ZONE"
        )
        cls.zone_estadio = node_create(
            code="F3-ZONE-ESTADIO", name="Estadio", node_type="ZONE"
        )
        cls.zone_belen = node_create(
            code="F3-ZONE-BELEN", name="Belen", node_type="ZONE"
        )
        cls.zone_isolated = node_create(
            code="F3-ZONE-ISOLATED", name="Aislada", node_type="ZONE"
        )
        cls.zone_reverse = node_create(
            code="F3-ZONE-REVERSE", name="Reversa", node_type="ZONE"
        )
        cls.zone_bidir = node_create(
            code="F3-ZONE-BIDIR", name="Bidireccional", node_type="ZONE"
        )

        # Direct route is slower: 30 instead of 5 + 7 + 8 = 20.
        for origin, destination, minutes, both in (
            (cls.base_north, cls.zone_belen, 30, False),
            (cls.base_north, cls.zone_laureles, 5, False),
            (cls.zone_laureles, cls.zone_estadio, 7, False),
            (cls.zone_estadio, cls.zone_belen, 8, False),
            (cls.zone_reverse, cls.base_south, 4, False),
            # Stored ZONE -> BASE; BASE -> ZONE must work in reverse.
            (cls.zone_bidir, cls.base_south, 6, True),
        ):
            connection_create(
                origin_id=origin.id,
                destination_id=destination.id,
                estimated_minutes=minutes,
                is_bidirectional=both,
            )

    def request_route(self, origin=None, destination=None):
        if origin is None:
            origin = self.base_north.id
        if destination is None:
            destination = self.zone_belen.id
        return self.client.get(
            self.url,
            {"origin_id": origin, "destination_id": destination},
        )

    def assert_bad_request(self, query, error_field):
        response = self.client.get(self.url, query)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn(error_field, response.data)

    def test_01_route_found_returns_http_200(self):
        self.assertEqual(self.request_route().status_code, status.HTTP_200_OK)

    def test_02_chooses_20_instead_of_direct_30(self):
        self.assertEqual(self.request_route().data["total_minutes"], 20)

    def test_03_mode_is_shortest_route(self):
        self.assertEqual(self.request_route().data["mode"], "shortest_route")

    def test_04_reachable_is_true(self):
        self.assertIs(self.request_route().data["reachable"], True)

    def test_05_path_order(self):
        response = self.request_route()
        self.assertEqual(
            [node["code"] for node in response.data["path"]],
            [
                "F3-BASE-NORTE",
                "F3-ZONE-LAURELES",
                "F3-ZONE-ESTADIO",
                "F3-ZONE-BELEN",
            ],
        )

    def test_06_segments_have_expected_minutes_and_direction(self):
        segments = self.request_route().data["segments"]
        self.assertEqual([segment["estimated_minutes"] for segment in segments], [5, 7, 8])
        self.assertEqual(
            [(s["origin"]["code"], s["destination"]["code"]) for s in segments],
            [
                ("F3-BASE-NORTE", "F3-ZONE-LAURELES"),
                ("F3-ZONE-LAURELES", "F3-ZONE-ESTADIO"),
                ("F3-ZONE-ESTADIO", "F3-ZONE-BELEN"),
            ],
        )

    def test_07_segments_add_up_to_total_minutes(self):
        response = self.request_route().data
        self.assertEqual(
            sum(item["estimated_minutes"] for item in response["segments"]),
            response["total_minutes"],
        )

    def test_08_dijkstra_trace_and_visited_count(self):
        response = self.request_route().data
        self.assertEqual(
            [node["code"] for node in response["traversal_order"]],
            ["F3-BASE-NORTE", "F3-ZONE-LAURELES", "F3-ZONE-ESTADIO", "F3-ZONE-BELEN"],
        )
        self.assertEqual(response["visited_count"], 4)
        self.assertEqual(len(response["traversal_order"]), response["visited_count"])

    def test_09_disconnected_zone_is_valid_http_200(self):
        response = self.request_route(destination=self.zone_isolated.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["reachable"], False)
        self.assertEqual(response.data["mode"], "shortest_route")

    def test_10_disconnected_zone_has_no_route_and_null_time(self):
        response = self.request_route(destination=self.zone_isolated.id).data
        self.assertEqual(response["path"], [])
        self.assertEqual(response["segments"], [])
        self.assertIsNone(response["total_minutes"])

    def test_11_nonexistent_origin(self):
        self.assert_bad_request(
            {"origin_id": 999999999, "destination_id": self.zone_belen.id},
            "origin",
        )

    def test_12_nonexistent_destination(self):
        self.assert_bad_request(
            {"origin_id": self.base_north.id, "destination_id": 999999999},
            "destination",
        )

    def test_13_origin_must_be_base(self):
        self.assert_bad_request(
            {"origin_id": self.zone_laureles.id, "destination_id": self.zone_belen.id},
            "origin",
        )

    def test_14_destination_must_be_zone(self):
        self.assert_bad_request(
            {"origin_id": self.base_north.id, "destination_id": self.base_south.id},
            "destination",
        )

    def test_15_missing_origin_id(self):
        self.assert_bad_request({"destination_id": self.zone_belen.id}, "origin_id")

    def test_16_missing_destination_id(self):
        self.assert_bad_request({"origin_id": self.base_north.id}, "destination_id")

    def test_17_non_numeric_id_parameters(self):
        for field in ("origin_id", "destination_id"):
            with self.subTest(field=field):
                params = {"origin_id": self.base_north.id, "destination_id": self.zone_belen.id}
                params[field] = "abc"
                self.assert_bad_request(params, field)

    def test_18_zero_and_negative_id_parameters(self):
        for field in ("origin_id", "destination_id"):
            for value in (0, -1):
                with self.subTest(field=field, value=value):
                    params = {"origin_id": self.base_north.id, "destination_id": self.zone_belen.id}
                    params[field] = value
                    self.assert_bad_request(params, field)

    def test_19_connection_is_not_traversed_in_reverse(self):
        response = self.request_route(self.base_south.id, self.zone_reverse.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["reachable"], False)
        self.assertEqual(response.data["path"], [])

    def test_20_bidirectional_connection_allows_reverse(self):
        response = self.request_route(self.base_south.id, self.zone_bidir.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIs(response.data["reachable"], True)
        self.assertEqual(response.data["total_minutes"], 6)
        self.assertEqual(
            [node["code"] for node in response.data["path"]],
            ["F3-BASE-SUR", "F3-ZONE-BIDIR"],
        )

    def test_21_get_does_not_change_persisted_network(self):
        before_nodes = list(CoverageNode.objects.order_by("pk").values_list())
        before_connections = list(Connection.objects.order_by("pk").values_list())
        response = self.request_route()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(before_nodes, list(CoverageNode.objects.order_by("pk").values_list()))
        self.assertEqual(before_connections, list(Connection.objects.order_by("pk").values_list()))

    def test_22_feature2_bfs_endpoint_still_works(self):
        response = self.client.get(
            self.reachability_url,
            {"origin_id": self.base_north.id, "destination_id": self.zone_belen.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["mode"], "check")
        self.assertIs(response.data["covered"], True)
        self.assertEqual(
            [node["code"] for node in response.data["path"]],
            ["F3-BASE-NORTE", "F3-ZONE-BELEN"],
        )
