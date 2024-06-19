import tkinter as tk

from PIL import Image, ImageTk


class AppControlButton(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        # Get config params
        self._config_params = config_params

        # Get ImageTk object
        self._config_params["image"] = self._read_icon_image(
            self._config_params["image_path"]
        )
        self._config_params.pop("image_path", None)

        self.configure(**self._config_params)

    def _read_icon_image(self, path: str) -> ImageTk.PhotoImage:
        button_png = Image.open(path).convert("RGBA")
        return ImageTk.PhotoImage(button_png)
