import yaml
import os
from typing import Any, List, Type, Dict

from api.data_source import DataSourcePlugin
from api.models.graph import Graph
from api.models.graph import GraphBuilder


class YAMLSource(DataSourcePlugin):
    """
    YAMLSource is a data source plugin that provides functionality to read YAML data from a specified file path.
    Returns the data as a Graph object.
    """

    plugin_name = 'yaml_source'

    def __init__(self, graph_builder_class: Type[GraphBuilder]):
        self.graph_builder_class = graph_builder_class

    def parse(self, yaml_path: str, directed: bool = True, encoding: str = "utf-8", **kwargs) -> Graph:
        """
        Parse YAML file and return a Graph instance.

        Args:
            yaml_path: Path to the YAML file
            directed: Whether the graph should be directed or undirected
            encoding: File encoding to use when reading the YAML file (default: "utf-8")
            **kwargs: Additional parameters for future extensions

        Returns:
            Graph instance built from the YAML data

        Raises:
            FileNotFoundError: if the YAML file is not found
            yaml.YAMLError: if the YAML file is malformed
            ValueError: if the YAML structure is not as expected
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        try:
            with open(yaml_path, 'r', encoding=encoding) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML file: {e}")

        return self._build_from_dict(data, directed=directed)

    def _build_from_dict(self, data: Dict, directed: bool = True) -> Graph:
        """
        Builds a Graph instance from a dictionary representation of the graph data.
        Expected YAML structure:
        nodes:
          - id: node1
            label: Čvor 1
            weight: 10
          - id: node2
            label: Čvor 2
            weight: 20
        edges:
          - id: edge1
            source: node1
            target: node2
            weight: 5

        Args:
            data: Dictionary containing the graph data with 'nodes' and 'edges' keys
            directed: Whether the graph should be directed or undirected

        Returns:
            Graph instance built from the dictionary data

        Raises:
            ValueError: if the data structure is invalid (missing required fields, wrong types)
        """
        if not isinstance(data, dict):
            raise ValueError(f"YAML must be an object of type dict")

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
        Return the name of the data source plugin
        """
        return self.plugin_name

    @classmethod
    def get_parameters_spec(cls) -> List[Dict[str, Any]]:
        """
        Returns the parameter specification for this plugin.
        
        Returns:
            List of parameter definitions, each containing:
            - name: parameter name
            - type: parameter type (string, boolean, integer, etc.)
            - required: whether the parameter is required
            - default: default value (if any)
            - description: human-readable description
            - placeholder: placeholder text for input field
        """
        return [
            {
                'name': 'yaml_path',
                'type': 'string',
                'required': True,
                'description': 'Path to the YAML file containing graph data',
                'placeholder': '/path/to/graph.yaml'
            },
            {
                'name': 'directed',
                'type': 'boolean',
                'required': False,
                'default': True,
                'description': 'Whether the graph should be directed or undirected',
                'placeholder': 'true'
            },
            {
                'name': 'encoding',
                'type': 'string',
                'required': False,
                'default': 'utf-8',
                'description': 'File encoding (e.g., utf-8, latin-1)',
                'placeholder': 'utf-8'
            }
        ]
