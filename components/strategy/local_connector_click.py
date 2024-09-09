import os

import tkinter as tk

from . import ConnectorClickStrategy
from components import AppControlButton

from utils import VideoMetadataListReader

# TODO: This will be configurable on first use or after in the settings menu.
FOLDER_PATH = r"C:\Users\drago\Downloads\The.Legend.of.Korra.S02.1080p.SKST.WEB-DL.DD+2.0.H.264-playWEB"


class LocalMovieBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.withdraw()  # Init in closed state

        self._config_params = config_params

        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Controls
        self.bind("<Escape>", self.close)

        # Widgets
        # Close button
        self.close_button = AppControlButton(
            self, self._config_params["LocalMovieBrowserModalCloseButton"]["Design"]
        )
        self.close_button.configure(command=self.close)
        self.close_button.place(
            **self._config_params["LocalMovieBrowserModalCloseButton"]["Placement"]
        )

        # Movie Buttons
        metadata_reader = VideoMetadataListReader(FOLDER_PATH)
        self._metadata = metadata_reader.get_metadata_list()

        for idx, metadata in enumerate(self._metadata):
            metadata_frame = tk.Frame(self, background="#282828", width=50, height=50, padx=5, pady=10, cursor="hand2")
            metadata_frame.grid(row=1, column=idx + 1)

            title = tk.Label(
                metadata_frame, 
                width=50, 
                height=2, 
                text=f"title: {metadata.title}"
            )
            title.pack()

            year = tk.Label(
                metadata_frame, 
                width=50, 
                height=2, 
                text=f"year: {metadata.year}"
            )
            year.pack()

            language = tk.Label(
                metadata_frame,
                width=50,
                height=2,
                text=f"language: {metadata.language}",
            )
            language.pack()

            length = tk.Label(
                metadata_frame,
                width=50,
                height=2,
                text=f"length: {metadata.length}",
            )
            length.pack()

            director = tk.Label(
                metadata_frame,
                width=50,
                height=2,
                text=f"director: {metadata.director}",
            )
            director.pack

            genres = tk.Label(
                metadata_frame,
                width=50,
                height=2,
                text=f"genres: {', '.join(metadata.genres)}",
            )
            genres.pack()

            image_panel = tk.Label(metadata_frame, image=metadata.image, width=200, height=200)
            image_panel.pack()

    def close(self, e=None) -> None:
        self.withdraw()
        self._parent.focus()

    def show(self) -> None:
        self.deiconify()
        self.focus()


class LocalConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = config_params
        self._window = None

    def execute(self):
        if self._window == None:
            self._window = LocalMovieBrowserModal(self._parent, self._config_params)
        self._window.show()
