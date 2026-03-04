"""
YAML Data Source Plugin for Graph Visualization Platform.

This plugin provides functionality to load graph data from YAML files.
"""

from plugins.yaml_data_source_plugin.yaml_plugin.yaml_plugin import YAMLSource

# Explicitly export the main class
_all_ = ['YAMLSource']

# Add plugin metadata for discovery
_version_ = '0.1.0'
_plugin_name_ = 'yaml_source'
_plugin_type_ = 'data_source'