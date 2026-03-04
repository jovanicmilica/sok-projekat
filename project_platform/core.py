from project_platform.plugin_manager import PluginManager


class GraphPlatform:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.plugin_manager = PluginManager()
        return cls._instance

    def get_data_source_plugins(self):
        return self.plugin_manager.get_all_data_plugin_names()
