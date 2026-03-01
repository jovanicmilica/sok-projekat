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