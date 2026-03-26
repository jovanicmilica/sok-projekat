"""
YAML Data Source Plugin for Graph Visualization Platform.

This plugin provides functionality to load graph data from YAML files.
"""

from .yaml_plugin import YAMLSource

# Explicitly export the main class
__all__ = ['YAMLSource']

# Add plugin metadata for discovery
__version__ = '0.1.0'
__plugin_name__ = 'yaml_source'
__plugin_type__ = 'data_source'
