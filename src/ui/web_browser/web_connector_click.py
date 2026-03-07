import os
import copy
import tkinter as tk

from utils.chrome import open_chrome, close_chrome
from utils.file_handling import load_yaml_file
from utils.events import KeyEvent
from ui.common.connector_click_strategy import ConnectorClickStrategy


class WebBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict, url: str):
        super().__init__(parent)
        self._parent = parent
        self._url = url
        self.withdraw()  # Init in closed state

        self._config_params = copy.deepcopy(config_params)

        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Controls
        self.bind(KeyEvent.ESCAPE, self.close)

        self._args = load_yaml_file(os.path.join(".", "config", "chrome_process_config.yaml"))
        self._profile = "Default"
        self._process = None

    def close(self, event=None) -> None:
        close_chrome(self._process)
        self._parent.focus()
        self.destroy()

    def show(self) -> None:
        self._process = open_chrome(self._url, self._profile, *self._args)


class WebConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict, url: str):
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._url = url
        self._window = None

    def execute(self) -> None:
        if self._window is None:
            self._window = WebBrowserModal(self._parent, self._config_params, self._url)
        self._window.show()
