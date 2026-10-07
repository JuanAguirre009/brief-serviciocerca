from rest_framework import status

from rest_framework.test import APITestCase
 
from apps.coverage.models import (

    Connection,

    CoverageNode,

    Technician,

)

from apps.coverage.services import (

    connection_create,

    node_create,

    technician_create,

)
 
 
class CoverageNodeAPITests(APITestCase):
 
    url = "/api/coverage/nodes/"
 
    def test_create_base_node(self):

        response = self.client.post(

            self.url,

            {

                "code": "BASE-NORTE",

                "name": "Base Norte",

                "type": "BASE",

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_201_CREATED,

        )
 
        self.assertEqual(

            CoverageNode.objects.count(),

            1,

        )
 
    def test_create_zone_node(self):

        response = self.client.post(

            self.url,

            {

                "code": "ZONA-001",

                "name": "Laureles",

                "type": "ZONE",

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_201_CREATED,

        )
 
    def test_reject_invalid_node_type(self):

        response = self.client.post(

            self.url,

            {

                "code": "NODO-001",

                "name": "Nodo",

                "type": "INVALID",

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
    def test_reject_duplicate_node(self):

        node_create(

            code="BASE-NORTE",

            name="Base Norte",

            node_type="BASE",

        )
 
        response = self.client.post(

            self.url,

            {

                "code": "BASE-NORTE",

                "name": "Otra Base",

                "type": "BASE",

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
    def test_list_nodes(self):

        node_create(

            code="BASE-NORTE",

            name="Base Norte",

            node_type="BASE",

        )
 
        node_create(

            code="ZONA-001",

            name="Laureles",

            node_type="ZONE",

        )
 
        response = self.client.get(

            self.url

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_200_OK,

        )
 
        self.assertEqual(

            len(response.data),

            2,

        )
 
 
class TechnicianAPITests(APITestCase):
 
    url = "/api/coverage/technicians/"
 
    def setUp(self):

        self.base = node_create(

            code="BASE-NORTE",

            name="Base Norte",

            node_type="BASE",

        )
 
        self.zone = node_create(

            code="ZONA-001",

            name="Laureles",

            node_type="ZONE",

        )
 
    def test_create_technician(self):

        response = self.client.post(

            self.url,

            {

                "code": "TEC-001",

                "name": "Carlos Pérez",

                "base_id": self.base.id,

                "is_available": True,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_201_CREATED,

        )
 
        self.assertEqual(

            Technician.objects.count(),

            1,

        )
 
    def test_reject_zone_as_base(self):

        response = self.client.post(

            self.url,

            {

                "code": "TEC-001",

                "name": "Carlos Pérez",

                "base_id": self.zone.id,

                "is_available": True,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
    def test_reject_nonexistent_base(self):

        response = self.client.post(

            self.url,

            {

                "code": "TEC-001",

                "name": "Carlos Pérez",

                "base_id": 99999,

                "is_available": True,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
 
class ConnectionAPITests(APITestCase):
 
    url = "/api/coverage/connections/"
 
    def setUp(self):

        self.base = node_create(

            code="BASE-NORTE",

            name="Base Norte",

            node_type="BASE",

        )
 
        self.zone = node_create(

            code="ZONA-001",

            name="Laureles",

            node_type="ZONE",

        )
 
    def test_create_connection(self):

        response = self.client.post(

            self.url,

            {

                "origin_id": self.base.id,

                "destination_id": self.zone.id,

                "estimated_minutes": 15,

                "is_bidirectional": True,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_201_CREATED,

        )
 
        self.assertEqual(

            Connection.objects.count(),

            1,

        )
 
    def test_reject_zero_weight(self):

        response = self.client.post(

            self.url,

            {

                "origin_id": self.base.id,

                "destination_id": self.zone.id,

                "estimated_minutes": 0,

                "is_bidirectional": False,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
    def test_reject_same_origin_and_destination(self):

        response = self.client.post(

            self.url,

            {

                "origin_id": self.base.id,

                "destination_id": self.base.id,

                "estimated_minutes": 10,

                "is_bidirectional": False,

            },

            format="json",

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_400_BAD_REQUEST,

        )
 
 
class CoverageNetworkAPITests(APITestCase):
 
    url = "/api/coverage/network/"
 
    def setUp(self):

        self.base = node_create(

            code="BASE-NORTE",

            name="Base Norte",

            node_type="BASE",

        )
 
        self.zone = node_create(

            code="ZONA-001",

            name="Laureles",

            node_type="ZONE",

        )
 
        technician_create(

            code="TEC-001",

            name="Carlos Pérez",

            base_id=self.base.id,

        )
 
        connection_create(

            origin_id=self.base.id,

            destination_id=self.zone.id,

            estimated_minutes=15,

            is_bidirectional=True,

        )
 
    def test_get_complete_network(self):

        response = self.client.get(

            self.url

        )
 
        self.assertEqual(

            response.status_code,

            status.HTTP_200_OK,

        )
 
        self.assertIn(

            "nodes",

            response.data,

        )
 
        self.assertIn(

            "technicians",

            response.data,

        )
 
        self.assertIn(

            "connections",

            response.data,

        )
 
        self.assertEqual(

            len(response.data["nodes"]),

            2,

        )
 
        self.assertEqual(

            len(response.data["technicians"]),

            1,

        )
 
        self.assertEqual(

            len(response.data["connections"]),

            1,

        )
 