import tkinter as tk


class CenterableToplevel(tk.Toplevel):
    """Base Toplevel that provides centering relative to a parent widget."""

    def _center(self) -> None:
        self._parent.update_idletasks()
        self.update_idletasks()

        frame_width = self._parent.winfo_width()
        frame_height = self._parent.winfo_height()
        frame_x = self._parent.winfo_rootx()
        frame_y = self._parent.winfo_rooty()

        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + (frame_height // 2) - (toplevel_height // 2)

        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def close(self, event=None) -> None:
        self.withdraw()
        self._parent.focus()
