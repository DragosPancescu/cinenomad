import copy
import tkinter as tk

from services.database import queries
from utils.events import KeyEvent
from ..common.centerable_toplevel import CenterableToplevel


class SettingsModal(CenterableToplevel):
    """Modal window for viewing and editing application settings."""

    def __init__(self, parent: tk.Widget, config_params: dict):
        super().__init__(parent)
        self._parent = parent

        # Configure
        self._config_params = copy.deepcopy(config_params)
        self.title(self._config_params["title"])
        self.geometry("500x300")
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(**self._config_params["Design"])
        self.focus()

        # Controls
        self.bind(KeyEvent.ESCAPE, self.close)

        # Settings entries (name -> Entry widget)
        self._entries = {}

        # Content frame for settings rows
        self._content_frame = tk.Frame(self, background=self._config_params["Design"]["background"])
        self._content_frame.place(relx=0.5, rely=0.05, relwidth=0.9, relheight=0.75, anchor="n")

        # Build settings rows
        self._build_settings_rows()

        # Buttons
        save_button = tk.Button(
            self,
            text=self._config_params["SaveButton"]["text"],
            command=self._save,
            **self._config_params["SaveButton"]["Design"],
        )
        save_button.place(**self._config_params["SaveButton"]["Placement"])

        cancel_button = tk.Button(
            self,
            text=self._config_params["CancelButton"]["text"],
            command=self.close,
            **self._config_params["CancelButton"]["Design"],
        )
        cancel_button.place(**self._config_params["CancelButton"]["Placement"])

        # Center on parent
        self._center()

    def _build_settings_rows(self) -> None:
        """Builds label + entry rows for each setting."""
        # Clear existing widgets
        for widget in self._content_frame.winfo_children():
            widget.destroy()
        self._entries.clear()

        settings = queries.get_all_settings()
        if settings is None:
            return

        label_config = copy.deepcopy(self._config_params["Label"]["Design"])
        entry_config = copy.deepcopy(self._config_params["Entry"]["Design"])

        for idx, setting in enumerate(settings):
            label = tk.Label(
                self._content_frame,
                text=setting.name,
                **label_config,
            )
            label.grid(row=idx, column=0, sticky="w", padx=(10, 20), pady=8)

            entry = tk.Entry(self._content_frame, **entry_config)
            entry.insert(0, setting.value if setting.value else "")
            entry.grid(row=idx, column=1, sticky="ew", padx=(0, 10), pady=8)

            self._entries[setting.name] = entry

        self._content_frame.grid_columnconfigure(1, weight=1)

    def refresh(self) -> None:
        """Reloads settings from the database."""
        self._build_settings_rows()

    def _save(self) -> None:
        """Saves all setting values to the database and closes the modal."""
        for name, entry in self._entries.items():
            queries.update_setting_value(name, entry.get())
        self.close()
