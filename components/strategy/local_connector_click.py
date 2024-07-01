import os

import tkinter as tk

from . import ConnectorClickStrategy
from components import AppControlButton

# TODO: This will be configurable on first use or after in the settings menu.
FOLDER_PATH = "/home/dragos/Videos"

class LocalMovieBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.withdraw()  # Init in closed state

        self._config_params = config_params

        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Controls
        self.bind("<Escape>", self.close)

        # Widgets
        # Close button
        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.close)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

    def close(self, e=None) -> None:
        self.withdraw()
        self._parent.focus()

    def show(self) -> None:
        self.deiconify()
        self.focus()


class LocalConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._window = LocalMovieBrowserModal(parent, config_params)

    def execute(self):
        self._window.show()
