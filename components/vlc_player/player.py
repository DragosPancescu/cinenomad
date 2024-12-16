import vlc
import os
import copy
import math
import yaml
import time
import threading

import tkinter as tk

from typing import Callable


class Player(tk.Toplevel):
    def __init__(
        self,
        parent: tk.Widget,
        config_params: dict,
        video_path: str,
        sub_path: str,
        total_seconds: int,
    ):
        super().__init__(parent)

        # Properties
        self._parent = parent
        self._video_path = video_path
        self._sub_path = sub_path
        self._config_params = copy.deepcopy(config_params)
        self.vlc_player_config_path = "settings/vlc_player_config.yaml"
        self._vlc_player_config = self._read_config()
        self._scale_updating = (
            False  # Track if the scale is being updated by the player
        )
        self._total_seconds = total_seconds

        # Variables used for mouse motion check
        self._prev_x, self._prev_y = None, None
        self._move_threshold = self._vlc_player_config["VlcPlayerProperties"][
            "CursorPixelMovingThreshold"
        ]

        # Controls inactivty hide mechanics
        self._inactivity_timeout = self._vlc_player_config["VlcPlayerProperties"][
            "InactivityTimeout"
        ]
        self._controls_hidden = False

        # Controls the time interval for updating the time slider
        self._update_timeslider_interval = self._vlc_player_config[
            "VlcPlayerProperties"
        ]["UpdateScaleTimeInterval"]

        # Configure widget
        self.configure(**self._config_params["Design"])

        # Keep the window on top
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.wm_overrideredirect(True)

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Get focus to this window
        self.focus()

        # Configure vlc player
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Initializing Player for {video_path}")
        self._vlc_instance = vlc.Instance(self._vlc_player_config["VlcInstanceOptions"])
        self._player = self._vlc_instance.media_player_new()

        # Set window id for the player
        self.update_idletasks()
        self._setup_vlc_event_callbacks()  # Set up event callbacks
        self._player.set_xwindow(self.winfo_id())

        # Try to add subs
        if os.path.exists(self._sub_path):
            self._sub = self._player.add_slave(
                vlc.MediaSlaveType.subtitle, self._sub_path, True
            )
        else:
            print(
                f"Could not find path to subtitle file: {self._sub_path}, trying to find subtitles embedded in the file."
            )
            if self._player.video_get_spu_count() > 0:
                # TODO: Helper function to extract english sub for now
                self._player.video_set_spu(1)

        self._media = self._vlc_instance.media_new(video_path)
        self._player.set_media(self._media)

        # Bindings
        self.bind("<Escape>", self.close)
        self.bind("<space>", self.toogle_play_state)
        self.bind("<Right>", self.go_forward)
        self.bind("<Left>", self.go_backward)
        self.bind("<Motion>", self.toogle_controls_visibility)

        # Add controls
        self._menu = PlayerMenu(
            self,
            self.play,
            self.stop,
            self.go_forward,
            self.go_backward,
            self.seek,
            self._total_seconds,
        )

        # Schedule the mouse hiding function
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def _setup_vlc_event_callbacks(self):
        event_manager = self._player.event_manager()

        # Setup update timeslider on media position change
        event_manager.event_attach(vlc.EventType.MediaPlayerPositionChanged, self._update_timeslider)

    def _update_timeslider(self, e=None):
        """Callback for when the media player's position changes."""
        seconds = self._player.get_time() // 1000

        # Update the time slider on the main thread
        self.after(0, self._menu.set_timeslider_value, seconds)

    def seek(self, time_in_seconds):
        """Seek the player to the specified time."""
        if not self._scale_updating:  # Avoid recursion from scale updates
            self._scale_updating = True
            self._player.set_time(time_in_seconds * 1000)  # Convert to milliseconds
            self._scale_updating = False

    def _reset_timer(self):
        if self._controls_hidden:
            self._show_controls()

        # Cancel the existing timer and restart
        self.after_cancel(self._timer_id)
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def toogle_controls_visibility(self, e=None):
        # If there is no event that means the callback does not come from the <Motion> bind
        if e == None:
            self._reset_timer()
            return

        # Check if the motion exceeds a certain degree, as this binding is very noisy
        # Get the current mouse position
        current_x, current_y = e.x, e.y

        # If this is the first motion event, initialize the previous position
        if self._prev_x == None or self._prev_y == None:
            self._prev_x, self._prev_y = current_x, current_y
            return

        # Calculate the euclidian distance moved
        distance = math.sqrt(
            (current_x - self._prev_x) ** 2 + (current_y - self._prev_y) ** 2
        )

        # Check if the distance exceeds the threshold
        if distance >= self._move_threshold:
            self._reset_timer()

            # Update the previous position
            self._prev_x, self._prev_y = current_x, current_y

    def toogle_play_state(self, e=None) -> None:
        self.toogle_controls_visibility()
        state = self._player.get_state()
        print(f"Toogle state: {state}")
        if state == vlc.State.Playing:
            self.stop()
        else:
            self.play()

    def play(self) -> None:
        """Start playback."""
        print("Starting playback...")
        self._player.play()
        state = self._player.get_state()
        print(f"Player state after play: {state}")
        if state != vlc.State.Playing:
            print("Error: Playback did not start.")

    def stop(self) -> None:
        """Pause playback."""
        print("Pausing playback.")
        self._player.set_pause(1)

    def close(self, e=None) -> None:
        """Stop the player and close the widget."""
        print("Stopping player.")
        self._player.stop()
        print(f"Video closed: {self._video_path}")
        self._media.release()
        self._vlc_instance.release()
        self._parent.focus()  # Shift focus back to the parent
        self._menu.destroy()
        self.destroy()

    def go_forward(self, e=None) -> None:
        """Go forward 5 sec"""
        self.toogle_controls_visibility()
        self.seek(self._player.get_time() // 1000 + 5)
        self._update_timeslider()

    def go_backward(self, e=None) -> None:
        """Go backward 5 sec"""
        self.toogle_controls_visibility()
        self.seek(self._player.get_time() // 1000 - 5)
        self._update_timeslider()

    def _hide_controls(self):
        self.config(cursor="none")
        self._menu.hide()
        self._controls_hidden = True

    def _show_controls(self):
        self.config(cursor="")
        self._menu.show()
        self._controls_hidden = False

    def _read_config(self):
        with open(self.vlc_player_config_path) as conf_f:
            try:
                return yaml.safe_load(conf_f)
            except yaml.YAMLError as err:
                return err


class PlayerMenu(tk.Toplevel):
    def __init__(
        self,
        parent: Player,
        play_callback: Callable,
        stop_callback: Callable,
        go_forward_callback: Callable,
        go_backwards_callback: Callable,
        timeslider_callback: Callable,
        total_seconds: int,
    ):
        super().__init__(parent)

        self.resizable(False, False)
        self.wm_overrideredirect(True)

        self._parent = parent

        # Used for moving the menu around
        self.x_offset = None
        self.y_offset = None
        self.is_dragging = False

        self._play_button = tk.Button(self, text="Play")
        self._play_button.configure(command=play_callback)

        self._stop_button = tk.Button(self, text="Stop")
        self._stop_button.configure(command=stop_callback)

        self._close_button = tk.Button(self, text="Close")
        self._close_button.configure(command=self._parent.close)

        self._forward_button = tk.Button(self, text="Forward")
        self._forward_button.configure(command=go_forward_callback)

        self._backwards_button = tk.Button(self, text="Backwards")
        self._backwards_button.configure(command=go_backwards_callback)

        self._timeslider = tk.Scale(
            self,
            from_=0,
            to=total_seconds,
            orient=tk.HORIZONTAL,
            command=lambda value: timeslider_callback(int(value)),
        )

        self._play_button.grid(row=0, column=0, padx=5, pady=10)
        self._stop_button.grid(row=0, column=1, padx=5, pady=10)
        self._backwards_button.grid(row=0, column=2, padx=5, pady=10)
        self._forward_button.grid(row=0, column=3, padx=5, pady=10)
        self._close_button.grid(row=0, column=4, padx=5, pady=10)
        self._timeslider.grid(
            row=1, column=0, columnspan=5, sticky=tk.W + tk.E, padx=10, pady=10
        )

        # Initial placement on screen
        self._place_bottom_center()

        # Bindings
        self.bind("<ButtonPress-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag_motion)
        self.bind("<ButtonRelease-1>", self._stop_drag)

    def set_timeslider_value(self, value):
        self._timeslider.set(value)

    def _place_bottom_center(self) -> None:
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

        # Calculate coordinates to place the toplevel bottom middle with 20% tolerance
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + frame_height - toplevel_height - int(0.10 * frame_height)

        # Position the toplevel window
        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def _start_drag(self, e):
        # Don't interfere with the time slider
        if self._timeslider == self.winfo_containing(e.x_root, e.y_root):
            return

        self.x_offset = e.x
        self.y_offset = e.y
        self.is_dragging = True

    def _drag_motion(self, e):
        if self.is_dragging:
            x = self.winfo_x() + e.x - self.x_offset
            y = self.winfo_y() + e.y - self.y_offset
            self.geometry(f"{self.winfo_width()}x{self.winfo_height()}+{x}+{y}")

    def _stop_drag(self, e):
        self.is_dragging = False

    def show(self) -> None:
        self.deiconify()

    def hide(self) -> None:
        self.withdraw()
