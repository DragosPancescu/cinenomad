import copy
import math
import tkinter as tk

from services.database import models
from utils.events import MouseEvent
from ..vlc_player import Player

from .poster import Poster


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
            text=str(metadata.length),
            **self._config_params["Entry"]["Design"],
        )

        overview_height = math.floor(entries_frame_height * 0.40)
        overview_font_size = max(10, int(overview_height * 0.3 * 0.3))
        # Use Text widget for better text handling
        self._overview = tk.Text(
            self._entries_frame,
            wrap=tk.WORD,  # Wrap at word boundaries
            font=("Roboto Mono", overview_font_size),
            height=overview_height,  # Number of lines
            width=max(
                1,
                int(
                    (entries_frame_width - (title_pad * 2))
                    // (overview_font_size * 0.6)
                ),
            ),  # Approximate character width
            padx=5,
            pady=5,
            state=tk.DISABLED,  # Make read-only
            **self._config_params["Overview"]["Design"],
        )

        # Insert text and re-enable for editing
        self._overview.config(state=tk.NORMAL)
        self._overview.delete("1.0", tk.END)
        self._overview.insert("1.0", metadata.tmdb_overview)
        self._overview.config(state=tk.DISABLED)

        play_button_height = math.floor(entries_frame_height * 0.1)
        play_button_width = math.floor(entries_frame_width * 0.35)
        play_button_font_size = max(10, int(play_button_height * 0.4))
        self._play_button = tk.Button(
            self._entries_frame,
            font=("Roboto Mono", play_button_font_size),
            command=self._open_player,
            **self._config_params["PlayButton"]["Design"],
        )
        self._play_button.bind(MouseEvent.ENTER, self._on_hover_switch_colors)
        self._play_button.bind(MouseEvent.LEAVE, self._on_hover_switch_colors)

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
            int(self._metadata.length.total_seconds()),
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
