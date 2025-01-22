import copy

from . import ConnectorClickStrategy
from utils.chrome import open_flatpak_chrome, close_chrome

import tkinter as tk


class NetflixBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
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
        self.bind("<Escape>", self.close)

        self._args = [
            "-kiosk",
            "--new-window",
            "--hide-scrollbars",
            "--force-device-scale-factor",
        ]
        self._profile = "Profile 1"
        self._process = None

    

    def close(self, event=None) -> None:
        close_chrome(self._process)
        self._parent.focus()
        self.destroy()

    def show(self) -> None:
        self._chrome_process = open_flatpak_chrome(
            "https://www.netflix.com", self._profile, *self._args
        )

class NetflixConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._window = None

    def execute(self) -> None:
        if self._window == None:
            self._window = NetflixBrowserModal(self._parent, self._config_params)
        self._window.show()
