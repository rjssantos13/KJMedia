from pathlib import Path
from kivy.config import Config
from .paths import PathManager


class AppSettings:
    """Application settings and configuration"""

    def __init__(self):
        self.path_manager = PathManager()
        self.config = Config
        self._setup_kivy_config()

    def _setup_kivy_config(self) -> None:
        """Configure Kivy settings"""
        Config.set("graphics", "resizable", "1")
        Config.set("graphics", "width", "1200")
        Config.set("graphics", "height", "800")
        Config.set("kivy", "log_level", "info")

    @property
    def karaoke_path(self) -> str:
        """Get karaoke download path"""
        return self.path_manager.get_path("karaoke")

    @property
    def audio_path(self) -> str:
        """Get audio download path"""
        return self.path_manager.get_path("audio")

    @property
    def video_path(self) -> str:
        """Get video download path"""
        return self.path_manager.get_path("video")

    def get_download_format(self, media_type: str) -> dict:
        """Get format settings for different media types"""
        formats = {
            "karaoke": {"ext": "mp4", "resolution": "720p"},
            "audio": {"ext": "mp3", "quality": "192"},
            "video": {"ext": "mp4", "resolution": "1080p"},
        }
        return formats.get(media_type, {})
