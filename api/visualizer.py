from abc import ABC, abstractmethod
from api.models.graph import Graph


class VisualizerPlugin(ABC):

    @abstractmethod
    def render(self, graph: Graph) -> str:
        """
        Generate a visual representation of the graph and return it as a string.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Return the name of the visualizer plugin.
        """
        pass

    def get_frontend_assets(self, graph: Graph) -> dict:
        """
        Return visual assets used by graph_explorer.

        Visualizer plugins own node HTML and CSS. The graph_explorer frontend owns
        layout, zoom, drag, selection and communication between views.
        """
        return {
            'name': self.get_name(),
            'css': '',
            'nodes': {},
            'defaults': {
                'width': 96,
                'height': 64,
            },
        }
