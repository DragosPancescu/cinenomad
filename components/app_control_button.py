import tkinter as tk

from PIL import Image, ImageTk


class AppControlButton(tk.Button):
    def __init__(self, parent, config_params):
        super().__init__(parent)

        # Get config params
        self.__config_params = config_params

        # Get ImageTk object
        self.__config_params["image"] = self.__read_icon_image(
            self.__config_params["image_path"]
        )
        self.__config_params.pop("image_path", None)

        self.configure(**self.__config_params)

    def __read_icon_image(self, path):
        button_png = Image.open(path).convert("RGBA")
        return ImageTk.PhotoImage(button_png)
