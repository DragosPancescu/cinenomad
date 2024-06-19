from abc import ABC, abstractmethod


class ConnectorClickStrategy(ABC):
    @abstractmethod
    def execute(self):
        pass


class NetflixConnectorClick(ConnectorClickStrategy):
    def execute(self):
        print("Click Netflix Connector")


class LocalConnectorClick(ConnectorClickStrategy):
    def execute(self):
        print("Click Local Connector")


def get_strategy_for_connector(name: str) -> ConnectorClickStrategy:
    if name == "Netflix":
        return NetflixConnectorClick()
    elif name == "Local":
        return LocalConnectorClick()
    else:
        return None