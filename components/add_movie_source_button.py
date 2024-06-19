import tkinter as tk


class AddMovieSourceButton(tk.Button):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)

        self._config_params = config_params

        # Transform list to tuple
        self._config_params["font"] = tuple(self._config_params["font"])

        self.configure(**self._config_params)

        self.bind("<Enter>", self._on_enter_add_movie_source)
        self.bind("<Leave>", self._on_exit_add_movie_source)

    def _on_enter_add_movie_source(self, e=None) -> None:
        self.configure(
            background=self._config_params["foreground"],
            foreground=self._config_params["background"]
        )

    def _on_exit_add_movie_source(self, e=None) -> None :
        self.configure(
            background=self._config_params["background"],
            foreground=self._config_params["foreground"]
        )
