from abc import abstractmethod
from typing import Any, Dict, Type

from api.data_source import DataSourcePlugin
from api.models.graph import Graph, GraphBuilder


class BaseGraphSource(DataSourcePlugin):
    """Base class for graph data source plugins."""

    def __init__(self, graph_builder_class: Type[GraphBuilder]):
        self.graph_builder_class = graph_builder_class

    def _coerce_bool(self, value: Any, field_name: str) -> bool:
        """Convert bool-ish values to bool."""
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            normalized = value.strip().lower()
            if normalized in {"true", "1", "yes", "y", "on"}:
                return True
            if normalized in {"false", "0", "no", "n", "off"}:
                return False

        if isinstance(value, (int, float)):
            if value == 1:
                return True
            if value == 0:
                return False

        raise ValueError(f"'{field_name}' must be a boolean value")

    def _normalize_id(self, raw_id: Any, field_name: str) -> str:
        """Normalize ID to non-empty string."""
        if raw_id is None:
            raise ValueError(f"'{field_name}' cannot be null")

        normalized = str(raw_id).strip()
        if normalized == "":
            raise ValueError(f"'{field_name}' cannot be empty")

        return normalized

    def _parse_data(self, data: Dict, directed: Any) -> Graph:
        """Parse data dict with coerced directed parameter."""
        return self._build_from_dict(data, directed=self._coerce_bool(directed, "directed"))

    def _build_from_dict(self, data: Dict, directed: bool = True) -> Graph:
        """Build graph from dict with nodes and edges."""
        if data is None:
            raise ValueError("Data cannot be null")

        if not isinstance(data, dict):
            raise ValueError("Data must be a dict")

        builder = self.graph_builder_class(directed=directed)
        node_ids = set()
        edge_ids = set()

        # Add nodes
        nodes = data.get('nodes', [])
        if not isinstance(nodes, list):
            raise ValueError("'nodes' must be a list")

        for node_data in nodes:
            if not isinstance(node_data, dict):
                raise ValueError("Each node must be an object")

            if 'id' not in node_data:
                raise ValueError("Each node must have an 'id' field")

            node_id = self._normalize_id(node_data.get('id'), 'id')
            if node_id in node_ids:
                raise ValueError(f"Duplicate node id found: {node_id}")
            node_ids.add(node_id)

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

            required_fields = ['id', 'source', 'target']
            missing = [
                field for field in required_fields if field not in edge_data]
            if missing:
                raise ValueError(
                    "Each edge must have 'id', 'source', and 'target' fields")

            edge_id = self._normalize_id(edge_data.get('id'), 'id')
            source = self._normalize_id(edge_data.get('source'), 'source')
            target = self._normalize_id(edge_data.get('target'), 'target')

            if edge_id in edge_ids:
                raise ValueError(f"Duplicate edge id found: {edge_id}")
            edge_ids.add(edge_id)

            if source not in node_ids:
                raise ValueError(
                    f"Edge '{edge_id}' references unknown source node: {source}")
            if target not in node_ids:
                raise ValueError(
                    f"Edge '{edge_id}' references unknown target node: {target}")

            # All other fields are considered properties of the edge
            properties = {k: v for k, v in edge_data.items()
                          if k not in ['id', 'source', 'target']}

            builder.add_edge(edge_id, source, target, **properties)

        # Build graph
        return builder.build()

    @abstractmethod
    def get_name(self) -> str:
        """Return the name of the data source plugin."""
        pass
