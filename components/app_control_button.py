import tkinter as tk
import copy

from utils.file_handling import read_tk_image


class AppControlButton(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        # Get config params
        self._config_params = copy.deepcopy(config_params)

        # Get ImageTk object
        self._config_params["image"] = read_tk_image(self._config_params["image_path"])
        self._config_params.pop("image_path", None)

        self.configure(**self._config_params)
