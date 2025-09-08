import os
import ctypes

import platform

from components import App
from utils import set_proc_name
from utils.database import schema
from utils.file_handling import load_yaml_file


def main():
    if platform.system() == "Linux":
        set_proc_name("cinenomad-alpha")

        # Ensure Xlib is thread-safe
        ctypes.CDLL("libX11.so").XInitThreads()
    
    # Create required folders if first run
    required_folders = load_yaml_file(os.path.join("settings", "required_folders.yaml"))
    for folder_path in required_folders:
        if isinstance(folder_path, list):
           folder_path = os.path.join(*folder_path)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    config_path = os.path.join("settings", "components_config.yaml")
    
    # Ensure sqlite3 database is created along with the schema
    schema.create_tables()

    # Start app
    app = App(config_path)
    app.mainloop()


if __name__ == "__main__":
    main()