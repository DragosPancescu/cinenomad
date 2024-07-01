from abc import ABC, abstractmethod


class ConnectorClickStrategy(ABC):
    @abstractmethod
    def execute(self):
        pass