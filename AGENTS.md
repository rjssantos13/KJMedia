# KJMedia - AI Assistant Guide

## Project Overview
KJMedia is a Kivy-based YouTube downloader and player application that supports downloading content in three formats:
- **Karaoke**: MP4 format for karaoke videos
- **Audio**: MP3 format for audio-only content  
- **Video**: MP4 format for regular videos

## Build & Development Commands

### Environment Setup
```bash
# Install dependencies using uv (preferred)
uv sync

# Or using pip
pip install -e .

# Create virtual environment (if needed)
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows
```

### Running the Application
```bash
# Run from project root
python main.py

# Or run as module
python -m src.kjmedia.main
```

### Testing Commands
```bash
# Run all tests (when tests are implemented)
pytest tests/

# Run with coverage
pytest tests/ --cov=src/kjmedia

# Run specific test file
pytest tests/test_youtube_service.py -v
```

### Linting & Formatting
```bash
# Format code (when black is configured)
black src/ tests/

# Lint code (when flake8 is configured)
flake8 src/ tests/

# Type checking (when mypy is configured)
mypy src/
```

## Project Architecture

### Directory Structure
```
src/kjmedia/
├── __init__.py              # Package initialization
├── main.py                  # Main entry point
├── app.py                   # Kivy application class
├── config/
│   ├── paths.py            # Download path management
│   └── settings.py         # App settings configuration
├── models/
│   └── media.py            # Media data models
├── services/
│   ├── youtube_service.py  # YouTube API integration
│   └── download_service.py # Download management service
├── ui/
│   ├── screens/
│   │   ├── home_screen.py  # Main application screen
│   │   └── settings_screen.py # Configuration screen
│   └── widgets/
│       ├── search_result_item.py # Search result widget
│       └── download_item.py      # Download queue widget
└── utils/
    ├── file_utils.py       # File operations
    └── validation.py       # Input validation
```

### Core Components

#### Models (`models/media.py`)
- `MediaItem`: Represents YouTube video data
- `DownloadTask`: Represents download state and progress
- `MediaType`: Enum for KARAOKE/AUDIO/VIDEO
- `DownloadStatus`: Enum for PENDING/DOWNLOADING/COMPLETED/FAILED

#### Services
- `YouTubeService`: Handles YouTube search and video info retrieval using yt-dlp
- `DownloadService`: Manages file downloads with progress tracking using yt-dlp

#### UI Structure
- `HomeScreen`: Main interface with search bar, results list, and download queue
- `SettingsScreen`: Configuration for download paths
- Custom widgets follow BoxLayout patterns as specified in requirements

## Code Style Guidelines

### Python Standards
- Use **Python 3.12+** with type hints throughout
- Follow PEP 8 naming conventions:
  - Classes: `PascalCase`
  - Functions/variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`
- Use dataclasses for simple data structures
- Use async/await for I/O operations when applicable

### Kivy-Specific Conventions
- **BoxLayout** is preferred for layouts (as specified in requirements)
- Horizontal organization for main search bar
- Vertical organization for button groups (3 buttons: Karaoke, Audio, Video)
- Use `size_hint_y=None` and fixed `height` for precise control
- Include proper padding and spacing using `dp()` units

### Import Organization
```python
# Standard library imports
import os
from pathlib import Path

# Third-party imports
from kivy.uix.boxlayout import BoxLayout
from pytube import YouTube

# Local imports
from ..models.media import MediaItem
from ...services.youtube_service import YouTubeService
```

### Error Handling
- Use try/except blocks for YouTube API calls
- Provide user-friendly error messages
- Log errors with context information
- Validate inputs before processing

### Naming Patterns
- Screen classes end with `Screen`: `HomeScreen`, `SettingsScreen`
- Widget classes are descriptive: `SearchResultItem`, `DownloadItem`
- Service classes end with `Service`: `YouTubeService`, `DownloadService`
- Model classes represent data: `MediaItem`, `DownloadTask`

## Application Functionality

### UI Requirements (from Agents.md)
- **Horizontal search bar** with text input and search functionality
- **Search results list** with:
  - Extracted thumbnails
  - Video descriptions and duration
  - BoxLayout with 3 vertical buttons (Karaoke, Audio, Video)
- **Download queue list** with:
  - Selected search result information
  - Item status (initially pending)
  - Media type display
  - Remove button for each item
- **Control buttons**:
  - Download all pending items
  - Clear download queue
  - Show download folders configuration

### File Type Handling
- **Karaoke**: Download as MP4, default location `~/Music/Karaoke`
- **Audio**: Download as MP3, default location `~/Music/Downloads`
- **Video**: Download as MP4, default location `~/Videos/Downloads`

### Configuration Management
- Paths stored in `~/.kjmedia/paths.json`
- Configurable via Settings screen
- Automatic directory creation on first use
- Default paths reset option available

### Data Flow
1. User searches YouTube via search bar
2. Results displayed with thumbnails and metadata
3. User selects download type (K/A/V buttons)
4. Item added to download queue with PENDING status
5. Download process updates status and progress
6. Completed files saved to configured locations

## Development Workflow

### Adding New Features
1. Update data models if needed (`models/media.py`)
2. Implement business logic in appropriate service
3. Create UI components in `ui/screens/` or `ui/widgets/`
4. Wire up components in main application class
5. Update configuration if new settings are required

### Testing Approach
- Unit tests for services and models
- Integration tests for UI components
- Mock YouTube API calls for testing
- Test file operations with temporary directories

### Configuration Changes
- Path settings managed by `PathManager` class
- JSON-based persistence in user's home directory
- Settings accessible via `AppSettings` class
- Automatic backup and validation of configuration

### Common Patterns
- Use callbacks for async operations (download progress)
- Implement proper cleanup in service destructors
- Separate UI updates from business logic
- Use relative imports within the package
- Handle network errors gracefully

## Dependencies
- `kivy>=2.3.1`: GUI framework
- `yt-dlp>=2024.1.0`: YouTube API integration and downloads
- `youtube-search>=2.2.0`: Search functionality

## Notes for AI Agents
- This is an early-stage project with basic structure implemented
- UI components follow the specific layout requirements from Agents.md
- Download functionality is implemented but may need error handling improvements
- Configuration system is in place and functional
- All components use proper typing and follow Python best practices