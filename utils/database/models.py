from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class MovieMetadata:
    """Class for keeping track of a video metadata."""

    language: str
    length: str  # format -> "%H:%M:%S.%f"
    image_path: str
    full_path: str
    full_sub_path: str
    tmdb_title: str
    tmdb_director: str
    tmdb_year: str
    tmdb_overview: str
    tmdb_genres: list[str]
    tmdb_poster_path: str

    def get_length_sec(self) -> int:
        """Methods that returns the movie movie length in seconds

        Returns:
            int: Number of seconds in the movie
        """
        time_obj = datetime.strptime(self.length, "%H:%M:%S.%f")
        return int(
            time_obj.hour * 3600
            + time_obj.minute * 60
            + time_obj.second
            + time_obj.microsecond / 1_000_000
        )

    def get_length_gui_format(self) -> str:
        """Returns the datetime format that appears in the GUI

        Returns:
            str: Datetime in the following format: %H:%M:%S
        """
        time_obj = datetime.strptime(self.length, "%H:%M:%S.%f")
        return time_obj.strftime("%H:%M:%S")
