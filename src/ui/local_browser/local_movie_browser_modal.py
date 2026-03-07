import copy
import math
import tkinter as tk

from services.database import queries
from utils import VideoMetadataReader
from utils.events import KeyEvent
from ..common.app_control_button import AppControlButton

from .movie_selection_model import MovieSelectionModel
from .local_movie_card import LocalMovieCard
from .poster_carousel import PosterCarousel


class LocalMovieBrowserModal(tk.Toplevel):
    """Modal window that serves as a browser for local media"""

    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        # Vars
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)

        metadata_reader = VideoMetadataReader(queries.get_setting_value("LocalFolder"))
        metadata_reader.update_metadata_db()

        metadata_list = queries.get_all_videos()

        # Configure
        self.withdraw()  # Init in closed state
        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        self.geometry(
            f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0"
        )  # Fullscreen

        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.hide)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        if not metadata_list:
            tk.Label(
                self,
                text="No videos available.\nAdd a local folder in Settings.",
                **self._config_params["EmptyStateLabel"]["Design"],
            ).place(**self._config_params["EmptyStateLabel"]["Placement"])
            return

        self._model = MovieSelectionModel(metadata_list)
        self._model.add_observer(self._on_selection_changed)

        # Widgets
        self._movie_card = LocalMovieCard(
            self,
            self._config_params["LocalMovieCard"],
            self._model.current_metadata,
            self.winfo_screenheight(),
            self.winfo_screenwidth(),
        )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)

        self._poster_carousel = PosterCarousel(
            self,
            config_params=self._config_params["LocalMovieCard"]["PosterCarousel"],
            model=self._model,
            height=math.floor(self.winfo_screenheight() * 0.25),
            width=self.winfo_screenwidth(),
            poster_count=9,
        )
        self._poster_carousel.place(
            x=0,
            y=math.floor(self.winfo_screenheight() * 0.75),
            width=self.winfo_screenwidth(),
            height=math.floor(self.winfo_screenheight() * 0.25),
        )

        # Force update/refresh
        self.update_idletasks()
        self.update()

        # Bindings
        if self._model.count > 1:
            self.bind_all(KeyEvent.LEFT, self._on_scroll_movies)
            self.bind_all(KeyEvent.RIGHT, self._on_scroll_movies)

        self.bind(KeyEvent.ESCAPE, self.hide)

    def hide(self, event=None) -> None:
        """Hides the modal and gives back the focus to the parent Widget

        Args:
            event (, optional): Tkinter binding event. Defaults to None.
        """
        self.withdraw()
        self._parent.focus()
        self.config(cursor="none")

    def show(self) -> None:
        """Shows the modal and sets the focus"""
        self.deiconify()
        self.focus()
        self.config(cursor="")

    def _on_scroll_movies(self, event) -> None:
        """Scroll through the movies using left/right arrow keys"""
        if event.keysym == "Left":
            self._model.select_prev()
        elif event.keysym == "Right":
            self._model.select_next()

    def _on_selection_changed(self, index: int) -> None:
        """Rebuilds the movie card when the selection changes."""
        self._movie_card.destroy()
        self._movie_card = LocalMovieCard(
            self,
            self._config_params["LocalMovieCard"],
            self._model.current_metadata,
            self.winfo_screenheight(),
            self.winfo_screenwidth(),
        )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)
        self._poster_carousel.lift()
