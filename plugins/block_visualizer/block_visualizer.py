from api.visualizer import VisualizerPlugin
from api.models.graph import Graph
from datetime import date
import json
from typing import Dict, List, Any
import os


class BlockVisualizer(VisualizerPlugin):
    """
    Visualizer represents nodes as blocks with their attributes listed inside,
    and edges as lines connecting the blocks.
    """

    def get_name(self) -> str:
        return "Block Visualizer"

    def render(self, graph: Graph) -> str:
        if not graph or not graph.nodes:
            return self._render_empty_graph()

        nodes_data = self._prepare_nodes_data(graph)
        edges_data = self._prepare_edges_data(graph)

        return self._generate_html(nodes_data, edges_data)

    def _render_empty_graph(self) -> str:
        return """
        <div class="alert alert-info" style="padding: 20px; text-align: center;">
            <h3>Graph is empty</h3>
            <p>There are no nodes or edges to display. Please add some data to visualize.</p>
        </div>
        """

    def _prepare_nodes_data(self, graph: Graph) -> List[Dict[str, Any]]:
        nodes_data = []
        for node_id, node in graph.nodes.items():
            attrs_for_display = {}
            for key, value in node.attributes.items():
                if isinstance(value, date):
                    attrs_for_display[key] = value.isoformat()
                else:
                    attrs_for_display[key] = str(value)

            nodes_data.append({
                "id": node_id,
                "attributes": attrs_for_display,
                "x": 0,
                "y": 0,
                "height": 40 + (len(attrs_for_display) * 20)
            })
        return nodes_data

    def _prepare_edges_data(self, graph: Graph) -> List[Dict[str, Any]]:
        edges_data = []
        for edge_id, edge in graph.edges.items():
            edges_data.append({
                "id": edge_id,
                "source": edge.source,
                "target": edge.target,
                "directed": graph.directed,
                "attributes": {k: str(v) for k, v in edge.attributes.items()}
            })
        return edges_data

    def _generate_html(self, nodes: List[Dict], edges: List[Dict]) -> str:
        # Convert nodes and edges to JSON strings
        nodes_json = json.dumps(nodes, ensure_ascii=False)
        edges_json = json.dumps(edges, ensure_ascii=False)

        # Load HTML template
        template_path = os.path.join(os.path.dirname(__file__), 'templates', 'base.html')

        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template = f.read()
        except FileNotFoundError:
            return f"<pre>Error loading template: {template_path} not found.</pre>"

        html = template.replace('{{ NODES_JSON }}', nodes_json)
        html = html.replace('{{ EDGES_JSON }}', edges_json)

        return html
