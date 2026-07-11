# Graph Visualization Application

## Team members
- Milica Jovanić SV 9/2023
- Danica Komatović SV 20/2023
- Lana Mirkov SV 23/2023
- Ana Paroški SV 53/2023

## Project Overview
This project is a modular, plugin-based platform for visualizing graph data structures. It allows users to load graph data from various sources and visualize it in multiple synchronized ways within a single web interface. The project's main goal is to demonstrate object-oriented design and a clean plugin architecture: the core platform never depends on a concrete data format or a concrete rendering style — it only depends on abstract contracts (`DataSourcePlugin`, `VisualizerPlugin`), and concrete implementations are discovered dynamically at runtime.

The platform supports loading data from different sources via **Data Source Plugins** and visualizing the resulting graph via **Visualizer Plugins**. A web application (built with Django) integrates the platform and plugins, providing an interactive UI with three synchronized views of the graph: Main View, Tree View, and Bird View.

## Key Features
- **Modular / plugin architecture** — the core platform (`project_platform/`) talks to independently developed and installed plugins only through the abstract API defined in `api/`.
- **Multiple data sources** — load graphs from JSON or YAML files via dedicated Data Source Plugins; new formats can be added without touching the core.
- **Multiple visualizations** — render the same graph in different styles (rounded "simple" nodes vs. detailed attribute "block" nodes) via Visualizer Plugins.
- **Three synchronized views**:
  - **Main View** — interactive canvas with pan, zoom, and drag-and-drop.
  - **Tree View** — collapsible, hierarchical representation of the graph.
  - **Bird View** — scaled-down overview with a viewport rectangle mirroring the Main View.
- **Graph manipulation via CLI** — an in-browser command line lets users create/edit/delete nodes and edges (`create node`, `edit edge`, `delete node`, ...).
- **Search & filter** — find nodes by free-text search or filter by attribute expressions (e.g. `Age > 30 && Height >= 150`), producing an induced subgraph.
- **Workspace management** — multiple independent graph "sessions" can be open at once, each with its own data source, visualizer, graph state, and applied operations.

