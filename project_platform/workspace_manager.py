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
    

