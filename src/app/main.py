import os
import sys
import ctypes

import platform

# Ensure src/ is on the path when running this file directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ui import App
from utils import set_proc_name
from services.database import schema
from services.logging import setup_logging
from utils.file_handling import load_yaml_file


def main():
    if platform.system() == "Linux":
        set_proc_name("cinenomad-alpha")

        # Ensure Xlib is thread-safe
        ctypes.CDLL("libX11.so").XInitThreads()
    
    # Create required folders if first run
    required_folders = load_yaml_file(os.path.join("config", "required_folders.yaml"))
    for folder_path in required_folders:
        if isinstance(folder_path, list):
           folder_path = os.path.join(*folder_path)
        
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
    
    # Ensure sqlite3 database is created along with the schema
    schema.create_tables()
    schema.seed_default()

    # Setup logging
    setup_logging(os.path.join("config", "logging_config.yaml"))

    # Start app
    app = App(os.path.join("config", "components_config.yaml"))
    app.mainloop()


if __name__ == "__main__":
    main()