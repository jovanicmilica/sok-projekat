from abc import ABC, abstractmethod

from api.models.graph import Graph


class DataSourcePlugin(ABC):

    @abstractmethod
    def parse(self, **kwargs) -> Graph:
        """
        Parse data and return a Graph object.
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Return the name of the data source plugin.
        """
        pass