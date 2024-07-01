import os

import tkinter as tk

from .connector_click_strategy import ConnectorClickStrategy
from ..app_control_button import AppControlButton

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
        self.close_button.place(**self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"])

    def close(self, e=None) -> None:
        self.withdraw()
        self._parent.focus()


    def show(self) -> None:
        self.deiconify()
        self.focus()

    def read_video_files(self) -> list[dict]:
        if not os.path.isdir(FOLDER_PATH):
            print(f"{FOLDER_PATH} does not exist or is not a folder.")
            return None
        
        for filename in os.listdir(FOLDER_PATH):
            f = os.path.join(FOLDER_PATH, filename)
            # checking if it is a file
            if os.path.isfile(f):
                print(f)


class LocalConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._window = LocalMovieBrowserModal(parent, config_params)

    def execute(self):
        self._window.show()
