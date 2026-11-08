from unittest import TestCase

from apps.coverage.algorithms.dijkstra import dijkstra_shortest_path


class DijkstraShortestPathTests(TestCase):

    def test_prefers_less_time_over_fewer_hops(self):
        """
        The hallmark case: more hops but lower total time.

        Direct:  1 -> 3         = 30 minutes, 1 hop
        Indirect: 1 -> 2 -> 4 -> 3 = 5 + 7 + 8 = 20 minutes, 3 hops
        """
        adjacency = {
            1: [(3, 30), (2, 5)],
            2: [(4, 7)],
            4: [(3, 8)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=3,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [1, 2, 4, 3])
        self.assertEqual(result["total_minutes"], 20)

    def test_direct_connection(self):
        adjacency = {
            1: [(2, 9)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=2,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [1, 2])
        self.assertEqual(result["total_minutes"], 9)

    def test_unreachable_destination(self):
        adjacency = {
            1: [(2, 9)],
            3: [],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=3,
        )

        self.assertFalse(result["reachable"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["total_minutes"])

    def test_reverse_direction_not_allowed_on_one_way_link(self):
        adjacency = {
            1: [(2, 9)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=2,
            destination_id=1,
        )

        self.assertFalse(result["reachable"])
        self.assertEqual(result["visited"], [2])

    def test_bidirectional_adjacency_allows_reverse_travel(self):
        adjacency = {
            1: [(2, 9)],
            2: [(1, 9)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=2,
            destination_id=1,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [2, 1])
        self.assertEqual(result["total_minutes"], 9)

    def test_cycle_does_not_loop_infinitely(self):
        adjacency = {
            1: [(2, 3)],
            2: [(3, 4)],
            3: [(1, 2)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=3,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["path"], [1, 2, 3])
        self.assertEqual(result["total_minutes"], 7)

    def test_same_origin_and_destination(self):
        adjacency = {}

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=1,
        )

        self.assertEqual(
            result,
            {
                "reachable": True,
                "path": [1],
                "total_minutes": 0,
                "visited": [1],
            },
        )

    def test_isolated_origin_with_destination(self):
        adjacency = {}

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=99,
        )

        self.assertFalse(result["reachable"])
        self.assertEqual(result["path"], [])
        self.assertIsNone(result["total_minutes"])
        self.assertEqual(result["visited"], [1])

    def test_discards_stale_heap_entries(self):
        """
        A worse candidate for node 2 is pushed first, then a better one.
        Dijkstra must ignore the stale entry.
        """
        adjacency = {
            1: [(2, 10), (3, 1)],
            3: [(2, 1)],
            2: [(4, 1)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=4,
        )

        self.assertEqual(result["path"], [1, 3, 2, 4])
        self.assertEqual(result["total_minutes"], 3)
        self.assertEqual(result["visited"], [1, 3, 2, 4])

    def test_equal_cost_paths_are_acceptable(self):
        adjacency = {
            1: [(2, 5), (3, 5)],
            2: [(4, 5)],
            3: [(4, 5)],
        }

        result = dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=4,
        )

        self.assertTrue(result["reachable"])
        self.assertEqual(result["total_minutes"], 10)
        self.assertIn(result["path"], ([1, 2, 4], [1, 3, 4]))

    def test_invalid_weights_are_rejected(self):
        invalid_weights = [0, -1, True, 1.5, "4", None]

        for weight in invalid_weights:
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    dijkstra_shortest_path(
                        {1: [(2, weight)]},
                        origin_id=1,
                        destination_id=2,
                    )

    def test_input_graph_is_not_modified(self):
        adjacency = {
            1: [(2, 5)],
            2: [],
        }
        original = {
            1: [(2, 5)],
            2: [],
        }

        dijkstra_shortest_path(
            adjacency,
            origin_id=1,
            destination_id=2,
        )

        self.assertEqual(adjacency, original)
