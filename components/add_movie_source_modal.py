import copy
import tkinter as tk


class AddMovieSourceModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.focus()

        self._config_params = copy.deepcopy(config_params)

        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])

        # Controls
        self.bind("<Escape>", self.close)

        # Widgets
        # Add Button for making selection
        AddButton = tk.Button(
            self,
            text=self._config_params["AddButton"]["text"],
            command=lambda: self.handle_user_choice(
                self._config_params["AddButton"]["text"]
            ),
            **self._config_params["AddButton"]["Design"],
        )
        AddButton.place(**self._config_params["AddButton"]["Placement"])

        # Cancel Button
        CancelButton = tk.Button(
            self,
            text=self._config_params["CancelButton"]["text"],
            command=lambda: self._handle_user_choice(
                self._config_params["CancelButton"]["text"]
            ),
            **self._config_params["CancelButton"]["Design"],
        )
        CancelButton.place(**self._config_params["CancelButton"]["Placement"])
        self._center(parent)

    def _handle_user_choice(self, choice: str) -> None:
        if choice == "Add":
            print("Added new movie source")
        else:
            print("Cancel new movie source")
        self.close()

    def _center(self, parent: tk.Widget) -> None:
        self.geometry("600x300")

        parent.update_idletasks()
        self.update_idletasks()

        # Get frame dimensions and position
        frame_width = parent.winfo_width()
        frame_height = parent.winfo_height()
        frame_x = parent.winfo_rootx()
        frame_y = parent.winfo_rooty()

        # Get toplevel dimensions
        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        # Calculate coordinates to center the toplevel within the frame
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + (frame_height // 2) - (toplevel_height // 2)

        # Position the toplevel window
        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def close(self, e=None) -> None:
        self.withdraw()
        self._parent.focus()
