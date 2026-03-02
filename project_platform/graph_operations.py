import re
from typing import Set

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
            if self._node_matches_search(node, query_lower):
                matching_node_ids.add(node.id)

        return self._build_subgraph(graph, matching_node_ids)

    @staticmethod
    def _node_matches_search(node: Node, query: str) -> bool:
        """
        Checks if node id or attribute contains query string.

        Args:
            node (Node): Node object which is being searched.
            query (str): Query string for searching.

        Returns:
            bool: True if node id or attribute contains query string.
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
        """
        Filter Graph nodes based on query string.

        Args:
            graph (Graph): Graph object which is being filtered.
            filter_query (str): Query string for filtering. Format:
                <attribute_name> <operator> <value_name>
                Operations: ==, <=, >=, <, >, !=

        Returns:
            Graph instance with filtered nodes and edges.

        Raises:
            ValueError: If query string is not valid.
        """
        if not filter_query or not filter_query.strip():
            return graph

        pattern = r'^(\w+)\s*(==|!=|>=|<=|>|<)\s*(.+)$'
        match = re.match(pattern, filter_query.strip())

        if not match:
            raise ValueError(f"Invalid filter format: '{filter_query}'. "
                             f"Expected: '<attribute> <operator> <value>'")

        attribute = match.group(1)
        operator = match.group(2)
        value = match.group(3).strip()

        matching_node_ids: Set[str] = set()

        for node in graph.nodes.values():
            try:
                if self._node_matches_filter(node, attribute, operator, value):
                    matching_node_ids.add(node.id)
            except ValueError as e:
                raise ValueError(
                    f"Filter error on node '{node.id}': {e}"
                ) from e

        return self._build_subgraph(graph, matching_node_ids)

    @staticmethod
    def _node_matches_filter(node: Node, attribute: str, operator: str, value: str) -> bool:
        """
        Checks if node fits the filter.

        Args:
            node (Node): Node object which is being filtered.
            attribute (str): Attribute name.
            operator (str): Operator (==, <=, >=, <, >, !=).
            value (str): Value of the attribute.

        Returns:
            bool: True if node fits the filter.

        Raises:
            ValueError: If attribute is not valid.
        """
        if attribute not in node.attributes:
            return False

        attribute_value = node.attributes[attribute]
        filter_value = GraphOperations._convert_to_type(value, attribute_value)
        if filter_value is None:
            raise ValueError(
                f"Cannot convert '{value}' to {type(attribute_value).__name__} "
                f"for attribute '{attribute}'"
            )
        return GraphOperations._apply_operator(attribute_value, operator, filter_value)

    @staticmethod
    def _convert_to_type(value_str: str, example_value) -> any:
        """
        Convert string to data type.
        Types: int, float, str, bool

        Args:
            value_str (str): String value to be converted.
            example_value (any): Value of node attribute.

        Returns:
            Any: Value of attribute converted to data type.
        """
        if example_value is None:
            return value_str

        target_type = type(example_value)

        try:
            if target_type == int:
                return int(value_str)
            elif target_type == float:
                return float(value_str)
            elif target_type == bool:
                lower_val = value_str.lower()
                if lower_val in ('true', 'yes', '1'):
                    return True
                elif lower_val in ('false', 'no', '0'):
                    return False
                else:
                    return bool(value_str)
            else:
                if (value_str.startswith('"') and value_str.endswith('"')) or \
                        (value_str.startswith("'") and value_str.endswith("'")):
                    return value_str[1:-1]
                return value_str
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _apply_operator(attr_value, operator: str, filter_value) -> bool:
        """
        Apply operator to attribute.

        Args:
            attr_value (any): Value of attribute in node.
            operator (str): Operator (==, <=, >=, <, >, !=).
            filter_value (any): Value of attribute from filter query.

        Returns:
            bool: True if attribute fits the filter.

        Raises:
            ValueError: If operator is not valid.
        """
        if operator == "==":
            return attr_value == filter_value
        elif operator == "!=":
            return attr_value != filter_value
        elif operator == ">":
            return attr_value > filter_value
        elif operator == ">=":
            return attr_value >= filter_value
        elif operator == "<":
            return attr_value < filter_value
        elif operator == "<=":
            return attr_value <= filter_value
        else:
            raise ValueError(f"Unknown operator: {operator}")

    @staticmethod
    def _build_subgraph(original: Graph, node_ids: Set[str]) -> Graph:
        """
        Create subgraph based on nodes found, add necessary edges.

        Args:
            original (Graph): Graph object.
            node_ids (Set[str]): Set of node ids in subgraph.

        Returns:
            Graph: New graph object.
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
