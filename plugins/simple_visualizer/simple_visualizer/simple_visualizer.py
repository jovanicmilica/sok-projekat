import json
from html import escape
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

    def get_frontend_assets(self, graph: Graph) -> dict:
        nodes = {}
        for node_id, node in graph.nodes.items():
            label = node.attributes.get('name') or node.attributes.get('label') or str(node_id)
            subtitle = node.attributes.get('type') or node.attributes.get('category') or node_id
            nodes[str(node_id)] = {
                'html': (
                    '<div class="simple-visualizer-node">'
                    f'<div class="simple-node-label">{escape(str(label))}</div>'
                    f'<div class="simple-node-id">{escape(str(subtitle))}</div>'
                    '</div>'
                ),
                'width': 118,
                'height': 74,
            }

        return {
            'name': self.plugin_name,
            'css': """
.simple-visualizer-node {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 5px;
    border-radius: 999px;
    border: 2px solid #d7fff4;
    background: #39a88f;
    color: #ffffff;
    box-shadow: 0 10px 24px rgba(17, 122, 100, 0.28);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    text-align: center;
    padding: 10px 12px;
}
.simple-node-label {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 13px;
    font-weight: 800;
    line-height: 1.1;
}
.simple-node-id {
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    font-size: 10px;
    font-weight: 700;
    opacity: 0.82;
}
.main-node.is-selected .simple-visualizer-node,
.tree-node.is-selected .simple-visualizer-node {
    border-color: #fff6c7;
    box-shadow: 0 0 0 4px rgba(255, 223, 110, 0.3), 0 12px 26px rgba(17, 122, 100, 0.35);
}
.main-node.is-dragging .simple-visualizer-node {
    background: #f59f5a;
    border-color: #ffe0bd;
}
""",
            'nodes': nodes,
            'defaults': {
                'width': 118,
                'height': 74,
            },
        }

    def get_name(self) -> str:
        return self.plugin_name
