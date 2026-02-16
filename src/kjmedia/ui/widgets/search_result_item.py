from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import AsyncImage
from kivy.metrics import dp


class SearchResultItem(BoxLayout):
    """Widget for displaying a single search result with 3 download buttons"""

    def __init__(self, media_item, on_download_selected=None, **kwargs):
        super().__init__(**kwargs)
        self.orientation = "horizontal"
        self.size_hint_y = None
        self.height = dp(150)
        self.padding = dp(5)
        self.spacing = dp(5)
        self.media_item = media_item
        self.on_download_selected = on_download_selected

        self._create_layout()

    def _create_layout(self):
        """Create the search result item layout"""
        # Thumbnail
        thumbnail = AsyncImage(
            source=self.media_item.thumbnail or "",
            size_hint_x=None,
            width=dp(150),
        )
        self.add_widget(thumbnail)

        # Info section
        info_layout = BoxLayout(orientation="vertical", spacing=dp(2))

        title_label = Label(
            text=self.media_item.title,
            halign="center",
            valign="top",
        )
        info_layout.add_widget(title_label)

        channel_text = self.media_item.channel or "Unknown"
        channel_label = Label(
            text=f"{channel_text}",
            font_size="12sp",
            halign="center",
            color=(0.7, 0.7, 0.7, 1),
        )
        info_layout.add_widget(channel_label)

        duration_label = Label(
            text=f"{self.media_item.duration}",
            font_size="12sp",
            halign="center",
            color=(0.7, 0.7, 0.7, 1),
        )
        info_layout.add_widget(duration_label)

        self.add_widget(info_layout)

        # Download buttons (Karaoke, Audio, Video) in vertical layout
        button_layout = GridLayout(
            cols=1, spacing=dp(5), size_hint_x=None, width=dp(60)
        )

        karaoke_btn = Button(
            text="Karaoke",
            size_hint_y=None,
            height=dp(20),
            font_size="10sp",
            background_color=(0.8, 0.2, 0.8, 1),  # Purple for karaoke
            on_press=self._on_karaoke_pressed,
        )
        button_layout.add_widget(karaoke_btn)

        audio_btn = Button(
            text="Audio",
            size_hint_y=None,
            height=dp(20),
            font_size="10sp",
            background_color=(0.2, 0.8, 0.2, 1),  # Green for audio
            on_press=self._on_audio_pressed,
        )
        button_layout.add_widget(audio_btn)

        video_btn = Button(
            text="Video",
            size_hint_y=None,
            height=dp(20),
            font_size="10sp",
            background_color=(0.2, 0.4, 0.8, 1),  # Blue for video
            on_press=self._on_video_pressed,
        )
        button_layout.add_widget(video_btn)

        self.add_widget(button_layout)

    def _on_karaoke_pressed(self, instance):
        """Handle karaoke button press"""
        self._handle_button_press("karaoke")

    def _on_audio_pressed(self, instance):
        """Handle audio button press"""
        self._handle_button_press("audio")

    def _on_video_pressed(self, instance):
        """Handle video button press"""
        self._handle_button_press("video")

    def _handle_button_press(self, media_type):
        """Common handler for all button types"""
        print(
            f"DEBUG: {media_type.title()} button pressed for: {self.media_item.title[:30]}..."
        )
        print(f"DEBUG: self.on_download_selected = {self.on_download_selected}")
        print(
            f"DEBUG: Has on_download_selected callable: {callable(self.on_download_selected)}"
        )

        if self.on_download_selected:
            try:
                print(
                    f"DEBUG: Calling on_download_selected with ({media_type}, {self.media_item.title[:30]})"
                )
                self.on_download_selected(self.media_item, media_type)
                print(f"DEBUG: on_download_selected call completed")
            except Exception as fallback_e:
                print(f"DEBUG: Fallback error in button press: {fallback_e}")
        else:
            print(f"DEBUG: No on_download_selected callback available!")
