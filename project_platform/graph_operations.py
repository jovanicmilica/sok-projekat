from typing import Type, Set

from api.models.graph import Graph
from api.models.node import Node
from api.models.graph import GraphBuilder


class GraphOperations:
    """
    GraphOperations provides search and filter methods.
    Methods return a Graph object.
    """

    def search(self, graph: Graph, query: str) -> Graph:
        """
        Search Graph nodes and see if they contain attribute or value of query string.

        Args:
            graph (Graph): Graph object which is being searched.
            query (str): Query string for searching.

        Returns:
            Graph instance with found nodes and edges.
        """
        if not query or not query.strip():
            return graph

        query_lower = query.lower().strip()
        matching_node_ids: Set[str] = set()

        for node in graph.nodes.values():
            if self._node_matches(node, query_lower):
                matching_node_ids.add(node.id)

        return self._build_subgraph(graph, matching_node_ids)

    @staticmethod
    def _node_matches(node: Node, query: str) -> bool:
        """
        Checks if node id or attribute contains query string.
        Returns true or false.
        """
        # Check node id
        if query in node.id.lower():
            return True

        # Check all attributes
        for key, value in node.attributes.items():
            # Check attribute name
            if query in key.lower():
                return True

            # Check attribute value
            if value is not None:
                str_value = str(value).lower()
                if query in str_value:
                    return True

        return False

    def filter(self, graph: Graph, filter_query: str) -> Graph:
        pass

    @staticmethod
    def _build_subgraph(original: Graph, node_ids: Set[str]) -> Graph:
        """
        Create subgraph based on nodes found, add necessary edges.
        Returns new graph object.
        """
        # If no nodes were found, return original graph
        if not node_ids:
            return GraphBuilder(directed=original.directed).build()

        builder = GraphBuilder(directed=original.directed)

        for node_id in node_ids:
            if node_id in original.nodes:
                node = original.nodes[node_id]
                builder.add_node(node_id, **node.attributes)

        for edge in original.edges.values():
            if edge.source in node_ids and edge.target in node_ids:
                builder.add_edge(
                    edge.id,
                    edge.source,
                    edge.target,
                    **edge.attributes
                )

        return builder.build()
