import copy
import tkinter as tk

from utils.events import MouseEvent


class AddMovieSourceButton(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._config_params = copy.deepcopy(config_params)

        self.configure(**self._config_params)

        # Controls
        self._colors_switch = False
        self.bind(MouseEvent.ENTER, self._on_hover_switch_colors)
        self.bind(MouseEvent.LEAVE, self._on_hover_switch_colors)

    def _on_hover_switch_colors(self, event=None) -> None:
        self._colors_switch = not self._colors_switch
        foreground = self._config_params["foreground"]
        background = self._config_params["background"]

        self.configure(
            background=(foreground if self._colors_switch else background),
            foreground=(background if self._colors_switch else foreground),
        )
