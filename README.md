# Graph Visualization Application

## Team members
- Milica Jovanić SV 9/2023
- Danica Komatović SV 20/2023
- Lana Mirkov SV 23/2023
- Ana Paroški SV 53/2023

## Project Overview
This project is a modular, plugin-based platform for visualizing graph data structures. It allows users to load graph data from various sources and visualize it in multiple ways within a single web interface. The project's main goal is to demonstrate the benefits of object-oriented programming and a plugin architecture, enabling easy extension and modification of core components.

The platform supports loading data from different sources via Data Source Plugins and visualizing the resulting graphs via Visualizer Plugins. A web application (built with Django) integrates the platform and plugins, providing an interactive user interface with three synchronized views of the graph: Main View, Tree View, and Bird View.

## Key Features
- Modular Architecture: A core platform communicates with independently developed and installed plugins through a well-defined API.

- Multiple Data Sources: Load graphs from various file formats or data sources (e.g., JSON, XML, CSV) using dedicated Data Source Plugins.

- Multiple Visualizations: Visualize the same graph in different styles (e.g., simple nodes vs. detailed blocks) using Visualizer Plugins. The project includes two visualization plugins.

- Three Synchronized Views:

  - Main View: An interactive canvas for exploring the graph with pan, zoom, and drag-and-drop.

  - Tree View: A collapsible, tree-like representation for exploring hierarchical relationships.

  - Bird View: A scaled-down overview of the entire graph with a viewport that mirrors the Main View.

- Graph Manipulation: Interact with the graph using an integrated Command Line Interface (CLI) to create, edit, and delete nodes and edges.

- Search & Filter: Find specific nodes by text search or filter the graph using attribute-based queries (e.g., Age > 30).

- Workspace Management: Manage multiple independent graph workspaces, each with its own data source, filters, and search results.

## Technology Stack
- Backend: Python 

- Web Framework: Django

- API/Plugin System: Custom implementation using abc (Abstract Base Classes) and typing.

- Frontend Visualization: HTML, CSS, JavaScript, with the D3.js library.

- CLI: Interactive terminal implemented in the web interface.

- Version Control: Git (GitHub) with Trunk-Based Development.

## Installation and Configuration
1. Create a virtual environment – isolate project dependencies using python -m venv venv

2. Activate the virtual environment – source venv/bin/activate (Linux/macOS) or venv\Scripts\activate (Windows)

3. Install the components – install the plugins (the web application will automatically use them):
   
    - pip install -e ./path/to/data_source_plugin_1
    - pip install -e ./path/to/data_source_plugin_2
    - pip install -e ./simple_visualizer
    - pip install -e ./block_visualizer
    - Run the web application: python graph_explorer/manage.py runserver

4. Access the application through your browser.
