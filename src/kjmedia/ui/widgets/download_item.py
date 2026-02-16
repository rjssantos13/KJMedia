import os
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.progressbar import ProgressBar
from kivy.metrics import dp
from kivy.clock import Clock
import threading
from ...models.media import DownloadStatus


class DownloadItem(BoxLayout):
    """Widget for displaying a download queue item with status and remove button"""

    def __init__(self, download_task, on_remove=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(60)
        self.padding = dp(5)
        self.spacing = dp(5)
        self.download_task = download_task
        self.on_remove = on_remove
        self.download_service = None

        self._create_layout()

    def _create_layout(self):
        """Create the download item layout"""
        # Title and info
        info_layout = BoxLayout(orientation="vertical", spacing=dp(2))

        title_label = Label(
            text=self.download_task.media_item.title,
            font_size="14sp",
            text_size=(dp(250), None),
            halign="left",
            valign="middle",
            max_lines=2,
        )
        info_layout.add_widget(title_label)

        # Media type and duration
        meta_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(20)
        )

        media_type_label = Label(
            text=f"{self.download_task.media_type.title()} • {self.download_task.media_item.duration}",
            font_size="12sp",
            color=(0.7, 0.7, 0.7, 1),
        )
        meta_layout.add_widget(media_type_label)
        info_layout.add_widget(meta_layout)

        self.add_widget(info_layout)

        # Status and progress section
        status_layout = BoxLayout(
            orientation="vertical", spacing=dp(2), size_hint_x=None, width=dp(150)
        )

        self.status_label = Label(
            text="Pending", font_size="12sp", size_hint_y=None, height=dp(20)
        )
        status_layout.add_widget(self.status_label)

        self.progress_bar = ProgressBar(
            max=100, value=0, size_hint_y=None, height=dp(15)
        )
        status_layout.add_widget(self.progress_bar)

        self.add_widget(status_layout)

        # Remove button
        remove_btn = Button(
            text="Remove",
            size_hint_x=None,
            width=dp(60),
            font_size="10sp",
            background_color=(0.8, 0.2, 0.2, 1),
            on_press=self._on_remove,
        )
        self.add_widget(remove_btn)

    def start_download(self):
        """Start the download process asynchronously"""
        # Debug output
        print(
            f"DEBUG: start_download called for {self.download_task.media_item.title[:30]}... status: {self.download_task.status.value}"
        )

        # Check if already downloading or completed
        if self.download_task.status in [
            DownloadStatus.DOWNLOADING,
            DownloadStatus.COMPLETED,
        ]:
            print(
                f"DEBUG: Skipping download - already {self.download_task.status.value}"
            )
            return

        # Start download in separate thread
        print(
            f"DEBUG: Starting download thread for {self.download_task.media_item.title[:30]}..."
        )
        threading.Thread(target=self._download_thread, daemon=True).start()

    def _download_thread(self):
        """Download thread to run in background"""
        # Import here to avoid circular imports
        from ...services.download_service import DownloadService

        # Check if already downloading or completed
        if self.download_task.status in [
            DownloadStatus.DOWNLOADING,
            DownloadStatus.COMPLETED,
        ]:
            return

        self.download_service = DownloadService()
        self.download_task.status = DownloadStatus.DOWNLOADING
        self._update_status("Downloading...")

        # Get download path based on media type
        from ...config.settings import AppSettings

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

        except Exception as e:
            self.download_task.status = DownloadStatus.FAILED
            self.download_task.error_message = str(e)
            error_msg = f"Failed: {str(e)}"

            # Update UI on main thread
            Clock.schedule_once(lambda dt, msg=error_msg: self._update_status(msg))

            print(f"Download exception: {str(e)}")
        finally:
            # Clean up
            self.download_service = None

    def _update_progress(self, progress):
        """Update download progress on main thread"""
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

    def _on_remove(self, instance):
        """Handle remove button press"""
        if self.on_remove:
            self.on_remove(self)
