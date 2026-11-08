from types import SimpleNamespace
from unittest import TestCase

from apps.coverage.algorithms.weighted_graph import build_weighted_adjacency


def make_connection(
    origin: int,
    destination: int,
    minutes: int,
    bidirectional: bool = False,
) -> SimpleNamespace:
    """Factory for connection-like test doubles."""
    return SimpleNamespace(
        origin_id=origin,
        destination_id=destination,
        estimated_minutes=minutes,
        is_bidirectional=bidirectional,
    )


class WeightedAdjacencyTests(TestCase):

    def test_unidirectional_connection_adds_single_arc(self):
        adjacency = build_weighted_adjacency([
            make_connection(1, 2, 15),
        ])

        self.assertEqual(
            adjacency,
            {1: [(2, 15)]},
        )

    def test_bidirectional_connection_adds_both_arcs(self):
        adjacency = build_weighted_adjacency([
            make_connection(1, 2, 8, bidirectional=True),
        ])

        self.assertEqual(
            adjacency,
            {
                1: [(2, 8)],
                2: [(1, 8)],
            },
        )

    def test_opposite_one_way_links_keep_different_weights(self):
        adjacency = build_weighted_adjacency([
            make_connection(1, 2, 7),
            make_connection(2, 1, 12),
        ])

        self.assertEqual(
            adjacency,
            {
                1: [(2, 7)],
                2: [(1, 12)],
            },
        )

    def test_mixed_links_preserve_direction_and_weight(self):
        adjacency = build_weighted_adjacency([
            make_connection(1, 2, 5, bidirectional=True),
            make_connection(2, 3, 10),
        ])

        self.assertEqual(
            adjacency,
            {
                1: [(2, 5)],
                2: [(1, 5), (3, 10)],
            },
        )

    def test_empty_connections_yield_empty_adjacency(self):
        adjacency = build_weighted_adjacency([])

        self.assertEqual(adjacency, {})

    def test_self_loop_is_rejected(self):
        with self.assertRaises(ValueError):
            build_weighted_adjacency([
                make_connection(1, 1, 5),
            ])

    def test_invalid_weights_are_rejected(self):
        invalid_weights = [0, -3, True, 2.5, "10", None]

        for weight in invalid_weights:
            with self.subTest(weight=weight):
                with self.assertRaises(ValueError):
                    build_weighted_adjacency([
                        make_connection(1, 2, weight),
                    ])

    def test_non_numeric_origin_is_rejected(self):
        connection = SimpleNamespace(
            origin_id="abc",
            destination_id=2,
            estimated_minutes=5,
            is_bidirectional=False,
        )

        with self.assertRaises(ValueError):
            build_weighted_adjacency([connection])

    def test_non_numeric_destination_is_rejected(self):
        connection = SimpleNamespace(
            origin_id=1,
            destination_id="xyz",
            estimated_minutes=5,
            is_bidirectional=False,
        )

        with self.assertRaises(ValueError):
            build_weighted_adjacency([connection])
