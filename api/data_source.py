from abc import ABC, abstractmethod
from typing import Any, Dict, List

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

    @classmethod
    @abstractmethod
    def get_parameters_spec(cls) -> List[Dict[str, Any]]:
        """
        Return a list of parameter specifications required by this plugin.
        Each specification is a dictionary with keys like 'name', 'type', 'description', and 'required'.
        """
        pass

