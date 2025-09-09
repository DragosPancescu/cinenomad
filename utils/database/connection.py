import os

import sqlite3
import threading

class AppDatabase:
    """Singleton class that handles connections to the sqlite3 local db
    """
    _conn = None
    _lock = threading.Lock()
    _path= os.path.join("db", "database.db")

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        """Returns a connection to the sqlite database.
        If it exists, else it creates a new one

        Returns:
            Connection: Live sqlite3 db connection
        """
        with cls._lock:
            if cls._conn is None:
                try:
                    cls._conn = sqlite3.connect(cls._path, check_same_thread=False)
                except Exception as e:
                    raise RuntimeError(f"Failed to connect to database: {e}") from e
        if cls._conn is None:
            raise RuntimeError("Database connection is None unexpectedly.")
        return cls._conn
