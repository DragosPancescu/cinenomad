from services.database import models


class MovieSelectionModel:
    """Holds the current movie selection and notifies observers on change."""

    def __init__(self, metadata_list: list[models.VideoMetadata]):
        self._metadata_list = metadata_list
        self._index = 0
        self._observers = []

    def add_observer(self, callback) -> None:
        self._observers.append(callback)

    def select(self, index: int) -> None:
        if 0 <= index < len(self._metadata_list):
            self._index = index
            for cb in self._observers:
                cb(self._index)

    def select_prev(self) -> None:
        self.select(self._index - 1)

    def select_next(self) -> None:
        self.select(self._index + 1)

    @property
    def current_index(self) -> int:
        return self._index

    @property
    def current_metadata(self) -> models.VideoMetadata:
        return self._metadata_list[self._index]

    @property
    def metadata_list(self) -> list[models.VideoMetadata]:
        return self._metadata_list

    @property
    def count(self) -> int:
        return len(self._metadata_list)
