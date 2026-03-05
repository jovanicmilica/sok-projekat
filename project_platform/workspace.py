import pickle
import os
from typing import Optional, List, Any

class Workspace:
    def __init__(self):
        self.name = ""
        self._filepath = None
        self.data_source_plugin = None
        self.visualizer_plugin = None
        self.graph = None
        self.search_queries: List[str] = []
        self.filter_queries: List[str] = []
            
    def set_name(self, name: str):
        self.name = name
        
    def get_name(self) -> str:
        return self.name
        
    def set_data_source_plugin(self, plugin_name: str):
        self.data_source_plugin = plugin_name
        
    def get_data_source_plugin(self) -> Optional[str]:
        return self.data_source_plugin
        
    def set_visualizer_plugin(self, plugin_name: str):
        self.visualizer_plugin = plugin_name
        
    def get_visualizer_plugin(self) -> Optional[str]:
        return self.visualizer_plugin
        
    def set_graph(self, graph):
        self.graph = graph
        
    def get_graph(self):
        return self.graph
            
    def set_search_queries(self, queries: List[str]):
        self.search_queries = queries.copy() if queries else []
        
    def get_search_queries(self) -> List[str]:
        return self.search_queries.copy()
        
    def set_filter_queries(self, queries: List[str]):
        self.filter_queries = queries.copy() if queries else []
        
    def get_filter_queries(self) -> List[str]:
        return self.filter_queries.copy()
    
    def get_filepath(self) -> Optional[str]:
        return self._filepath
    
    @classmethod
    def name_to_filepath(cls, name: str, directory: str = "workspaces") -> str:
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_')
        filename = f"{safe_name}.pkl" if safe_name else "workspace.pkl"
        
        if directory:
            return os.path.join(directory, filename)
        return filename
    
    def save(self, directory: str = "workspaces") -> str:
        """Saves the workspace to a file. Returns the filepath."""
        filepath = self.name_to_filepath(self.name, directory)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
            print(f"Workspace saved: {filepath}")
            self._filepath = filepath
            return filepath
        except Exception as e:
            print(f"Error saving workspace: {e}")
            raise
    
    @classmethod
    def load(cls, file: str) -> 'Workspace':
        """Loads a workspace from a file by name."""
        filepath = file

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                workspace = pickle.load(f)
            print(f"Workspace loaded from: {filepath}")
            return workspace
        except Exception as e:
            print(f"Error loading workspace: {e}")
            raise
    
    def __str__(self):
        return (f"Workspace(name='{self.name}', "
                f"filepath='{self._filepath}', "
                f"data_plugin={self.data_source_plugin}, "
                f"viz_plugin={self.visualizer_plugin}, "
                f"searches={len(self.search_queries)}, "
                f"filters={len(self.filter_queries)})")
    
    def __repr__(self):
        return self.__str__()