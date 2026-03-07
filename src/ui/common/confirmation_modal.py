import copy
import tkinter as tk

from utils.events import KeyEvent
from .centerable_toplevel import CenterableToplevel


class ConfirmationModal(CenterableToplevel):
    """A centered modal dialog that asks the user to confirm an action."""

    def __init__(self, parent: tk.Widget, message: str, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.result = False

        self._config_params = copy.deepcopy(config_params)
        self.title(self._config_params["title"])
        self.geometry("400x150")
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])

        self.bind(KeyEvent.ESCAPE, self.close)

        label_config = copy.deepcopy(self._config_params["Message"])
        tk.Label(self, text=message, **label_config).place(relx=0.5, rely=0.3, anchor="center")

        yes_button = tk.Button(
            self,
            text=self._config_params["YesButton"]["text"],
            command=self._confirm,
            **self._config_params["YesButton"]["Design"],
        )
        yes_button.place(**self._config_params["YesButton"]["Placement"])

        no_button = tk.Button(
            self,
            text=self._config_params["NoButton"]["text"],
            command=self.close,
            **self._config_params["NoButton"]["Design"],
        )
        no_button.place(**self._config_params["NoButton"]["Placement"])

        self.grab_set()
        self._center()

    def _confirm(self) -> None:
        self.result = True
        self.destroy()

    def close(self, event=None) -> None:
        self.result = False
        self.destroy()
