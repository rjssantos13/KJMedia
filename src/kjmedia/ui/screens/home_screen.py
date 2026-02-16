from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import pickle
from pathlib import Path
import time
from ..widgets.search_result_item import SearchResultItem
from ..widgets.download_indicator import DownloadIndicator
from ...services.youtube_service import YouTubeService
from .edit_filename_screen import EditFilenameScreen
from ..widgets.download_list_item import DownloadListItem
from ...models.media import DownloadTask, DownloadStatus, MediaItem


class HomeScreen(Screen):
    """Main application screen with search and download functionality"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "home"
        self.youtube_service = YouTubeService()
        self.search_results = []
        self.download_queue = []
        self.max_concurrent_downloads = 2  # Limit concurrent downloads
        self.download_indicator = DownloadIndicator()
        self.downloads_pickle_file = Path.home() / ".kjmedia" / "downloads.pkl"
        self._create_layout()
        self._load_downloads()

    def _create_layout(self):
        """Create the main application layout"""
        main_layout = BoxLayout(orientation="vertical", spacing=10, padding=15)

        # Header section with app title
        header = Label(
            text="KJMedia - YouTube Downloader",
            font_size="24sp",
            size_hint_y=None,
            height=40,
            bold=True,
        )
        main_layout.add_widget(header)

        # Search bar section (horizontal bar as requested)
        search_section = self._create_search_section()
        main_layout.add_widget(search_section)

        # Download indicator
        # main_layout.add_widget(self.download_indicator)

        # Content area with two lists
        content_area = self._create_content_area()
        main_layout.add_widget(content_area)

        self.add_widget(main_layout)

    def _create_search_section(self):
        """Create horizontal search bar with all controls"""
        search_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=50, spacing=10
        )

        self.search_input = TextInput(
            hint_text="Search YouTube for audio/video...",
            multiline=False,
            font_size="22sp",
            unfocus_on_touch=False,
        )
        self.search_input.bind(on_text_validate=self._on_search_enter)

        search_btn = Button(
            text="Search", size_hint_x=None, width=100, on_press=self._perform_search
        )

        download_all_btn = Button(
            text="Download All",
            size_hint_x=None,
            width=120,
            background_color=(0.2, 0.6, 0.2, 1),
            on_press=self._download_all_pending,
        )

        clear_queue_btn = Button(
            text="Clear Queue",
            size_hint_x=None,
            width=120,
            background_color=(0.8, 0.4, 0.2, 1),
            on_press=self._clear_download_queue,
        )

        config_btn = Button(
            text="Folders",
            size_hint_x=None,
            width=100,
            on_press=self._show_config_screen,
        )

        # Add all widgets to search layout
        search_layout.add_widget(self.search_input)
        search_layout.add_widget(search_btn)
        search_layout.add_widget(download_all_btn)
        search_layout.add_widget(clear_queue_btn)
        search_layout.add_widget(config_btn)

        return search_layout

    def _create_content_area(self):
        """Create content area with search results and download queue"""
        content_layout = BoxLayout(orientation="horizontal", spacing=10)

        # Search results section
        search_section = BoxLayout(orientation="vertical", spacing=5)
        search_label = Label(
            text="Search Results",
            font_size="18sp",
            size_hint_y=None,
            height=30,
            bold=True,
        )
        search_section.add_widget(search_label)

        self.search_results_container = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.search_results_container.bind(
            minimum_height=self.search_results_container.setter("height")
        )

        search_scroll = ScrollView()
        search_scroll.add_widget(self.search_results_container)
        search_section.add_widget(search_scroll)

        # Download queue section
        queue_section = BoxLayout(orientation="vertical", spacing=5)
        queue_label = Label(
            text="Download Queue",
            font_size="18sp",
            size_hint_y=None,
            height=30,
            bold=True,
        )
        queue_section.add_widget(queue_label)

        self.download_queue_container = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.download_queue_container.bind(
            minimum_height=self.download_queue_container.setter("height")
        )

        queue_scroll = ScrollView()
        queue_scroll.add_widget(self.download_queue_container)
        queue_section.add_widget(queue_scroll)

        content_layout.add_widget(search_section)
        content_layout.add_widget(queue_section)

        return content_layout

    def _on_search_enter(self, instance):
        """Handle Enter key in search input"""
        self._perform_search(None)

    def _perform_search(self, instance):
        """Perform YouTube search"""
        query = self.search_input.text.strip()
        if not query:
            return

        # Clear previous results
        self.search_results_container.clear_widgets()
        self.search_results = []

        # Add loading indicator
        loading_label = Label(text="Searching...")
        self.search_results_container.add_widget(loading_label)

        # Perform search
        try:
            results = self.youtube_service.search_videos(query, max_results=50)
            self.search_results_container.clear_widgets()

            for media_item in results:
                # Create search result item with 3 buttons (Karaoke, Audio, Video)
                result_item = SearchResultItem(
                    media_item=media_item,
                    on_download_selected=self._add_to_download_queue,
                )
                self.search_results_container.add_widget(result_item)
                self.search_results.append(result_item)

        except Exception as e:
            self.search_results_container.clear_widgets()
            error_label = Label(text=f"Search error: {str(e)}")
            self.search_results_container.add_widget(error_label)

    def _add_to_download_queue(self, media_item, media_type):
        media_item_dict = {
            "id": media_item.id,
            "title": media_item.title,
            "url": media_item.url,
            "duration": media_item.duration,
            "thumbnail": media_item.thumbnail,
            "channel": media_item.channel,
        }

        def open_popup(dt):
            edit_popup = EditFilenameScreen(
                media_item=media_item_dict,
                media_type=media_type,
                on_continue=self._media_title_edited,
                on_cancel=lambda: None,
            )
            edit_popup.open()
            Clock.schedule_once(
                lambda dt, popup=edit_popup: setattr(popup.title_input, "focus", True)
            )

        Clock.schedule_once(open_popup)

    def _media_title_edited(self, media_type, media_item, formatted):

        media_item["title"] = formatted
        media_item_obj = MediaItem(
            id=media_item["id"],
            title=media_item["title"],
            url=media_item["url"],
            duration=media_item["duration"],
            thumbnail=media_item["thumbnail"],
            channel=media_item["channel"],
        )

        self._continue_add_to_download_queue(
            media_item=media_item_obj, media_type=media_type
        )

    def _continue_add_to_download_queue(self, media_item, media_type):
        """Add item to download queue"""
        # Debug output
        print(f"DEBUG: Adding {media_item.title} as {media_type}")
        print(
            f"DEBUG: on_download_selected callback: {self.search_results[-1].on_download_selected if self.search_results else None}"
        )

        # Check if already in queue
        for download_item in self.download_queue:
            if (
                download_item.download_task.media_item.id == media_item.id
                and download_item.download_task.media_type == media_type
            ):
                print(f"DEBUG: Already in queue: {media_item.title} as {media_type}")
                return  # Already in queue

        # Check if item is already being downloaded or completed with same media type
        for download_item in self.download_queue:
            if (
                download_item.download_task.media_item.id == media_item.id
                and download_item.download_task.status.value
                in ["downloading", "completed"]
            ):
                print(
                    f"Item {media_item.title} ({media_type}) is already {download_item.download_task.status.value}"
                )
                return  # Already downloading or completed

        download_task = DownloadTask(
            media_item=media_item,
            media_type=media_type,
            status=DownloadStatus.PENDING,
            thumbnail=media_item.thumbnail,
        )

        download_item = DownloadListItem(
            download_task=download_task,
            on_remove=self._remove_from_queue,
            on_status_change=self._save_downloads,
        )

        self.download_queue_container.add_widget(download_item)
        self.download_queue.append(download_item)
        self._save_downloads()

    def _remove_from_queue(self, download_item):
        """Remove item from download queue"""
        if download_item in self.download_queue:
            self.download_queue_container.remove_widget(download_item)
            self.download_queue.remove(download_item)
            self._save_downloads()

    def _download_all_pending(self, instance):
        """Download all pending items in queue with staggered starts"""
        # Check if downloads are already running
        downloading_count = sum(
            1
            for item in self.download_queue
            if item.download_task.status.value == "downloading"
        )

        if downloading_count >= self.max_concurrent_downloads:
            return  # Already at max concurrent downloads

        pending_items = [
            item
            for item in self.download_queue
            if item.download_task.status.value == "pending"
        ]

        # Calculate how many more downloads we can start
        available_slots = self.max_concurrent_downloads - downloading_count
        # items_to_start = pending_items[:available_slots]

        # Stagger downloads to prevent overwhelming the system
        for i, download_item in enumerate(pending_items):
            delay = i * 1.0  # 1 second delay between downloads
            Clock.schedule_once(
                lambda dt, item=download_item: self._start_download_with_indicator(
                    item
                ),
                delay,
            )

        # Update download indicator (only if needed)
        Clock.schedule_once(lambda dt: self._update_download_indicator())

    def _clear_download_queue(self, instance):
        """Clear the download queue"""
        self.download_queue_container.clear_widgets()
        self.download_queue = []
        self._update_download_indicator()
        if self.downloads_pickle_file.exists():
            self.downloads_pickle_file.unlink()

    def _start_download_with_indicator(self, download_item):
        """Start download and update indicator"""
        download_item.start_download()
        Clock.schedule_once(lambda dt: self._update_download_indicator())

    def _update_download_indicator(self):
        """Update download status indicator"""
        downloading_count = sum(
            1
            for item in self.download_queue
            if item.download_task.status.value == "downloading"
        )

        # Only update if indicator exists and count has changed
        if hasattr(self, "download_indicator") and downloading_count != getattr(
            self, "_last_downloading_count", 0
        ):
            self.download_indicator.update_status(downloading_count)
            self._last_downloading_count = downloading_count

    def _show_config_screen(self, instance):
        """Show configuration screen"""
        self.manager.current = "settings"

    def _save_downloads(self):
        """Save download queue to pickle file"""
        data = []
        for download_item in self.download_queue:
            task = download_item.download_task
            data.append(
                {
                    "media_item": {
                        "id": task.media_item.id,
                        "title": task.media_item.title,
                        "url": task.media_item.url,
                        "duration": task.media_item.duration,
                        "thumbnail": task.media_item.thumbnail,
                        "channel": task.media_item.channel,
                    },
                    "status": task.status.value,
                    "media_type": task.media_type,
                }
            )

        self.downloads_pickle_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.downloads_pickle_file, "wb") as f:
            pickle.dump(data, f)

    def _load_downloads(self):
        """Load download queue from pickle file"""
        if not self.downloads_pickle_file.exists():
            return

        try:
            with open(self.downloads_pickle_file, "rb") as f:
                data = pickle.load(f)

            for item_data in data:
                media_item = MediaItem(
                    id=item_data["media_item"]["id"],
                    title=item_data["media_item"]["title"],
                    url=item_data["media_item"]["url"],
                    duration=item_data["media_item"]["duration"],
                    thumbnail=item_data["media_item"]["thumbnail"],
                    channel=item_data["media_item"]["channel"],
                )

                status = DownloadStatus(item_data["status"])
                download_task = DownloadTask(
                    media_item=media_item,
                    media_type=item_data["media_type"],
                    status=status,
                    thumbnail=media_item.thumbnail,
                )

                download_item = DownloadListItem(
                    download_task=download_task,
                    on_remove=self._remove_from_queue,
                    on_status_change=self._save_downloads,
                )

                self.download_queue_container.add_widget(download_item)
                self.download_queue.append(download_item)

                if status == DownloadStatus.COMPLETED:
                    download_item.status_label.text = "Completed"
                    download_item.status_label.color = (0.2, 0.8, 0.2, 1)
                    download_item.progress_bar.value = 100
                elif status == DownloadStatus.FAILED:
                    download_item.status_label.text = "Failed"
                    download_item.status_label.color = (0.8, 0.2, 0.2, 1)
                elif status == DownloadStatus.DOWNLOADING:
                    download_item.status_label.text = "Downloading..."
                    download_item.status_label.color = (0.2, 0.6, 0.8, 1)
        except (pickle.PickleError, IOError, KeyError):
            pass
