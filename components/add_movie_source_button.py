import tkinter as tk


class AddMovieSourceButton(tk.Button):
    def __init__(self, parent, config_params):
        super().__init__(parent)

        self.__config_params = config_params

        # Transform list to tuple
        self.__config_params["font"] = tuple(self.__config_params["font"])

        self.configure(**self.__config_params)

        self.bind("<Enter>", self.__on_enter_add_movie_source)
        self.bind("<Leave>", self.__on_exit_add_movie_source)

    def __on_enter_add_movie_source(self, e=None):
        self.configure(
            background=self.__config_params["foreground"],
            foreground=self.__config_params["background"]
        )

    def __on_exit_add_movie_source(self, e=None):
        self.configure(
            background=self.__config_params["background"],
            foreground=self.__config_params["foreground"]
        )
