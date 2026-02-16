from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
import threading, os
from ...models.media import DownloadStatus
from ...services.download_service import DownloadService
from ...config.settings import AppSettings


class DownloadListItem(BoxLayout):
    """Widget for displaying a download task with thumbnail in the download list"""

    def __init__(self, download_task, on_remove=None, on_status_change=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(150)
        self.padding = dp(5)
        self.spacing = dp(5)
        self.download_task = download_task
        self.on_remove = on_remove
        self.on_status_change = on_status_change

        self._create_layout()

    def _create_layout(self):
        """Create layout with thumbnail, info, and progress"""
        # Thumbnail
        thumbnail = AsyncImage(
            source=self.download_task.media_item.thumbnail or "",
            size_hint_x=None,
            width=dp(150),
        )

        # Info section
        info_layout = BoxLayout(orientation="vertical", spacing=dp(2))

        # Title
        title_label = Label(
            text=self.download_task.media_item.title,
            halign="center",
            valign="middle",
            bold=True,
        )
        info_layout.add_widget(title_label)

        media_type_label = Label(
            text=self.download_task.media_type.title(),
            color=(0.7, 0.7, 0.7, 1),
        )

        duration_label = Label(
            text=f"• {self.download_task.media_item.duration}",
            color=(0.7, 0.7, 0.7, 1),
        )

        info_layout.add_widget(media_type_label)
        info_layout.add_widget(duration_label)

        # Status and progress section
        status_layout = GridLayout(cols=1, spacing=dp(5), size_hint_x=None, width=100)

        # Status label
        self.status_label = Label(
            text="Pending",
            font_size="10sp",
            size_hint_y=None,
            height=dp(15),
        )
        status_layout.add_widget(self.status_label)

        # Progress bar
        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=dp(10),
        )
        status_layout.add_widget(self.progress_bar)

        # Remove button
        remove_btn = Button(
            text="Remove",
            size_hint_y=None,
            height=20,
            background_color=(0.8, 0.2, 0.2, 1),
            on_press=self._on_remove,
        )
        status_layout.add_widget(remove_btn)

        # Add all sections to main layout
        self.add_widget(thumbnail)
        self.add_widget(info_layout)
        self.add_widget(status_layout)

    def _get_thumbnail(self):
        """Get thumbnail image with fallback"""
        thumbnail = self.download_task.media_item.thumbnail
        if thumbnail:
            return thumbnail
        else:
            # Return a placeholder image or default
            return self._generate_placeholder_thumbnail()

    def _generate_placeholder_thumbnail(self):
        """Generate a placeholder thumbnail when no image available"""
        # For now, return empty string - in future we could use a default icon
        return ""

    def start_download(self):
        """Start the download process asynchronously"""

        # Check if already downloading or completed
        if self.download_task.status in [
            DownloadStatus.DOWNLOADING,
            DownloadStatus.COMPLETED,
        ]:
            return

        # Start download in separate thread
        print(
            f"DEBUG: Starting download thread for {self.download_task.media_item.title[:30]}..."
        )
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        """Download thread to run in background"""

        self.download_service = DownloadService()
        self.download_task.status = DownloadStatus.DOWNLOADING
        self._download_complete = False
        self._update_status("Downloading...")

        # Get download path based on media type

        settings = AppSettings()

        download_paths = {
            "karaoke": settings.karaoke_path,
            "audio": settings.audio_path,
            "video": settings.video_path,
        }

        download_path = download_paths.get(
            self.download_task.media_type, settings.video_path
        )

        try:
            filepath = self.download_service.download_media(
                self.download_task.media_item,
                self.download_task.media_type,
                download_path,
                progress_callback=self._update_progress,
            )
            self._download_complete = True
            # Check if download actually completed successfully
            if filepath and os.path.exists(filepath):
                self.download_task.status = DownloadStatus.COMPLETED
                self.download_task.local_path = filepath

                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._update_status("Completed"))
                Clock.schedule_once(lambda dt: setattr(self.progress_bar, "value", 100))

                print(f"Download completed: {os.path.basename(filepath)}")
            else:
                self.download_task.status = DownloadStatus.FAILED
                self.download_task.error_message = "Download failed - file not found"

                # Update UI on main thread
                Clock.schedule_once(lambda dt: self._update_status("Failed"))
                print(f"Download failed: File not saved")

            if self.on_status_change:
                Clock.schedule_once(lambda dt: self.on_status_change())

        except Exception as e:
            self.download_task.status = DownloadStatus.FAILED
            self.download_task.error_message = str(e)
            error_msg = f"Failed: {str(e)}"

            # Update UI on main thread
            Clock.schedule_once(lambda dt, msg=error_msg: self._update_status(msg))

            print(f"Download exception: {str(e)}")

            if self.on_status_change:
                Clock.schedule_once(lambda dt: self.on_status_change())
        finally:
            # Clean up
            self.download_service = None

    def _update_progress(self, progress):
        # Guard against late callbacks after completion
        if self.download_task.status in (
            DownloadStatus.COMPLETED,
            DownloadStatus.FAILED,
        ):
            return
        if self.download_task.status != DownloadStatus.DOWNLOADING:
            return
        # Update progress text safely
        progress_percent = int(progress * 100)
        status_text = f"Downloading... {progress_percent}%"

        # Schedule UI updates on main thread
        Clock.schedule_once(
            lambda dt, val=progress_percent: setattr(self.progress_bar, "value", val)
        )
        Clock.schedule_once(lambda dt, txt=status_text: self._update_status(txt))

    def _update_status(self, status_text):
        """Update status label"""
        self.status_label.text = status_text

        if status_text:
            self.status_label.text = status_text

        # Update color based on status
        if self.download_task.status == DownloadStatus.COMPLETED:
            self.status_label.color = (0.2, 0.8, 0.2, 1)  # Green
        elif self.download_task.status == DownloadStatus.FAILED:
            self.status_label.color = (0.8, 0.2, 0.2, 1)  # Red
        else:
            self.status_label.color = (0.2, 0.6, 0.8, 1)  # Blue

    def _on_remove(self, instance):
        """Handle remove button press"""
        if self.on_remove:
            self.on_remove(self)
