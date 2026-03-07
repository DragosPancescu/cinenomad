import copy
import tkinter as tk

from ui.common.connector_click_strategy import ConnectorClickStrategy
from .local_movie_browser_modal import LocalMovieBrowserModal


class LocalConnectorClick(ConnectorClickStrategy):
    """The local connector click strategy class, that opens the local browser window."""

    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._window = None

    def execute(self) -> None:
        if self._window is None:
            self._window = LocalMovieBrowserModal(self._parent, self._config_params)
        self._window.show()
