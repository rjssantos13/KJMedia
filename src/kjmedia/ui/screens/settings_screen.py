from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup


class SettingsScreen(Screen):
    """Configuration screen for download folder settings"""

    def __init__(self, settings, **kwargs):
        super().__init__(**kwargs)
        self.settings = settings
        self.name = "settings"
        self._create_layout()

    def _create_layout(self):
        """Create settings screen layout"""
        layout = BoxLayout(orientation="vertical", spacing=20, padding=30)

        # Header
        header = BoxLayout(orientation="horizontal", size_hint_y=None, height=50)

        back_btn = Button(
            text="← Back", size_hint_x=None, width=100, on_press=self._go_home
        )
        header.add_widget(back_btn)

        title = Label(text="Download Folders Configuration", font_size="20sp")
        header.add_widget(title)

        layout.add_widget(header)

        # Description
        desc_label = Label(
            text="Configure download locations for each media type:",
            font_size="14sp",
            size_hint_y=None,
            height=30,
        )
        layout.add_widget(desc_label)

        # Download paths configuration
        paths_layout = BoxLayout(orientation="vertical", spacing=15)

        # Karaoke path
        karaoke_layout = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=40
        )
        karaoke_label = Label(text="Karaoke (MP4):", size_hint_x=0.25)
        self.karaoke_input = TextInput(text=self.settings.karaoke_path)
        karaoke_browse_btn = Button(
            text="Browse",
            size_hint_x=None,
            width=50,
            on_press=lambda x: self._browse_folder("karaoke"),
        )
        karaoke_layout.add_widget(karaoke_label)
        karaoke_layout.add_widget(self.karaoke_input)
        karaoke_layout.add_widget(karaoke_browse_btn)
        paths_layout.add_widget(karaoke_layout)

        # Audio path
        audio_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        audio_label = Label(text="Audio (MP3):", size_hint_x=0.25)
        self.audio_input = TextInput(text=self.settings.audio_path)
        audio_browse_btn = Button(
            text="Browse",
            size_hint_x=None,
            width=50,
            on_press=lambda x: self._browse_folder("audio"),
        )
        audio_layout.add_widget(audio_label)
        audio_layout.add_widget(self.audio_input)
        audio_layout.add_widget(audio_browse_btn)
        paths_layout.add_widget(audio_layout)

        # Video path
        video_layout = BoxLayout(orientation="horizontal", size_hint_y=None, height=40)
        video_label = Label(text="Video (MP4):", size_hint_x=0.25)
        self.video_input = TextInput(text=self.settings.video_path)
        video_browse_btn = Button(
            text="Browse",
            size_hint_x=None,
            width=50,
            on_press=lambda x: self._browse_folder("video"),
        )
        video_layout.add_widget(video_label)
        video_layout.add_widget(self.video_input)
        video_layout.add_widget(video_browse_btn)
        paths_layout.add_widget(video_layout)

        layout.add_widget(paths_layout)

        # Save button
        save_btn = Button(
            text="Save Settings",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.2, 1),
            on_press=self._save_settings,
        )
        layout.add_widget(save_btn)

        # Reset to defaults button
        reset_btn = Button(
            text="Reset to Defaults",
            size_hint_y=None,
            height=40,
            background_color=(0.8, 0.6, 0.2, 1),
            on_press=self._reset_to_defaults,
        )
        layout.add_widget(reset_btn)

        layout.add_widget(BoxLayout())  # Spacer

        self.add_widget(layout)

    def _save_settings(self, instance):
        """Save current settings"""
        self.settings.path_manager.set_path("karaoke", self.karaoke_input.text)
        self.settings.path_manager.set_path("audio", self.audio_input.text)
        self.settings.path_manager.set_path("video", self.video_input.text)
        self.settings.path_manager.save_paths()
        self.settings.path_manager.save_pickle()
        self.settings.path_manager.ensure_directories()

    def _reset_to_defaults(self, instance):
        """Reset paths to default values"""
        from pathlib import Path

        default_paths = {
            "karaoke": str(Path.home() / "Music" / "Karaoke"),
            "audio": str(Path.home() / "Music" / "Downloads"),
            "video": str(Path.home() / "Videos" / "Downloads"),
        }

        self.karaoke_input.text = default_paths["karaoke"]
        self.audio_input.text = default_paths["audio"]
        self.video_input.text = default_paths["video"]

    def _go_home(self, instance):
        """Navigate back to home screen"""
        self.manager.current = "home"

    def _browse_folder(self, folder_type):
        """Open folder browser dialog"""
        current_path = getattr(self, f"{folder_type}_input").text

        content = BoxLayout(orientation="vertical", spacing=10, padding=10)
        file_chooser = FileChooserListView(
            path=current_path if current_path else ".", dirselect=True
        )
        content.add_widget(file_chooser)

        button_layout = BoxLayout(size_hint_y=None, height=40, spacing=10)
        cancel_btn = Button(text="Cancel", size_hint_x=0.5)
        select_btn = Button(text="Select", size_hint_x=0.5)
        button_layout.add_widget(cancel_btn)
        button_layout.add_widget(select_btn)
        content.add_widget(button_layout)

        popup = Popup(
            title=f"Select {folder_type.title()} Folder",
            content=content,
            size_hint=(0.9, 0.9),
            auto_dismiss=False,
        )

        def on_select(instance):
            selected = file_chooser.selection
            if selected:
                getattr(self, f"{folder_type}_input").text = selected[0]
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=popup.dismiss)

        popup.open()
