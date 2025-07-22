import json
import requests

from typing import Any

from utils.file_handling import load_yaml_file


# Build script global values
tmdb_settings = load_yaml_file("settings/tmdb_settings.yaml")

MOVIE_GENRE_MAP = tmdb_settings["MovieGenreMap"]
TV_GENRE_MAP = tmdb_settings["TvGenreMap"]
HEADERS = tmdb_settings["ApiHeaders"]
HEADERS["Authorization"] = str(HEADERS["Authorization"]).replace(
    "$token$", load_yaml_file("./settings/api_keys.yaml")["TmdbApiKey"]
)


def search_crew_tmdb_api_call(tmdb_id: str, is_tvshow: bool) -> str | None:
    """Sends an API call to the movie or tv show endpoint to retrieve the director (or in the case of a tv show, the producer) name

    Args:
        tmdb_id (str): TMDB entity id
        is_tvshow (bool): Indicates whether the media is a TV Show (True) or a Movie (False)

    Returns:
        Optional[str]: Name of the director or produces
    """
    try:
        search_type = "tv" if is_tvshow else "movie"
        request_url = f"https://api.themoviedb.org/3/{search_type}/{tmdb_id}/credits?language=en-US"

        response = requests.get(request_url, headers=HEADERS, timeout=5)
        if response.status_code != 200:
            print(
                f"Failed to get data for id: {tmdb_id}. HTTP status code: {response.status_code}"
            )
            print(response.text)
            return None

        response_dict = json.loads(response.text)
        directors_iterator = filter(
            lambda pers: (
                pers["job"] == "Producer" if is_tvshow else pers["job"] == "Director"
            ),
            response_dict["crew"],
        )

        director_data = next(directors_iterator, None)
        if not director_data:
            print(f"Failed to find director for id: {tmdb_id}")
            return None

        return director_data["name"]
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to search crew member on TMDB. Exception: {exception}"
        )
    return None


def search_movie_tmbd_api_call(movie_name: str, is_tvshow: bool) -> list[dict[str, Any]] | None:
    """Sends an API call to the search endpoint to retrieve data about the movie or tv show
    
    Args:
        movie_name (str): Name of the movie
        is_tvshow (bool): Indicates whether the media is a TV Show (True) or a Movie (False)

    Returns:
        Optional[list[dict]]: List of dictionary structures that contains the retrieved information
    """
    try:
        search_type = "tv" if is_tvshow else "movie"
        search_url = f"https://api.themoviedb.org/3/search/{search_type}?query={movie_name}&include_adult=false&language=en-US&page=1"

        response = requests.get(search_url, headers=HEADERS, timeout=5)

        if response.status_code != 200:
            print(
                f"Failed to get data for {movie_name}. HTTP status code: {response.status_code}"
            )
            print(response.text)
            return None

        response_dict = json.loads(response.text)

        if len(response_dict["results"]) == 0:
            print(f"Query returned no data for: {movie_name}")
            return None
        return response_dict["results"]
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to search movie on TMDB. Exception: {exception}"
        )
    return None

def get_movie_details_api_call(id: str, is_tvshow: bool) -> dict[str, Any]:
    try:
        search_type = "tv" if is_tvshow else "movie"
        details_url = f"https://api.themoviedb.org/3/{search_type}/{id}"

        response = requests.get(details_url, headers=HEADERS, timeout=5)

        if response.status_code != 200:
            print(
                f"Failed to get details for id: {id}. HTTP status code: {response.status_code}"
            )
            print(response.text)
            return None

        response_dict = json.loads(response.text)
        return response_dict
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to search details for id: {id}. Exception: {exception}"
        )
    return None
    

def get_tmdb_metadata(movie_data: dict, is_tvshow: bool) -> dict:
    empty_output = {
        "title": "",
        "year": "",
        "overview": "",
        "genres": "",
        "poster_path": "",
        "id": "",
        "original_language": "",
    }

    try:
        if movie_data is None:
            return empty_output

        title = (
            movie_data["original_name"] if is_tvshow else movie_data["original_title"]
        )
        release_date = (
            movie_data["first_air_date"] if is_tvshow else movie_data["release_date"]
        )
        genre_map = TV_GENRE_MAP if is_tvshow else MOVIE_GENRE_MAP

        tmdb_metadata = {
            "title": title,
            "year": release_date[0:4],
            "overview": movie_data["overview"],
            "genres": [genre_map[genre_id] for genre_id in movie_data["genre_ids"]],
            "poster_path": movie_data["poster_path"],
            "id": movie_data["id"],
            "original_language": movie_data["original_language"],
        }
        return tmdb_metadata
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to retrieve needed metadata from TMDB data. Exception: {exception}"
        )
    return empty_output


def get_tmdb_configuration() -> dict | list | None:
    """Sends an API call to retrieve tmdb configuration

    Returns:
        Optional[requests.Response]: TMDB configuration call response object
    """
    try:
        config_url = "https://api.themoviedb.org/3/configuration"
        response = requests.get(config_url, headers=HEADERS, timeout=5)

        if response.status_code != 200:
            print(
                f"Failed to fetch configuration. HTTP status code: {response.status_code}"
            )
            print(response.text)
            return None

        return response.json()
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to retrieve tmdb configuration. Exception: {exception}"
        )
    return None


def download_tmdb_poster(poster_path: str, download_location: str, tmdb_configuration: dict | list) -> None:
    """Downloads a poster image from TMDB given the poster path

    Args:
        poster_path (str): Poster path on TMDB
        download_location (str): Where to download said poster image
    """
    try:
        if tmdb_configuration is None:
            return

        # Get correct poster size
        poster_sizes = tmdb_configuration["images"]["poster_sizes"]
        size = poster_sizes[-2]  # Choose the second largest available size

        # Build the image URL
        base_url = "https://image.tmdb.org/t/p/"
        poster_url = f"{base_url}{size}{poster_path}"

        # Download the image
        response = requests.get(poster_url, timeout=5)

        if response.status_code != 200:
            print(
                f"Failed to download poster. HTTP status code: {response.status_code}"
            )
            print(response.text)
            return

        with open(download_location, "wb") as file:
            file.write(response.content)
            print(f"Poster saved to: {download_location}")
    except Exception as exception:
        print(
            f"Encountered unexpected exception while trying to save poster. Exception: {exception}"
        )
