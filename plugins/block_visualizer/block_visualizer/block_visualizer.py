import json
from typing import Dict, List, Any
from html import escape
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

    def get_frontend_assets(self, graph: Graph) -> dict:
        nodes = {}
        for node in self._prepare_nodes_data(graph):
            attrs = node['attributes']
            attr_rows = ''.join(
                '<div class="block-node-row">'
                f'<span>{escape(str(key))}</span>'
                f'<strong>{escape(self._shorten(value, 28))}</strong>'
                '</div>'
                for key, value in attrs.items()
            )
            if not attr_rows:
                attr_rows = '<div class="block-node-empty">No attributes</div>'

            nodes[str(node['id'])] = {
                'html': (
                    '<div class="block-visualizer-node">'
                    f'<div class="block-node-title">{escape(str(node["id"]))}</div>'
                    f'<div class="block-node-attrs">{attr_rows}</div>'
                    '</div>'
                ),
                'width': 196,
                'height': node['height'],
            }

        return {
            'name': self.plugin_name,
            'css': """
.block-visualizer-node {
    width: 100%;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    border-radius: 8px;
    border: 2px solid #224f8f;
    background: #3178c6;
    color: #ffffff;
    box-shadow: 0 12px 24px rgba(18, 43, 79, 0.28);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
.block-node-title {
    padding: 8px 10px;
    background: rgba(10, 29, 56, 0.32);
    border-bottom: 1px solid rgba(255, 255, 255, 0.22);
    font-size: 12px;
    font-weight: 800;
    text-align: center;
    text-transform: uppercase;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.block-node-attrs {
    min-height: 0;
    padding: 7px 9px 9px;
    display: flex;
    flex-direction: column;
    gap: 5px;
}
.block-node-row {
    display: grid;
    grid-template-columns: minmax(0, 0.85fr) minmax(0, 1.15fr);
    gap: 7px;
    align-items: center;
    font-size: 10px;
    line-height: 1.25;
}
.block-node-row span,
.block-node-row strong {
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}
.block-node-row span {
    color: rgba(255, 255, 255, 0.72);
    font-weight: 700;
}
.block-node-row strong {
    color: #ffffff;
    font-weight: 800;
}
.block-node-empty {
    color: rgba(255, 255, 255, 0.75);
    font-size: 11px;
    text-align: center;
    padding-top: 10px;
}
.main-node.is-selected .block-visualizer-node,
.tree-node.is-selected .block-visualizer-node {
    border-color: #fff6c7;
    box-shadow: 0 0 0 4px rgba(255, 223, 110, 0.3), 0 14px 28px rgba(18, 43, 79, 0.35);
}
.main-node.is-dragging .block-visualizer-node {
    background: #f59f5a;
    border-color: #ffe0bd;
}
""",
            'nodes': nodes,
            'defaults': {
                'width': 196,
                'height': 86,
            },
        }

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
                'height': max(82, 48 + (len(attributes) * 22))
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

    def _shorten(self, value: Any, limit: int) -> str:
        text = str(value)
        if len(text) <= limit:
            return text
        return text[:limit - 3] + '...'

    def get_name(self) -> str:
        return self.plugin_name
