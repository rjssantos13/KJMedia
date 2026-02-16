from dataclasses import dataclass
from typing import Optional
from enum import Enum


class MediaType(Enum):
    """Media download types"""

    KARAOKE = "karaoke"
    AUDIO = "audio"
    VIDEO = "video"


class DownloadStatus(Enum):
    """Download status tracking"""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MediaItem:
    """Represents a media item from YouTube"""

    id: str
    title: str
    url: str
    duration: str
    thumbnail: Optional[str] = None
    channel: Optional[str] = None
    media_type: MediaType = MediaType.VIDEO

    def __post_init__(self):
        if isinstance(self.media_type, str):
            self.media_type = MediaType(self.media_type)


@dataclass
class DownloadTask:
    """Represents a download task"""

    media_item: MediaItem
    status: DownloadStatus = DownloadStatus.PENDING
    progress: float = 0.0
    error_message: Optional[str] = None
    local_path: Optional[str] = None
    media_type: str = "video"
    thumbnail: Optional[str] = None
    def __post_init__(self):
        if isinstance(self.status, str):
            self.status = DownloadStatus(self.status)
