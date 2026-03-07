import os
import copy
import platform
import math
import tkinter as tk

import vlc

from utils.file_handling import load_yaml_file
from utils.events import KeyEvent, MouseEvent

from .player_menu import PlayerMenu


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
        self._attach_to_window()
        self._media = self._vlc_instance.media_new(self._video_path)
        self._player.set_media(self._media)

        # Bindings
        self.bind(KeyEvent.ENTER, self.close)
        self.bind(KeyEvent.SPACE, self.toogle_play_state)
        self.bind(KeyEvent.RIGHT, self.go_forward)
        self.bind(KeyEvent.LEFT, self.go_backward)
        self.bind(MouseEvent.MOVE, self.toogle_controls_visibility)

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

    def _attach_to_window(self) -> None:
        """Attach the VLC player to the tkinter window using the platform-appropriate method."""
        wid = self.winfo_id()
        system = platform.system()
        if system == "Windows":
            self._player.set_hwnd(wid)
        else:
            self._player.set_xwindow(wid)

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
            clamped = max(0, min(time_in_seconds, self._total_seconds))
            self._player.set_time(clamped * 1000)  # Convert to milliseconds
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
        self._menu.lift()
        self._controls_hidden = False
