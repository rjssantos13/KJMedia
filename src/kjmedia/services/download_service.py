import os
import subprocess
import re
from pathlib import Path
from ..models.media import MediaItem, MediaType


class DownloadService:
    """Service for downloading media from YouTube using yt-dlp"""

    def __init__(self):
        self._progress_callback = None
        self.retry = 0

    def download_media(
        self,
        media_item: MediaItem,
        media_type: str,
        download_path: str,
        progress_callback=None,
    ) -> str:
        """Download media from YouTube"""
        self._progress_callback = progress_callback

        try:
            # Ensure download directory exists
            Path(download_path).mkdir(parents=True, exist_ok=True)

            # Setup download options
            filename = self._sanitize_filename(f"{media_item.title}")
            filepath = os.path.join(download_path, filename)

            # Download via yt-dlp CLI
            if media_type == MediaType.AUDIO.value:
                cmd = [
                    "yt-dlp",
                    media_item.url,
                    "-f",
                    "bestaudio/best",
                    "--extract-audio",
                    "--audio-format",
                    "mp3",
                    "--audio-quality",
                    "192",
                    "-o",
                    os.path.join(download_path, f"{filename}.%(ext)s"),
                ]
            elif media_type == MediaType.KARAOKE.value:
                cmd = [
                    "yt-dlp",
                    media_item.url,
                    "-f",
                    "bestvideo[height<=720]+bestaudio/best",
                    "--merge-output-format",
                    "mp4",
                    "-o",
                    os.path.join(download_path, f"{filename}.%(ext)s"),
                ]
            else:
                cmd = [
                    "yt-dlp",
                    media_item.url,
                    "-f",
                    "bestvideo[height<=1080]+bestaudio/best",
                    "--merge-output-format",
                    "mp4",
                    "-o",
                    os.path.join(download_path, f"{filename}.%(ext)s"),
                ]

            proc = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
            )
            out_lines = []
            progress = 0.0
            # Simple progress parse: look for percentage lines
            for line in iter(proc.stdout.readline, ""):
                out_lines.append(line)
                m = re.search(r"(\d{1,3}(?:\.\d+)?)%", line)
                if m:
                    try:
                        progress = float(m.group(1)) / 100.0
                        if self._progress_callback:
                            self._progress_callback(progress)
                    except:
                        pass

            proc.stdout.close()
            proc.wait()
            if proc.returncode != 0:
                raise Exception("CLI download failed: " + "".join(out_lines))

            # Infer final file path based on ext
            ext = "mp3" if media_type == MediaType.AUDIO.value else "mp4"
            final_filepath = os.path.join(download_path, f"{filename}.{ext}")
            # Cleanup: remove potential leftover source video after audio extraction
            # Only remove webm leftovers for now (default container is webm)
            if media_type == MediaType.AUDIO.value and ext == "mp3":
                base_no_ext = os.path.join(download_path, filename)
                candidate = f"{base_no_ext}.webm"
                if candidate != final_filepath and os.path.exists(candidate):
                    try:
                        os.remove(candidate)
                    except Exception:
                        pass

            print("RS Download complete!!!")
            return final_filepath

        except Exception as e:
            if media_type == MediaType.AUDIO.value:
                final_filepath = os.path.join(download_path, f"{filename}.mp3")
            else:
                final_filepath = os.path.join(download_path, f"{filename}.mp4")
            if not os.path.exists(final_filepath):
                raise Exception(f"RS Download failed: {str(e)}")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for filesystem"""
        # Remove or replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, "_")
        return filename
