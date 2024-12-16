import json
import requests

MOVIE_GENRE_MAP = {
    28: "Action",
    12: "Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    14: "Fantasy",
    36: "History",
    27: "Horror",
    10402: "Music",
    9648: "Mystery",
    10749: "Romance",
    878: "Science Fiction",
    10770: "TV Movie",
    53: "Thriller",
    10752: "War",
    37: "Western",
}

TV_GENRE_MAP = {
    10759: "Action & Adventure",
    16: "Animation",
    35: "Comedy",
    80: "Crime",
    99: "Documentary",
    18: "Drama",
    10751: "Family",
    10762: "Kids",
    9648: "Mystery",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    37: "Western",
}

BEARER_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJmNzYzYzAxZGFhNTliZWZhNzFmOTQ2NDI4NjM1MGE2NCIsIm5iZiI6MTcxMTI3MDQwMy4zODgsInN1YiI6IjY1ZmZlYTAzNDU5YWQ2MDE4N2Y5MzQ4ZSIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.Bil-l7scOUnepuyK3x8Hvg1R6QcVHRrF5izjD2SSn6Y"
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {BEARER_TOKEN}",
}


def search_crew_tmdb_api_call(tmdb_id: str, is_tvshow: bool) -> str:
    movie_crew_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/credits?language=en-US"
    tv_crew_url = f"https://api.themoviedb.org/3/tv/{tmdb_id}/credits?language=en-US"

    request_url = tv_crew_url if is_tvshow else movie_crew_url
    response = requests.get(request_url, headers=HEADERS)

    if response.status_code != 200:
        print(
            f"Failed to get data for id: {tmdb_id}. HTTP status code: {response.status_code}"
        )
        print(response.text)
        return None

    response_dict = json.loads(response.text)
    directors_iterator = filter(
        lambda pers: pers["job"] == "Director", response_dict["crew"]
    )

    director_data = next(directors_iterator, None)
    if not director_data:
        return ""

    return director_data["name"]

def search_movie_tmbd_api_call(movie_name: str, is_tvshow: bool) -> dict:
    search_type = "tv" if is_tvshow else "movie"
    details_url = f"https://api.themoviedb.org/3/search/{search_type}?query={movie_name}&include_adult=false&language=en-US&page=1"

    response = requests.get(details_url, headers=HEADERS)

    if response.status_code != 200:
        print(
            f"Failed to get data for {movie_name}. HTTP status code: {response.status_code}"
        )
        print(response.text)
        return None

    response_dict = json.loads(response.text)

    # TODO: Right now we pick the first as a default, maybe we can filter by year in the future
    if len(response_dict["results"]) == 0:
        print(f"Query returned no data for: {movie_name}")
        return None

    return response_dict["results"][0]


def get_tmdb_metadata(movie_data: dict, is_tvshow: bool) -> dict:
    if movie_data == None:
        return {
            "tmdb_title": "",
            "tmdb_year": "",
            "tmdb_overview": "",
            "tmdb_genres": "",
            "tmdb_poster_path": "",
            "tmdb_id": "",
        }

    title = movie_data["original_name"] if is_tvshow else movie_data["original_title"]
    genre_map = lambda gid: TV_GENRE_MAP[gid] if is_tvshow else MOVIE_GENRE_MAP[gid]
    release_date = (
        movie_data["first_air_date"] if is_tvshow else movie_data["release_date"]
    )

    tmdb_metadata = {
        "tmdb_title": title,
        "tmdb_year": release_date[0:4],
        "tmdb_overview": movie_data["overview"],
        "tmdb_genres": [genre_map(genre_id) for genre_id in movie_data["genre_ids"]],
        "tmdb_poster_path": movie_data["poster_path"],
        "tmdb_id": movie_data["id"],
    }

    return tmdb_metadata


def download_tmdb_poster(poster_path: str, download_location: str) -> None:
    print(poster_path)
    # Get TMDB configuration
    config_url = f"https://api.themoviedb.org/3/configuration"
    response = requests.get(config_url, headers=HEADERS)

    if response.status_code != 200:
        print("Failed to fetch configuration.")
        print(response.text)
        return

    poster_sizes = response.json()["images"]["poster_sizes"]
    size = poster_sizes[-2]  # Choose the largest available size

    # Build the image URL
    base_url = "https://image.tmdb.org/t/p/"
    poster_url = f"{base_url}{size}{poster_path}"

    # Download the image
    response = requests.get(poster_url)

    if response.status_code != 200:
        print(f"Failed to download poster. HTTP status code: {response.status_code}")
        print(response.text)
        return

    with open(download_location, "wb") as file:
        file.write(response.content)
        print(f"Poster saved to: {download_location}")
