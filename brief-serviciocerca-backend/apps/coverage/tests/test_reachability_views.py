from rest_framework import status
from rest_framework.test import APITestCase

from apps.coverage.services import (
    connection_create,
    node_create,
)


class CoverageReachabilityAPITests(
    APITestCase
):

    url = "/api/coverage/reachability/"

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

        cls.zone_isolated = node_create(
            code="ZONA-AISLADA",
            name="Zona Aislada",
            node_type="ZONE",
        )

        cls.zone_reverse = node_create(
            code="ZONA-REVERSA",
            name="Zona Reversa",
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
            origin_id=cls.zone_reverse.id,
            destination_id=cls.base_south.id,
            estimated_minutes=10,
            is_bidirectional=False,
        )

    def test_check_coverage_success(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
                "destination_id": (
                    self.zone_estadio.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["mode"],
            "check",
        )

        self.assertTrue(
            response.data["covered"]
        )

        self.assertEqual(
            response.data[
                "origin"
            ]["code"],
            "BASE-NORTE",
        )

        self.assertEqual(
            response.data[
                "destination"
            ]["code"],
            "ZONA-ESTADIO",
        )

        self.assertEqual(
            [
                node["code"]
                for node
                in response.data["path"]
            ],
            [
                "BASE-NORTE",
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
            ],
        )

    def test_check_coverage_returns_trace(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
                "destination_id": (
                    self.zone_estadio.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            [
                node["code"]
                for node
                in response.data[
                    "traversal_order"
                ]
            ],
            [
                "BASE-NORTE",
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
            ],
        )

    def test_disconnected_zone_is_valid_business_result(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
                "destination_id": (
                    self.zone_isolated.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["covered"]
        )

        self.assertEqual(
            response.data["path"],
            [],
        )

        self.assertIn(
            "no es alcanzable",
            response.data["message"],
        )

    def test_origin_only_lists_reachable_zones(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["mode"],
            "reachability",
        )

        self.assertEqual(
            response.data[
                "reachable_count"
            ],
            2,
        )

        self.assertEqual(
            [
                node["code"]
                for node
                in response.data[
                    "reachable_nodes"
                ]
            ],
            [
                "ZONA-LAURELES",
                "ZONA-ESTADIO",
            ],
        )

    def test_missing_origin_parameter(self):
        response = self.client.get(
            self.url
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "origin_id",
            response.data,
        )

    def test_invalid_origin_parameter(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": "ABC",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "origin_id",
            response.data,
        )

    def test_nonexistent_origin(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": 999999,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "origin",
            response.data,
        )

    def test_nonexistent_destination(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
                "destination_id": 999999,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "destination",
            response.data,
        )

    def test_origin_must_be_base(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.zone_laureles.id
                ),
                "destination_id": (
                    self.zone_estadio.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "origin",
            response.data,
        )

    def test_destination_must_be_zone(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_north.id
                ),
                "destination_id": (
                    self.base_south.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "destination",
            response.data,
        )

    def test_directionality_is_respected(self):
        response = self.client.get(
            self.url,
            {
                "origin_id": (
                    self.base_south.id
                ),
                "destination_id": (
                    self.zone_reverse.id
                ),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            response.data["covered"]
        )

        self.assertEqual(
            response.data["path"],
            [],
        )
