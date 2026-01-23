import copy
import math
import tkinter as tk

from components import AppControlButton
from utils import VideoMetadataReader
from utils.database import queries, models

from . import ConnectorClickStrategy
from ..vlc_player import Player


class LocalMovieBrowserModal(tk.Toplevel):
    """Modal window that serves as a browser for local media"""

    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        # Vars
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)

        metadata_reader = VideoMetadataReader(queries.get_setting_value("LocalFolder"))
        metadata_reader.update_metadata_db()

        self._metadata_list = queries.get_all_videos()
        self._movie_index = 0
        self._movie_list_length = (
            len(self._metadata_list) if self._metadata_list is not None else 0
        )

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

        # Widgets
        # TODO: Check if empty
        self._movie_card = LocalMovieCard(
            self,
            self._config_params["LocalMovieCard"],
            self._metadata_list[self._movie_index],
            self.winfo_screenheight(),
            self.winfo_screenwidth(),
        )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)

        self._poster_carousel = PosterCarousel(
            self,
            config_params=self._config_params["LocalMovieCard"]["PosterCarousel"],
            metadata_list=self._metadata_list,
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

        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.hide)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        # Bindings
        if len(self._metadata_list) > 1:
            self.bind_all("<Left>", self._on_scroll_movies)
            self.bind_all("<Right>", self._on_scroll_movies)

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

    def _on_scroll_movies(self, event) -> None:
        """Scroll through the movies using left/right arrow keys"""
        if event.keysym == "Left":  # Move left (decrease index)
            if self._movie_index > 0:
                self._movie_index -= 1
                self._poster_carousel.move_left()
        elif event.keysym == "Right":  # Move right (increase index)
            if self._movie_index < self._movie_list_length - 1:
                self._movie_index += 1
                self._poster_carousel.move_right()

        # TODO: After I finish carousel, make this functionality part of LocalMovieCard
        self._movie_card.destroy()
        self._movie_card = LocalMovieCard(
            self,
            self._config_params["LocalMovieCard"],
            self._metadata_list[self._movie_index],
            self.winfo_screenheight(),
            self.winfo_screenwidth(),
        )
        self._movie_card.pack(fill="both", expand=True)
        self._movie_card.pack_propagate(False)

        self._poster_carousel.lift()


class Poster(tk.Label):
    """Label widget that holds the poster image of a movie."""

    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        metadata: models.VideoMetadata,
        height: int,
        width: int,
    ):
        self._poster_image = metadata.get_image_object(width, height)
        super().__init__(parent, image=self._poster_image, **config_params)


