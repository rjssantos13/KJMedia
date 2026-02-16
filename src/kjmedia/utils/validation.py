import re


def is_valid_youtube_url(url: str) -> bool:
    """Validate YouTube URL"""
    youtube_regex = re.compile(
        r"(https?://)?(www\.)?(youtube\.com/(watch\?v=|embed/|shorts/)|youtu\.be/|music\.youtube\.com/watch\?v=)[\w-]{11,}"
    )
    return bool(youtube_regex.match(url))


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for filesystem"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    return filename


def is_valid_directory_path(path: str) -> bool:
    """Check if directory path is valid"""
    return not any(char in path for char in '<>:"|?*')


def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL"""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/|youtube\.com/shorts/|music\.youtube\.com/watch\?v=)([\w-]{11,})",
        r"youtube\.com/watch\?v=([\w-]{11,})",
        r"youtu\.be/([\w-]{11,})",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return ""
