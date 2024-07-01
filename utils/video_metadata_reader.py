import os
import yaml

import cv2


class FolderNotFoundException(Exception):
    """Exception raised for when a folder path is not found

    Args:
        folder_path (str): Folder path that caused the error
    """

    def __init__(self, folder_path):
        self.message = f"Path: {folder_path} is not found or is not a folder path, please check your settings."
        super().__init__(self.message)


class VideoMetadataListBuilder():
    def __init__(self, folder_path: str) -> None:
        self._folder_path = folder_path
        self._file_names = self._read_video_file_names()
        self._accepted_extensions = self._read_accepted_extensions()
        
        self._metadata_list = []
        for file_name in self._file_names:
            self._metadata_list.append(
                self._get_video_file_metadata(os.join(self._folder_path, file_name)),
                self._get_video_file_screenshot(os.join(self._folder_path, file_name)),
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
        
    def _get_video_file_metadata(self, video_file_path: str) -> dict:
        """Uses MediaInfo wrapper to get local video file metadata:

        Args:
            video_file_path (str): Path to the video file to extract metadata from

        Returns:
            dict: Local video file metada dictionary
        """
        pass
    
    def _get_video_file_screenshot(self, video_file_path: str) -> object:
        """Uses OpenCV to get local video file sneek peak screenshot for the UI:

        Args:
            video_file_path (str): Path to the video file to extract the screenshot from

        Returns:
            TBD
        """
        pass
    

    def get_metadata_list(self) -> list:
        return self._metadata_list
    
    def _read_accepted_extensions(self) -> list:
        with open(self.config_path) as conf_f:
            try:
                return yaml.safe_load(conf_f)
            except yaml.YAMLError as err:
                return err

"""
from pymediainfo import MediaInfo

# Open the video file
video_path = 'path_to_your_video_file.mp4'
media_info = MediaInfo.parse(video_path)

# Print general and video metadata
for track in media_info.tracks:
    if track.track_type == "General":
        print(f"Title: {track.title}")
        print(f"Year: {track.recorded_date}")
        print(f"Genre: {track.genre}")
        print(f"Duration (seconds): {track.duration / 1000}")  # Duration is in milliseconds
    elif track.track_type == "Video":
        print(f"Frame Width: {track.width}")
        print(f"Frame Height: {track.height}")
        print(f"Frame Rate: {track.frame_rate}")
        print(f"Codec: {track.codec_id}")

# Print all available metadata for all tracks
for track in media_info.tracks:
    print(track.to_data())
"""