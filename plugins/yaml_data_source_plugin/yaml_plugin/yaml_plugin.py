import yaml
import os
from typing import Any, List, Type, Dict

from api.data_source_base import BaseGraphSource
from api.models.graph import Graph
from api.models.graph import GraphBuilder


class YAMLSource(BaseGraphSource):
    """
    YAMLSource is a data source plugin that provides functionality to read YAML data from a specified file path.
    Returns the data as a Graph object.
    """

    plugin_name = 'yaml_source'

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
            ValueError: if the YAML file is malformed or structure is invalid
        """
        if not os.path.exists(yaml_path):
            raise FileNotFoundError(f"YAML file not found: {yaml_path}")

        try:
            with open(yaml_path, 'r', encoding=encoding) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML file: {e}") from e
        except UnicodeDecodeError as e:
            raise ValueError(
                f"Cannot decode YAML file with encoding '{encoding}': {e}") from e

        if data is None:
            raise ValueError("YAML file is empty")

        return self._parse_data(data, directed)

    def _build_from_dict(self, data: Dict, directed: bool = True) -> Graph:
        """Build graph from dict using base implementation."""
        return super()._build_from_dict(data, directed)

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
