import copy
import time
import tkinter as tk

from . import ConnectorClickStrategy
from components import AppControlButton

from utils import VideoMetadataListReader, MovieMetadata

from ..vlc_player import Player

# TODO: This will be configurable on first use or after in the settings menu.
FOLDER_PATH = r"/home/dragos/Downloads/input"


class LocalMovieBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.withdraw()  # Init in closed state

        self._config_params = copy.deepcopy(config_params)

        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Controls
        self.bind("<Escape>", self.hide)

        # Widgets
        # Close button
        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.hide)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        # Movie Buttons
        metadata_reader = VideoMetadataListReader(FOLDER_PATH)
        self._metadata = metadata_reader.get_metadata_list()

        # Init player manager
        # ------

        row, col = 1, 1
        for idx, metadata in enumerate(self._metadata):
            movie_card = LocalMovieCard(
                self, self._config_params["LocalMovieCard"], metadata
            )

            # Position on the grid
            if idx > 0 and idx % 5 == 0:
                row += 1
                col = 1
            col += 1

            movie_card.grid(row=row, column=col)

    def hide(self, e=None) -> None:
        self.withdraw()
        self._parent.focus()

    def show(self) -> None:
        self.deiconify()
        self.focus()


class LocalMovieCard(tk.Frame):
    def __init__(self, parent: tk.Widget, config_params: dict, metadata: MovieMetadata):
        super().__init__(parent)
        self._parent = parent

        self._config_params = copy.deepcopy(config_params)
        self._metadata = metadata
        self._player = None

        self.configure(**self._config_params["Design"])
        
        title = tk.Label(
            self,
            text=f"title: {metadata.title}",
            **self._config_params["Entry"]["Design"],
        )
        title.pack()

        year = tk.Label(
            self,
            text=f"year: {metadata.year}",
            **self._config_params["Entry"]["Design"],
        )
        year.pack()

        language = tk.Label(
            self,
            text=f"language: {metadata.language}",
            **self._config_params["Entry"]["Design"],
        )
        language.pack()

        length = tk.Label(
            self,
            text=f"length: {metadata.length}",
            **self._config_params["Entry"]["Design"],
        )
        length.pack()

        director = tk.Label(
            self,
            text=f"director: {metadata.director}",
            **self._config_params["Entry"]["Design"],
        )
        director.pack

        genres = tk.Label(
            self,
            text=f"genres: {', '.join(metadata.genres)}",
            **self._config_params["Entry"]["Design"],
        )
        genres.pack()

        image_panel = tk.Label(
            self,
            image=metadata.image,
            **self._config_params["Screenshot"]["Design"],
        )
        image_panel.pack()

        # Bind the left mouse button click event to the on_frame_click function
        image_panel.bind("<Button-1>", self._open_player)

    def _open_player(self, e=None):
        self._player = Player(self._parent, self._config_params["Player"], self._metadata.full_path, self._metadata.sub_path)
        self._player.play()
    
class LocalConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = config_params
        self._window = None

    def execute(self):
        if self._window == None:
            self._window = LocalMovieBrowserModal(self._parent, self._config_params)
        self._window.show()
