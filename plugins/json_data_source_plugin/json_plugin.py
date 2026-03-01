import json
import os
from typing import Dict, Type

from api.data_source import DataSourcePlugin
from api.models.graph import Graph
from api.models.graph import GraphBuilder


class JSONSource(DataSourcePlugin):
    """
    JSONSource is a data source plugin that provides functionality to read JSON data from a specified file path.
    Returns the data as a Graph object.
    """

    plugin_name = "json_source"

    def __init__(self, graph_builder_class: Type[GraphBuilder]):
        self.graph_builder_class = graph_builder_class

    def parse(self, json_path: str, directed: bool = True, encoding: str = "utf-8", **kwargs) -> Graph:
        """
        Parse JSON file and return a Graph instance.

        Args:
            json_path: Path to the JSON file
            directed: Whether the graph should be directed or undirected
            encoding: File encoding to use when reading the JSON file (default: "utf-8")
            **kwargs: Additional parameters for future extensions

        Returns:
            Graph instance built from the JSON data

        Raises:
            FileNotFoundError: if the JSON file is not found
            json.JSONDecodeError: if the JSON file is not valid
            ValueError: if the JSON structure is not as expected
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        try:
            with open(json_path, 'r', encoding=encoding) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON file: {e}", e.doc, e.pos)

        return self._build_from_dict(data, directed=directed)

    def parse_string(self, json_string: str, directed: bool = True) -> Graph:
        """
        Parse JSON string and return a Graph instance.

        Args:
            json_string: JSON string to parse
            directed: Whether the graph should be directed or undirected

        Returns:
            Graph instance built from the JSON data

        Raises:
            json.JSONDecodeError: if the JSON string is not valid
            ValueError: if the JSON structure is not as expected
        """
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Invalid JSON string: {e}", e.doc, e.pos)

        return self._build_from_dict(data, directed=directed)

    def _build_from_dict(self, data: Dict, directed: bool = True) -> Graph:
        """
        Builds a Graph instance from a dictionary representation of the graph data.
        Expected JSON structure:
        {
            "nodes": [
                {"id": "node1", "label": "Čvor 1", "weight": 10},
                {"id": "node2", "label": "Čvor 2", "weight": 20}
            ],
            "edges": [
                {"id": "edge1", "source": "node1", "target": "node2", "weight": 5}
            ]
        }

        Args:
            data: Dictionary containing the graph data with 'nodes' and 'edges' keys
            directed: Whether the graph should be directed or undirected

        Returns:
            Graph instance built from the dictionary data

        Raises:
            ValueError: if the data structure is invalid (missing required fields, wrong types)
        """
        if not isinstance(data, dict):
            raise ValueError("JSON must be an object of type dict")

        builder = self.graph_builder_class(directed=directed)

        # Add nodes
        nodes = data.get('nodes', [])
        if not isinstance(nodes, list):
            raise ValueError("'nodes' must be a list")

        for node_data in nodes:
            if not isinstance(node_data, dict):
                raise ValueError("Each node must be an object")

            node_id = node_data.get('id')
            if not node_id:
                raise ValueError("Each node must have an 'id' field")

            # Extract all other fields as properties
            properties = {k: v for k, v in node_data.items() if k != 'id'}
            builder.add_node(node_id, **properties)

        # Add edges
        edges = data.get('edges', [])
        if not isinstance(edges, list):
            raise ValueError("'edges' must be a list")

        for edge_data in edges:
            if not isinstance(edge_data, dict):
                raise ValueError("Each edge must be an object")

            edge_id = edge_data.get('id')
            source = edge_data.get('source')
            target = edge_data.get('target')

            if not all([edge_id, source, target]):
                raise ValueError("Each edge must have 'id', 'source', and 'target' fields")

            # All other fields are considered properties of the edge
            properties = {k: v for k, v in edge_data.items()
                          if k not in ['id', 'source', 'target']}

            builder.add_edge(edge_id, source, target, **properties)

        # Build graph
        return builder.build()

    def get_name(self) -> str:
        """
        Return the name of the data source plugin.
        """
        return self.plugin_name
