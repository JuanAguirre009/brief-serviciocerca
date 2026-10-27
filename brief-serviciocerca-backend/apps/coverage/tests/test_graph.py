from types import SimpleNamespace

from django.test import SimpleTestCase

from apps.coverage.algorithms.graph import build_adjacency


class BuildAdjacencyTests(SimpleTestCase):

    def test_unidirectional_connection(self):
        connections = [
            SimpleNamespace(
                origin_id=1,
                destination_id=2,
                is_bidirectional=False,
            )
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {
                1: [2],
            },
        )

    def test_bidirectional_connection(self):
        connections = [
            SimpleNamespace(
                origin_id=1,
                destination_id=2,
                is_bidirectional=True,
            )
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {
                1: [2],
                2: [1],
            },
        )

    def test_mixed_connections_respect_directionality(self):
        connections = [
            SimpleNamespace(
                origin_id=1,
                destination_id=2,
                is_bidirectional=True,
            ),
            SimpleNamespace(
                origin_id=2,
                destination_id=3,
                is_bidirectional=False,
            ),
        ]

        adjacency = build_adjacency(connections)

        self.assertEqual(
            adjacency,
            {
                1: [2],
                2: [1, 3],
            },
        )