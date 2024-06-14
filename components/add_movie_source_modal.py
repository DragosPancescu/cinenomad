import tkinter as tk


class AddMovieSourceModal(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)

        # self.__config_params = config_params

        # self.configure(**self.__config_params)

        self.title("Add new movie source")
        self.resizable(False, False)
        self.wm_overrideredirect(True)
        self.configure(
            background="#282828", 
            highlightthickness=1, 
            highlightbackground="#D9D9D9"
        )

        # Controls
        self.bind("<Escape>", self.close)

        # Add Button for making selection
        button1 = tk.Button(
            self,
            text="Add",
            highlightthickness=1,
            highlightbackground="#D9D9D9",
            borderwidth=0,
            background="#282828",
            foreground="#D9D9D9",
            activebackground="#D9D9D9",
            cursor="hand2",
            command=lambda: self.handle_user_choice("add"),
        )
        button1.place(relx=0.5, rely=0.5, anchor="center", x=-40, y=100)

        button2 = tk.Button(
            self,
            text="Cancel",
            highlightthickness=1,
            highlightbackground="#D9D9D9",
            borderwidth=0,
            background="#282828",
            foreground="#D9D9D9",
            activebackground="#D9D9D9",
            cursor="hand2",
            command=lambda: self.handle_user_choice("cancel"),
        )
        button2.place(relx=0.5, rely=0.5, anchor="center", x=40, y=100)
        self.__center(parent)

    def handle_user_choice(self, choice):
        if choice == "add":
            print("Added new movie source")
        else:
            print("Cancel new movie source")
        self.close()
        
    def __center(self, parent):
        self.geometry("600x300")

        parent.update_idletasks()
        self.update_idletasks()
        
        # Get frame dimensions and position
        frame_width = parent.winfo_width()
        frame_height = parent.winfo_height()
        frame_x = parent.winfo_rootx()
        frame_y = parent.winfo_rooty()

        # Get toplevel dimensions
        toplevel_width = self.winfo_width()
        toplevel_height = self.winfo_height()

        # Calculate coordinates to center the toplevel within the frame
        x = frame_x + (frame_width // 2) - (toplevel_width // 2)
        y = frame_y + (frame_height // 2) - (toplevel_height // 2)

        # Position the toplevel window
        self.geometry(f"{toplevel_width}x{toplevel_height}+{x}+{y}")

    def close(self, e=None):
        self.withdraw()
