import ctypes

import platform

from components import App
from utils import set_proc_name
from utils.database import schema


def main():
    # Change process name
    if platform.system() == "Linux":
        set_proc_name("cinenomad-alpha")

    # Ensure Xlib is thread-safe          
    ctypes.CDLL("libX11.so").XInitThreads()

    config_path = "settings/components_config.yaml"
    connector_data_path = "connectors/connector_obj.json"

    # Ensure sqlite3 database is created along with the schema
    schema.create_tables()

    # Start app
    app = App(config_path, connector_data_path)
    app.mainloop()


if __name__ == "__main__":
    main()
    