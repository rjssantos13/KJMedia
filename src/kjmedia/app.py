from kivy.app import App
from kivy.uix.screenmanager import ScreenManager
from .config.settings import AppSettings
from .ui.screens.home_screen import HomeScreen
from .ui.screens.settings_screen import SettingsScreen


class KJMediaApp(App):
    """Main Kivy Application"""

    def __init__(self):
        super().__init__()
        self.settings = AppSettings()
        self.settings.path_manager.ensure_directories()

    def build(self):
        """Build the main app"""
        sm = ScreenManager()

        # Create screens
        home_screen = HomeScreen(name="home")
        settings_screen = SettingsScreen(settings=self.settings, name="settings")

        # Add screens to manager
        sm.add_widget(home_screen)
        sm.add_widget(settings_screen)

        return sm

    def on_start(self):
        """Called when app starts"""
        self.title = "KJMedia - YouTube Downloader"

    def on_stop(self):
        """Called when app stops"""
        self.settings.path_manager.save_paths()
