import sqlite3
import threading

class AppDatabase:
    _conn = None
    _lock = threading.Lock()

    # TODO": Make configurable
    _path= r"/home/shared/Media-System-Player/db/database.db"

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Returns a connection to the sqlite database.
        If it exists, else it creates a new one

        Returns:
            Connection: Live sqlite3 db connection
        """
        with cls._lock:
            if cls._conn is None:
                print("No connection found, will create a new one")
                cls._conn = sqlite3.connect(cls._path, check_same_thread=False)
        return cls._conn
