import copy
import tkinter as tk

from PIL import Image, ImageTk, UnidentifiedImageError

from .strategy import ConnectorClickStrategy


class ConnectorIcon(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict, image_path: str, text: str, strategy: ConnectorClickStrategy):
        super().__init__(parent)

        self._config_params = copy.deepcopy(config_params)

        # Transform list to tuple
        self._config_params["font"] = tuple(self._config_params["font"])

        # Get ImageTk object
        self._config_params["image"] = self._read_icon_image(image_path)

        # Keep reference so the image is rendered
        self._image = self._config_params["image"]

        self._config_params["text"] = text
        self._strategy = strategy

        self.configure(
            command=lambda: self._on_click(None), 
            **self._config_params
        )

        self.bind("<Enter>", lambda event: self._on_enter_highlight(event))
        self.bind("<Leave>", lambda event: self._on_exit_no_highlight(event))

    def _read_icon_image(self, path: str) -> ImageTk.PhotoImage:
        try:
            button_png = Image.open(path).convert("RGBA")
            return ImageTk.PhotoImage(button_png)
        except UnidentifiedImageError as err:
            return err.strerror

    def _on_enter_highlight(self, event) -> None:
        self.configure(highlightbackground="#D9D9D9")
        print(f"Enter: {event.widget['text']}")

    def _on_exit_no_highlight(self, event) -> None:
        self.configure(highlightbackground=self._config_params["highlightbackground"])
        print(f"Exit: {event.widget['text']}")

    def _on_click(self, event) -> None:
        self.configure(cursor="watch")
        self._strategy.execute()
        self.configure(cursor=self._config_params["cursor"])


class ConnectorLabel(tk.Label):
    def __init__(self, parent: tk.Widget, config_params: dict, text: str):
        super().__init__(parent)

        self._config_params = copy.deepcopy(config_params)

        # Transform list to tuple
        self._config_params["font"] = tuple(self._config_params["font"])

        self._config_params["text"] = text

        self.configure(**self._config_params)


class ConnectorsFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, config_params: dict, connector_count: int):
        super().__init__(parent)

        self._config_params = copy.deepcopy(config_params)

        self.configure(**self._config_params)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure([idx for idx in range(connector_count)], weight=1)
