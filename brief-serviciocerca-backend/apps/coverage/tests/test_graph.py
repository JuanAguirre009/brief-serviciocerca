from collections import namedtuple

from django.test import TestCase

from apps.coverage.algorithms.graph import build_adjacency


MockConnection = namedtuple(
    "MockConnection",
    [
        "origin_id",
        "destination_id",
        "is_bidirectional",
    ],
)


class BuildAdjacencyTests(TestCase):

    def test_unidirectional_connection(self):
        connections = [
            MockConnection(1, 2, False),
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {1: [2]},
        )

    def test_bidirectional_connection(self):
        connections = [
            MockConnection(1, 2, True),
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {
                1: [2],
                2: [1],
            },
        )

    def test_multiple_connections(self):
        connections = [
            MockConnection(1, 2, False),
            MockConnection(1, 3, False),
            MockConnection(3, 4, True),
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {
                1: [2, 3],
                3: [4],
                4: [3],
            },
        )

    def test_empty_connections(self):
        adjacency = build_adjacency([])

        self.assertEqual(
            adjacency,
            {},
        )

    def test_self_connection(self):
        """
        A self-loop is preserved as-is. Validation happens elsewhere.
        """
        connections = [
            MockConnection(1, 1, False),
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {1: [1]},
        )
