from abc import ABC, abstractmethod


class ConnectorClickStrategy(ABC):
    """Connector Click Strategy interface"""

    @abstractmethod
    def execute(self) -> None:
        """Methods that gets called when the connector is clicked."""
