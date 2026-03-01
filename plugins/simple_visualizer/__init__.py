"""
Simple Visualizer Plugin for Graph Visualization Platform.

This plugin provides a simple visualization of graphs where nodes are
displayed as basic shapes (circles) with minimal information.
"""

from .simple_visualizer import SimpleVisualizer

__all__ = ['SimpleVisualizer']
__version__ = '0.1.0'
__plugin_name__ = 'simple_visualizer'
__plugin_type__ = 'visualizer'
