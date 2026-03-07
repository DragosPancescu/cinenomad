import copy
import tkinter as tk

from functools import partial

from utils.events import MouseEvent

from .poster import Poster
from .movie_selection_model import MovieSelectionModel


class PosterCarousel(tk.Frame):
    """Poster carousel that sits under the movie cards and previews what's ahead and behind the current selection

    Make sure **poster_count** is always an odd number, otherwise this will break
    """

    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        model: MovieSelectionModel,
        height: int,
        width: int,
        poster_count: int,
    ):
        super().__init__(parent)
        self._parent = parent
        self._model = model
        self._model.add_observer(self._on_selection_changed)
        self._height = height
        self._width = width
        self._poster_count = poster_count

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.configure(height=height, width=width, **self._config_params["Design"])

        # Posters
        gaps = self._poster_count + 1
        padding_percent = 0.01

        self._visible_posters = [None for _ in range(0, self._poster_count)]
        self._poster_pad = int(self._width * padding_percent)
        self._poster_width = (
            self._width - (gaps * self._poster_pad)
        ) // self._poster_count
        self._poster_heigh = self._height - self._poster_pad

        # The UI
        self._update_posters()
        self._show_posters()
        self.lift()

    def _on_selection_changed(self, index: int) -> None:
        self._update_posters()
        self._show_posters()

    def _update_posters(self) -> None:
        """Updates the posters list, it adds the posters around the current selection if there are any, else leaves it empty"""
        selected = self._model.current_index
        start = selected - (self._poster_count // 2)
        end = selected + (self._poster_count // 2) + 1

        for poster in self._visible_posters:
            if poster:
                poster.destroy()
        self._visible_posters = [None for _ in range(0, self._poster_count)]

        posters_idx = 0
        for metadata_idx in range(start, end):
            self._visible_posters[posters_idx] = None
            if metadata_idx >= 0 and metadata_idx < self._model.count:
                poster = Poster(
                    parent=self,
                    config_params=self._config_params["Poster"]["Design"],
                    metadata=self._model.metadata_list[metadata_idx],
                    height=self._poster_heigh,
                    width=self._poster_width,
                    hoverable=True,
                )
                poster.bind(
                    MouseEvent.LEFT_CLICK,
                    partial(self._poster_on_click, idx=metadata_idx),
                )
                self._visible_posters[posters_idx] = poster
            posters_idx += 1

        # Put border around currently selected poster
        self._visible_posters[self._poster_count // 2].configure(
            highlightthickness=3, highlightbackground="#D9D9D9"
        )

    def _poster_on_click(self, event, idx: int) -> None:
        self._model.select(idx)

    def _show_posters(self) -> None:
        """Iterates the posters list and makes them visible in the UI"""
        for idx, poster in enumerate(self._visible_posters):
            # Places the selected poster higher than the rest of the carousel
            selected_y_padding = self._poster_pad * 0.5
            if idx == self._poster_count // 2:
                selected_y_padding = 0

            if poster:
                poster.place(
                    x=(self._poster_width * idx) + self._poster_pad * (idx + 1),
                    y=selected_y_padding,
                    width=self._poster_width,
                    height=self._poster_heigh,
                )
                poster.lift()
