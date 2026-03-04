import importlib
import importlib.metadata
import inspect
import pkgutil
import sys
from pathlib import Path
from typing import Dict, Type, Optional

from api.data_source import DataSourcePlugin
from api.visualizer import VisualizerPlugin


class PluginManager:
    """
    Manages discovery and access to data source and visualizer plugins.
    Discovers plugins ONLY via entry points (installed packages).
    """
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._data_plugins: Dict[str, Type[DataSourcePlugin]] = {}
        self._visualizer_plugins: Dict[str, Type[VisualizerPlugin]] = {}
        self._loaded = False
        self._initialized = True

    def _load_plugins(self):
        """Loads plugins ONLY from installed packages via entry points."""
        if self._loaded:
            return

        self._load_installed_plugins()

        self._loaded = True

    def _load_installed_plugins(self):
        """
        Finds plugins (pip install -e .)
        Uses Python 'entry points' mechanism to discover plugins defined in installed packages.
        """

        try:
            # load data source plugins
            entry_points = importlib.metadata.entry_points()

            if hasattr(entry_points, 'select'):
                data_eps = entry_points.select(group='graph_platform.data_sources')
                vis_eps = entry_points.select(group='graph_platform.visualizers')
            else:
                data_eps = entry_points.get('graph_platform.data_sources', [])
                vis_eps = entry_points.get('graph_platform.visualizers', [])

            # load data source plugins
            for entry_point in data_eps:
                try:
                    # first import the module
                    module = importlib.import_module(entry_point.module)

                    # then get the plugin class
                    plugin_class = getattr(module, entry_point.attr)

                    # register the plugin class with the name from the entry point
                    self._data_plugins[entry_point.name] = plugin_class
                    print(f"Loaded data plugin: {entry_point.name}")

                except Exception as e:
                    print(f"Error loading {entry_point.name}: {type(e).__name__}: {e}")

            # load visualizer plugins
            for entry_point in vis_eps:
                try:
                    module = importlib.import_module(entry_point.module)
                    plugin_class = getattr(module, entry_point.attr)

                    self._visualizer_plugins[entry_point.name] = plugin_class
                    print(f"Loaded visualizer plugin: {entry_point.name}")

                except Exception as e:
                    print(f"Error loading {entry_point.name}: {type(e).__name__}: {e}")

        except Exception as e:
            print(f"Error discovering plugins: {e}")

    def get_data_source_plugins(self) -> Dict[str, Type[DataSourcePlugin]]:
        self._load_plugins()
        return self._data_plugins

    def get_visualizer_plugins(self) -> Dict[str, Type[VisualizerPlugin]]:
        self._load_plugins()
        return self._visualizer_plugins

    def get_data_plugin_class(self, name: str) -> Optional[Type[DataSourcePlugin]]:
        self._load_plugins()
        return self._data_plugins.get(name)

    def get_visualizer_plugin_class(self, name: str) -> Optional[Type[VisualizerPlugin]]:
        self._load_plugins()
        return self._visualizer_plugins.get(name)

    def instantiate_data_plugin(self, name: str, **kwargs):
        plugin_class = self.get_data_plugin_class(name)
        if plugin_class:
            try:
                return plugin_class(**kwargs)
            except Exception as e:
                print(f"Error instantiating {name}: {e}")
        return None

    def get_all_plugin_info(self) -> Dict:
        """Returns information about all loaded plugins"""
        self._load_plugins()

        info = {
            'data_plugins': [],
            'visualizer_plugins': []
        }

        for key, plugin_class in self._data_plugins.items():
            info['data_plugins'].append({
                'key': key,
                'class_name': plugin_class.__name__,
                'module': key  # module is the same as key
            })

        for key, plugin_class in self._visualizer_plugins.items():
            info['visualizer_plugins'].append({
                'key': key,
                'class_name': plugin_class.__name__,
                'module': key
            })

        return info
