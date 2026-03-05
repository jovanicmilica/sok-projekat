import os
from typing import List
from workspace import Workspace

class WorkspaceManager:
    def __init__(self, directory: str = "workspaces"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)
    
    def get_workspace_files(self) -> List[str]:
        """Returns a list of workspace pickle files available in the directory."""
        workspaces = []
        for filename in os.listdir(self.directory):
            workspaces.append(f"{self.directory}/{filename}") if filename.endswith('.pkl') else None
        return workspaces
    
    def get_workspace_names(self) -> List[str]:
        """Returns a list of workspace names derived from the filenames."""
        names = []
        files = self.get_workspace_files()
        for file in files:
            try:
                workspace = Workspace.load(file)
                names.append(workspace.get_name())
            except Exception as e:
                print(f"Error loading workspace from file {file}: {e}")
        return names
    
    def load_workspace(self, name: str) -> Workspace:
        """Loads a workspace by name."""
        try:
            return Workspace.load(name, self.directory)
        except Exception as e:
            print(f"Error loading workspace '{name}': {e}")
            raise

    def save_workspace(self, workspace: Workspace) -> str:
        """Saves a workspace and returns the filepath."""
        try:
            return workspace.save(self.directory)
        except Exception as e:
            print(f"Error saving workspace '{workspace.get_name()}': {e}")
            raise
    

import os
from workspace_manager import WorkspaceManager
from workspace import Workspace


def create_test_workspace(name: str, data_plugin: str, viz_plugin: str, searches: list, filters: list) -> Workspace:
    """Helper function to create a test workspace with given parameters."""
    ws = Workspace()
    ws.set_name(name)
    ws.set_data_source_plugin(data_plugin)
    ws.set_visualizer_plugin(viz_plugin)
    ws.set_search_queries(searches)
    ws.set_filter_queries(filters)
    return ws


def main():
    print("=" * 70)
    print("🧪 TESTING WORKSPACE MANAGER - CREATING 5 WORKSPACES")
    print("=" * 70)
    
    # 1. Inicijalizuj manager
    manager = WorkspaceManager("workspaces")
    print(f"\n📁 Workspace directory: {manager.directory}")
    
    # 2. Obriši postojeće fajlove (za čist test)
    print("\n🧹 Cleaning up old test files...")
    for file in manager.get_workspace_files():
        filepath = os.path.join(manager.directory, file)
        os.remove(filepath)
        print(f"   Removed: {file}")
    
    # 3. Kreiraj 5 test workspace-ova
    print("\n📝 Creating 5 test workspaces...")
    
    workspaces = [
        create_test_workspace(
            name="JSON Test",
            data_plugin="json_source",
            viz_plugin="simple-view",
            searches=["nesto"],
            filters=["type = person", "active = true"]
        ),
        create_test_workspace(
            name="CSV Export",
            data_plugin="csv_source",
            viz_plugin="block-view",
            searches=["city"],
            filters=["department = IT", "status = active"]
        ),
        create_test_workspace(
            name="XML Data",
            data_plugin="xml_source",
            viz_plugin="simple-view",
            searches=["created"],
            filters=["type = document", "format = xml"]
        ),
        create_test_workspace(
            name="YAML Config",
            data_plugin="yaml_source",
            viz_plugin="block-view",
            searches=["env"],
            filters=["service = api", "replicas >= 3"]
        ),
        create_test_workspace(
            name="RDF Graph",
            data_plugin="rdf_source",
            viz_plugin="simple-view",
            searches=["subject"],
            filters=["object = organization", "confidence > 0.8"]
        )
    ]
    
    # 4. Sačuvaj sve workspace-ove
    print("\n💾 Saving all workspaces...")
    saved_paths = []
    
    for i, ws in enumerate(workspaces, 1):
        try:
            filepath = manager.save_workspace(ws)
            saved_paths.append(filepath)
            print(f"   {i}. ✅ {ws.get_name()} -> {os.path.basename(filepath)}")
        except Exception as e:
            print(f"   {i}. ❌ {ws.get_name()}: {e}")
    
    # 5. Provjeri da li su sačuvani
    print("\n🔍 Checking saved files...")
    files = manager.get_workspace_files()
    print(f"   Found {len(files)} file(s) in directory:")
    for file in sorted(files):
        print(f"      📄 {file}")
    
    # 6. Učitaj nazad sve workspace-ove
    print("\n📂 Loading all workspaces back...")
    loaded_workspaces = []
    
    for i, ws in enumerate(workspaces, 1):
        try:
            loaded = manager.load_workspace(ws.get_name())
            loaded_workspaces.append(loaded)
            print(f"   {i}. ✅ Loaded: {loaded.get_name()}")
        except Exception as e:
            print(f"   {i}. ❌ {ws.get_name()}: {e}")
    
    # 7. Provjeri da li se podaci poklapaju
    print("\n⚖️ Verifying data integrity...")
    all_match = True
    
    for i, (original, loaded) in enumerate(zip(workspaces, loaded_workspaces), 1):
        print(f"\n   {i}. {original.get_name()}:")
        
        checks = [
            ("name", original.get_name(), loaded.get_name()),
            ("data_plugin", original.get_data_source_plugin(), loaded.get_data_source_plugin()),
            ("viz_plugin", original.get_visualizer_plugin(), loaded.get_visualizer_plugin()),
            ("searches", original.get_search_queries(), loaded.get_search_queries()),
            ("filters", original.get_filter_queries(), loaded.get_filter_queries()),
        ]
        
        ws_match = True
        for field, orig_val, loaded_val in checks:
            if orig_val == loaded_val:
                print(f"      ✅ {field}: matches")
            else:
                print(f"      ❌ {field}: ORIG='{orig_val}', LOADED='{loaded_val}'")
                ws_match = False
                all_match = False
        
        if ws_match:
            print(f"      ✅ All fields match for this workspace")
    
    # 8. Dohvati sva imena workspace-ova
    print("\n📋 Getting all workspace names...")
    try:
        names = manager.get_workspace_names()
        print(f"   Found {len(names)} workspace(s):")
        for i, name in enumerate(sorted(names), 1):
            print(f"      {i}. {name}")
    except Exception as e:
        print(f"   ❌ Error getting names: {e}")
    
    # 9. Zaključak
    print("\n" + "=" * 70)
    if all_match and len(workspaces) == len(loaded_workspaces) == len(files):
        print("✅✅✅ TEST PASSED: All 5 workspaces created, saved, and loaded successfully!")
        print(f"   📁 Directory: {os.path.abspath(manager.directory)}")
        print(f"   📊 Files: {len(files)}")
        print(f"   🔄 Workspaces: {len(loaded_workspaces)}")
    else:
        print("❌❌❌ TEST FAILED:")
        print(f"   Created: {len(workspaces)}")
        print(f"   Saved files: {len(files)}")
        print(f"   Loaded: {len(loaded_workspaces)}")
        print(f"   Data match: {all_match}")
    print("=" * 70)


def quick_test():
    """Quick test without all the verification."""
    print("🚀 Quick test - creating 5 workspaces")
    
    manager = WorkspaceManager("workspaces")
        
    # for ws in workspaces:
    #     manager.save_workspace(ws)
    #     print(f"   Saved: {ws.get_name()}")
    
    # print(f"✅ Done! Check {manager.directory} folder.")

    # files = manager.get_workspace_files()
    names = manager.get_workspace_names()
    print(f"   Workspace names found: {names}")


if __name__ == "__main__":
    # Pokreni glavni test
    # main()
    
    # Opciono: pokreni brzi test
    quick_test()