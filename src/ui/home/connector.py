import copy
import logging
import tkinter as tk

logger = logging.getLogger(__name__)

from utils.file_handling import read_tk_image
from utils.events import MouseEvent
from ..common.connector_click_strategy import ConnectorClickStrategy


class ConnectorIcon(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict, image_path: str, text: str, strategy: ConnectorClickStrategy):
        super().__init__(parent)
        self._config_params = copy.deepcopy(config_params["Design"])
        self._fallback_config = config_params.get("FallbackDesign", {})

        # Get ImageTk object
        connector_image = read_tk_image(image_path)
        if connector_image is not None:
            self._config_params["image"] = connector_image
            # Keep reference so the image is rendered
            self._image = connector_image
        else:
            self._config_params["text"] = text
            self._config_params.update(self._fallback_config)
        self._strategy = strategy

        self.configure(
            command=self._on_click,
            **self._config_params
        )

        # Controls
        self._switch_highlight = False
        self.bind(MouseEvent.ENTER, self._on_hover_highlight)
        self.bind(MouseEvent.LEAVE, self._on_hover_highlight)

    def _on_hover_highlight(self, event) -> None:
        self._switch_highlight = not self._switch_highlight
        self.configure(
            highlightbackground=(
                "#D9D9D9"
                if self._switch_highlight
                else self._config_params["highlightbackground"]
            )
        )
        logger.debug(f"Connector hover event: {event}")

    def _on_click(self, event=None) -> None:
        self.configure(cursor="watch")
        self._strategy.execute()
        self.configure(cursor=self._config_params["cursor"])


class ConnectorLabel(tk.Label):
    def __init__(self, parent: tk.Widget, config_params: dict, text: str):
        super().__init__(parent)

        self._config_params = copy.deepcopy(config_params)

        self._config_params["text"] = text

        self.configure(**self._config_params)


class ConnectorsFrame(tk.Frame):
    def __init__(self, parent: tk.Widget, config_params: dict, connector_count: int):
        super().__init__(parent)

        self._config_params = copy.deepcopy(config_params)

        self.configure(**self._config_params)

        self.grid_rowconfigure((0, 1), weight=1)
        self.grid_columnconfigure([idx for idx in range(connector_count)], weight=1)
