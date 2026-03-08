import platform
import subprocess
import tkinter as tk
import tkinter.font as tkfont
from importlib.metadata import version, PackageNotFoundError

from tk_alert import AlertGenerator

from .common.app_control_button import AppControlButton
from .common.confirmation_modal import ConfirmationModal
from .common.connector_click_strategy import ConnectorClickStrategy
from .home.add_movie_source_button import AddMovieSourceButton
from .home.add_movie_source_modal import AddMovieSourceModal
from .home.connector import ConnectorIcon, ConnectorLabel, ConnectorsFrame
from .home.settings_modal import SettingsModal
from .local_browser import LocalConnectorClick
from .web_browser import WebConnectorClick

from services.database import queries
from utils.file_handling import load_yaml_file


class App(tk.Tk):
    """Main app class"""

    def __init__(self, config_path: str):
        super().__init__()

        for font_name in tkfont.names():
            tkfont.nametofont(font_name).configure(family="Roboto Mono")

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
        self._connector_data = queries.get_connectors()
        if self._connector_data is not None and len(self._connector_data) != 0:
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

        # Settings button
        self.settings_button = AppControlButton(
            self, self._configs["SettingsButton"]["Design"]
        )
        self.settings_button.configure(command=self.show_settings_modal)
        self.settings_button.place(**self._configs["SettingsButton"]["Placement"])

        # Settings modal (toplevel)
        self.settings_modal = SettingsModal(self, self._configs["SettingsModal"])

        # Version tag
        try:
            app_version = f"v{version('cinenomad')}"
        except PackageNotFoundError:
            app_version = "dev"
        self.version_tag = tk.Label(
            self, text=app_version, **self._configs["VersionTag"]["Design"]
        )
        self.version_tag.place(**self._configs["VersionTag"]["Placement"])

    def show_add_local_folder_path(self) -> None:
        pass
    
    def show_settings_modal(self) -> None:
        """Opens the settings modal with current values from the database."""
        self.settings_modal.refresh()
        self.settings_modal.deiconify()
        self.settings_modal._center()
        self.settings_modal.focus()

    def show_add_new_connector_modal(self) -> None:
        """Makes the 'Add new connector modal' visible and brings the focus to it."""
        self.new_connector_modal.deiconify()
        self.new_connector_modal._center()
        self.new_connector_modal.focus()

    def _place_connectors(self) -> None:
        for idx, connector in enumerate(self._connector_data):
            connector_button = ConnectorIcon(
                self.connectors_frame,
                self._configs["ConnectorIcon"],
                connector.icon_path,
                connector.name,
                self._get_strategy_for_connector(  # Inject click strategy
                    connector.name
                ),
            )
            connector_button.grid(
                column=idx, **self._configs["ConnectorIcon"]["Placement"]
            )

            connector_label = ConnectorLabel(
                self.connectors_frame,
                self._configs["ConnectorLabel"]["Design"],
                connector.name,
            )
            connector_label.grid(
                column=idx, **self._configs["ConnectorLabel"]["Placement"]
            )

    def _get_strategy_for_connector(self, name: str) -> ConnectorClickStrategy | None:
        if name == "Netflix":
            return WebConnectorClick(self, self._configs["WebBrowserModal"], "https://www.netflix.com")
        if name == "Local":
            return LocalConnectorClick(self, self._configs["LocalMovieBrowserModal"])
        if name == "Youtube":
            return WebConnectorClick(self, self._configs["WebBrowserModal"], "https://www.youtube.com")
        return None

    def close(self, event=None) -> None:
        """Close functionality for the main app.

        Args:
            event (n/a, optional): Event sent by the event handler in Tkinter. Defaults to None.
        """
        modal = ConfirmationModal(self, "Are you sure you want to shut down?", self._configs["ConfirmationModal"])
        self.wait_window(modal)
        if not modal.result:
            return

        print("App closed.")
        self.quit()
        self.destroy()

        if platform.system() == "Windows":
            subprocess.run(["shutdown", "/s", "/t", "0"], check=False)
        else:
            subprocess.run(["sudo", "/sbin/shutdown", "-h", "now"], check=False)
