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
            cls._instance.current_visualizer_instance = None
            cls._instance.graph_operations = GraphOperations()
            cls._instance.workspaces = {}
            cls._instance.active_workspace_id = None
            cls._instance.workspace_sequence = 1
            cls._instance._create_initial_workspace()
        return cls._instance

    def _create_initial_workspace(self):
        self.workspaces['default'] = self._empty_workspace('default', 'Default Workspace')
        self.active_workspace_id = 'default'

    def _empty_workspace(self, workspace_id: str, name: str) -> dict:
        return {
            'id': workspace_id,
            'name': name,
            'original_graph': None,
            'current_graph': None,
            'data_source_plugin': None,
            'visualizer_plugin': None,
            'parameters': {},
            'operations': [],
        }

    def _get_active_workspace(self) -> dict:
        if self.active_workspace_id not in self.workspaces:
            self._create_initial_workspace()
        return self.workspaces[self.active_workspace_id]

    def _set_runtime_from_workspace(self, workspace: dict):
        self.original_graph = workspace.get('original_graph')
        self.current_graph = workspace.get('current_graph')
        self.current_data_plugin = workspace.get('data_source_plugin')
        self.current_visualizer = workspace.get('visualizer_plugin')
        self.current_visualizer_instance = None

        if self.current_visualizer:
            visualizer_class = self.plugin_manager.get_visualizer_plugin_class(self.current_visualizer)
            if visualizer_class:
                self.current_visualizer_instance = visualizer_class()

    def _store_runtime_in_workspace(self):
        workspace = self._get_active_workspace()
        workspace['original_graph'] = self.original_graph
        workspace['current_graph'] = self.current_graph
        workspace['data_source_plugin'] = self.current_data_plugin
        workspace['visualizer_plugin'] = self.current_visualizer

    def _graph_to_json(self, graph):
        if not graph:
            return {'nodes': {}, 'edges': [], 'directed': True}
        return graph.to_json()

    def _workspace_summary(self, workspace: dict) -> dict:
        graph = workspace.get('current_graph')
        return {
            'id': workspace['id'],
            'name': workspace['name'],
            'active': workspace['id'] == self.active_workspace_id,
            'has_graph': graph is not None,
            'node_count': len(graph.nodes) if graph else 0,
            'edge_count': len(graph.edges) if graph else 0,
            'data_source_plugin': workspace.get('data_source_plugin'),
            'visualizer_plugin': workspace.get('visualizer_plugin'),
            'operations_count': len(workspace.get('operations') or []),
        }

    def _workspace_payload(self, workspace: dict = None) -> dict:
        workspace = workspace or self._get_active_workspace()
        self._set_runtime_from_workspace(workspace)
        graph = workspace.get('current_graph')

        return {
            'workspace': self._workspace_summary(workspace),
            'workspaces': self.list_workspaces(),
            'graph': self._graph_to_json(graph),
            'operations': workspace.get('operations') or [],
            'visualizer_assets': self.get_current_visualizer_assets(),
        }

    def get_data_source_plugins(self):
        return self.plugin_manager.get_all_data_plugin_names()

    def get_data_source_plugin_parameters(self, plugin_name: str):
        return self.plugin_manager.get_plugin_parameters(plugin_name)

    def get_visualizer_plugins(self):
        return list(self.plugin_manager.get_visualizer_plugins().keys())

    def load_graph(self, data_source_plugin_name: str, visualizer_plugin_name: str, **parameters):
        plugin_instance = self.plugin_manager.instantiate_data_plugin(
            data_source_plugin_name,
            graph_builder_class=GraphBuilder
        )

        if not plugin_instance:
            raise ValueError(f"Cannot instantiate data plugin: {data_source_plugin_name}")

        graph = plugin_instance.parse(**parameters)

        self.original_graph = graph
        self.current_graph = graph
        self.current_data_plugin = data_source_plugin_name

        visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_plugin_name)
        if not visualizer_class:
            raise ValueError(f"Visualizer plugin not found: {visualizer_plugin_name}")

        try:
            visualizer_instance = visualizer_class()
            self.current_visualizer_instance = visualizer_instance
            self.current_visualizer = visualizer_plugin_name
        except Exception as e:
            print(f"Error instantiating visualizer: {e}")
            raise

        workspace = self._get_active_workspace()
        workspace['original_graph'] = graph
        workspace['current_graph'] = graph
        workspace['data_source_plugin'] = data_source_plugin_name
        workspace['visualizer_plugin'] = visualizer_plugin_name
        workspace['parameters'] = dict(parameters)
        workspace['operations'] = []

        return graph

    def apply_operations(self, operations: list[dict]) -> dict:
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
        workspace = self._get_active_workspace()
        workspace['current_graph'] = graph
        workspace['operations'] = normalized_operations

        return {
            'graph': graph.to_json(),
            'operations': normalized_operations,
            'visualizer_assets': self.get_current_visualizer_assets(),
            'node_count': len(graph.nodes),
            'edge_count': len(graph.edges),
            'workspaces': self.list_workspaces(),
            'workspace': self._workspace_summary(workspace),
        }

    def render_current_graph(self):
        if not self.current_graph:
            return "<div>No graph loaded</div>"

        if not self.current_visualizer_instance:
            return "<div>No visualizer selected</div>"

        try:
            return self.current_visualizer_instance.render(self.current_graph)
        except Exception as e:
            return f"<div>Error rendering graph: {e}</div>"

    def get_current_visualizer_assets(self, visualizer_plugin_name: str = None):
        if visualizer_plugin_name and visualizer_plugin_name != 'none':
            visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_plugin_name)
            if not visualizer_class:
                raise ValueError(f"Visualizer plugin not found: {visualizer_plugin_name}")
            self.current_visualizer_instance = visualizer_class()
            self.current_visualizer = visualizer_plugin_name
            workspace = self._get_active_workspace()
            workspace['visualizer_plugin'] = visualizer_plugin_name

        if not self.current_graph or not self.current_visualizer_instance:
            return {
                'name': self.current_visualizer,
                'css': '',
                'nodes': {},
                'defaults': {'width': 96, 'height': 64},
            }

        return self.current_visualizer_instance.get_frontend_assets(self.current_graph)

    def get_active_workspace_payload(self) -> dict:
        return self._workspace_payload(self._get_active_workspace())

    def list_workspaces(self) -> list[dict]:
        return [self._workspace_summary(workspace) for workspace in self.workspaces.values()]

    def create_workspace(self, name: str) -> dict:
        clean_name = (name or '').strip() or f"Workspace {self.workspace_sequence}"
        workspace_id = f"ws_{self.workspace_sequence}"
        self.workspace_sequence += 1

        while workspace_id in self.workspaces:
            workspace_id = f"ws_{self.workspace_sequence}"
            self.workspace_sequence += 1

        workspace = self._empty_workspace(workspace_id, clean_name)
        self.workspaces[workspace_id] = workspace
        self.active_workspace_id = workspace_id
        self._set_runtime_from_workspace(workspace)
        return self._workspace_payload(workspace)

    def switch_workspace(self, workspace_id: str) -> dict:
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace not found: {workspace_id}")

        self.active_workspace_id = workspace_id
        workspace = self.workspaces[workspace_id]
        self._set_runtime_from_workspace(workspace)
        return self._workspace_payload(workspace)

    def save_workspace(self, workspace_id: str = None, name: str = None) -> dict:
        if workspace_id:
            if workspace_id not in self.workspaces:
                raise ValueError(f"Workspace not found: {workspace_id}")
            workspace = self.workspaces[workspace_id]
        else:
            workspace = self._get_active_workspace()

        if name and name.strip():
            workspace['name'] = name.strip()

        if workspace['id'] == self.active_workspace_id:
            self._store_runtime_in_workspace()

        return self._workspace_payload(workspace)

    def delete_workspace(self, workspace_id: str) -> dict:
        if workspace_id == 'default':
            raise ValueError("Default workspace cannot be deleted")
        if workspace_id not in self.workspaces:
            raise ValueError(f"Workspace not found: {workspace_id}")

        del self.workspaces[workspace_id]

        if self.active_workspace_id == workspace_id:
            self.active_workspace_id = 'default'
            self._set_runtime_from_workspace(self.workspaces['default'])

        return self._workspace_payload(self._get_active_workspace())
