# simple_visualizer/simple_visualizer.py
from typing import Dict, List, Tuple
from api.visualizer import VisualizerPlugin
from api.models.graph import Graph
from api.models.node import Node
from api.models.edge import Edge


class SimpleVisualizer(VisualizerPlugin):
    """
    Simple visualizer plugin that renders graph nodes as basic shapes.
    Each node is displayed as a circle with its ID or name.
    """

    plugin_name = "simple_visualizer"

    # Constants for layout configuration
    GRID_COLS = 5
    NODE_SPACING = 200
    MARGIN = 100
    NODE_RADIUS = 25
    MIN_SVG_WIDTH = 800
    MIN_SVG_HEIGHT = 600
    MAX_LABEL_LENGTH = 15

    def render(self, graph: Graph) -> str:
        """
        Generate a simple visual representation of the graph.

        Args:
            graph: The graph to visualize

        Returns:
            HTML string containing the visualization
        """
        css_styles = self._generate_styles()
        svg_dimensions = self._calculate_svg_dimensions(graph)
        svg_content = self._build_svg_content(graph, svg_dimensions)

        return css_styles + svg_content

    def _generate_styles(self) -> str:
        """Generate CSS styles for the visualization."""
        return """
        <style>
            .graph-container {
                width: 100%;
                height: 600px;
                border: 1px solid #ccc;
                background-color: #f9f9f9;
                overflow: auto;
                position: relative;
            }
            .graph-svg {
                width: 100%;
                height: 100%;
                min-width: 800px;
                min-height: 600px;
            }
            .node-circle {
                fill: #4CAF50;
                stroke: #333;
                stroke-width: 2;
                transition: fill 0.3s;
            }
            .node-circle:hover {
                fill: #45a049;
                cursor: pointer;
            }
            .node-label {
                fill: white;
                font-family: Arial, sans-serif;
                font-size: 12px;
                text-anchor: middle;
                dominant-baseline: middle;
                pointer-events: none;
            }
            .edge-line {
                stroke: #999;
                stroke-width: 2;
                stroke-linecap: round;
            }
            .edge-label {
                fill: #666;
                font-family: Arial, sans-serif;
                font-size: 10px;
                text-anchor: middle;
                paint-order: stroke;
                stroke: white;
                stroke-width: 2px;
                stroke-linecap: round;
                stroke-linejoin: round;
            }
        </style>
        """

    def _calculate_svg_dimensions(self, graph: Graph) -> Tuple[int, int]:
        """
        Calculate required SVG dimensions based on graph size.

        Returns:
            Tuple of (width, height)
        """
        num_nodes = len(graph.nodes)
        rows = (num_nodes + self.GRID_COLS - 1) // self.GRID_COLS

        width = max(self.MIN_SVG_WIDTH,
                    self.MARGIN * 2 + self.GRID_COLS * self.NODE_SPACING)
        height = max(self.MIN_SVG_HEIGHT,
                     self.MARGIN * 2 + rows * self.NODE_SPACING)

        return width, height

    def _build_svg_content(self, graph: Graph, dimensions: Tuple[int, int]) -> str:
        """
        Build the complete SVG content including edges and nodes.
        """
        width, height = dimensions

        svg_parts = ['<div class="graph-container">']
        svg_parts.append(
            f'<svg class="graph-svg" viewBox="0 0 {width} {height}" '
            f'preserveAspectRatio="xMidYMid meet">'
        )

        # Draw edges first (to be behind nodes)
        svg_parts.extend(self._draw_all_edges(graph))

        # Draw nodes on top
        svg_parts.extend(self._draw_all_nodes(graph))

        svg_parts.append('</svg>')
        svg_parts.append('</div>')

        return '\n'.join(svg_parts)

    def _draw_all_nodes(self, graph: Graph) -> List[str]:
        """Generate SVG for all nodes in the graph."""
        if not graph.nodes:
            return []

        node_positions = self._calculate_node_positions(graph)
        return [self._draw_single_node(node, node_positions[node.id])
                for node in graph.nodes.values()]

    def _draw_all_edges(self, graph: Graph) -> List[str]:
        """Generate SVG for all edges in the graph."""
        if not graph.edges:
            return []

        node_positions = self._calculate_node_positions(graph)
        return [self._draw_single_edge(edge, node_positions)
                for edge in graph.edges.values()]

    def _calculate_node_positions(self, graph: Graph) -> Dict[str, Tuple[float, float]]:
        """
        Calculate positions for all nodes based on grid layout.

        Returns:
            Dictionary mapping node_id to (x, y) coordinates
        """
        positions = {}
        node_list = list(graph.nodes.values())

        for index, node in enumerate(node_list):
            row = index // self.GRID_COLS
            col = index % self.GRID_COLS

            x = self.MARGIN + col * self.NODE_SPACING
            y = self.MARGIN + row * self.NODE_SPACING

            positions[node.id] = (x, y)

        return positions

    def _draw_single_node(self, node: Node, position: Tuple[float, float]) -> str:
        """
        Draw a single node as a circle with a label.
        """
        x, y = position
        label = self._get_node_label(node)

        return f"""
        <g class="node" data-node-id="{node.id}">
            <circle class="node-circle" cx="{x}" cy="{y}" r="{self.NODE_RADIUS}" />
            <text class="node-label" x="{x}" y="{y}">{label}</text>
        </g>
        """

    def _draw_single_edge(self, edge: Edge,
                          node_positions: Dict[str, Tuple[float, float]]) -> str:
        """
        Draw a single edge as a line between two nodes.
        """
        source_pos = node_positions.get(edge.source)
        target_pos = node_positions.get(edge.target)

        if not source_pos or not target_pos:
            return ""

        x1, y1 = source_pos
        x2, y2 = target_pos

        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2

        edge_label = edge.attributes.get('type', '')

        return f"""
        <g class="edge" data-edge-id="{edge.id}">
            <line class="edge-line" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" />
            <text class="edge-label" x="{mid_x}" y="{mid_y}">{edge_label}</text>
        </g>
        """

    def _get_node_label(self, node: Node) -> str:
        """
        Extract and truncate node label if necessary.
        """
        label = node.attributes.get('name', node.id)

        if len(label) > self.MAX_LABEL_LENGTH:
            label = label[:self.MAX_LABEL_LENGTH - 3] + '...'

        return label

    def get_name(self) -> str:
        """Return the name of the visualizer plugin."""
        return self.plugin_name
    