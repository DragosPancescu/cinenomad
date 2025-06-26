from .connection import AppDatabase
from .models import MovieMetadata


def insert_movie(metadata: MovieMetadata) -> None:
    """Inserts metadata about a movie

    Args:
        metadata (MovieMetadata): Metadata object
    """    
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO movie_metadata (
            language, length, image_path, full_path, full_sub_path,
            tmdb_title, tmdb_director, tmdb_year, tmdb_overview,
            tmdb_genres, tmdb_poster_path
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        (
            metadata.language,
            metadata.length,
            metadata.image_path,
            metadata.full_path,
            metadata.full_sub_path,
            metadata.tmdb_title,
            metadata.tmdb_director,
            metadata.tmdb_year,
            metadata.tmdb_overview,
            "|".join(metadata.tmdb_genres),
            metadata.tmdb_poster_path,
        ),
    )

    conn.commit()

