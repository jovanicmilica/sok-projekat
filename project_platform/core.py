import shlex
from datetime import datetime

from api.models.edge import Edge
from api.models.graph import Graph, GraphBuilder
from api.models.node import Node
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
            cls._instance.cli_operations = []
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
        self.cli_operations = list(workspace.get('operations') or [])
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
        workspace['operations'] = list(self.cli_operations or [])

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
        self.cli_operations = []

        visualizer_class = self.plugin_manager.get_visualizer_plugin_class(visualizer_plugin_name)
        if not visualizer_class:
            raise ValueError(f"Visualizer plugin not found: {visualizer_plugin_name}")

        self.current_visualizer_instance = visualizer_class()
        self.current_visualizer = visualizer_plugin_name

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
            normalized_operations.append({'type': operation_type, 'query': query})

        self.current_graph = graph
        self.cli_operations = normalized_operations
        workspace = self._get_active_workspace()
        workspace['current_graph'] = graph
        workspace['operations'] = normalized_operations
        return self._graph_payload(f"Applied {len(normalized_operations)} operation(s)", operations=normalized_operations)

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
            self._get_active_workspace()['visualizer_plugin'] = visualizer_plugin_name

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

    def execute_cli_command(self, command: str) -> dict:
        command = (command or '').strip()
        if not command:
            raise ValueError("Command is empty")
        try:
            tokens = shlex.split(command)
        except ValueError as e:
            raise ValueError(f"Invalid command syntax: {e}") from e
        if not tokens:
            raise ValueError("Command is empty")
        action = tokens[0].lower()
        if action == 'help':
            return self._graph_payload(self._help_text(), changed=False)
        if action == 'clear':
            return self._clear_graph()
        if action == 'create':
            return self._execute_create(tokens[1:])
        if action == 'edit':
            return self._execute_edit(tokens[1:])
        if action == 'delete':
            return self._execute_delete(tokens[1:])
        if action == 'filter':
            return self._execute_cli_filter(command, tokens[1:])
        if action == 'search':
            return self._execute_cli_search(command, tokens[1:])
        raise ValueError(f"Unknown command: {action}. Type 'help' for available commands.")

    def _ensure_graph(self):
        if not self.current_graph:
            self.current_graph = Graph(directed=True)
            self.original_graph = self.current_graph
        if not self.original_graph:
            self.original_graph = self.current_graph
        return self.current_graph

    def _execute_create(self, tokens: list[str]) -> dict:
        if not tokens:
            raise ValueError("Expected: create node|edge ...")
        target = tokens[0].lower()
        if target == 'node':
            options, positional = self._parse_cli_options(tokens[1:])
            node_id = options.get('id') or (positional[0] if positional else None)
            if not node_id:
                raise ValueError("Node id is required: create node --id=1")
            graph = self._ensure_graph()
            if node_id in graph.nodes:
                raise ValueError(f"Node already exists: {node_id}")
            graph.nodes[node_id] = Node(node_id, options.get('properties', {}))
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Created node {node_id}")
        if target == 'edge':
            options, positional = self._parse_cli_options(tokens[1:])
            if len(positional) < 2:
                raise ValueError("Edge source and target are required: create edge --id=e1 source target")
            source, target_node = positional[-2], positional[-1]
            edge_id = options.get('id') or f"{source}->{target_node}"
            graph = self._ensure_graph()
            if edge_id in graph.edges:
                raise ValueError(f"Edge already exists: {edge_id}")
            if source not in graph.nodes:
                raise ValueError(f"Source node does not exist: {source}")
            if target_node not in graph.nodes:
                raise ValueError(f"Target node does not exist: {target_node}")
            graph.edges[edge_id] = Edge(edge_id, source, target_node, options.get('properties', {}))
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Created edge {edge_id}")
        raise ValueError("Expected: create node|edge ...")

    def _execute_edit(self, tokens: list[str]) -> dict:
        if not tokens:
            raise ValueError("Expected: edit node|edge ...")
        target = tokens[0].lower()
        options, positional = self._parse_cli_options(tokens[1:])
        item_id = options.get('id') or (positional[0] if positional else None)
        if not item_id:
            raise ValueError(f"{target.capitalize()} id is required")
        graph = self._ensure_graph()
        properties = options.get('properties', {})
        if target == 'node':
            if item_id not in graph.nodes:
                raise ValueError(f"Node not found: {item_id}")
            graph.nodes[item_id].attributes.update(properties)
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Edited node {item_id}")
        if target == 'edge':
            if item_id not in graph.edges:
                raise ValueError(f"Edge not found: {item_id}")
            graph.edges[item_id].attributes.update(properties)
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Edited edge {item_id}")
        raise ValueError("Expected: edit node|edge ...")

    def _execute_delete(self, tokens: list[str]) -> dict:
        if not tokens:
            raise ValueError("Expected: delete node|edge ...")
        target = tokens[0].lower()
        options, positional = self._parse_cli_options(tokens[1:])
        item_id = options.get('id') or (positional[0] if positional else None)
        if not item_id:
            raise ValueError(f"{target.capitalize()} id is required")
        graph = self._ensure_graph()
        if target == 'node':
            if item_id not in graph.nodes:
                raise ValueError(f"Node not found: {item_id}")
            connected_edges = [edge.id for edge in graph.edges.values() if edge.source == item_id or edge.target == item_id]
            if connected_edges:
                raise ValueError(f"Cannot delete node {item_id}; delete connected edges first: {', '.join(connected_edges)}")
            del graph.nodes[item_id]
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Deleted node {item_id}")
        if target == 'edge':
            if item_id not in graph.edges:
                raise ValueError(f"Edge not found: {item_id}")
            del graph.edges[item_id]
            self._sync_original_graph_after_mutation()
            return self._graph_payload(f"Deleted edge {item_id}")
        raise ValueError("Expected: delete node|edge ...")

    def _execute_cli_filter(self, raw_command: str, tokens: list[str]) -> dict:
        query = self._extract_query(raw_command, 'filter', tokens)
        if not self.original_graph:
            raise ValueError("No graph loaded")
        parts = [part.strip() for part in query.split('&&') if part.strip()]
        if not parts:
            raise ValueError("Filter query is empty")
        operations = self.cli_operations + [{'type': 'filter', 'query': part} for part in parts]
        return self.apply_operations(operations)

    def _execute_cli_search(self, raw_command: str, tokens: list[str]) -> dict:
        query = self._extract_query(raw_command, 'search', tokens)
        if not self.original_graph:
            raise ValueError("No graph loaded")
        if '=' in query and all(operator not in query for operator in ('==', '!=', '>=', '<=', '>', '<')):
            query = query.split('=', 1)[1].strip()
        operations = self.cli_operations + [{'type': 'search', 'query': query}]
        return self.apply_operations(operations)

    def _clear_graph(self) -> dict:
        self.current_graph = Graph(directed=True)
        self.original_graph = self.current_graph
        self.cli_operations = []
        self._store_runtime_in_workspace()
        return self._graph_payload("Cleared graph", operations=[])

    def _parse_cli_options(self, tokens: list[str]) -> tuple[dict, list[str]]:
        options = {'properties': {}}
        positional = []
        index = 0
        while index < len(tokens):
            token = tokens[index]
            if token == '--property':
                index += 1
                if index >= len(tokens):
                    raise ValueError("--property requires key=value")
                key, value = self._parse_key_value(tokens[index])
                options['properties'][key] = self._parse_value(value)
            elif token.startswith('--property='):
                key, value = self._parse_key_value(token.split('=', 1)[1])
                options['properties'][key] = self._parse_value(value)
            elif token == '--id':
                index += 1
                if index >= len(tokens):
                    raise ValueError("--id requires a value")
                options['id'] = tokens[index]
            elif token.startswith('--id='):
                options['id'] = token.split('=', 1)[1]
            else:
                positional.append(token)
            index += 1
        return options, positional

    def _parse_key_value(self, token: str) -> tuple[str, str]:
        if '=' not in token:
            raise ValueError(f"Expected key=value, got: {token}")
        key, value = token.split('=', 1)
        if not key:
            raise ValueError("Property name cannot be empty")
        return key, value

    def _parse_value(self, value: str):
        lower = value.lower()
        if lower in ('true', 'yes'):
            return True
        if lower in ('false', 'no'):
            return False
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        try:
            return datetime.strptime(value, '%Y-%m-%d').date()
        except ValueError:
            return value

    def _extract_query(self, raw_command: str, action: str, tokens: list[str]) -> str:
        if tokens:
            return ' '.join(tokens).strip()
        return raw_command[len(action):].strip()

    def _sync_original_graph_after_mutation(self):
        self.original_graph = self.current_graph
        self.cli_operations = []
        self._store_runtime_in_workspace()

    def _graph_payload(self, message: str, changed: bool = True, operations: list[dict] = None) -> dict:
        graph = self.current_graph or Graph(directed=True)
        workspace = self._get_active_workspace()
        workspace['current_graph'] = self.current_graph
        workspace['original_graph'] = self.original_graph
        workspace['operations'] = self.cli_operations if operations is None else operations
        return {
            'status': 'success',
            'message': message,
            'changed': changed,
            'graph': graph.to_json(),
            'operations': self.cli_operations if operations is None else operations,
            'visualizer_assets': self.get_current_visualizer_assets(),
            'node_count': len(graph.nodes),
            'edge_count': len(graph.edges),
            'workspace': self._workspace_summary(workspace),
            'workspaces': self.list_workspaces(),
        }

    def _help_text(self) -> str:
        return (
            "Commands:\n"
            "create node --id=1 --property Name=Alice --property Age=25\n"
            "create edge --id=e1 --property Name=Siblings 1 2\n"
            "edit node --id=2 --property Age=40\n"
            "edit edge --id=e1 --property Name=Friend\n"
            "delete node --id=2\n"
            "delete edge --id=e1\n"
            "filter 'Age>30 && Height>=150'\n"
            "search 'Name=Tom'\n"
            "clear\n"
            "help"
        )
