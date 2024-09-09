import os
import yaml
from dataclasses import dataclass
from enum import Enum

import cv2

from PIL import Image, ImageTk
from pymediainfo import MediaInfo

from .exceptions import FolderNotFoundException

    
@dataclass
class MovieMetadata:
    """Class for keeping track of a video metadata."""
    title: str
    year: str
    language: str
    length: str
    director: str
    genres: list[str]
    image: ImageTk
    

class VideoMetadataListReader():
    def __init__(self, folder_path: str) -> None:
        self._folder_path = folder_path
        self._config_path = "./settings/accepted_extension.yaml"
        self._accepted_extensions = self._read_accepted_extensions()
        self._file_names = self._read_video_file_names()
        
        self._metadata_list = []
        for file_name in self._file_names:
            extracted_metadata = self._get_video_file_metadata(os.path.join(self._folder_path, file_name))

            self._metadata_list.append(
                MovieMetadata(
                    title="",
                    year="",
                    language=extracted_metadata["audio_language_list"],
                    length=extracted_metadata["other_duration"][0],
                    director="",
                    genres=[""],
                    image=self._get_video_file_screenshot(os.path.join(self._folder_path, file_name))
                )
            )

    def _read_video_file_names(self) -> list:
        if not os.path.isdir(self._folder_path):
            raise FolderNotFoundException(self._folder_path)
        
        file_names = []
        for file in os.listdir(self._folder_path):
            if os.path.isfile(os.path.join(self._folder_path, file)):
                file_names.append(file)

        # Filter using the accepted extensions list
        file_names = [
            file_name for file_name in file_names if file_name.split(".")[-1] in self._accepted_extensions
        ]
        return file_names

    def _get_movie_metadata(self, movie_name: str) -> object:
        pass
    
    # TODO: Get needed metadata
    def _get_video_file_metadata(self, video_file_path: str) -> dict:
        """Uses MediaInfo wrapper to get local video file metadata:

        Args:
            video_file_path (str): Path to the video file to extract metadata from

        Returns:
            dict: Local video file metada dictionary
        """
        media_info = MediaInfo.parse(video_file_path)

        for track in media_info.tracks:
            if track.track_type == "General":
                return track.to_data()
    
    # TODO: Find a way to get nice screenshots
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

        frame_id = video.get(cv2.CAP_PROP_FPS) * 30 # Frame at 30th second
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_id)

        res, frame = video.read()
        if not res:
            print(f"Could not get screenshot of: {video_file_path}")
            return None

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_pil = Image.fromarray(frame).resize((200, 200), Image.Resampling.LANCZOS)
        return ImageTk.PhotoImage(image=frame_pil)
        
    

    def get_metadata_list(self) -> list[MovieMetadata]:
        return self._metadata_list
    
    def _read_accepted_extensions(self) -> list:
        with open(self._config_path) as conf_f:
            try:
                return yaml.safe_load(conf_f)
            except yaml.YAMLError as err:
                return err
