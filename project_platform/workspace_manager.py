import os
from typing import List

from project_platform.workspace import Workspace


class WorkspaceManager:
    def __init__(self, directory: str = "workspaces"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def get_workspace_files(self) -> List[str]:
        """Returns a list of workspace pickle files available in the directory."""
        return [
            os.path.join(self.directory, filename)
            for filename in os.listdir(self.directory)
            if filename.endswith('.pkl')
        ]

    def get_workspace_names(self) -> List[str]:
        """Returns a list of workspace names derived from the files."""
        names = []
        for file in self.get_workspace_files():
            try:
                workspace = Workspace.load(file)
                names.append(workspace.get_name())
            except Exception as e:
                print(f"Error loading workspace from file {file}: {e}")
        return names

    def load_workspace(self, name: str) -> Workspace:
        """Loads a workspace by workspace name."""
        filepath = Workspace.name_to_filepath(name, self.directory)
        try:
            return Workspace.load(filepath)
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
