import vlc
import tkinter as tk
import os
import copy

from typing import Callable


class Player(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict, video_path: str, sub_path: str):
        super().__init__(parent)

        # Configure widget
        # Keep the window on top
        self.attributes("-topmost", True)

        self.resizable(False, False)
        self.wm_overrideredirect(True)

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Get focus to this window
        self.focus()

        self._parent = parent
        self._video_path = video_path
        self._sub_path = sub_path
        self._config_params = copy.deepcopy(config_params)

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        print(f"Initializing Player for {video_path}")
        self._vlc_instance = vlc.Instance("--no-xlib")
        self._player = self._vlc_instance.media_player_new()
        self._media = self._vlc_instance.media_new(video_path)
        self._player.set_media(self._media)

        # Try to add subs
        if os.path.exists(self._sub_path):
            self._sub = self._player.add_slave(self._player, self._sub_path, True)
        else:
            print(f"Could not find path to subtitle file: {self._sub_path}, trying to find subtitles embedded in the file.")
            if self._player.video_get_spu_count() > 0:
                # Get the list of subtitle tracks
                for i in range(self._player.video_get_spu_count()):
                    spu_description = self._player.video_get_spu_description()
                    print(f"Track {i}: {spu_description[i]}")
            # TODO: Helper function to extract english sub for now
            self._player.video_set_spu(1)

        self.update_idletasks()
        self._player.set_xwindow(self.winfo_id())

        # Add controls
        self._menu = PlayerMenu(self, self.play, self.stop)

        # Controls
        self.bind("<Escape>", self.close)
        self.bind("<space>", self._toogle_play_state)

        # Controls inactivty hide mechanics
        self._inactivity_timeout = 1000
        self._controls_hidden = False

        # Bind events to reset the inactivity timer
        self.bind("<Motion>", self._reset_timer)

        # Schedule the mouse hiding function
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def _toogle_play_state(self, e=None) -> None:
        self._reset_timer()
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
        self._parent.focus()  # Shift focus back to the parent
        self.destroy()

    def _reset_timer(self, e=None):
        if self._controls_hidden:
            self._show_controls()

        # Cancel the existing timer and restart
        self.after_cancel(self._timer_id)
        self._timer_id = self.after(self._inactivity_timeout, self._hide_controls)

    def _hide_controls(self):
        self.config(cursor="none")  # Hide the mouse pointer
        self._menu.hide()
        self._controls_hidden = True

    def _show_controls(self):
        self.config(cursor="")  # Restore the default cursor
        self._menu.show()
        self._controls_hidden = False


class PlayerMenu(tk.Toplevel):
    def __init__(
        self,
        parent: Player,
        play_callback: Callable,
        stop_callback: Callable
    ):
        super().__init__(parent)

        self.resizable(False, False)
        self.wm_overrideredirect(True)

        self._parent = parent

        self._play_button = tk.Button(self, text="Play")
        self._play_button.configure(command=play_callback)

        self._stop_button = tk.Button(self, text="Stop")
        self._stop_button.configure(command=stop_callback)

        self._close_button = tk.Button(self, text="Close")
        self._close_button.configure(command=self._parent.close)

        self._play_button.grid(row=0, column=0, padx=10, pady=10)
        self._stop_button.grid(row=0, column=1, padx=10, pady=10)
        self._close_button.grid(row=0, column=2, padx=10, pady=10)

        # Change placement on screen
        self._place_bottom_center()

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

        # Calculate coordinates to place the toplevel bottom middle with 10% tolerance
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + frame_height - toplevel_height - int(0.15 * frame_height)
        
        # Position the toplevel window
        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def show(self) -> None:
        self.deiconify()

    def hide(self) -> None:
        self.withdraw()