class LocalMovieCard(tk.Frame):
    """Card that holds meta information about the movie, poster / screenshot and the play button"""

    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        metadata: models.VideoMetadata,
        height: int,
        width: int,
    ):
        super().__init__(parent)
        self._parent = parent
        self._metadata = metadata
        self._player = None
        self._colors_switch = False

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.configure(height=height, width=width, **self._config_params["Design"])

        entries_left_padx = math.floor(width * 0.02)
        title_pad = math.floor(height * 0.02)

        self._genres = tk.Label(
            self,
            text=f"{' | '.join(metadata.tmdb_genres)}",
            **self._config_params["Genres"]["Design"],
        )

        poster_frame_height = math.floor(height * 0.75)
        poster_frame_width = math.floor(poster_frame_height * 0.66)
        self._poster_frame = tk.Frame(self, **self._config_params["Design"])

        poster_height = poster_frame_height - (title_pad * 2)
        poster_width = poster_frame_width - (title_pad * 2)
        self._poster = Poster(
            self,
            config_params["Poster"]["Design"],
            self._metadata,
            poster_height,
            poster_width,
        )

        entries_frame_height = math.floor(height * 0.75)
        entries_frame_width = math.floor(width - poster_frame_width)
        self._entries_frame = tk.Frame(self, **self._config_params["Design"])

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

        overview_height = math.floor(entries_frame_height * 0.40)
        overview_font_size = max(10, int(overview_height * 0.3 * 0.3))
        self._overview = tk.Label(
            self._entries_frame,
            text=metadata.tmdb_overview,
            font=("Roboto Mono", overview_font_size),
            wraplength=entries_frame_width - (title_pad * 2),
            **self._config_params["Overview"]["Design"],
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

        # Placement
        self._poster_frame.place(
            x=0, y=0, width=poster_frame_width, height=poster_frame_height
        )
        self._poster.place(
            x=title_pad, y=title_pad, width=poster_width, height=poster_height
        )

        self._entries_frame.place(
            x=width - entries_frame_width,
            y=0,
            width=entries_frame_width,
            height=entries_frame_height,
        )
        self._title.place(
            x=entries_left_padx,
            y=title_pad,
            width=entries_frame_width,
            height=title_height,
        )
        self._year_director.place(
            x=entries_left_padx,
            y=title_height + (title_pad * 2),
            width=entries_width,
            height=entries_height,
        )
        self._language.place(
            x=entries_left_padx,
            y=title_height + entries_height + (title_pad * 2),
            width=entries_width,
            height=entries_height,
        )
        self._length.place(
            x=entries_left_padx,
            y=title_height + (entries_height * 2) + (title_pad * 2),
            width=entries_width,
            height=entries_height,
        )
        self._overview.place(
            x=entries_left_padx,
            y=title_height * 2 + (entries_height * 3) + (title_pad * 2),
            width=entries_frame_width - (title_pad * 4),
            height=overview_height,
        )
        self._play_button.place(
            x=entries_left_padx,
            y=entries_frame_height - play_button_height - title_pad,
            width=play_button_width,
            height=play_button_height,
        )

    def _open_player(self, event=None) -> None:
        self._player = Player(
            self._parent,
            self._config_params["Player"],
            self._metadata.full_path,
            self._metadata.full_sub_path,
            self._metadata.get_length_sec(),
        )
        self._player.play()
        self._player.setup_subtitles()

    def _on_hover_switch_colors(self, event=None) -> None:
        self._colors_switch = not self._colors_switch
        foreground = self._config_params["PlayButton"]["Design"]["foreground"]
        background = self._config_params["PlayButton"]["Design"]["background"]

        self._play_button.configure(
            background=(foreground if self._colors_switch else background),
            foreground=(background if self._colors_switch else foreground),
        )


class PosterCarousel(tk.Frame):
    """Poster carousel that sits under the movie cards and previews what's ahead and behind the current selection

    Make sure **poster_count** is always an odd number, otherwise this will break
    """

    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        metadata_list: list[models.VideoMetadata],
        height: int,
        width: int,
        poster_count: int,
    ):
        super().__init__(parent)
        self._parent = parent
        self._metadata_list = metadata_list
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
        self._selected = 0

        # The UI
        self._update_posters()
        self._show_posters()
        self.lift()

    def _update_posters(self) -> None:
        """Updates the posters list, it adds the posters around the _selected if there are any, else leaves it empty"""
        start = self._selected - (self._poster_count // 2)
        end = self._selected + (self._poster_count // 2) + 1

        for poster in self._visible_posters:
            if poster:
                poster.destroy()
        self._visible_posters = [None for _ in range(0, self._poster_count)]

        posters_idx = 0
        for metadata_idx in range(start, end):
            self._visible_posters[posters_idx] = None
            if metadata_idx >= 0 and metadata_idx < len(self._metadata_list):
                poster = Poster(
                    parent=self,
                    config_params=self._config_params["Poster"]["Design"],
                    metadata=self._metadata_list[metadata_idx],
                    height=self._poster_heigh,
                    width=self._poster_width,
                )
                self._visible_posters[posters_idx] = poster
            posters_idx += 1

        # Put border around currently selected poster
        self._visible_posters[self._poster_count // 2].configure(
            highlightthickness=3, highlightbackground="#D9D9D9"
        )

    def _show_posters(self) -> None:
        """Iterates the posters list and makes them visible in the UI"""
        for idx, poster in enumerate(self._visible_posters):
            if poster:
                poster.place(
                    x=(self._poster_width * idx) + self._poster_pad * (idx + 1),
                    y=0,
                    width=self._poster_width,
                    height=self._poster_heigh,
                )

    def move_right(self) -> None:
        """Moves the list 1 poster to the right"""
        if self._selected == len(self._metadata_list):
            return

        self._selected += 1
        self._update_posters()
        self._show_posters()

    def move_left(self) -> None:
        """Moves the list 1 poster to the left"""
        if self._selected == 0:
            return

        self._selected -= 1
        self._update_posters()
        self._show_posters()


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
