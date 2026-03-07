import tkinter as tk

from services.database import models
from utils.events import MouseEvent


class Poster(tk.Label):
    """Label widget that holds the poster image of a movie."""

    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        metadata: models.VideoMetadata,
        height: int,
        width: int,
        hoverable=False,
    ):
        self._poster_image = metadata.get_image_object(width, height)
        super().__init__(parent, image=self._poster_image, **config_params)

        if hoverable:
            self.bind(MouseEvent.ENTER, self._on_hover_switch_cursor)
            self.bind(MouseEvent.LEAVE, self._on_hover_switch_cursor)

    def _on_hover_switch_cursor(self, event=None) -> None:
        if self.cget("cursor") == "":
            self.config(cursor="hand2")
        else:
            self.config(cursor="")
