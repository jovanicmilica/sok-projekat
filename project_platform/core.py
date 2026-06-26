from api.models.graph import GraphBuilder
from project_platform.graph_operations import GraphOperations
from project_platform.plugin_manager import PluginManager


class GraphPlatform:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.plugin_manager = PluginManager()
            cls._instance.original_graph = None
            cls._instance.current_graph = None
            cls._instance.current_data_plugin = None
            cls._instance.current_visualizer = None
            cls._instance.current_visualizer_instance = None  # za instancu vizualizera
            cls._instance.graph_operations = GraphOperations()
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
        self.original_graph = graph
        self.current_graph = graph
        self.current_data_plugin = data_source_plugin_name
        
        # 4. Get visualizer class
        visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_plugin_name)
        if not visualizer_class:
            raise ValueError(f"Visualizer plugin not found: {visualizer_plugin_name}")
        
        # 5. Instance visualizer and store it
        try:
            visualizer_instance = visualizer_class()
            self.current_visualizer_instance = visualizer_instance
            self.current_visualizer = visualizer_plugin_name
        except Exception as e:
            print(f"Error instantiating visualizer: {e}")
            raise
        
        return graph
    

    def apply_operations(self, operations: list[dict]) -> dict:
        """
        Apply search/filter operations successively from the original graph.
        """
        if not self.original_graph:
            raise ValueError("No graph loaded")

        graph = self.original_graph
        normalized_operations = []

        for operation in operations or []:
            operation_type = operation.get('type')
            query = operation.get('query', '')

            if operation_type == 'search':
                graph = self.graph_operations.search(graph, query)
            elif operation_type == 'filter':
                graph = self.graph_operations.filter(graph, query)
            else:
                raise ValueError(f"Unknown graph operation: {operation_type}")

            normalized_operations.append({
                'type': operation_type,
                'query': query,
            })

        self.current_graph = graph

        return {
            'graph': graph.to_json(),
            'operations': normalized_operations,
            'visualizer_assets': self.get_current_visualizer_assets(),
            'node_count': len(graph.nodes),
            'edge_count': len(graph.edges),
        }

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

    def get_current_visualizer_assets(self, visualizer_plugin_name: str = None):
        """Return HTML/CSS assets for the current frontend visualizer."""
        if visualizer_plugin_name and visualizer_plugin_name != 'none':
            visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_plugin_name)
            if not visualizer_class:
                raise ValueError(f"Visualizer plugin not found: {visualizer_plugin_name}")
            self.current_visualizer_instance = visualizer_class()
            self.current_visualizer = visualizer_plugin_name

        if not self.current_graph or not self.current_visualizer_instance:
            return {
                'name': self.current_visualizer,
                'css': '',
                'nodes': {},
                'defaults': {'width': 96, 'height': 64},
            }

        return self.current_visualizer_instance.get_frontend_assets(self.current_graph)
