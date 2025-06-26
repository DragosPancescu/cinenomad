from .connection import AppDatabase


def create_tables() -> None:
    """Runs SQL query to create the schema
    """    
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS movie_metadata (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        language TEXT NOT NULL,
        length TEXT NOT NULL,
        image_path TEXT NOT NULL,
        full_path TEXT NOT NULL,
        full_sub_path TEXT NOT NULL,
        tmdb_title TEXT NOT NULL,
        tmdb_director TEXT NOT NULL,
        tmdb_year TEXT NOT NULL,
        tmdb_overview TEXT NOT NULL,
        tmdb_genres TEXT NOT NULL,
        tmdb_poster_path TEXT NOT NULL
    )
    """
    )

    conn.commit()
