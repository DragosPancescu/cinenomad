from components.app import App
from utils.process_utils import set_proc_name

import platform


def main():
    App()


if __name__ == "__main__":
    if platform.system() == "Linux": set_proc_name("Media System App")
    
    main()
