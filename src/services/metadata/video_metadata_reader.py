import os
import re
import copy
import base64
import logging
from datetime import timedelta

import cv2
import numpy as np

from pymediainfo import MediaInfo
from langcodes import Language, LanguageTagError
from torrent_name_parser import TorrentNameParser as TNP

from utils.file_handling import load_yaml_file

logger = logging.getLogger(__name__)
from services.database import queries, models
from utils.exceptions import FolderNotFoundException
from .tmdb_api import (
    search_movie_tmbd_api_call,
    get_tmdb_metadata,
    get_movie_details_api_call,
    download_tmdb_poster,
    search_crew_tmdb_api_call,
    get_tmdb_configuration,
)


class VideoMetadataReader:
    """Utility class for retrieving metadata from a multimedia file stored locally and storing the info in the database"""

    def __init__(self, folder_path: str) -> None:
        self._folder_path = folder_path
        self._accepted_extensions = load_yaml_file(os.path.join(".", "config", "accepted_extension.yaml"))
        # Full paths
        self._file_names = self._read_video_file_names()
        self._tmdb_configuration = get_tmdb_configuration()

    def _read_video_file_names(self) -> list[str] | None:
        """Retrieves all file names from 'self._folder_path' filtered by the 'self._accepted_extensions'

        Returns:
            list: List containing valid file names
        """
        file_names = []
        try:
            for dirpath, _, filenames in os.walk(self._folder_path):
                for file in filenames:
                    full_path = os.path.join(dirpath, file)
                    if os.path.isfile(full_path):
                        file_names.append(full_path)

            # Filter using the accepted extensions list
            file_names = [
                file_name
                for file_name in file_names
                if file_name.split(".")[-1].lower() in self._accepted_extensions
            ]
        except FolderNotFoundException as exception:
            logger.error(f"Folder path: {self._folder_path} not found: {exception}")
        except Exception as exception:
            logger.error(
                f"Unexpected exception caught while retrieved file names from folder: {self._folder_path}, exception: {exception}"
            )
        return file_names

    def _get_tmdb_movie_metadata(self, file_name: str, runtime_mins: int) -> dict[str, str]:
        """Preprocessing and API call to TMDB to retrieve data about the movie / show

        Args:
            file_name (str): Original local media file name
            runtime_mins (int): Video length in minutes
            
        Returns:
            dict: Extracted data from TMDB
        """

        # Extract movie name from file_name
        tnp = TNP()
        movie_name = tnp.parse(file_name).title
        logger.debug(f"Parsed movie name: {movie_name}")

        season_episode = re.search("[sS][0-9]{1,2}[eE][0-9]{1,2}", file_name)
        is_tvshow = bool(season_episode)

        # API Call to  get info about movie / show
        movie_search_results = search_movie_tmbd_api_call(movie_name, is_tvshow)
        
        # Filter based on runtime
        movie_data = None
        runtime_key = "episode_run_time" if is_tvshow else "runtime"

        if movie_search_results is not None and len(movie_search_results) > 0:
            for search_result in movie_search_results:
                if is_tvshow:
                    movie_data = search_result
                    break

                details = get_movie_details_api_call(search_result["id"], is_tvshow)

                try:
                    tmdb_runtime = details[runtime_key][0] if is_tvshow else details[runtime_key]
                except Exception as e:
                    logger.warning(f"Could not get runtime for id: {search_result['id']}: {e}")
                    tmdb_runtime = 0

                if abs(int(tmdb_runtime) - runtime_mins) <= 1:
                    movie_data = search_result
                    break

        # Return dict with needed data
        metadata = get_tmdb_metadata(movie_data, is_tvshow)

        # API Call for Director name
        director = ""
        if metadata["id"] != "":
            director = search_crew_tmdb_api_call(metadata["id"], is_tvshow)

        metadata["director"] = director

        return metadata

    def _get_video_file_metadata(self, video_file_path: str) -> dict[str, str]:
        """Uses MediaInfo wrapper to get local video file metadata:

        Args:
            video_file_path (str): Path to the video file to extract metadata from

        Returns:
            dict: Local video file metada dictionary
        """
        media_info = MediaInfo.parse(video_file_path)

        general_track = list(
            filter(lambda track: track.track_type == "General", media_info.tracks)
        )[0]
        audio_tracks = list(
            filter(lambda track: track.track_type == "Audio", media_info.tracks)
        )

        language = ""
        if audio_tracks and "language" in audio_tracks[0].to_data().keys():
            language = audio_tracks[0].to_data()["language"]

        metadata = copy.deepcopy(general_track.to_data())
        metadata["language"] = language

        return metadata

    def _get_embedded_thumbnail(self, video_file_path: str) -> np.ndarray | None:
        """Attempts to extract an embedded cover image from the video file via MediaInfo.

        Args:
            video_file_path (str): Path to the video file

        Returns:
            numpy.ndarray | None: The decoded image as an RGB array, or None if not available
        """
        media_info = MediaInfo.parse(video_file_path, cover_data=True)
        general_track = next(
            (t for t in media_info.tracks if t.track_type == "General"), None
        )
        if general_track is None:
            return None

        cover_data = getattr(general_track, "cover_data", None)
        if not cover_data:
            return None

        raw_bytes = base64.b64decode(cover_data)
        image_array = np.frombuffer(raw_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        if image is None:
            return None

        return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def _get_video_frame_screenshot(self, video_file_path: str) -> np.ndarray | None:
        """Uses OpenCV to capture a frame from the video as a fallback screenshot.

        Args:
            video_file_path (str): Path to the video file to extract the screenshot from

        Returns:
            numpy.ndarray | None: The captured frame as an RGB array, or None on failure
        """
        video = cv2.VideoCapture(video_file_path)
        if not video.isOpened():
            logger.error(f"Could not open: {video_file_path}")
            return None

        # Get position where to capture the screenshot
        len_seconds = int(video.get(cv2.CAP_PROP_FRAME_COUNT)) / video.get(
            cv2.CAP_PROP_FPS
        )
        pos_seconds = 30 if len_seconds >= 120 else len_seconds / 4

        # Position video at pos_seconds
        frame_id = video.get(cv2.CAP_PROP_FPS) * pos_seconds
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

        res, frame = video.read()
        if not res:
            logger.error(f"Could not get screenshot of: {video_file_path}")
            return None

        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def _get_video_file_screenshot(self, video_file_path: str) -> np.ndarray | None:
        """Gets a preview image for a video file.

        Tries embedded thumbnail first, falls back to capturing a video frame.

        Args:
            video_file_path (str): Path to the video file

        Returns:
            numpy.ndarray | None: The image as an RGB array, or None on failure
        """
        return (
            self._get_embedded_thumbnail(video_file_path)
            or self._get_video_frame_screenshot(video_file_path)
        )

    def update_metadata_db(self) -> None:
        db_metadata_list = queries.get_all_videos()
        db_full_paths = {db_metadata.full_path for db_metadata in db_metadata_list}
        folder_paths = set(self._file_names)

        # Remove metadata from the database that is not in the folder
        for stale_path in db_full_paths - folder_paths:
            queries.delete_video_by_path(stale_path)
            logger.info(f"Deleted stale entry from database: {stale_path}")

        for file_name in folder_paths - db_full_paths:
            # Get file name without extension
            file_name_no_ext = os.path.splitext(os.path.basename(file_name))[0]
            
            sub_path = os.path.join(
                self._folder_path,
                f"{file_name_no_ext}.srt",
            )

            # Get data
            extracted_metadata = self._get_video_file_metadata(file_name)
            
            duration_ms = float(extracted_metadata.get("duration", 0))
            length = timedelta(milliseconds=duration_ms)
            runtime_mins = int(length.total_seconds()) // 60
            tmdb_metadata = self._get_tmdb_movie_metadata(file_name_no_ext, runtime_mins)

            # Language value priority is as follows:
            #   1. language extracted from the local file metadata
            #   2. language extracted from tmdb
            if (
                "language" in extracted_metadata.keys()
                and extracted_metadata["language"] != ""
            ):
                try:
                    language = Language.get(extracted_metadata["language"]).display_name()
                except LanguageTagError as e:
                    logger.warning(f"Unrecognised language tag: {e}")
                    language = extracted_metadata["language"]
            elif tmdb_metadata["original_language"] != "":
                language = Language.get(
                    tmdb_metadata["original_language"]
                ).display_name()
            else:
                language = "N/A"

            # Download poster from TMDB
            poster_download_path = os.path.join(
                "resources",
                "movie_posters",
                f"{file_name_no_ext}.jpg",
            )
            download_tmdb_poster(
                tmdb_metadata["poster_path"],
                poster_download_path,
                self._tmdb_configuration,
            )

            # If poster download did not work save a screenshot from the video instead
            if not os.path.exists(poster_download_path):
                poster_image = self._get_video_file_screenshot(
                    os.path.join(self._folder_path, file_name)
                )
                if poster_image is not None:
                    cv2.imwrite(poster_download_path, poster_image)

            # Add metadata to the database
            metadata = models.VideoMetadata(
                language=language,
                length=length,
                image_path=poster_download_path,
                full_path=file_name,
                full_sub_path=sub_path,
                tmdb_title=tmdb_metadata["title"],
                tmdb_director=tmdb_metadata["director"],
                tmdb_year=tmdb_metadata["year"],
                tmdb_overview=tmdb_metadata["overview"],
                tmdb_genres=tmdb_metadata["genres"],
                tmdb_poster_path=tmdb_metadata["poster_path"],
            )
            queries.insert_video(metadata)
