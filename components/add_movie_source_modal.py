import copy
import tkinter as tk


class AddMovieSourceModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.title(self._config_params["title"])
        self.geometry("600x300")
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        self.focus()

        # Controls
        self.bind("<Escape>", self.close)

        # Widgets
        self._init_widgets()

        # Change placement on screen
        self._center()

    def _handle_user_choice(self, choice: str) -> None:
        if choice == "Add":
            print("Added new movie source")
        else:
            print("Cancel new movie source")
        self.close()

    def _center(self) -> None:
        self._parent.update_idletasks()
        self.update_idletasks()

        # Get frame dimensions and position
        frame_width = self._parent.winfo_width()
        frame_height = self._parent.winfo_height()
        frame_x = self._parent.winfo_rootx()
        frame_y = self._parent.winfo_rooty()

        # Get toplevel dimensions
        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        # Calculate coordinates to center the toplevel within the frame
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + (frame_height // 2) - (toplevel_height // 2)

        # Position the toplevel window
        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def _init_widgets(self) -> None:
        add_button = tk.Button(
            self,
            text=self._config_params["AddButton"]["text"],
            command=lambda: self._handle_user_choice(
                self._config_params["AddButton"]["text"]
            ),
            **self._config_params["AddButton"]["Design"],
        )
        add_button.place(**self._config_params["AddButton"]["Placement"])

        cancel_button = tk.Button(
            self,
            text=self._config_params["CancelButton"]["text"],
            command=lambda: self._handle_user_choice(
                self._config_params["CancelButton"]["text"]
            ),
            **self._config_params["CancelButton"]["Design"],
        )
        cancel_button.place(**self._config_params["CancelButton"]["Placement"])

    def close(self, event=None) -> None:
        self.withdraw()
        self._parent.focus()
