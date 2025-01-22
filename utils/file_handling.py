from typing import Optional

from exceptions import custom_exceptions

from PIL import Image, ImageTk, UnidentifiedImageError

def read_tk_image(image_path: str) -> Optional[ImageTk.PhotoImage]:
    try:
        with Image.open(image_path) as img:
            pill_img = img.load()
        pill_img = pill_img.convert("RGBA")
        
        return ImageTk.PhotoImage(pill_img)
    except UnidentifiedImageError as exception:
        # TODO: Logger
        print(exception)