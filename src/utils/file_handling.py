import json
import logging

from PIL import Image, ImageTk, UnidentifiedImageError
import yaml

logger = logging.getLogger(__name__)


def read_tk_image(image_path: str) -> ImageTk.PhotoImage | None:
    """Given a path reads an image that can be used in any place that an image object is expected in Tkinter

    Args:
        image_path (str): Path to the image file

    Returns:
        Optional[ImageTk.PhotoImage]: Tkinter image object
    """
    try:
        with Image.open(image_path) as img:
            pill_img = img.convert("RGBA")

        return ImageTk.PhotoImage(pill_img)
    except UnidentifiedImageError as exception:
        logger.error(f"Error while trying to open image ({image_path}) using PIL: {exception}")
    except Exception as exception:
        logger.error(f"An unexpected error occurred on image ({image_path}): {exception}")
    return None


def load_json_file(json_file_path: str) -> dict | list | None:
    """Given a path reads and loads a json file into a dictionary or a list

    Args:
        json_file_path (str): Path to the json file

    Returns:
        Optional[dict]: Dictionary or List structure of the json
    """
    try:
        with open(json_file_path, encoding="utf_8") as json_f:
            return json.load(json_f)
    except FileNotFoundError:
        logger.error(f"The file '{json_file_path}' was not found.")
    except PermissionError:
        logger.error(f"Permission denied to read the file '{json_file_path}'.")
    except json.JSONDecodeError as exception:
        logger.error(f"Failed to decode JSON from '{json_file_path}': {exception}")
    except Exception as exception:
        logger.error(f"An unexpected error occurred reading '{json_file_path}': {exception}")
    return None


def load_yaml_file(yaml_file_path: str) -> dict | list | None:
    """Given a path reads and loads a yaml file into a dictionary or a list

    Args:
        json_file_path (str): Path to the yaml file

    Returns:
        Optional[dict]: Dictionary or List structure of the yaml
    """
    try:
        with open(yaml_file_path, encoding="utf_8") as yaml_f:
            return yaml.safe_load(yaml_f)
    except FileNotFoundError:
        logger.error(f"The file '{yaml_file_path}' was not found.")
    except PermissionError:
        logger.error(f"Permission denied to read the file '{yaml_file_path}'.")
    except yaml.YAMLError as exception:
        logger.error(f"Failed to decode YAML from '{yaml_file_path}': {exception}")
    except Exception as exception:
        logger.error(f"An unexpected error occurred reading '{yaml_file_path}': {exception}")
    return None
