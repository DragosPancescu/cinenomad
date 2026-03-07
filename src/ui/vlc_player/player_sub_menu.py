import tkinter as tk

class SubtitleMenu(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)
        self._parent = parent
