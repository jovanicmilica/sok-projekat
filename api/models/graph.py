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