import yaml
import json

import tkinter as tk

from .app_control_button import AppControlButton
from .add_movie_source_button import AddMovieSourceButton
from .connector import ConnectorIcon, ConnectorLabel, ConnectorsFrame
from .add_movie_source_modal import AddMovieSourceModal


class App(tk.Tk):
    def __init__(self):
        print("App started")

        super().__init__()

        # Configure
        self.config_path = "settings/components_config.yaml"
        self.__configs = self._read_config()  # TODO: Check error

        self.connector_data_path = "connectors/connector_obj.json"
        self.__connector_data = self._read_connector_data()  # TODO: Check error

        self.configure(**self.__configs["App"])
        self.attributes("-fullscreen", True)

        # Controls
        self.bind("<Escape>", self.close)

        # ----- Widgets
        # Close button
        self.close_button = AppControlButton(
            self, self.__configs["CloseButton"]["Design"]
        )
        self.close_button.configure(command=self.close)
        self.close_button.place(**self.__configs["CloseButton"]["Placement"])

        # Sleep button
        self.sleep_button = AppControlButton(
            self, self.__configs["SleepButton"]["Design"]
        )
        self.sleep_button.configure(command=lambda: print("Sleep"))
        self.sleep_button.place(**self.__configs["SleepButton"]["Placement"])

        # New Connector button
        self.new_connector_button = AddMovieSourceButton(
            self, self.__configs["NewConnectorButton"]["Design"]
        )
        self.new_connector_button.place(
            **self.__configs["NewConnectorButton"]["Placement"]
        )
        self.new_connector_button.configure(command=self.show_add_new_connector_modal)

        # Connectors
        self.connectors_frame = ConnectorsFrame(
            self,
            self.__configs["ConnectorsFrame"]["Design"],
            len(self.__connector_data),
        )
        self.connectors_frame.place(**self.__configs["ConnectorsFrame"]["Placement"])

        for idx, connector in enumerate(self.__connector_data):
            # TODO: Check if image is available
            connector_button = ConnectorIcon(
                self.connectors_frame,
                self.__configs["ConnectorIcon"]["Design"],
                connector["image_path"],
                connector["text"],
            )

            connector_button.grid(
                column=idx, **self.__configs["ConnectorIcon"]["Placement"]
            )
            
            connector_label = ConnectorLabel(
                self.connectors_frame,
                self.__configs["ConnectorLabel"]["Design"],
                connector["text"],
            )
            connector_label.grid(
                column=idx, **self.__configs["ConnectorLabel"]["Placement"]
            )

        # Add new connector modal (toplevel)
        self.new_connector_modal = AddMovieSourceModal(self, self.__configs["AddMovieSourceModal"])
        self.new_connector_modal.withdraw() # Keep it hidden

        # Render loop
        self.mainloop()

    def _read_config(self):
        with open(self.config_path) as conf_f:
            try:
                return yaml.safe_load(conf_f)
            except yaml.YAMLError as err:
                return err

    def _read_connector_data(self):
        with open(self.connector_data_path) as conf_c:
            try:
                return json.load(conf_c)
            except json.JSONDecodeError as err:
                return err

    def show_add_new_connector_modal(self):
        self.new_connector_modal.deiconify()

    def close(self, e=None):
        print("App closed")
        self.destroy()
