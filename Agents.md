# KJMedia YouTube Downloader - Agent Development Guide

## Project Overview
KJMedia is a Kivy-based YouTube downloader application with three download modes:
- **Karaoke**: MP4 video with instrumental audio (when available)
- **Audio**: MP3 audio extraction
- **Video**: MP4 video download

## Build/Lint/Test Commands

```bash
# Install dependencies
uv sync

# Run the application
uv run python main.py

# Development mode with hot reload (if implemented)
uv run python main.py --dev

# Run tests (when implemented)
uv run pytest

# Code formatting
uv run black .

# Import sorting
uv run isort .

# Type checking
uv run mypy .

# Linting
uv run ruff check .
uv run ruff check --fix .
```

## Code Style Guidelines

### Python Conventions
- **Python Version**: 3.12+
- **Style**: PEP 8 with Black formatting
- **Line Length**: 88 characters
- **Import Order**: Standard library → third-party → local imports
- **Type Hints**: Required for all functions and class attributes

### Import Organization
```python
# Standard library
from typing import Dict, List, Optional, Tuple
import os
import sys

# Third-party
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.properties import ObjectProperty, StringProperty
from pytube import YouTube
from youtube_search import YoutubeSearch

# Local imports
from .config import ConfigManager
from .downloader import DownloadManager
```

### Naming Conventions
- **Classes**: PascalCase (`DownloadQueue`, `SearchResults`)
- **Functions/Variables**: snake_case (`download_audio`, `search_results`)
- **Constants**: UPPER_SNAKE_CASE (`DEFAULT_DOWNLOAD_PATH`, `SUPPORTED_FORMATS`)
- **Private methods**: Leading underscore (`_validate_url`, _update_ui`)

### Error Handling
```python
# Always handle specific exceptions
try:
    youtube = YouTube(url)
    stream = youtube.streams.get_highest_resolution()
except pytube.exceptions.PytubeError as e:
    logger.error(f"YouTube error: {e}")
    return None
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise
```

## Project Structure

```
KJMedia/
├── main.py                  # Application entry point
├── pyproject.toml          # Dependencies and project config
├── Agents.md               # This file
├── README.md               # Project documentation
├── src/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main_app.py     # Main KivyApp class
│   │   ├── screens/        # Kivy Screen widgets
│   │   │   ├── __init__.py
│   │   │   ├── search_screen.py
│   │   │   ├── download_screen.py
│   │   │   └── config_screen.py
│   │   └── widgets/        # Custom Kivy widgets
│   │       ├── __init__.py
│   │       ├── search_item.py
│   │       ├── download_item.py
│   │       └── status_bar.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── downloader.py   # DownloadManager class
│   │   ├── search.py       # YouTube search functionality
│   │   └── config.py       # Configuration management
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py   # File operations
│       └── validators.py   # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_downloader.py
│   ├── test_search.py
│   └── test_config.py
├── assets/
│   ├── icons/              # UI icons
│   └── themes/             # Kivy theme files
└── downloads/              # Default download directory
```

## Application Functionality Requirements

### Core Features
1. **Horizontal Search Bar**
   - Text input field for YouTube search queries
   - Enter key triggers search
   - Search button (optional for accessibility)

2. **Search Results Display**
   - List of BoxLayout items with:
     - Video thumbnail (from YouTube API)
     - Video description
     - Video duration
   - Three action buttons per item:
     - **Karaoke**: MP4 with instrumental audio
     - **Audio**: MP3 extraction
     - **Video**: MP4 download

3. **Download Queue Management**
   - Secondary list showing queued downloads
   - Status tracking: pending, downloading, completed, failed
   - Media type indicator
   - Remove button for each item

4. **Queue Control Buttons**
   - Download all pending items
   - Clear completed/failed items
   - Pause/resume downloads

5. **Download Configuration**
   - Folder selection for different media types
   - Quality settings
   - Concurrent download limits

### Technical Implementation Notes
- Use `pytube` for YouTube video information and downloads
- Use `youtube-search` for search functionality
- Implement async download management with threading
- Store configuration in JSON format
- Log all operations for debugging

## Development Workflow

### Before Making Changes
1. Run tests: `uv run pytest`
2. Check code quality: `uv run ruff check .`
3. Ensure type hints pass: `uv run mypy .`

### Adding New Features
1. Create feature branch from main
2. Implement with proper error handling and logging
3. Add unit tests for new functionality
4. Update documentation as needed
5. Run full test suite before submitting

### Git Commit Conventions
- `feat:` New features
- `fix:` Bug fixes
- `refactor:` Code refactoring without functionality changes
- `test:` Adding or modifying tests
- `docs:` Documentation updates
- `style:` Code formatting changes

### Testing Strategy
- Unit tests for core functionality
- Integration tests for download processes
- Mock YouTube API responses for reliable testing
- Test error conditions and edge cases

## Configuration Management

### Default Settings
```python
DEFAULT_CONFIG = {
    "download_paths": {
        "karaoke": "./downloads/karaoke/",
        "audio": "./downloads/audio/", 
        "video": "./downloads/video/"
    },
    "max_concurrent_downloads": 3,
    "preferred_quality": "high",
    "auto_create_folders": True
}
```

### Runtime Configuration
- Store user preferences in `config.json`
- Validate all paths on startup
- Handle permission errors gracefully
- Support configuration reset to defaults

## Performance Considerations

### Download Optimization
- Implement download queue with priority management
- Use threading for concurrent downloads
- Cache YouTube video metadata to reduce API calls
- Implement resume capability for interrupted downloads

### UI Responsiveness
- Use Kivy's Clock for non-blocking operations
- Update UI elements asynchronously
- Implement loading indicators for long operations
- Handle network timeouts gracefully

## Security Best Practices

### Input Validation
- Sanitize all user inputs
- Validate YouTube URLs before processing
- Check file path traversal attempts
- Limit file name length and characters

### Error Logging
- Log errors without exposing sensitive information
- Use structured logging for easier debugging
- Implement log rotation for production use
- Never log passwords or API keys

This guide should help future AI agents understand the project structure, coding standards, and implementation requirements for maintaining and extending the KJMedia application.