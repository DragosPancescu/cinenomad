import subprocess
import tkinter as tk
from typing import Optional

from components import (
    AppControlButton,
    AddMovieSourceButton,
    ConnectorIcon,
    ConnectorLabel,
    ConnectorsFrame,
    AddMovieSourceModal,
)

from .strategy import ConnectorClickStrategy, NetflixConnectorClick, LocalConnectorClick
from utils.file_handling import load_json_file, load_yaml_file
from tk_alert import AlertGenerator


class App(tk.Tk):
    """Main app class"""

    def __init__(self, config_path: str, connector_data_path: str):
        super().__init__()

        ####### Configure #######
        self._configs = load_yaml_file(config_path)
        if self._configs is None:
            self.close()
            raise Exception("Cannot start application, encountered errors while loading the config file.")

        self.configure(**self._configs["App"])
        self.attributes("-fullscreen", True)

        # Alert object
        self._alert_generator = AlertGenerator(self)

        ####### Widgets #######
        # Close button
        self.close_button = AppControlButton(
            self, self._configs["CloseButton"]["Design"]
        )
        self.close_button.configure(command=self.close)
        self.close_button.place(**self._configs["CloseButton"]["Placement"])

        # Sleep button
        self.sleep_button = AppControlButton(
            self, self._configs["SleepButton"]["Design"]
        )
        self.sleep_button.configure(command=lambda: print("Sleep"))
        self.sleep_button.place(**self._configs["SleepButton"]["Placement"])

        # New Connector button
        self.new_connector_button = AddMovieSourceButton(
            self, self._configs["NewConnectorButton"]["Design"]
        )
        self.new_connector_button.place(
            **self._configs["NewConnectorButton"]["Placement"]
        )
        self.new_connector_button.configure(command=self.show_add_new_connector_modal)

        # Connectors
        self._connector_data = load_json_file(connector_data_path)

        if self._connector_data != None and len(self._connector_data) != 0:
            self.connectors_frame = ConnectorsFrame(
                self,
                self._configs["ConnectorsFrame"]["Design"],
                len(self._connector_data),
            )
            self.connectors_frame.place(**self._configs["ConnectorsFrame"]["Placement"])
            self._place_connectors()

        # Add new connector modal (toplevel)
        self.new_connector_modal = AddMovieSourceModal(
            self, self._configs["AddMovieSourceModal"]
        )
        self.new_connector_modal.withdraw()  # Keep it hidden

        # Version tag
        self.version_tag = tk.Label(
            self, text="v0.0.1-alpha", **self._configs["VersionTag"]["Design"]
        )
        self.version_tag.place(**self._configs["VersionTag"]["Placement"])

    def show_add_new_connector_modal(self) -> None:
        """Makes the 'Add new connector modal' visible and brings the focus to it."""
        self.new_connector_modal.deiconify()
        self.new_connector_modal.focus()

    def _place_connectors(self) -> None:
        for idx, connector in enumerate(self._connector_data):
            connector_button = ConnectorIcon(
                self.connectors_frame,
                self._configs["ConnectorIcon"]["Design"],
                connector["image_path"],
                connector["text"],
                self._get_strategy_for_connector(  # Inject click strategy
                    connector["text"]
                ),
            )
            connector_button.grid(
                column=idx, **self._configs["ConnectorIcon"]["Placement"]
            )

            connector_label = ConnectorLabel(
                self.connectors_frame,
                self._configs["ConnectorLabel"]["Design"],
                connector["text"],
            )
            connector_label.grid(
                column=idx, **self._configs["ConnectorLabel"]["Placement"]
            )

    def _get_strategy_for_connector(self, name: str) -> Optional[ConnectorClickStrategy]:
        if name == "Netflix":
            return NetflixConnectorClick(self, self._configs["NetflixBrowserModal"])
        if name == "Local":
            return LocalConnectorClick(self, self._configs["LocalMovieBrowserModal"])
        return None

    def close(self, event=None) -> None:
        """Close functionality for the main app.

        Args:
            event (n/a, optional): Event sent by the event handler in Tkinter. Defaults to None.
        """
        # TODO: Logger
        print("App closed")
        self.quit()
        self.destroy()
        subprocess.run(["sudo", "/sbin/shutdown", "-h", "now"], check=False)
