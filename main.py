# main.py
import sys
from pathlib import Path

# Dodaj root u putanju (ako treba)
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from project_platform.plugin_manager import PluginManager


def main():
    print("=" * 60)
    print("STARTING GRAPH VISUALIZATION PLATFORM")
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