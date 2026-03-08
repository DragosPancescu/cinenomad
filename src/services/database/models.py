import re
import os

from dataclasses import dataclass
from datetime import timedelta

from PIL import Image, ImageTk


@dataclass(frozen=True)
class VideoMetadata:
    """Model class for keeping track of a video metadata."""

    language: str
    length: timedelta
    image_path: str
    full_path: str
    full_sub_path: str
    tmdb_title: str
    tmdb_director: str
    tmdb_year: str
    tmdb_overview: str
    tmdb_genres: list[str]
    tmdb_poster_path: str

    def get_gui_title(self) -> str:
        """Returns the title string that appears in the GUI

        Returns:
            str: Title of the video
        """
        season_episode = re.search("[sS][0-9]{1,2}[eE][0-9]{1,2}", self.full_path)
        is_tvshow = bool(season_episode)

        if is_tvshow:
            return f"{self.tmdb_title} - {season_episode.group()}"
        return self.tmdb_title

    def get_image_object(self, width: int, height: int) -> ImageTk.PhotoImage | None:
        """Retrieves the resized poster image ready to use in the GUI

        Args:
            width (int): Resize width
            height (int): Resize height

        Returns:
            Optional[ImageTk.PhotoImage]: ImageTk image object easy to embbed in the GUI
        """
        if os.path.exists(self.image_path):
            image = Image.open(self.image_path).resize((width, height), Image.LANCZOS)
            return ImageTk.PhotoImage(image)
        return None


@dataclass(frozen=True)
class LogEntry:
    """Model class for a log entry stored in the database."""

    timestamp: str
    level: str
    logger_name: str
    message: str
    module: str
    func_name: str
    line_no: int
    traceback: str | None


@dataclass()
class Connector:
    """Model class for keeping connector data"""

    name: str
    icon_path: str


@dataclass()
class Setting:
    """Model class for the application settings that can be accessed by the user"""

    name: str
    value: str
