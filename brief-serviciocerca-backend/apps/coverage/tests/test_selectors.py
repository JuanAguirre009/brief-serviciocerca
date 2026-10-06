from django.test import TestCase
from apps.coverage.models import CoverageNode
from apps.coverage.selectors import (
   connection_list,
   network_get,
   node_list,
   technician_list,
)
from apps.coverage.services import (
   connection_create,
   node_create,
   technician_create,
)

class CoverageSelectorsTests(TestCase):
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
       cls.zone_1 = node_create(
           code="ZONA-001",
           name="Laureles",
           node_type="ZONE",
       )
       cls.zone_2 = node_create(
           code="ZONA-002",
           name="Belén",
           node_type="ZONE",
       )
       cls.technician_1 = technician_create(
           code="TEC-001",
           name="Carlos Pérez",
           base_id=cls.base_north.id,
           is_available=True,
       )
       cls.technician_2 = technician_create(
           code="TEC-002",
           name="Ana Gómez",
           base_id=cls.base_south.id,
           is_available=False,
       )
       cls.connection_1 = connection_create(
           origin_id=cls.base_north.id,
           destination_id=cls.zone_1.id,
           estimated_minutes=15,
           is_bidirectional=True,
       )
       cls.connection_2 = connection_create(
           origin_id=cls.base_south.id,
           destination_id=cls.zone_2.id,
           estimated_minutes=20,
       )
   def test_node_list_returns_all_nodes(self):
       nodes = node_list()
       self.assertEqual(
           nodes.count(),
           4,
       )
   def test_node_list_filter_by_base(self):
       nodes = node_list(
           node_type=CoverageNode.NodeType.BASE,
       )
       self.assertEqual(
           nodes.count(),
           2,
       )
       self.assertTrue(
           all(
               node.type == CoverageNode.NodeType.BASE
               for node in nodes
           )
       )
   def test_node_list_filter_by_zone(self):
       nodes = node_list(
           node_type=CoverageNode.NodeType.ZONE,
       )
       self.assertEqual(
           nodes.count(),
           2,
       )
   def test_technician_list_returns_all(self):
       technicians = technician_list()
       self.assertEqual(
           technicians.count(),
           2,
       )
   def test_technician_list_filter_by_base(self):
       technicians = technician_list(
           base_id=self.base_north.id,
       )
       self.assertEqual(
           technicians.count(),
           1,
       )
       self.assertEqual(
           technicians.first().code,
           "TEC-001",
       )
   def test_technician_list_filter_available(self):
       technicians = technician_list(
           is_available=True,
       )
       self.assertEqual(
           technicians.count(),
           1,
       )
       self.assertEqual(
           technicians.first().code,
           "TEC-001",
       )
   def test_connection_list_returns_connections(self):
       connections = connection_list()
       self.assertEqual(
           connections.count(),
           2,
       )
   def test_network_get_returns_complete_network(self):
       network = network_get()
       self.assertIn(
           "nodes",
           network,
       )
       self.assertIn(
           "technicians",
           network,
       )
       self.assertIn(
           "connections",
           network,
       )
       self.assertEqual(
           network["nodes"].count(),
           4,
       )
       self.assertEqual(
           network["technicians"].count(),
           2,
       )
       self.assertEqual(
           network["connections"].count(),
           2,
       )