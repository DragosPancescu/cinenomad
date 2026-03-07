class FolderNotFoundException(Exception):
    """Exception raised for when a folder path is not found

    Args:
        folder_path (str): Folder path that caused the error
    """

    def __init__(self, folder_path: str):
        self.message = f"Path: {folder_path} is not found or is not a folder path, please check your settings."
        super().__init__(self.message)
