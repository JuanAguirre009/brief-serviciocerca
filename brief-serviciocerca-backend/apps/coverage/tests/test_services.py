from django.core.exceptions import ValidationError
from django.test import TestCase
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

class NodeCreateServiceTests(TestCase):
   def test_create_base_node(self):
       node = node_create(
           code="BASE-NORTE",
           name="Base Norte",
           node_type="BASE",
       )
       self.assertEqual(
           node.code,
           "BASE-NORTE",
       )
       self.assertEqual(
           node.type,
           CoverageNode.NodeType.BASE,
       )
   def test_create_zone_node(self):
       node = node_create(
           code="ZONA-001",
           name="Laureles",
           node_type="ZONE",
       )
       self.assertEqual(
           node.type,
           CoverageNode.NodeType.ZONE,
       )
   def test_normalize_node_code(self):
       node = node_create(
           code=" base-norte ",
           name="Base Norte",
           node_type="base",
       )
       self.assertEqual(
           node.code,
           "BASE-NORTE",
       )
       self.assertEqual(
           node.type,
           CoverageNode.NodeType.BASE,
       )
   def test_normalize_node_name(self):
       node = node_create(
           code="BASE-NORTE",
           name="  Base    Norte  ",
           node_type="BASE",
       )
       self.assertEqual(
           node.name,
           "Base Norte",
       )
   def test_reject_invalid_identifier(self):
       with self.assertRaises(ValidationError):
           node_create(
               code="BASE NORTE!",
               name="Base Norte",
               node_type="BASE",
           )
   def test_reject_duplicate_node_code(self):
       node_create(
           code="BASE-NORTE",
           name="Base Norte",
           node_type="BASE",
       )
       with self.assertRaises(ValidationError):
           node_create(
               code="BASE-NORTE",
               name="Otra Base",
               node_type="BASE",
           )

class TechnicianCreateServiceTests(TestCase):
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
       technician = technician_create(
           code="TEC-001",
           name="Carlos Pérez",
           base_id=self.base.id,
       )
       self.assertEqual(
           technician.base,
           self.base,
       )
       self.assertTrue(
           technician.is_available,
       )
   def test_create_unavailable_technician(self):
       technician = technician_create(
           code="TEC-001",
           name="Carlos Pérez",
           base_id=self.base.id,
           is_available=False,
       )
       self.assertFalse(
           technician.is_available,
       )
   def test_reject_zone_as_technician_base(self):
       with self.assertRaises(ValidationError):
           technician_create(
               code="TEC-001",
               name="Carlos Pérez",
               base_id=self.zone.id,
           )
   def test_reject_nonexistent_base(self):
       with self.assertRaises(ValidationError):
           technician_create(
               code="TEC-001",
               name="Carlos Pérez",
               base_id=99999,
           )
   def test_normalize_technician_code(self):
       technician = technician_create(
           code=" tec-001 ",
           name="Carlos Pérez",
           base_id=self.base.id,
       )
       self.assertEqual(
           technician.code,
           "TEC-001",
       )

class ConnectionCreateServiceTests(TestCase):
   def setUp(self):
       self.base = node_create(
           code="BASE-NORTE",
           name="Base Norte",
           node_type="BASE",
       )
       self.zone_1 = node_create(
           code="ZONA-001",
           name="Laureles",
           node_type="ZONE",
       )
       self.zone_2 = node_create(
           code="ZONA-002",
           name="Belén",
           node_type="ZONE",
       )
   def test_create_unidirectional_connection(self):
       connection = connection_create(
           origin_id=self.base.id,
           destination_id=self.zone_1.id,
           estimated_minutes=15,
       )
       self.assertFalse(
           connection.is_bidirectional,
       )
       self.assertEqual(
           connection.estimated_minutes,
           15,
       )
   def test_create_bidirectional_connection(self):
       connection = connection_create(
           origin_id=self.base.id,
           destination_id=self.zone_1.id,
           estimated_minutes=12,
           is_bidirectional=True,
       )
       self.assertTrue(
           connection.is_bidirectional,
       )
   def test_reject_zero_weight(self):
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.base.id,
               destination_id=self.zone_1.id,
               estimated_minutes=0,
           )
   def test_reject_negative_weight(self):
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.base.id,
               destination_id=self.zone_1.id,
               estimated_minutes=-5,
           )
   def test_reject_same_origin_and_destination(self):
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.base.id,
               destination_id=self.base.id,
               estimated_minutes=10,
           )
   def test_reject_nonexistent_origin(self):
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=99999,
               destination_id=self.zone_1.id,
               estimated_minutes=10,
           )
   def test_reject_nonexistent_destination(self):
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.base.id,
               destination_id=99999,
               estimated_minutes=10,
           )
   def test_reject_duplicate_connection(self):
       connection_create(
           origin_id=self.base.id,
           destination_id=self.zone_1.id,
           estimated_minutes=10,
       )
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.base.id,
               destination_id=self.zone_1.id,
               estimated_minutes=20,
           )
   def test_allow_opposite_unidirectional_connections(self):
       connection_create(
           origin_id=self.base.id,
           destination_id=self.zone_1.id,
           estimated_minutes=10,
       )
       connection_create(
           origin_id=self.zone_1.id,
           destination_id=self.base.id,
           estimated_minutes=15,
       )
       self.assertEqual(
           Connection.objects.count(),
           2,
       )
   def test_reject_reverse_of_bidirectional_connection(self):
       connection_create(
           origin_id=self.base.id,
           destination_id=self.zone_1.id,
           estimated_minutes=10,
           is_bidirectional=True,
       )
       with self.assertRaises(ValidationError):
           connection_create(
               origin_id=self.zone_1.id,
               destination_id=self.base.id,
               estimated_minutes=10,
           )