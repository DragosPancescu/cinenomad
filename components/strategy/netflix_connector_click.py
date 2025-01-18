import subprocess
import signal
import copy
import os

from . import ConnectorClickStrategy

import tkinter as tk


class NetflixBrowserModal(tk.Toplevel):
    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent
        self.withdraw()  # Init in closed state

        self._config_params = copy.deepcopy(config_params)

        self.focus()
        self.title(self._config_params["title"])
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])

        # Make fullscreen
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")

        # Controls
        self.bind("<Escape>", self.close)

        self._args = [
            "-kiosk",
            "--new-window",
            "--hide-scrollbars",
            "--force-device-scale-factor",
        ]
        self._profile = "Profile 1"
        self._process = None

    def _open_flatpak_chrome(self, url: str, profile: str, *args) -> subprocess.Popen:
        """
        Opens a URL in Google Chrome installed via Flatpak with optional arguments.

        :param url: The URL to open.
        :param args: Chromium accepted arguments
        """
        # Base command
        command = ["flatpak", "run", "com.google.Chrome"]

        # Add any additional arguments
        if args:
            command.extend(args)

        # Specify the user profile
        command.append(f"--profile-directory={profile}")

        # Append the URL
        command.append(url)
        print(command)

        try:
            # Run the command and return the process
            process = subprocess.Popen(command, preexec_fn=os.setpgrp)
            return process
        except FileNotFoundError:
            print("Flatpak is not installed, or Chrome is not installed via Flatpak.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to open Chrome via Flatpak: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")
            return None

    def _close_chrome(self, process: subprocess.Popen) -> None:
        """
        Closes the Chrome instance launched via Flatpak.

        :param process: The Popen process object for the Chrome instance.
        """
        if process:
            try:
                # Kill the entire process group using the PGID
                pgid = os.getpgid(process.pid)
                os.killpg(pgid, signal.SIGTERM)
                print("Chrome closed successfully.")
            except Exception as e:
                print(f"An error occurred while closing Chrome: {e}")
        else:
            print("No process found to terminate.")

    def close(self, e=None) -> None:
        self._close_chrome(self._process)
        self._parent.focus()
        self.destroy()

    def show(self) -> None:
        # self.deiconify()
        # self.config(cursor="")

        self._chrome_process = self._open_flatpak_chrome(
            "https://www.netflix.com", self._profile, *self._args
        )

        # self.focus()


class NetflixConnectorClick(ConnectorClickStrategy):
    def __init__(self, parent: tk.Widget, config_params: dict):
        self._parent = parent
        self._config_params = config_params
        self._window = None
        self._chrome_process = None

    def execute(self):
        if self._window == None:
            self._window = NetflixBrowserModal(self._parent, self._config_params)
        self._window.show()
