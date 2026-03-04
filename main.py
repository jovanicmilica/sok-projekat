import sys
from pathlib import Path
import importlib.metadata

root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from project_platform.plugin_manager import PluginManager


def main():
    print("=" * 60)
    print("STARTING GRAPH VISUALIZATION PLATFORM")
    print("=" * 60)

    print("\n=== Entry Points Debug ===")
    eps = importlib.metadata.entry_points()

    if hasattr(eps, 'select'):
        data_eps = list(eps.select(group='graph_platform.data_sources'))
        vis_eps = list(eps.select(group='graph_platform.visualizers'))
    else:
        data_eps = list(eps.get('graph_platform.data_sources', []))
        vis_eps = list(eps.get('graph_platform.visualizers', []))

    print(f"Data source entry points: {len(data_eps)}")
    for ep in data_eps:
        print(f"  {ep.name} -> {ep.value}")
        print(f"    module: {ep.module}")
        print(f"    attr: {ep.attr}")

    print(f"\nVisualizer entry points: {len(vis_eps)}")
    for ep in vis_eps:
        print(f"  {ep.name} -> {ep.value}")
        print(f"    module: {ep.module}")
        print(f"    attr: {ep.attr}")
    print("=" * 60)

    # 1. Create plugin manager instance
    pm = PluginManager()

    # 2. Load plugins
    data_plugins = pm.get_data_source_plugins()

    # 3. Show loaded plugins
    print("\n" + "=" * 60)
    print(f"LOADED: {len(data_plugins)}")
    print("=" * 60)

    if data_plugins:
        for i, (plugin_key, plugin_class) in enumerate(data_plugins.items(), 1):
            print(f"\n  {i}. {plugin_key}")
            print(f" Class: {plugin_class.__name__}")

    else:
        print("\nNo plugins found.")

    all_info = pm.get_all_plugin_info()
    print(f"\n Data plugins: {len(all_info['data_plugins'])}")
    print(f" Visualizer plugins: {len(all_info['visualizer_plugins'])}")


if __name__ == "__main__":
    main()