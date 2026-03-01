from typing import Dict

from node import Node
from edge import Edge


class Graph:
    def __init__(self, directed: bool = True):
        self.directed = directed
        self.nodes: dict[str, Node] = {}
        self.edges: dict[str, Edge] = {}

    def add_node(self, node: Node):
        self.nodes[node.id] = node

    def add_edge(self, edge: Edge):
        if edge.source not in self.nodes:
            raise ValueError("Source node does not exist.")
        elif edge.target not in self.nodes:
            raise ValueError("Target node does not exist.")
        self.edges[edge.id] = edge

    def get_node(self, node_id: str) -> Node:
        return self.nodes.get(node_id)

    def get_edges(self) -> list[Edge]:
        return list(self.edges.values())

    '''
        @classmethod - method can be called on the class itself, rather than on an instance
    '''
    @classmethod
    def builder(cls, directed: bool = True) -> 'GraphBuilder':
        """Factory method - returns a new instance of GraphBuilder with the specified directed flag."""
        return GraphBuilder(directed)


class GraphBuilder:
    """
    GraphBuilder is a helper class for constructing Graph objects.
    It provides methods to add nodes and edges to the graph, and a build method to create the final Graph instance.
    """

    def __init__(self, directed: bool = True):
        self._directed = directed
        self._nodes: Dict[str, Node] = {}
        self._edges: Dict[str, Edge] = {}

    def add_node(self, node_id: str, **properties) -> 'GraphBuilder':
        """
        Adds a node to the graph with the given node_id and properties.
        """
        node = Node(node_id, properties)
        self._nodes[node_id] = node
        return self

    def add_edge(self, edge_id: str, source_id: str, target_id: str, **properties) -> 'GraphBuilder':
        """
        Adds an edge to the graph with the given edge_id, source_id, target_id, and properties.
        """

        edge = Edge(edge_id, source_id, target_id, properties)

        self._edges[edge_id] = edge
        return self

    def build(self) -> Graph:
        """
        Builds and returns a Graph instance with the added nodes and edges.
        """
        graph = Graph(self._directed)

        for node in self._nodes.values():
            graph.add_node(node)

        for edge in self._edges.values():
            graph.add_edge(edge)

        return graph
