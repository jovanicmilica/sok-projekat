import importlib
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
    Discovers plugins by scanning the 'plugins' directory for packages that
    contain classes inheriting from DataSourcePlugin or VisualizerPlugin.
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
        """Searches the 'plugins' directory for valid plugin packages and loads them."""
        if self._loaded:
            return
                
        # Determine the path to the plugins directory
        current_file = Path(__file__).resolve()
        project_root = current_file.parent.parent
        plugins_dir = project_root / "plugins"
        
        if not plugins_dir.exists():
            self._loaded = True
            return
        
        
        if str(plugins_dir) not in sys.path:
            sys.path.insert(0, str(plugins_dir))
        
        plugin_folders = [f for f in plugins_dir.iterdir() if f.is_dir()]
        
        if not plugin_folders:
            self._loaded = True
            return
        
        for plugin_folder in plugin_folders:
            if not (plugin_folder / "__init__.py").exists():
                continue    # skip if not a package
            
            plugin_name = plugin_folder.name
            
            try:
                plugin_module = importlib.import_module(plugin_name)
                
                self._scan_package(plugin_module, plugin_name)
                
            except Exception as e:
                print(f"Error loading plugin '{plugin_name}': {e}")

        self._loaded = True

    def _scan_package(self, package, package_name):
        """Recursively scans a package for plugin classes"""
        if not hasattr(package, '__path__'):
            return
            
        for _, module_name, is_pkg in pkgutil.iter_modules(package.__path__):
            full_name = f"{package_name}.{module_name}"
            
            try:
                if is_pkg:
                    subpackage = importlib.import_module(full_name)
                    self._scan_package(subpackage, full_name)
                else:
                    module = importlib.import_module(full_name)
                    self._scan_module(module, full_name)
            except Exception as e:
                print(f"Error loading module {full_name}: {e}")

    def _scan_module(self, module, module_name):
        """Searches a module for classes that are plugins"""
        for name, obj in inspect.getmembers(module):
            if not inspect.isclass(obj):
                continue
                
            try:
                if (issubclass(obj, DataSourcePlugin) and 
                    obj != DataSourcePlugin and 
                    not inspect.isabstract(obj)):
                    
                    plugin_key = f"{module_name}.{name}"
                    self._data_plugins[plugin_key] = obj
                
                if (issubclass(obj, VisualizerPlugin) and 
                    obj != VisualizerPlugin and 
                    not inspect.isabstract(obj)):
                    
                    plugin_key = f"{module_name}.{name}"
                    self._visualizer_plugins[plugin_key] = obj
                    
            except TypeError:
                pass
            except Exception as e:
                print(f"Error checking plugin {name}: {e}")

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
                'module': key.rsplit('.', 1)[0]
            })
        
        for key, plugin_class in self._visualizer_plugins.items():
            info['visualizer_plugins'].append({
                'key': key,
                'class_name': plugin_class.__name__,
                'module': key.rsplit('.', 1)[0]
            })
        
        return info