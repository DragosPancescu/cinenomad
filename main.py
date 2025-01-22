import ctypes

from components import App
from utils import set_proc_name

import platform


def main():
    # Change process name
    if platform.system() == "Linux":
        set_proc_name("media-app-alpha")

    # Ensure Xlib is thread-safe
    ctypes.CDLL("libX11.so").XInitThreads()

    # Start app
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
