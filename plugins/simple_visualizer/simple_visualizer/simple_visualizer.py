import json
from api.visualizer import VisualizerPlugin
from api.models.graph import Graph
import os


class SimpleVisualizer(VisualizerPlugin):
    plugin_name = "simple_visualizer"

    def render(self, graph: Graph) -> str:
        # load files
        current_dir = os.path.dirname(os.path.abspath(__file__))

        with open(os.path.join(current_dir, 'static', 'css', 'style.css'), 'r', encoding='utf-8') as f:
            css_content = f.read()

        with open(os.path.join(current_dir, 'static', 'js', 'visualization.js'), 'r', encoding='utf-8') as f:
            js_content = f.read()

        with open(os.path.join(current_dir, 'templates', 'base.html'), 'r', encoding='utf-8') as f:
            html_template = f.read()

        # convert graph to dict
        graph_data = {
            'nodes': [
                {
                    'id': node_id,
                    'name': node.attributes.get('name') or node.attributes.get('label') or str(node_id),
                    'attributes': node.attributes
                }
                for node_id, node in graph.nodes.items()
            ],
            'edges': [
                {
                    'id': edge_id,
                    'source': edge.source,
                    'target': edge.target,
                    'type': edge.attributes.get('type', ''),
                    'attributes': edge.attributes
                }
                for edge_id, edge in graph.edges.items()
            ]
        }

        # Replace placeholders
        html = html_template.replace('{{CSS_CONTENT}}', css_content)
        html = html.replace('{{JS_CONTENT}}', js_content)
        html = html.replace('{{GRAPH_DATA}}', json.dumps(graph_data))

        return html

    def get_name(self) -> str:
        return self.plugin_name
