import logging

from .connection import AppDatabase
from .models import VideoMetadata, Connector, Setting, LogEntry

logger = logging.getLogger(__name__)


def insert_video(metadata: VideoMetadata) -> None:
    """Inserts metadata about a video

    Args:
        metadata (VideoMetadata): Metadata object
    """
    conn = AppDatabase.get_connection()

    conn.execute(
        """
        INSERT INTO video_metadata (
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


def get_all_videos() -> list[VideoMetadata]:
    """Retrieves all the video's metadatas from the database

    Returns:
        list[VideoMetadata]: List of VideoMetadata objects
    """    
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM video_metadata
        ORDER BY tmdb_title;
        """
    )

    rows = cursor.fetchall()
    if not rows:
        logger.debug("Could not find any videos")
        return []

    all_videos_list = []
    for row in rows:
        all_videos_list.append(
            VideoMetadata(
                language=row[1],
                length=row[2],
                image_path=row[3],
                full_path=row[4],
                full_sub_path=row[5],
                tmdb_title=row[6],
                tmdb_director=row[7],
                tmdb_year=row[8],
                tmdb_overview=row[9],
                tmdb_genres=list(row[10].split("|")),
                tmdb_poster_path=row[11],
            )
        )
    return all_videos_list


def get_video_by_path(path: str) -> VideoMetadata | None:
    """Retrieves a video's data given its full path

    Args:
        path (str): Full path to the video file

    Returns:
        VideoMetadata: Metadata object
    """
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM video_metadata
        WHERE full_path LIKE ?;
        """,
        path,
    )

    row = cursor.fetchone()
    if row is None:
        logger.debug(f"Could not find any video with path: {path}")
        return None

    return VideoMetadata(
        language=row[1],
        length=row[2],
        image_path=row[3],
        full_path=row[4],
        full_sub_path=row[5],
        tmdb_title=row[6],
        tmdb_director=row[7],
        tmdb_year=row[8],
        tmdb_overview=row[9],
        tmdb_genres=list(row[10].split("|")),
        tmdb_poster_path=row[11],
    )


def delete_video_by_path(path: str) -> None:
    """Deletes a video from video_metadata given its full path

    Args:
        path (str): Full path to the video file
    """
    conn = AppDatabase.get_connection()

    conn.execute(
        """
        DELETE FROM video_metadata
        WHERE full_path LIKE ?;
        """,
        [path]
    )
    conn.commit()


def get_connectors() -> list[Connector] | None:
    """Retrieves all available connectors

    Returns:
        Optional[list[Connector]]: List of Connector objects
    """    
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM connector
        ORDER BY id;
        """
    )

    rows = cursor.fetchall()
    if not rows:
        logger.debug("Could not find any connectors")
        return None
    
    connectors = []
    for row in rows:
        connectors.append(
            Connector(
                name=row[1],
                icon_path=row[2]
            )
        )
    return connectors


def get_setting_value(name: str) -> str | None:
    """Retrievs a setting's value

    Args:
        name (str): Name of the setting

    Returns:
        Optional[str]: Value of the given setting
    """
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT value
        FROM setting
        WHERE name LIKE ?;
        """,
        [name]
    )

    row = cursor.fetchone()
    if row is None:
        logger.debug(f"Could not find setting: {name}")
        return None
    
    return row[0]


def get_all_settings() -> list[Setting] | None:
    """Retrives all settings

    Returns:
        list[Setting] | None: _description_
    """
    conn = AppDatabase.get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM setting;
        """
    )

    rows = cursor.fetchall()
    if not rows:
        logger.debug("Could not find any settings")
        return None
    
    settings = []
    for row in rows:
        settings.append(
            Setting(
                name=row[1],
                value=row[2]
            )
        )
    return settings


def update_setting_value(name: str, value: str) -> None:
    """Updates a setting's value

    Args:
        name (str): Name of the setting
        value (str): New value for the setting
    """
    conn = AppDatabase.get_connection()
    conn.execute(
        """
        UPDATE setting
        SET value = ?
        WHERE name = ?;
        """,
        [value, name],
    )
    conn.commit()


def insert_log(record: LogEntry) -> None:
    """Inserts a log entry into the database

    Args:
        record (LogEntry): Log entry to insert
    """
    conn = AppDatabase.get_connection()
    conn.execute(
        """
        INSERT INTO log (
            timestamp, level, logger_name, message,
            module, func_name, line_no, traceback
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            record.timestamp,
            record.level,
            record.logger_name,
            record.message,
            record.module,
            record.func_name,
            record.line_no,
            record.traceback,
        ],
    )
    conn.commit()