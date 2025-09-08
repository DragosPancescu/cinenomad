import copy
import math
import tkinter as tk

from components import AppControlButton
from utils import VideoMetadataReader
from utils.database import queries, models

from . import ConnectorClickStrategy
from ..vlc_player import Player

# TODO: This will be configurable on first use or after in the settings menu.
# FOLDER_PATH = r"/home/shared/Local Movies"
FOLDER_PATH = r"D:\Documents\cinenomad_local"


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
        # TODO: Check if empty
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
        
        entries_left_padx = math.floor(width * 0.02)
        title_pad = math.floor(height * 0.02)
        
        # TODO : Widget components
        self._genres = tk.Label(
            self,
            text=f"{' | '.join(metadata.tmdb_genres)}",
            **self._config_params["Genres"]["Design"],
        )
        
        poster_frame_height = math.floor(height * 0.75)
        poster_frame_width = math.floor(poster_frame_height * 0.66)
        self._poster_frame = tk.Frame(
            self,
            background="#282828"
        )
        
        poster_height = poster_frame_height - (title_pad * 2)
        poster_width = poster_frame_width - (title_pad * 2)
        self._poster_image = metadata.get_image_object(poster_width, poster_height)
        self._poster = tk.Label(
            self,
            image=self._poster_image,
            **self._config_params["Poster"]["Design"],
        )

        entries_frame_height = math.floor(height * 0.75)
        entries_frame_width = math.floor(width - poster_frame_width)
        self._entries_frame = tk.Frame(
            self,
            background="#282828"
        )
        
        title_height = math.floor(entries_frame_height * 0.1)
        title_font_size = max(10, int(title_height * 0.70))
        self._title = tk.Label(
            self._entries_frame,
            text=metadata.get_gui_title(),
            font=("Roboto Mono", title_font_size),
            **self._config_params["Title"]["Design"],
        )
        
        entries_height = math.floor(entries_frame_height * 0.06)
        entries_width = math.floor(entries_frame_width * 0.5)
        entries_font_size = max(10, int(entries_height * 0.6))
        
        self._year_director = tk.Label(
            self._entries_frame,
            font=("Roboto Mono", entries_font_size),
            text=f"{metadata.tmdb_year} | {metadata.tmdb_director}",
            **self._config_params["Entry"]["Design"],
        )
        
        self._language = tk.Label(
            self._entries_frame,
            font=("Roboto Mono", entries_font_size),
            text=f"{metadata.language.title()}",
            **self._config_params["Entry"]["Design"],
        )

        self._length = tk.Label(
            self._entries_frame,
            font=("Roboto Mono", entries_font_size),
            text=f"{metadata.get_length_gui_format()}",
            **self._config_params["Entry"]["Design"],
        )
        
        play_button_height = math.floor(entries_frame_height * 0.1)
        play_button_width = math.floor(entries_frame_width * 0.35)
        play_button_font_size = max(10, int(play_button_height * 0.4))
        self._play_button = tk.Button(
            self._entries_frame,
            font=("Roboto Mono", play_button_font_size),
            command=self._open_player,
            **self._config_params["PlayButton"]["Design"],
        )
        self._play_button.bind("<Enter>", self._on_hover_switch_colors)
        self._play_button.bind("<Leave>", self._on_hover_switch_colors)

        overview_height = math.floor(height * 0.25)
        overview_font_size = max(10, int(overview_height * 0.4 * 0.3))
        self._overview = tk.Label(
            self,
            text=metadata.tmdb_overview,
            font=("Roboto Mono", overview_font_size),
            wraplength=width - (title_pad * 2),
            **self._config_params["Overview"]["Design"],
        )
        
        # Placement
        self._poster_frame.place(x=0, y=0, width=poster_frame_width, height=poster_frame_height)
        self._poster.place(x=title_pad, y=title_pad, width=poster_width, height=poster_height)
        
        self._entries_frame.place(x=width - entries_frame_width, y=0, width=entries_frame_width, height=entries_frame_height)
        self._title.place(x=entries_left_padx, y=title_pad, width=entries_frame_width, height=title_height)
        self._year_director.place(x=entries_left_padx, y=title_height + (title_pad * 2), width=entries_width, height=entries_height)
        self._language.place(x=entries_left_padx, y=title_height + entries_height + (title_pad * 2), width=entries_width, height=entries_height)
        self._length.place(x=entries_left_padx, y=title_height + (entries_height * 2) + (title_pad * 2), width=entries_width, height=entries_height)
        self._play_button.place(x=entries_left_padx, y=entries_frame_height - play_button_height - title_pad, width=play_button_width, height=play_button_height)
        
        self._overview.place(x=title_pad, y=height - overview_height, width=width - (title_pad * 2), height=overview_height)


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
