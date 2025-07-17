import sqlite3

from .connection import AppDatabase


def create_tables() -> None:
    """Runs SQL query to create the schema"""
    conn = AppDatabase.get_connection()

    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS video_metadata (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    language TEXT NOT NULL,
                    length TEXT NOT NULL,
                    image_path TEXT NOT NULL,
                    full_path TEXT NOT NULL,
                    full_sub_path TEXT NOT NULL,
                    tmdb_title TEXT NOT NULL,
                    tmdb_director TEXT,
                    tmdb_year TEXT NOT NULL,
                    tmdb_overview TEXT NOT NULL,
                    tmdb_genres TEXT NOT NULL,
                    tmdb_poster_path TEXT NOT NULL
                );
                """
            )
    except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
        raise RuntimeError(f"Could not create table 'movie_metadata': {e}") from e
