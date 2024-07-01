import os

FOLDER_PATH = "/home/dragos/Videos"


def read_video_files() -> None:
    if not os.path.isdir(FOLDER_PATH):
        print(f"{FOLDER_PATH} does not exist or is not a folder.")
        return None

    for filename in os.listdir(FOLDER_PATH):
        f = os.path.join(FOLDER_PATH, filename)
        # checking if it is a file
        if os.path.isfile(f):
            print(f)

read_video_files()