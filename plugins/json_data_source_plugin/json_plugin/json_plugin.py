import json
import os
from typing import Dict, Type, List, Any

from api.data_source_base import BaseGraphSource
from api.models.graph import Graph
from api.models.graph import GraphBuilder


class JSONSource(BaseGraphSource):
    """
    JSONSource is a data source plugin that provides functionality to read JSON data from a specified file path.
    Returns the data as a Graph object.
    """

    plugin_name = "json_source"

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
                'name': 'json_path',
                'type': 'string',
                'required': True,
                'description': 'Path to the JSON file containing graph data',
                'placeholder': '/path/to/graph.json'
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
            ValueError: if the JSON file is not valid
            ValueError: if the JSON structure is not as expected
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"JSON file not found: {json_path}")

        try:
            with open(json_path, 'r', encoding=encoding) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}") from e
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Cannot decode JSON file with encoding '{encoding}': {e}") from e

        return self._parse_data(data, directed)

    def parse_string(self, json_string: str, directed: bool = True) -> Graph:
        """Parse JSON string and return graph."""
        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON string: {e}") from e

        return self._parse_data(data, directed)

    def get_name(self) -> str:
        return self.plugin_name
