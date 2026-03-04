from api.models.graph import GraphBuilder
from project_platform.plugin_manager import PluginManager


class GraphPlatform:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.plugin_manager = PluginManager()
            cls._instance.current_graph = None    
            cls._instance.current_data_plugin = None
            cls._instance.current_visualizer = None
            cls._instance.current_visualizer_instance = None  # za instancu vizualizera
        return cls._instance

    def get_data_source_plugins(self):
        return self.plugin_manager.get_all_data_plugin_names()
    
    def get_data_source_plugin_parameters(self, plugin_name: str):
        return self.plugin_manager.get_plugin_parameters(plugin_name)
    
    def get_visualizer_plugins(self):
        """Vraća listu svih dostupnih vizualizera"""
        return list(self.plugin_manager.get_visualizer_plugins().keys())
    
    def load_graph(self, data_source_plugin_name: str, visualizer_plugin_name: str, **parameters):
        """
        Load a graph using the specified data source plugin and parameters.
        
        Args:
            data_source_plugin_name: Name of the data source plugin to use
            visualizer_plugin_name: Name of the visualizer plugin to use (simple or block)
            **parameters: Parameters for the data source plugin
        """
        # 1. Load graph using data source plugin
        plugin_instance = self.plugin_manager.instantiate_data_plugin(
            data_source_plugin_name,
            graph_builder_class=GraphBuilder  
        )
        
        if not plugin_instance:
            raise ValueError(f"Cannot instantiate data plugin: {data_source_plugin_name}")
        
        graph = plugin_instance.parse(**parameters)
        
        # 2. Store current graph
        self.current_graph = graph
        self.current_data_plugin = data_source_plugin_name
        
        visualizer_map = {
            "simple-view": "simple",   
            "block-view": "block"      
        }
        
        visualizer_key = visualizer_map.get(visualizer_plugin_name)
        if not visualizer_key:
            raise ValueError(f"Unknown visualizer: {visualizer_plugin_name}")
        
        # 4. Get visualizer class
        visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_key)
        if not visualizer_class:
            raise ValueError(f"Visualizer plugin not found: {visualizer_key}")
        
        # 5. Instance visualizer and store it
        try:
            visualizer_instance = visualizer_class()
            self.current_visualizer_instance = visualizer_instance
            self.current_visualizer = visualizer_plugin_name
        except Exception as e:
            print(f"Error instantiating visualizer: {e}")
            raise
        
        return graph
    
    def render_current_graph(self):
        """Renderuje trenutni graf koristeći izabrani vizualizer"""
        if not self.current_graph:
            return "<div>No graph loaded</div>"
        
        if not self.current_visualizer_instance:
            return "<div>No visualizer selected</div>"
        
        try:
            # Render current graph
            return self.current_visualizer_instance.render(self.current_graph)
        except Exception as e:
            return f"<div>Error rendering graph: {e}</div>"