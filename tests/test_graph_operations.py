import unittest
import sys
import os

from api.models.graph import Graph
from project_platform.graph_operations import GraphOperations

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestGraphOperations(unittest.TestCase):
    """
    Tests for GraphOperations class
    Test Search and Filter operations
    """

    def setUp(self):
        """
        SetUp data before each test
        """
        self.graph = self._create_test_graph()
        self.operations = GraphOperations()

    def _create_test_graph(self) -> Graph:
        """
        Create test graph
        """
        builder = Graph.builder(directed=True)

        # Add nodes
        builder.add_node(
            "1",
            name="Marko Markovic",
            age=25,
            city="Beograd",
            salary=75000.50,
            active=True,
            department="IT"
        )

        builder.add_node(
            "2",
            name="Ana Anic",
            age=30,
            city="Novi Sad",
            salary=85000.75,
            active=True,
            department="HR"
        )

        builder.add_node(
            "3",
            name="Petar Petrovic",
            age=35,
            city="Beograd",
            salary=95000.00,
            active=False,
            department="IT"
        )

        builder.add_node(
            "4",
            name="Jelena Jelenic",
            age=28,
            city="Nis",
            salary=65000.25,
            active=True,
            department="Finance"
        )

        builder.add_node(
            "5",
            name="Nikola Nikolic",
            age=42,
            city="Kragujevac",
            salary=120000.00,
            active=True,
            department="IT"
        )

        # Add edges
        builder.add_edge("e1", "1", "2", type="prijatelj", weight=5)
        builder.add_edge("e2", "2", "3", type="kolega", weight=3)
        builder.add_edge("e3", "1", "3", type="poznanik", weight=2)
        builder.add_edge("e4", "3", "4", type="kolega", weight=4)
        builder.add_edge("e5", "4", "5", type="prijatelj", weight=5)
        builder.add_edge("e6", "5", "1", type="saradnik", weight=1)

        return builder.build()

    @staticmethod
    def _count_nodes_and_edges(graph: Graph) -> tuple:
        """
        Count nodes and edges
        """
        return len(graph.nodes), len(graph.edges)

    # ============= SEARCH TESTS =============

    def test_search_empty_query(self):
        """Test: Empty query returns original graph"""
        result = self.operations.search(self.graph, "")
        self.assertEqual(self._count_nodes_and_edges(result), (5, 6))

        result = self.operations.search(self.graph, "   ")
        self.assertEqual(self._count_nodes_and_edges(result), (5, 6))

    def test_search_by_node_id(self):
        """Test: Search by node id"""
        # Expect 2 nodes and 1 edge
        # Node 5 has salary = 120000 and that contains '1'
        result = self.operations.search(self.graph, "1")
        self.assertEqual(self._count_nodes_and_edges(result), (2, 1))

        # Expect nodes 1 and 5
        self.assertIn("1", result.nodes)
        self.assertIn("5", result.nodes)

        # Expect edge between nodes
        self.assertEqual(len(result.edges), 1)
        edge = list(result.edges.values())[0]
        self.assertEqual(edge.source, "5")
        self.assertEqual(edge.target, "1")

    def test_search_by_name_attribute(self):
        """Test: Search by attribute value"""
        # Expect 1 node and no edges
        result = self.operations.search(self.graph, "marko")
        self.assertEqual(self._count_nodes_and_edges(result), (1, 0))

        # Expect node 1 with name Marko Markovic
        node = result.nodes.get("1")
        self.assertIsNotNone(node)
        self.assertEqual(node.attributes["name"], "Marko Markovic")

    def test_search_by_city(self):
        """Test: Search by city value"""
        result = self.operations.search(self.graph, "beograd")
        self.assertEqual(self._count_nodes_and_edges(result), (2, 1))

        # Expect nodes 1 and 3
        self.assertIn("1", result.nodes)
        self.assertIn("3", result.nodes)

        # Expect edge between nodes
        self.assertEqual(len(result.edges), 1)
        edge = list(result.edges.values())[0]
        self.assertEqual(edge.source, "1")
        self.assertEqual(edge.target, "3")

    def test_search_by_attribute_name(self):
        """Test: Search attribute name 'salary'"""
        result = self.operations.search(self.graph, "salary")
        # Expect original graph, all nodes have attribute salary
        self.assertEqual(self._count_nodes_and_edges(result), (5, 6))

    def test_search_case_insensitive(self):
        """Test: Show tests are case insensitive"""
        result1 = self.operations.search(self.graph, "MARKO")
        result2 = self.operations.search(self.graph, "marko")
        result3 = self.operations.search(self.graph, "Marko")

        self.assertEqual(len(result1.nodes), len(result2.nodes))
        self.assertEqual(len(result1.nodes), len(result3.nodes))

    def test_search_no_results(self):
        """Test: Search based on non-existent criteria"""
        # Expect no nodes and edges
        result = self.operations.search(self.graph, "nonexistent")
        self.assertEqual(self._count_nodes_and_edges(result), (0, 0))

    def test_search_partial_match(self):
        """Test: Search based on partial match"""
        # Expect 3 nodes and 1 edge
        result = self.operations.search(self.graph, "ni")
        self.assertEqual(self._count_nodes_and_edges(result), (3, 1))

        # Expect nodes 2, 4, and 5
        self.assertIn("2", result.nodes)
        self.assertIn("4", result.nodes)
        self.assertIn("5", result.nodes)

        # Expect edge between nodes 4 and 5
        self.assertEqual(len(result.edges), 1)
        edge = list(result.edges.values())[0]
        self.assertEqual(edge.source, "4")
        self.assertEqual(edge.target, "5")

    # ============= FILTER TESTS =============

    def test_filter_empty_query(self):
        """Test: Empty filter returns original graph"""
        result = self.operations.filter(self.graph, "")
        self.assertEqual(self._count_nodes_and_edges(result), (5, 6))

    def test_filter_invalid_format(self):
        """Test: Invalid filter query format"""
        # Expect raises ValueError
        with self.assertRaises(ValueError) as context:
            self.operations.filter(self.graph, "age 25")

        self.assertIn("Invalid filter format", str(context.exception))

    def test_filter_unknown_operator(self):
        """Test: Unknown filter operator"""
        # Expect raises ValueError
        with self.assertRaises(ValueError):
            self.operations.filter(self.graph, "age ?? 25")

    def test_filter_equals_string(self):
        """Test: Filter nodes where city is Belgrade"""
        result = self.operations.filter(self.graph, 'city == "Beograd"')
        self.assertEqual(self._count_nodes_and_edges(result), (2, 1))

        # Expect nodes 1 and 3
        self.assertIn("1", result.nodes)
        self.assertIn("3", result.nodes)

    def test_filter_equals_string_no_quotes(self):
        """Test: Filter string without quotation marks"""
        result = self.operations.filter(self.graph, "city == Beograd")
        self.assertEqual(self._count_nodes_and_edges(result), (2, 1))

    def test_filter_not_equals(self):
        """Test: Filter city is not Belgrade"""
        result = self.operations.filter(self.graph, "city != Beograd")
        # Expect nodes 2, 4, 5
        self.assertEqual(self._count_nodes_and_edges(result), (3, 1))

        # Don't expect nodes 1 and 3
        self.assertNotIn("1", result.nodes)
        self.assertNotIn("3", result.nodes)

    def test_filter_greater_than_int(self):
        """Test: Filter age greater than"""
        # Expect 2 nodes and no edges
        result = self.operations.filter(self.graph, "age > 30")
        self.assertEqual(self._count_nodes_and_edges(result), (2, 0))

        # Expect nodes 3 and 5
        self.assertIn("3", result.nodes)
        self.assertIn("5", result.nodes)

        # Expect 0 edges
        edges = list(result.edges.values())
        self.assertEqual(len(edges), 0)

    def test_filter_less_than_or_equal(self):
        """Test: Filter salary less than or equal"""
        # Expect 2 nodes and no edges
        result = self.operations.filter(self.graph, "salary <= 85000")
        self.assertEqual(self._count_nodes_and_edges(result), (2, 0))

        # Expect nodes 1 and 3
        self.assertIn("1", result.nodes)
        self.assertIn("4", result.nodes)

        # Expect 0 edges
        self.assertEqual(len(result.edges), 0)

    def test_filter_boolean_true(self):
        """Test: Filter boolean"""
        # Expect 4 nodes and 3 edges
        result = self.operations.filter(self.graph, "active == true")
        self.assertEqual(self._count_nodes_and_edges(result), (4, 3))

        # Don't expect node 3
        self.assertNotIn("3", result.nodes)

        # Expect all nodes with active attribute set on True
        for node in result.nodes.values():
            self.assertTrue(node.attributes.get("active"))

    def test_filter_nonexistent_attribute(self):
        """Test: Filter nonexistent attribute"""
        # Expect no nodes, since attribute doesn't exist
        result = self.operations.filter(self.graph, "nonexistent == value")
        self.assertEqual(self._count_nodes_and_edges(result), (0, 0))

    def test_filter_type_conversion_error(self):
        """Test: Error converting type"""
        # Expect raises ValueError
        with self.assertRaises(ValueError) as context:
            self.operations.filter(self.graph, "age > thirty")

        self.assertIn("Cannot convert 'thirty' to int", str(context.exception))

    # ============= SUCCESSIVE OPERATIONS TESTS =============

    def test_search_then_filter(self):
        """Test: Search and then filter the graph"""
        # Search all nodes where city is Belgrade
        # Expect 2 nodes and 1 edge
        belgrade_graph = self.operations.search(self.graph, "beograd")
        self.assertEqual(self._count_nodes_and_edges(belgrade_graph), (2, 1))

        # Filter those with age greater than 30
        result = self.operations.filter(belgrade_graph, "age > 30")
        # Expect 1 node and no edges
        self.assertEqual(self._count_nodes_and_edges(result), (1, 0))
        # Expect node 3
        self.assertIn("3", result.nodes)

    def test_multiple_filters(self):
        """Test: Successive filter"""
        # Filter age greater than 25
        g1 = self.operations.filter(self.graph, "age > 25")
        # Expect 4 nodes and 3 edges
        self.assertEqual(self._count_nodes_and_edges(g1), (4, 3))

        # Filter city == Belgrade
        g2 = self.operations.filter(g1, "city == Beograd")
        # Expect 1 node and no edges
        self.assertEqual(self._count_nodes_and_edges(g2), (1, 0))
        # Expect node 3
        self.assertIn("3", g2.nodes)

        # Filter active == true
        g3 = self.operations.filter(g2, "active == true")
        # Expect no nodes
        self.assertEqual(self._count_nodes_and_edges(g3), (0, 0))

    # ============= EDGE CASES =============

    def test_empty_graph(self):
        """Test: Empty graph"""
        empty_graph = Graph.builder().build()

        search_result = self.operations.search(empty_graph, "test")
        self.assertEqual(self._count_nodes_and_edges(search_result), (0, 0))

        filter_result = self.operations.filter(empty_graph, "age > 30")
        self.assertEqual(self._count_nodes_and_edges(filter_result), (0, 0))

    def test_graph_without_attributes(self):
        """Test: Nodes without attributes"""
        builder = Graph.builder()
        builder.add_node("1")
        builder.add_node("2")
        builder.add_node("3")
        builder.add_edge("e1", "1", "2")

        simple_graph = builder.build()

        # Search id - expect 1 node
        result = self.operations.search(simple_graph, "1")
        self.assertEqual(self._count_nodes_and_edges(result), (1, 0))

        # Expect no results
        result = self.operations.search(simple_graph, "x")
        self.assertEqual(self._count_nodes_and_edges(result), (0, 0))

        # Filter age attribute (attribute doesn't exist) - expect no results
        result = self.operations.filter(simple_graph, "age > 30")
        self.assertEqual(self._count_nodes_and_edges(result), (0, 0))

    def test_unicode_characters(self):
        """Test: Unicode characters in query"""
        builder = Graph.builder()
        builder.add_node("1", name="Živko Živić", grad="Čačak")
        builder.add_node("2", name="Šana Šarić", grad="Žabljak")

        unicode_graph = builder.build()

        # Use unicode characters in search query
        result = self.operations.search(unicode_graph, "Živko")
        self.assertEqual(len(result.nodes), 1)

        result = self.operations.search(unicode_graph, "Čačak")
        self.assertEqual(len(result.nodes), 1)

        result = self.operations.search(unicode_graph, "Ž")
        self.assertEqual(len(result.nodes), 2)


if __name__ == '__main__':
    unittest.main()
