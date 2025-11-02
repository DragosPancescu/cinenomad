import os
import time
import copy
import math
import tkinter as tk

from datetime import timedelta
from typing import Callable

import vlc
import customtkinter as ctk

from utils.file_handling import load_yaml_file, read_tk_image


class Player(tk.Toplevel):
    """Local Media Player GUI class representation"""

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
        self._vlc_player_config = load_yaml_file(os.path.join("config", "vlc_player_config.yaml"))
        self._total_seconds = total_seconds
        # Tracks if the scale is being updated by the player
        self._scale_updating = False

        # Variables used for mouse motion check
        self._cursor_prev_x, self._cursor_prev_y = None, None
        self._cursor_move_threshold = self._vlc_player_config["VlcPlayerProperties"][
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
        self.attributes("-topmost", True)
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.focus()

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Configure vlc (libvlc) player
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Initializing Player for {video_path}")
        self._vlc_instance = vlc.Instance(self._vlc_player_config["VlcInstanceOptions"])
        self._player = self._vlc_instance.media_player_new()

        # Set window id for the player
        self.update_idletasks()
        self._setup_vlc_event_callbacks()  # Set up event callbacks
        self._player.set_xwindow(self.winfo_id())
        self._media = self._vlc_instance.media_new(self._video_path)
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
            self._config_params["PlayerMenu"],
            self.play,
            self.stop,
            self.go_forward,
            self.go_backward,
            self.seek,
            self._total_seconds,
        )

        # Schedule the mouse hiding function
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def _setup_vlc_event_callbacks(self) -> None:
        event_manager = self._player.event_manager()

        # Setup update timeslider on media position change
        event_manager.event_attach(
            vlc.EventType.MediaPlayerPositionChanged, self._update_timeslider
        )

    def _update_timeslider(self, event=None) -> None:
        """Callback for when the media player's position changes."""
        seconds = self._player.get_time() // 1000

        # Update the time slider on the main thread
        self.after(0, self._menu.set_timeslider_value, seconds)

    def seek(self, time_in_seconds: int) -> None:
        """Seek the player to the specified time."""
        if not self._scale_updating:  # Avoid recursion from scale updates
            self._scale_updating = True
            self._player.set_time(time_in_seconds * 1000)  # Convert to milliseconds
            self._scale_updating = False

    def _reset_timer(self) -> None:
        if self._controls_hidden:
            self._show_controls()

        # Cancel the existing timer and restart
        self.after_cancel(self._timer_id)
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def toogle_controls_visibility(self, event=None) -> None:
        # If there is no event that means the callback does not come from the <Motion> bind
        if event is None:
            self._reset_timer()
            return
        
        # Get the current mouse position
        current_x, current_y = event.x, event.y

        # If this is the first motion event, initialize the previous position
        if self._cursor_prev_x is None or self._cursor_prev_y is None:
            self._cursor_prev_x, self._cursor_prev_y = current_x, current_y
            return

        # Calculate the euclidian distance moved
        distance = math.sqrt((current_x - self._cursor_prev_x) ** 2 + (current_y - self._cursor_prev_y) ** 2)

        # Check if the distance exceeds the threshold
        # Using a threshold as this binding is very noisy
        if distance >= self._cursor_move_threshold:
            self._reset_timer()
            # Update the previous position
            self._cursor_prev_x, self._cursor_prev_y = current_x, current_y

    def toogle_play_state(self, event=None) -> None:
        self.toogle_controls_visibility()
        state = self._player.get_state()
        print(f"Toogle state: {state}")
        if state == vlc.State.Playing:
            self.stop()
        else:
            self.play()

    def setup_subtitles(self) -> None:
        def extract_eng_subtitles(player):
            subtitles = player.video_get_spu_description()

            eng_sub = [sub for sub in subtitles if "english" in str(sub[1]).lower()]
            if len(eng_sub) > 0:
                return eng_sub[0][0]
            return -1
        
        # Try to add subs
        if os.path.exists(self._sub_path):
            self._player.add_slave(
                vlc.MediaSlaveType.subtitle, self._sub_path, True
            )
        else:
            print(
                f"Could not find path to subtitle file: {self._sub_path}, trying to find subtitles embedded in the file."
            )
            if self._player.video_get_spu_count() > 0:
                eng_sub_index = extract_eng_subtitles(self._player)
                print(f"Setting up subtitle with index: {eng_sub_index}")
                self._player.video_set_spu(eng_sub_index)

    def play(self) -> None:
        """Start playback."""
        print("Starting playback...")
        self._player.play()
        state = self._player.get_state()
        print(f"Player state after play: {state}")
        if state != vlc.State.Playing:
            print("Error: Playback did not start.")
        time.sleep(1)

    def stop(self) -> None:
        """Pause playback."""
        print("Pausing playback.")
        self._player.set_pause(1)

    def close(self, event=None) -> None:
        """Stop the player and close the widget."""
        print("Stopping player.")

        # Detach the event handler to avoid callbacks after closing
        self._player.event_manager().event_detach(vlc.EventType.MediaPlayerPositionChanged)

        self._player.stop()
        print(f"Video closed: {self._video_path}")
        self._media.release()
        self._vlc_instance.release()
        self._parent.focus()  # Shift focus back to the parent
        self._menu.destroy()
        self.destroy()

    def go_forward(self, event=None) -> None:
        """Go forward 5 sec"""
        self.toogle_controls_visibility()
        self.seek(self._player.get_time() // 1000 + 5)
        self._update_timeslider()

    def go_backward(self, event=None) -> None:
        """Go backward 5 sec"""
        self.toogle_controls_visibility()
        self.seek(self._player.get_time() // 1000 - 5)
        self._update_timeslider()

    def _hide_controls(self) -> None:
        self.config(cursor="none")
        self._menu.withdraw()
        self._controls_hidden = True

    def _show_controls(self) -> None:
        self.config(cursor="")
        self._menu.deiconify()
        self._controls_hidden = False


class PlayerMenu(tk.Toplevel):
    """GUI class that encapsulate the media player controls"""
    def __init__(
        self,
        parent: Player,
        config_params: dict,
        play_callback: Callable,
        stop_callback: Callable,
        go_forward_callback: Callable,
        go_backwards_callback: Callable,
        timeslider_callback: Callable,
        total_seconds: int,
    ):
        super().__init__(parent)
        self._parent = parent
        self._config_params = copy.deepcopy(config_params)
        self._total_seconds = total_seconds

        # Configure
        self.configure(**self._config_params["Design"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)

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
        self.bind("<ButtonPress-1>", self._start_drag)
        self.bind("<B1-Motion>", self._drag_motion)
        self.bind("<ButtonRelease-1>", self._stop_drag)

        # Initial placement on screen
        self._place_controls()
        self._place_bottom_center()

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
        tk.Label(self).grid(row=0, column=7, padx=5, pady=(35, 10))

        self._current_time.grid(row=1, column=0, pady=(20, 35))
        self._timeslider.grid(
            row=1, column=1, columnspan=6, sticky=tk.W + tk.E, padx=5, pady=(20, 35)
        )
        self._duration.grid(row=1, column=7, pady=(20, 35))

    def _start_drag(self, event) -> None:
        # Don't interfere with the time slider
        if self.winfo_containing(event.x_root, event.y_root).winfo_name() == "!ctkcanvas":
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


class SubtitleMenu(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
