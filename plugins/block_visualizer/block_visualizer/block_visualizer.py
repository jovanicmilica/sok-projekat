import json
from typing import Dict, List, Any
from api.visualizer import VisualizerPlugin
from api.models.graph import Graph
from datetime import date
import os


class BlockVisualizer(VisualizerPlugin):
    plugin_name = "block_visualizer"

    def render(self, graph: Graph) -> str:
        # Load files
        current_dir = os.path.dirname(os.path.abspath(__file__))

        # CSS
        css_path = os.path.join(current_dir, 'static', 'css', 'style.css')
        with open(css_path, 'r', encoding='utf-8') as f:
            css_content = f.read()

        # JS
        js_path = os.path.join(current_dir, 'static', 'js', 'visualization.js')
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()

        # HTML template
        html_path = os.path.join(current_dir, 'templates', 'base.html')
        with open(html_path, 'r', encoding='utf-8') as f:
            html_template = f.read()

        # Prepare data
        nodes_data = self._prepare_nodes_data(graph)
        edges_data = self._prepare_edges_data(graph)

        graph_data = {
            'nodes': nodes_data,
            'edges': edges_data
        }

        # Replace placeholders
        html = html_template.replace('{{CSS_CONTENT}}', css_content)
        html = html.replace('{{JS_CONTENT}}', js_content)
        html = html.replace('{{GRAPH_DATA}}', json.dumps(graph_data))

        return html

    def _prepare_nodes_data(self, graph: Graph) -> List[Dict[str, Any]]:
        nodes = []
        for node_id, node in graph.nodes.items():
            attributes = {}
            for key, value in node.attributes.items():
                if isinstance(value, date):
                    attributes[key] = value.isoformat()
                else:
                    attributes[key] = str(value)

            node_data = {
                'id': node_id,
                'attributes': attributes,
                'height': 50 + (len(attributes) * 20)
            }
            nodes.append(node_data)
        return nodes

    def _prepare_edges_data(self, graph: Graph) -> List[Dict[str, Any]]:
        edges = []
        for edge_id, edge in graph.edges.items():
            edges.append({
                'id': edge_id,
                'source': edge.source,
                'target': edge.target,
                'directed': graph.directed,
                'attributes': {k: str(v) for k, v in edge.attributes.items()}
            })
        return edges

    def get_name(self) -> str:
        return self.plugin_name
