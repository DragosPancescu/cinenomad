import os
import copy
import tkinter as tk

from datetime import timedelta
from typing import Callable

import customtkinter as ctk

from utils.file_handling import read_tk_image
from utils.events import MouseEvent

class PlayerMenu(tk.Toplevel):
    """GUI class that encapsulate the media player controls"""

    def __init__(
        self,
        parent: tk.Toplevel,
        config_params: dict,
        play_callback: Callable,
        stop_callback: Callable,
        go_forward_callback: Callable,
        go_backwards_callback: Callable,
        timeslider_callback: Callable,
        close_callback: Callable,
        total_seconds: int,
    ):
        super().__init__(parent)
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._total_seconds = total_seconds

        # Configure
        self.withdraw()  # Hide while building so winfo_width/height are accurate
        self.configure(**self._config_params["Design"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.attributes("-topmost", True)

        # Used for moving the menu around
        self.x_offset = None
        self.y_offset = None
        self.is_dragging = False

        # Widgets
        # Configure Play button
        self._play_button_icon = read_tk_image(
            os.path.join("resources", "player_buttons", "Play.png")
        )
        self._play_button = tk.Button(
            self,
            image=self._play_button_icon,
            **self._config_params["Buttons"]["Design"],
        )
        self._play_button.configure(command=play_callback)

        # Configure Stop button
        self._stop_button_icon = read_tk_image(
            os.path.join("resources", "player_buttons", "Pause.png")
        )
        self._stop_button = tk.Button(
            self,
            image=self._stop_button_icon,
            **self._config_params["Buttons"]["Design"],
        )
        self._stop_button.configure(command=stop_callback)

        # Configure Forward button
        self._forward_button_icon = read_tk_image(
            os.path.join("resources", "player_buttons", "Forward.png")
        )
        self._forward_button = tk.Button(
            self,
            image=self._forward_button_icon,
            **self._config_params["Buttons"]["Design"],
        )
        self._forward_button.configure(command=go_forward_callback)

        # Configure Backward button
        self._backward_button_icon = read_tk_image(
            os.path.join("resources", "player_buttons", "Backward.png")
        )
        self._backwards_button = tk.Button(
            self,
            image=self._backward_button_icon,
            **self._config_params["Buttons"]["Design"],
        )
        self._backwards_button.configure(command=go_backwards_callback)

        # Configure Close button
        self._close_button = tk.Button(
            self,
            text="Close",
            fg="white",
            **self._config_params["Buttons"]["Design"],
        )
        self._close_button.configure(command=close_callback)

        self._timeslider = ctk.CTkSlider(
            self,
            from_=0,
            to=total_seconds,
            command=lambda value: timeslider_callback(int(value)),
            **self._config_params["Timeslider"]["Design"],
        )

        self._current_time = tk.Label(
            self,
            text=self._format_time_label(0),
            **self._config_params["Timestamp"]["Design"],
        )

        self._duration = tk.Label(
            self,
            text=self._format_time_label(self._total_seconds),
            **self._config_params["Timestamp"]["Design"],
        )

        # Bindings
        self.bind(MouseEvent.LEFT_PRESS, self._start_drag)
        self.bind(MouseEvent.DRAG_LEFT, self._drag_motion)
        self.bind(MouseEvent.LEFT_RELEASE, self._stop_drag)

        # Initial placement on screen
        self._place_controls()
        self.update_idletasks()  # Force geometry calculation while withdrawn
        self._place_bottom_center()
        self.deiconify()  # Show now that position and size are correct
        self.lift()

    def set_timeslider_value(self, value: int) -> None:
        """Updates the timeslider value so it matches the timeline on the video

        Args:
            value (int): Value in seconds
        """
        self._timeslider.set(value)
        self._current_time.configure(
            text=self._format_time_label(value),
        )

    def _format_time_label(self, seconds: int) -> str:
        """Formats the integer number of seconds into the following:

        Args:
            seconds (int): Number of seconds

        Returns:
            str: Formated output used in the GUI
        """
        return str(timedelta(seconds=seconds))

    def _place_bottom_center(self) -> None:
        self._parent.update_idletasks()

        # Get frame dimensions and position
        frame_width = self._parent.winfo_width()
        frame_height = self._parent.winfo_height()
        frame_x = self._parent.winfo_rootx()
        frame_y = self._parent.winfo_rooty()

        # Get toplevel dimensions (use reqwidth/reqheight as winfo_width returns 1 while withdrawn on Windows)
        toplevel_width = self.winfo_reqwidth()
        toplevel_height = self.winfo_reqheight()

        # Calculate coordinates to place the toplevel bottom middle with 20% tolerance
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + frame_height - toplevel_height - int(0.10 * frame_height)

        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def _place_controls(self) -> None:
        self.grid_columnconfigure(0, weight=1, minsize=75)
        self.grid_columnconfigure(1, weight=1, minsize=100)
        self.grid_columnconfigure(6, weight=1, minsize=100)
        self.grid_columnconfigure(7, weight=1, minsize=75)

        tk.Label(self).grid(row=0, column=0, padx=5, pady=(35, 10))
        tk.Label(self).grid(row=0, column=1, padx=5, pady=(35, 10))
        self._play_button.grid(row=0, column=2, padx=5, pady=(35, 10))
        self._stop_button.grid(row=0, column=3, padx=5, pady=(35, 10))
        self._forward_button.grid(row=0, column=4, padx=5, pady=(35, 10))
        self._backwards_button.grid(row=0, column=5, padx=5, pady=(35, 10))
        tk.Label(self).grid(row=0, column=6, padx=5, pady=(35, 10))
        self._close_button.grid(row=0, column=7, padx=5, pady=(35, 10))

        self._current_time.grid(row=1, column=0, pady=(20, 35))
        self._timeslider.grid(
            row=1, column=1, columnspan=6, sticky=tk.W + tk.E, padx=5, pady=(20, 35)
        )
        self._duration.grid(row=1, column=7, pady=(20, 35))

    def _start_drag(self, event) -> None:
        # Don't interfere with the time slider
        if (
            self.winfo_containing(event.x_root, event.y_root).winfo_name()
            == "!ctkcanvas"
        ):
            return

        self.x_offset = event.x
        self.y_offset = event.y
        self.is_dragging = True

    def _drag_motion(self, event) -> None:
        if self.is_dragging:
            x = self.winfo_x() + event.x - self.x_offset
            y = self.winfo_y() + event.y - self.y_offset
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{x}+{y}")

    def _stop_drag(self, event=None) -> None:
        self.is_dragging = False
