from .connector_click_strategy import ConnectorClickStrategy

class NetflixConnectorClick(ConnectorClickStrategy):
    def execute(self):
        print("Click Netflix Connector")