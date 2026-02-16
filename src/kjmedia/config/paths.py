import os
import pickle
import json
from pathlib import Path
from typing import Dict, Optional


class PathManager:
    """Manages download paths for different media types"""

    def __init__(self):
        self.config_file = Path.home() / ".kjmedia" / "paths.json"
        self.pickle_file = Path.home() / ".kjmedia" / "settings.pkl"
        self.default_paths = {
            "karaoke": str(Path.home() / "Music" / "Karaoke"),
            "audio": str(Path.home() / "Music" / "Audio"),
            "video": str(Path.home() / "Music" / "Video"),
        }
        self.paths = self._load_paths()
        self._load_pickle()

    def _load_pickle(self) -> None:
        """Load paths from pickle file if it exists"""
        if self.pickle_file.exists():
            try:
                with open(self.pickle_file, "rb") as f:
                    data = pickle.load(f)
                    if isinstance(data, dict):
                        self.paths = data
            except (pickle.PickleError, IOError):
                pass

    def save_pickle(self) -> None:
        """Save current paths to pickle file"""
        self.pickle_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.pickle_file, "wb") as f:
            pickle.dump(self.paths, f)

    def _load_paths(self) -> Dict[str, str]:
        """Load paths from config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self.default_paths.copy()
        return self.default_paths.copy()

    def save_paths(self) -> None:
        """Save current paths to config file"""
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.paths, f, indent=2)

    def get_path(self, media_type: str) -> str:
        """Get download path for media type"""
        return self.paths.get(media_type, self.default_paths.get(media_type, ""))

    def set_path(self, media_type: str, path: str) -> None:
        """Set download path for media type"""
        self.paths[media_type] = path

    def ensure_directories(self) -> None:
        """Ensure all download directories exist"""
        for path in self.paths.values():
            Path(path).mkdir(parents=True, exist_ok=True)
