import copy
import logging
import tkinter as tk

logger = logging.getLogger(__name__)

from utils.events import KeyEvent
from ..common.centerable_toplevel import CenterableToplevel


class AddMovieSourceModal(CenterableToplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.withdraw()

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.title(self._config_params["title"])
        self.geometry("600x300")
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        self.focus()

        # Controls
        self.bind(KeyEvent.ESCAPE, self.close)

        # Widgets
        self._init_widgets()

    def _handle_user_choice(self, choice: str) -> None:
        if choice == "Add":
            logger.info("Added new movie source")
        else:
            logger.debug("Cancel new movie source")
        self.close()

    def _init_widgets(self) -> None:
        add_button = tk.Button(
            self,
            text=self._config_params["AddButton"]["text"],
            command=lambda: self._handle_user_choice(
                self._config_params["AddButton"]["text"]
            ),
            **self._config_params["AddButton"]["Design"],
        )
        add_button.place(**self._config_params["AddButton"]["Placement"])

        cancel_button = tk.Button(
            self,
            text=self._config_params["CancelButton"]["text"],
            command=lambda: self._handle_user_choice(
                self._config_params["CancelButton"]["text"]
            ),
            **self._config_params["CancelButton"]["Design"],
        )
        cancel_button.place(**self._config_params["CancelButton"]["Placement"])
