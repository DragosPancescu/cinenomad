import copy
import math
import tkinter as tk

from components import AppControlButton
from utils import VideoMetadataReader
from utils.database import queries, models

from . import ConnectorClickStrategy
from ..vlc_player import Player

# TODO: This will be configurable on first use or after in the settings menu.
FOLDER_PATH = r"/home/shared/Local Movies"


class LocalMovieBrowserModal(tk.Toplevel):
    """Modal window that serves as a browser for local media"""

    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        # Vars
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)

        metadata_reader = VideoMetadataReader(FOLDER_PATH)
        metadata_reader.update_metadata_db()

        self._metadata = queries.get_all_videos()
        self._movie_index = 0
        self._movie_list_length = len(self._metadata) if self._metadata is not None else 0

        # Configure
        self.withdraw()  # Init in closed state
        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0") # Fullscreen

        # Widgets
        self._movie_card = LocalMovieCard(
                self,
                self._config_params["LocalMovieCard"],
                self._metadata[self._movie_index],
                self.winfo_screenheight(),
                self.winfo_screenwidth()
            )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)
            
        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.hide)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        # Bindings
        if len(self._metadata) > 1:
            self.bind_all("<Button-4>", self._on_mousewheel)
            self.bind_all("<Button-5>", self._on_mousewheel)
            self.bind_all("<Up>", self._on_mousewheel)
            self.bind_all("<Down>", self._on_mousewheel)

        self.bind("<Escape>", self.hide)

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

    def _on_mousewheel(self, event) -> None:
        """Scroll the canvas using the mouse wheel"""
        if event.num == 4 or event.keysym == "Up":  # Scroll up
            if self._movie_index > 0:
                self._movie_index -= 1
            else:
                return
        elif event.num == 5 or event.keysym == "Down":  # Scroll down
            if self._movie_index < self._movie_list_length - 1:
                self._movie_index += 1
            else:
                return

        self._movie_card.destroy()
        self._movie_card = LocalMovieCard(
                self,
                self._config_params["LocalMovieCard"],
                self._metadata[self._movie_index ],
                self.winfo_screenheight(),
                self.winfo_screenwidth()
            )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)


class LocalMovieCard(tk.Frame):
    """Card that hold meta information about the movie, poster / screenshot and the play button"""

    def __init__(self, parent: tk.Widget, config_params: dict, metadata: models.VideoMetadata, height: int, width: int):
        super().__init__(parent)
        self._parent = parent
        self._metadata = metadata
        self._player = None
        self._colors_switch = False

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.configure(
            height=height,
            width=width,
            **self._config_params["Design"]
        )
        self._config_params["Title"]["Placement"]["pady"] = tuple(
            self._config_params["Title"]["Placement"]["pady"]
        )
        
        # Widget components
        self._poster_image = metadata.get_image_object()
        self._poster = tk.Label(
            self,
            image=self._poster_image,
            **self._config_params["Poster"]["Design"],
        )

        self._right_side_panel = tk.Frame(
            self, **self._config_params["RightSidePanel"]["Design"]
        )

        self._title = tk.Label(
            self._right_side_panel,
            text=metadata.get_gui_title(),
            **self._config_params["Title"]["Design"],
        )

        self._year_director = tk.Label(
            self._right_side_panel,
            text=f"{metadata.tmdb_year} | {metadata.tmdb_director}",
            **self._config_params["Entry"]["Design"],
        )

        self._length = tk.Label(
            self._right_side_panel,
            text=f"{metadata.get_length_gui_format()}",
            **self._config_params["Entry"]["Design"],
        )

        self._language = tk.Label(
            self._right_side_panel,
            text=f"{metadata.language.title()}",
            **self._config_params["Entry"]["Design"],
        )

        self._play_button = tk.Button(
            self._right_side_panel,
            command=self._open_player,
            **self._config_params["PlayButton"]["Design"],
        )
        self._play_button.bind("<Enter>", self._on_hover_switch_colors)
        self._play_button.bind("<Leave>", self._on_hover_switch_colors)

        self._overview = tk.Label(
            self,
            text=metadata.tmdb_overview,
            width=width,
            height=math.floor(height / 5),
            **self._config_params["Overview"]["Design"],
        )

        self._genres = tk.Label(
            self,
            text=f"{' | '.join(metadata.tmdb_genres)}",
            **self._config_params["Genres"]["Design"],
        )

        # Placement
        self._poster.grid(**self._config_params["Poster"]["Placement"])
        self._title.pack(**self._config_params["Title"]["Placement"])
        self._year_director.pack(**self._config_params["Entry"]["Placement"])
        self._language.pack(**self._config_params["Entry"]["Placement"])
        self._play_button.pack(**self._config_params["PlayButton"]["Placement"])
        self._length.pack(**self._config_params["Entry"]["Placement"])
        self._right_side_panel.grid(
            **self._config_params["RightSidePanel"]["Placement"]
        )
        self._overview.grid(**self._config_params["Overview"]["Placement"])
        self._genres.grid(**self._config_params["Genres"]["Placement"])

    def _open_player(self, event=None) -> None:
        self._player = Player(
            self._parent,
            self._config_params["Player"],
            self._metadata.full_path,
            self._metadata.full_sub_path,
            self._metadata.get_length_sec()
        )
        self._player.play()
        self._player.setup_subtitles()

    def _on_hover_switch_colors(self, event=None) -> None:
        self._colors_switch = not self._colors_switch
        foreground = self._config_params["PlayButton"]["Design"]["foreground"]
        background = self._config_params["PlayButton"]["Design"]["background"]

        self._play_button.configure(
            background=(foreground if self._colors_switch else background),
            foreground=(background if self._colors_switch else foreground)
        )


class LocalConnectorClick(ConnectorClickStrategy):
    """The local connector click strategy class, that opens the local browser window."""

    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._window = None

    def execute(self) -> None:
        if self._window is None:
            self._window = LocalMovieBrowserModal(self._parent, self._config_params)
        self._window.show()
