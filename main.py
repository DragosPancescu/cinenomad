import ctypes

from components import App
from utils import set_proc_name

import platform


def main():
    # Change process name
    if platform.system() == "Linux": set_proc_name("Media System App")

    # Ensure Xlib is thread-safe
    ctypes.CDLL("libX11.so").XInitThreads()

    # Start app
    App()


if __name__ == "__main__":
    main()