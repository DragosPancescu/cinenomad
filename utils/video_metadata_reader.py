import os
import re
import yaml
import copy

from dataclasses import dataclass
from datetime import datetime

import cv2

from PIL import Image, ImageTk
from pymediainfo import MediaInfo
from langcodes import Language

from .exceptions import FolderNotFoundException
from .tmdb_utils import (
    search_movie_tmbd_api_call,
    get_tmdb_metadata,
    download_tmdb_poster,
    search_crew_tmdb_api_call
)


@dataclass
class MovieMetadata:
    """Class for keeping track of a video metadata."""

    language: str
    length: str  # format -> "%H:%M:%S.%f"
    director: str
    image: ImageTk
    file_name: str
    full_path: str
    sub_path: str
    tmdb_title: str
    tmdb_year: str
    tmdb_overview: str
    tmdb_genres: list[str]
    tmdb_poster_path: str

    def get_length_sec(self) -> int:
        time_obj = datetime.strptime(self.length, "%H:%M:%S.%f")
        return int(
            time_obj.hour * 3600
            + time_obj.minute * 60
            + time_obj.second
            + time_obj.microsecond / 1_000_000
        )
    
    def get_length_gui_format(self) -> str:
        time_obj = datetime.strptime(self.length, "%H:%M:%S.%f")
        return time_obj.strftime("%H:%M:%S")


class VideoMetadataListReader:
    def __init__(self, folder_path: str) -> None:
        self._folder_path = folder_path
        self._config_path = "./settings/accepted_extension.yaml"
        self._accepted_extensions = self._read_accepted_extensions()
        self._file_names = self._read_video_file_names()

        self._metadata_list = []
        for file_name in self._file_names:
            full_path = os.path.join(self._folder_path, file_name)
            sub_path = os.path.join(
                self._folder_path,
                f"{os.path.splitext(os.path.basename(file_name))[0]}.srt",
            )

            # Get data
            extracted_metadata = self._get_video_file_metadata(full_path)
            tmdb_metadata = self._get_tmdb_movie_metadata(file_name)

            # Download poster from TMDB
            poster_download_path = os.path.join(
                "resources/movie_posters",
                os.path.splitext(os.path.basename(full_path))[0] + ".jpg",
            )

            download_tmdb_poster(
                tmdb_metadata["tmdb_poster_path"], poster_download_path
            )
            
            # If poster download successful use that, else take a screenshot
            if os.path.exists(poster_download_path):
                image = Image.open(poster_download_path).resize((200, 300), Image.Resampling.LANCZOS)
                poster_image = ImageTk.PhotoImage(image)
            else:
                poster_image = self._get_video_file_screenshot(
                    os.path.join(self._folder_path, file_name)
                )

            # Add metadata to list
            self._metadata_list.append(
                MovieMetadata(
                    language=(
                        Language.get(extracted_metadata["language"]).display_name()
                        if "language" in extracted_metadata.keys() and extracted_metadata["language"] != ""
                        else Language.get(tmdb_metadata["tmdb_original_language"]).display_name()
                    ),
                    length=extracted_metadata["other_duration"][3],
                    director=tmdb_metadata["director"],
                    image=poster_image,
                    file_name=file_name,
                    full_path=full_path,
                    sub_path=sub_path,
                    tmdb_title=tmdb_metadata["tmdb_title"],
                    tmdb_year=tmdb_metadata["tmdb_year"],
                    tmdb_overview=tmdb_metadata["tmdb_overview"],
                    tmdb_genres=tmdb_metadata["tmdb_genres"],
                    tmdb_poster_path=tmdb_metadata["tmdb_poster_path"],
                )
            )

        self._metadata_list = sorted(self._metadata_list, key=lambda md: md.tmdb_title)

    def _read_video_file_names(self) -> list:
        if not os.path.isdir(self._folder_path):
            raise FolderNotFoundException(self._folder_path)

        file_names = []
        for file in os.listdir(self._folder_path):
            if os.path.isfile(os.path.join(self._folder_path, file)):
                file_names.append(file)

        # Filter using the accepted extensions list
        file_names = [
            file_name
            for file_name in file_names
            if file_name.split(".")[-1].lower() in self._accepted_extensions
        ]
        return file_names

    def _get_tmdb_movie_metadata(self, file_name: str) -> dict:

        # Extract movie name from file_name
        movie_name = re.sub("[^a-zA-Z]", " ", file_name)
        movie_name = " ".join(
            [word.title() for word in movie_name.split() if word != ""][0:3]
        )

        if len(movie_name.split()[-1]) <= 2:
            movie_name = " ".join(movie_name.split()[0:-1])

        is_tvshow = bool(re.search("[sS][0-9]{1,2}[eE][0-9]{1,2}", file_name))

        # API CALL
        movie_data = search_movie_tmbd_api_call(movie_name, is_tvshow)

        # Return dict with needed data
        metadata = get_tmdb_metadata(movie_data, is_tvshow)

        # API CALL for Director name
        director = ""
        if metadata["tmdb_id"] != "":
            director = search_crew_tmdb_api_call(metadata["tmdb_id"], is_tvshow)
        
        metadata["director"] = director
        return metadata

    # TODO: Get needed metadata
    def _get_video_file_metadata(self, video_file_path: str) -> dict:
        """Uses MediaInfo wrapper to get local video file metadata:

        Args:
            video_file_path (str): Path to the video file to extract metadata from

        Returns:
            dict: Local video file metada dictionary
        """
        media_info = MediaInfo.parse(video_file_path)

        general_track = list(filter(lambda track: track.track_type == "General", media_info.tracks))[0]
        audio_track = list(filter(lambda track: track.track_type == "Audio", media_info.tracks))[0]

        language = ""
        if "language" in audio_track.to_data().keys():
            language = audio_track.to_data()["language"]

        metadata = copy.deepcopy(general_track.to_data())
        metadata["language"] = language

        return metadata


    # TODO: Find a way to get nice screenshots
    # TODO: Get metadata frame for screenshot
    def _get_video_file_screenshot(self, video_file_path: str) -> ImageTk:
        """Uses OpenCV to get local video file sneek peak screenshot for the UI:

        Args:
            video_file_path (str): Path to the video file to extract the screenshot from

        Returns:
            ImageTk: Ready to be used in a widget
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
        frame_pil = Image.fromarray(frame).resize((200, 300), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image=frame_pil)

    def get_metadata_list(self) -> list[MovieMetadata]:
        return self._metadata_list

    def _read_accepted_extensions(self) -> list:
        with open(self._config_path) as conf_f:
            try:
                return yaml.safe_load(conf_f)
            except yaml.YAMLError as err:
                return err
