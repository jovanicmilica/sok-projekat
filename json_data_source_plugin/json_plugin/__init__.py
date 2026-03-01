"""
JSON Data Source Plugin for Graph Visualization Platform.

This plugin provides functionality to load graph data from JSON files.
"""

from .json_plugin import JSONSource

# Explicitly export the main class
__all__ = ['JSONSource']

# Add plugin metadata for discovery
__version__ = '0.1.0'
__plugin_name__ = 'json_source'
__plugin_type__ = 'data_source'
