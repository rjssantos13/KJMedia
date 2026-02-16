from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.metrics import dp


class DownloadIndicator(Label):
    """Simple indicator showing active download count"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text = "Ready"
        self.size_hint_x = None
        self.size_hint_y = None
        self.width = dp(100)
        self.height = dp(30)
        self.font_size = "12sp"
        self.color = (0.2, 0.8, 0.2, 1)
        self.italic = True

    def update_status(self, downloading_count):
        """Update the indicator text"""
        if downloading_count == 0:
            self.text = "Ready"
            self.color = (0.2, 0.8, 0.2, 1)  # Green
        elif downloading_count == 1:
            self.text = "1 downloading"
            self.color = (0.8, 0.6, 0.2, 1)  # Orange
        else:
            self.text = f"{downloading_count} downloading"
            self.color = (0.8, 0.2, 0.2, 1)  # Red
