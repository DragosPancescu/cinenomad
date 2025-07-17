import re
import copy
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
        self._parent = parent

        self._config_params = copy.deepcopy(config_params)

        # Configure
        self.withdraw()  # Init in closed state
        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Widgets
        self._canvas = tk.Canvas(self, **self._config_params["Canvas"]["Design"])
        self._frame = tk.Frame(self._canvas, **self._config_params["Frame"]["Design"])

        self._canvas.pack(**self._config_params["Canvas"]["Placement"])
        self._canvas.create_window(
            (4, 4), window=self._frame, anchor="nw", tags="self._frame"
        )

        # Close button
        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.hide)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        # Movie Buttons
        metadata_reader = VideoMetadataReader(FOLDER_PATH)
        metadata_reader.update_metadata_db()
        self._metadata = queries.get_all_videos()

        # TODO: CHECK LENGTH DYNAMICALLY
        if len(self._metadata) > 3:
            self._frame.bind("<Configure>", self._on_frame_configure)
            # Bind mouse wheel and up / down keys for scrolling
            self.bind_all("<Button-4>", self._on_mousewheel)
            self.bind_all("<Button-5>", self._on_mousewheel)
            self.bind_all("<Up>", self._on_mousewheel)
            self.bind_all("<Down>", self._on_mousewheel)

        # Bindings
        self.bind("<Escape>", self.hide)

        # Init player manager
        row, col = 1, 1
        for idx, metadata in enumerate(self._metadata):
            movie_card = LocalMovieCard(
                self._frame, self._config_params["LocalMovieCard"], metadata
            )
            # Position on the grid
            if idx > 0 and idx % 2 == 0:
                row += 1
                col = 1
            col += 1

            movie_card.grid(row=row, column=col, padx=70, pady=12)

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

    def _on_frame_configure(self, event=None) -> None:
        """Reset the scroll region to encompass the inner frame"""
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_mousewheel(self, event) -> None:
        """Scroll the canvas using the mouse wheel"""
        if event.num == 4 or event.keysym == "Up":  # Scroll up
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.keysym == "Down":  # Scroll down
            self._canvas.yview_scroll(1, "units")


class LocalMovieCard(tk.Frame):
    """Card that hold meta information about the movie, poster / screenshot and the play button"""

    def __init__(self, parent: tk.Widget, config_params: dict, metadata: models.VideoMetadata):
        super().__init__(parent)
        self._parent = parent
        self._metadata = metadata
        self._player = None
        self._colors_switch = False

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.configure(**self._config_params["Design"])
        self._config_params["Title"]["Placement"]["pady"] = tuple(
            self._config_params["Title"]["Placement"]["pady"]
        )

        # Widget components
        self._poster = tk.Label(
            self,
            image=metadata.get_image_object(),
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
            text=f"{metadata.tmdb_overview}",
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
