from typing import List, Optional, Dict, Any
import yt_dlp
from youtube_search import YoutubeSearch
from ..models.media import MediaItem, MediaType


class YouTubeService:
    """Service for interacting with YouTube API using yt-dlp"""

    def __init__(self):
        self.ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
        }

    def search_videos(self, query: str, max_results: int = 20) -> List[MediaItem]:
        """Search YouTube videos"""
        try:
            # Use youtube-search for video search
            results = YoutubeSearch(query, max_results=max_results).to_dict()
            media_items = []

            for video in results:
                media_item = MediaItem(
                    id=video["id"],
                    title=video["title"],
                    url=f"https://www.youtube.com{video['url_suffix']}",
                    duration=video.get("duration", "Unknown"),
                    thumbnail=video.get("thumbnails", [{}])[0]
                    if video.get("thumbnails")
                    else None,
                    channel=video.get("channel", "Unknown"),
                )
                media_items.append(media_item)

            return media_items
        except Exception as e:
            print(f"Search error: {e}")
            return []

    def get_video_info(self, url: str) -> Optional[MediaItem]:
        """Get detailed video information"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                thumbnail = None
                if info.get("thumbnail"):
                    thumbnail = info["thumbnail"]

                return MediaItem(
                    id=info["id"],
                    title=info["title"],
                    url=info["webpage_url"],
                    duration=self._format_duration(info.get("duration", 0)),
                    thumbnail=thumbnail,
                    channel=info.get("uploader", "Unknown"),
                )
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None

    def get_download_info(
        self, url: str, media_type: MediaType
    ) -> Optional[Dict[str, Any]]:
        """Get download information for specific media type"""
        try:
            opts = self.ydl_opts.copy()

            if media_type == MediaType.AUDIO:
                opts.update(
                    {
                        "format": "bestaudio/best",
                        "postprocessors": [
                            {
                                "key": "FFmpegExtractAudio",
                                "preferredcodec": "mp3",
                                "preferredquality": "192",
                            }
                        ],
                    }
                )
            else:  # VIDEO or KARAOKE
                opts.update(
                    {
                        "format": "best[ext=mp4]/best[height<=720]"
                        if media_type == MediaType.KARAOKE
                        else "best[ext=mp4]/best",
                    }
                )

            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                return info

        except Exception as e:
            print(f"Error getting download info: {e}")
            return None

    def _format_duration(self, seconds: int) -> str:
        """Format duration in seconds to MM:SS format"""
        if seconds <= 0:
            return "Unknown"

        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"

    def get_download_streams(self, url: str, media_type: MediaType):
        """Get available download streams"""
        try:
            yt = YouTube(url)

            if media_type == MediaType.AUDIO:
                return yt.streams.filter(only_audio=True).order_by("abr").desc()
            elif media_type in [MediaType.KARAOKE, MediaType.VIDEO]:
                return (
                    yt.streams.filter(progressive=True, file_extension="mp4")
                    .order_by("resolution")
                    .desc()
                )

            return yt.streams.filter(progressive=True)
        except Exception as e:
            print(f"Error getting streams: {e}")
            return None