## Technology Stack
- **Backend:** Python 3.10+
- **Web framework:** Django (`graph_explorer/`)
- **Plugin system:** custom implementation using `abc` (Abstract Base Classes), `typing`, and Python **entry points** (`importlib.metadata`) for discovery
- **Frontend:** HTML, CSS, JavaScript, [D3.js](https://d3js.org/) for rendering/zoom/drag behaviour
- **CLI:** interactive terminal implemented inside the web page, backed by a REST endpoint
- **Version control:** Git (GitHub), Trunk-Based Development

## Architecture at a Glance

```
api/                      Abstract contracts + domain model (framework-agnostic)
  data_source.py            DataSourcePlugin (ABC)
  visualizer.py              VisualizerPlugin (ABC)
  models/graph.py            Graph, GraphBuilder
  models/node.py, edge.py    Node, Edge

project_platform/         Core platform (orchestration, no UI, no I/O formats)
  core.py                    GraphPlatform — singleton facade used by the web layer
  plugin_manager.py          PluginManager — singleton, discovers plugins via entry points
  graph_operations.py        GraphOperations — search/filter algorithms
  workspace.py / workspace_manager.py   Workspace persistence (pickle-based, currently unused by the Django app, which keeps workspaces in-memory in GraphPlatform)

plugins/                  Concrete, independently installable plugins
  json_data_source_plugin/   JSONSource(DataSourcePlugin)
  yaml_data_source_plugin/   YAMLSource(DataSourcePlugin)
  simple_visualizer/         SimpleVisualizer(VisualizerPlugin)
  block_visualizer/          BlockVisualizer(VisualizerPlugin)

graph_explorer/           Django project (the actual web app)
  config/                    Django settings/urls/wsgi
  viewer/                    Django app: views.py (REST endpoints), templates, static JS/CSS
```

### Request flow (loading a graph)
1. User picks a data source plugin + parameters (e.g. `json_source`, `json_path=...`) and a visualizer plugin in the UI.
2. The browser POSTs to `viewer/api/load-graph/` → `views.load_graph`.
3. The view asks the `GraphPlatform` singleton to `load_graph(...)`.
4. `GraphPlatform` asks `PluginManager` to instantiate the requested `DataSourcePlugin` (found via entry points) and calls `.parse(**parameters)`, which returns a `Graph` built through `GraphBuilder`.
5. `GraphPlatform` also resolves the requested `VisualizerPlugin` class and instantiates it.
6. The graph (serialized via `Graph.to_json()`) and the visualizer's frontend assets (`get_frontend_assets`: per-node HTML + CSS) are returned as JSON.
7. The frontend JS pushes this data into a shared `GraphSubject` (Observer pattern), which notifies the Main/Tree/Bird views so they re-render in sync.

### CLI / search / filter flow
- CLI commands and search/filter queries are sent to `viewer/api/cli/execute/` and `viewer/api/graph-operations/`.
- `GraphPlatform` parses the command (using `shlex`) and mutates the in-memory `Graph`, or delegates to `GraphOperations.search()` / `GraphOperations.filter()`, which build a new induced subgraph (matching nodes + edges whose both endpoints match) via `GraphBuilder`.
- The active workspace is updated and the new graph/operations list is returned to refresh all three views.

## Design Patterns Used

| Pattern | Where | Why |
|---|---|---|
| **Strategy / Plugin (Provider)** | `DataSourcePlugin`, `VisualizerPlugin` (abstract base classes in `api/`) with concrete strategies in `plugins/` | The platform depends only on an abstract interface; concrete parsing/rendering algorithms are swappable at runtime without changing core code. |
| **Singleton** | `GraphPlatform` (`project_platform/core.py`), `PluginManager` (`project_platform/plugin_manager.py`) — both override `__new__` | There must be exactly one platform state and one plugin registry shared across all Django requests in the process. |
| **Builder** | `GraphBuilder` (`api/models/graph.py`) | Decouples the step-by-step construction of a `Graph` (adding nodes/edges with validation) from its final representation; used by data source plugins and by `GraphOperations._build_subgraph`. |
| **Factory Method** | `Graph.builder(directed=...)` | Provides a convenient, discoverable way to obtain a new `GraphBuilder` from the `Graph` class itself. |
| **Service Locator / Plugin Discovery** | `PluginManager._load_installed_plugins()` using `importlib.metadata.entry_points()` (groups `graph_platform.data_sources` / `graph_platform.visualizers`) | Plugins are regular pip-installable packages; the core discovers them by name at startup instead of importing them directly, so new plugins can be added by just `pip install -e`. |
| **Facade** | `GraphPlatform` | Exposes a single, simplified API (`load_graph`, `apply_operations`, `execute_cli_command`, workspace methods) that Django views call, hiding the coordination between `PluginManager`, `GraphOperations`, and workspace state. |
| **Observer** | `GraphSubject` (`graph_explorer/viewer/static/js/graph_observer.js`) | Decouples the three views (Main/Tree/Bird) from the code that loads/mutates graph data — each view subscribes to graph/selection/viewport changes and stays in sync without the views knowing about each other. |
| **Memento-like state snapshot** | `GraphPlatform` workspaces (`original_graph` vs `current_graph`, `cli_operations` list) | Search/filter always re-applies from `original_graph`, so operations are non-destructive and can be recomputed/undone by replaying the operation list. |

## Installation and Configuration
1. Create a virtual environment: `python -m venv venv`
2. Activate it:
   - Windows: `venv\Scripts\activate`
   - Linux/macOS: `source venv/bin/activate`
3. Install the platform's dependencies: `pip install -r requirements.txt`
4. Install the plugins as editable packages (this registers their entry points so `PluginManager` can discover them):
   ```
   pip install -e plugins/json_data_source_plugin
   pip install -e plugins/yaml_data_source_plugin
   pip install -e plugins/simple_visualizer
   pip install -e plugins/block_visualizer
   ```
5. Run the web application:
   ```
   python graph_explorer/manage.py runserver
   ```
6. Open the app in your browser (default: `http://127.0.0.1:8000/`).

## Class Diagram
See [`docs/class_diagram.png`](docs/class_diagram.png) (rendered image) / [`docs/class_diagram.puml`](docs/class_diagram.puml) (PlantUML source). It covers the graph model (`Node`, `Edge`, `Graph`, `GraphBuilder`), the plugin contracts (`DataSourcePlugin`, `VisualizerPlugin`), the concrete plugins (`JSONSource`, `YAMLSource`, `SimpleVisualizer`, `BlockVisualizer`), and the core services (`GraphPlatform`, `PluginManager`, `GraphOperations`).

To regenerate the PNG after editing the `.puml` file (requires Java + [Graphviz](https://graphviz.org/download/), so PlantUML can lay out the arrows cleanly instead of using its slower built-in layout engine):
```
java -jar plantuml.jar -tpng docs/class_diagram.puml -o .
```

## CLI Commands (inside the web UI)
```
create node --id=1 --property Name=Alice --property Age=25
create edge --id=e1 --property Name=Siblings 1 2
edit node --id=2 --property Age=40
edit edge --id=e1 --property Name=Friend
delete node --id=2
delete edge --id=e1
filter 'Age>30 && Height>=150'
search 'Name=Tom'
clear
help
```
