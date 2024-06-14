import tkinter as tk

from PIL import Image, ImageTk, UnidentifiedImageError

class ConnectorIcon(tk.Button):
    def __init__(self, parent, config_params, image_path, text):
        super().__init__(parent)

        self.__config_params = config_params

        # Transform list to tuple
        self.__config_params["font"] = tuple(self.__config_params["font"])

        # Get ImageTk object
        self.__config_params["image"] = self.__read_icon_image(image_path)

        # Keep reference so the image is rendered
        self.image = self.__config_params["image"]

        self.__config_params["text"] = text

        self.configure(**self.__config_params)

        self.bind("<Enter>", self.__on_enter_highlight)
        self.bind("<Leave>", self.__on_exit_no_highlight)

    def __read_icon_image(self, path):
        try:
            button_png = Image.open(path).convert("RGBA")
            return ImageTk.PhotoImage(button_png)
        except UnidentifiedImageError as err:
            return err

    def __on_enter_highlight(self, e=None):
        self.configure(highlightbackground="#D9D9D9")
        print(f"Enter: {self.__config_params['text']}")

    def __on_exit_no_highlight(self, e=None):
        self.configure(highlightbackground=self.__config_params["highlightbackground"])
        print(f"Exit: {self.__config_params['text']}")


class ConnectorLabel(tk.Label):
    def __init__(self, parent, config_params, text):
        super().__init__(parent)

        self.__config_params = config_params

        # Transform list to tuple
        self.__config_params["font"] = tuple(self.__config_params["font"])

        self.__config_params["text"] = text

        self.configure(**self.__config_params)


class ConnectorsFrame(tk.Frame):
    def __init__(self, parent, config_params, connector_count):
        super().__init__(parent)

        self.__config_params = config_params

        self.configure(**self.__config_params)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure([idx for idx in range(connector_count)], weight=1)
