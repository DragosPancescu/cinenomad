import os
import re
import copy

from datetime import datetime

import cv2
import numpy as np

from pymediainfo import MediaInfo
from langcodes import Language

from utils.file_handling import load_yaml_file
from utils.database import queries, models
from .exceptions import FolderNotFoundException
from .tmdb_utils import (
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
        self._accepted_extensions = load_yaml_file(os.path.join(".", "settings", "accepted_extension.yaml"))
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
            for file in os.listdir(self._folder_path):
                if os.path.isfile(os.path.join(self._folder_path, file)):
                    file_names.append(os.path.join(self._folder_path, file))

            # Filter using the accepted extensions list
            file_names = [
                file_name
                for file_name in file_names
                if file_name.split(".")[-1].lower() in self._accepted_extensions
            ]
        except FolderNotFoundException as exception:
            print(f"Folder path: {self._folder_path} not found: {exception}")
        except Exception as exception:
            print(
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
        movie_name = re.sub("[^a-zA-Z]", " ", file_name)
        movie_name = " ".join(
            [word.title() for word in movie_name.split() if word != ""][0:3]
        )

        if len(movie_name.split()[-1]) <= 2:
            movie_name = " ".join(movie_name.split()[0:-1])

        season_episode = re.search("[sS][0-9]{1,2}[eE][0-9]{1,2}", file_name)
        is_tvshow = bool(season_episode)

        # API Call to  get info about movie / show
        movie_search_results = search_movie_tmbd_api_call(movie_name, is_tvshow)
        
        # Filter based on runtime
        movie_data = None
        runtime_key = "episode_run_time" if is_tvshow else "runtime"

        if movie_search_results is not None and len(movie_search_results) > 0:
            for search_result in movie_search_results:
                details = get_movie_details_api_call(search_result["id"], is_tvshow)

                try:
                    tmdb_runtime = details[runtime_key][0] if is_tvshow else details[runtime_key]
                except Exception as e:
                    print(f"{e}, id: {search_result['id']}")
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
        audio_track = list(
            filter(lambda track: track.track_type == "Audio", media_info.tracks)
        )[0]

        language = ""
        if "language" in audio_track.to_data().keys():
            language = audio_track.to_data()["language"]

        metadata = copy.deepcopy(general_track.to_data())
        metadata["language"] = language

        return metadata

    # TODO: Find a way to get nice screenshots (Get metadata frame for screenshot)
    def _get_video_file_screenshot(self, video_file_path: str) -> np.ndarray | None:
        """Uses OpenCV to get local video file sneek peak screenshot for the UI:

        Args:
            video_file_path (str): Path to the video file to extract the screenshot from

        Returns:
            numpy.ndarray: Ready to be used in a widget
        """
        video = cv2.VideoCapture(video_file_path)
        if not video.isOpened():
            print(f"Could not open: {video_file_path}")
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
            print(f"Could not get screenshot of: {video_file_path}")
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return frame

    # TODO: Calculate set() difference and iterate through that to get the lists
    def update_metadata_db(self) -> None:
        db_metadata_list = queries.get_all_videos()
        db_full_paths = [db_metadata.full_path for db_metadata in db_metadata_list]

        # Remove metadata from the database that is not in the folder
        for db_full_path in db_full_paths:
            if not db_full_path in self._file_names:
                queries.delete_video_by_path(db_full_path)
                print(f"Deleted: {db_full_path} from database")

        for file_name in self._file_names:
            # If video metadata already exists
            if file_name in db_full_paths:
                continue
            
            # Get file name without extension
            file_name_no_ext = os.path.splitext(os.path.basename(file_name))[0]
            
            sub_path = os.path.join(
                self._folder_path,
                f"{file_name_no_ext}.srt",
            )

            # Get data
            extracted_metadata = self._get_video_file_metadata(file_name)
            
            time_obj = datetime.strptime(extracted_metadata["other_duration"][3], "%H:%M:%S.%f")
            runtime_mins = int(
                time_obj.hour * 60
                + time_obj.minute
                + time_obj.second / 3600
                + time_obj.microsecond / 1_000_000
            )
            tmdb_metadata = self._get_tmdb_movie_metadata(file_name_no_ext, runtime_mins)

            # Language value priority is as follows:
            #   1. language extracted from the local file metadata
            #   2. language extracted from tmdb
            if (
                "language" in extracted_metadata.keys()
                and extracted_metadata["language"] != ""
            ):
                language = Language.get(extracted_metadata["language"]).display_name()
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
                length=extracted_metadata["other_duration"][3],
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
