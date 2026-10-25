from django.test import TestCase

from apps.coverage.algorithms.bfs import bfs_reachability


class BfsReachabilityTests(TestCase):

    def test_origin_equals_destination(self):
        adjacency = {
            1: [2, 3],
            2: [3],
            3: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=1,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [1])
        self.assertEqual(result["visited"], [1, 2, 3])

    def test_simple_path(self):
        adjacency = {
            1: [2],
            2: [3],
            3: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=3,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [1, 2, 3])

    def test_unidirectional_connection_only_allows_one_way(self):
        adjacency = {
            1: [2],
            2: [],
        }

        forward = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=2,
        )

        self.assertTrue(forward["reachable"])
        self.assertEqual(forward["path"], [1, 2])

        backward = bfs_reachability(
            adjacency,
            origin_id=2,
            destination_id=1,
        )

        self.assertFalse(backward["reachable"])
        self.assertEqual(backward["path"], [])

    def test_bidirectional_connection_allows_both_ways(self):
        adjacency = {
            1: [2],
            2: [1],
        }

        forward = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=2,
        )

        backward = bfs_reachability(
            adjacency,
            origin_id=2,
            destination_id=1,
        )

        self.assertTrue(forward["reachable"])
        self.assertTrue(backward["reachable"])
        self.assertEqual(forward["path"], [1, 2])
        self.assertEqual(backward["path"], [2, 1])

    def test_unreachable_destination(self):
        adjacency = {
            1: [2],
            2: [],
            3: [4],
            4: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=4,
        )

        self.assertFalse(result["reachable"])
        self.assertEqual(result["path"], [])
        self.assertEqual(result["visited"], [1, 2])

    def test_isolated_node(self):
        adjacency = {
            1: [2],
            2: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=3,
            destination_id=None,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["visited"], [3])
        self.assertEqual(result["path"], [])

    def test_disconnected_network(self):
        adjacency = {
            1: [2],
            2: [1],
            3: [4],
            4: [3],
        }

        from_component_a = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=None,
        )

        from_component_b = bfs_reachability(
            adjacency,
            origin_id=3,
            destination_id=None,
        )

        self.assertEqual(from_component_a["visited"], [1, 2])
        self.assertEqual(from_component_b["visited"], [3, 4])

    def test_cycle_does_not_cause_infinite_loop(self):
        adjacency = {
            1: [2],
            2: [3],
            3: [1],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=None,
        )

        self.assertEqual(result["visited"], [1, 2, 3])

    def test_no_destination_returns_all_reachable_nodes(self):
        adjacency = {
            1: [2, 3],
            2: [4],
            3: [4],
            4: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=None,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["visited"], [1, 2, 3, 4])
        self.assertEqual(result["path"], [])

    def test_shortest_path_with_multiple_options(self):
        adjacency = {
            1: [2, 3],
            2: [4],
            3: [4],
            4: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=4,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(len(result["path"]), 3)
        self.assertEqual(result["path"][0], 1)
        self.assertEqual(result["path"][-1], 4)

    def test_destination_not_in_graph(self):
        adjacency = {
            1: [2],
            2: [],
        }

        result = bfs_reachability(
            adjacency,
            origin_id=1,
            destination_id=99,
        )

        self.assertFalse(result["reachable"])
        self.assertEqual(result["path"], [])
