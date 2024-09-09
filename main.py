from components import App
from utils import set_proc_name

import platform


def main():
    App()


if __name__ == "__main__":
    if platform.system() == "Linux": set_proc_name("Media System App")
    
    main()