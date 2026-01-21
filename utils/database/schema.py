import os

import sqlite3

from .connection import AppDatabase
from utils.file_handling import load_yaml_file
from . import queries


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
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS connector (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    icon_path TEXT NOT NULL
                );
                """
            )

            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS setting (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value TEXT
                );
                """
            )
    except (sqlite3.OperationalError, sqlite3.IntegrityError) as e:
        raise RuntimeError(f"Could not create tables: {e}") from e


def seed_default() -> None:
    """Seeds the default values in database, mainly settings names"""
    setting_names = load_yaml_file(os.path.join(".", "config", "app_settings.yaml"))
    conn = AppDatabase.get_connection()
    with conn:
        for setting_name in setting_names:
            if queries.get_setting_value(setting_name) is not None:
                continue

            conn.execute(
                f"""
                INSERT INTO setting ('name', 'value')
                VALUES ('{setting_name}', '');
                """
            )
