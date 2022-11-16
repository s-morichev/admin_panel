import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class JsonFileStorage:
    """File storage that saves and loads data in json format."""

    def __init__(self, file_path: Path):
        """Initialize storage at file path.

        If file doesn't exist then creates it and save empty state.
        """
        self._file_path = file_path
        if not self._file_path.is_file():
            self._file_path.parent.mkdir(parents=True, exist_ok=True)
            self._file_path.touch()
            self.save_state({})

    def save_state(self, state: dict) -> None:
        """Save state in json."""
        with self._file_path.open("w") as file:
            try:
                json.dump(state, file)
            except TypeError:
                logger.exception("Some state values isn't JSON serializable")
                raise

    def retrieve_state(self) -> dict:
        """Load state from json."""
        with self._file_path.open("r") as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                logger.exception("Invalid saved state in file %s", self._file_path)
                raise


class State:
    """Persistent state for storing serializable values.

    Uses json internally.
    """

    def __init__(self, storage: JsonFileStorage):
        """Load state from storage on initialization."""
        self._storage = storage
        self._state = self._load_state()

    def set_value(self, key: str, value: Any) -> None:
        """Set value for key."""
        self._state[key] = value
        self._storage.save_state(self._state)

    def get_value(self, key: str) -> Any:
        """Get value by key."""
        return self._state.get(key)

    def _load_state(self) -> dict:
        """Load state from storage."""
        return self._storage.retrieve_state()
