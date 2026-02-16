from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.metrics import dp


class EditFilenameScreen(Popup):
    """Modal popup to edit the filename before enqueue.

    Expects:
      - media_item: dict-like with 'title', 'thumbnail', 'url', etc.
      - media_type: 'karaoke' | 'audio' | 'video'
      - on_continue(media_type, media_item, new_title)
      - on_cancel()
    """

    def __init__(self, media_item, media_type, on_continue, on_cancel, **kwargs):
        super().__init__(**kwargs)
        self.media_item = dict(media_item)
        self.media_type = media_type
        self._on_continue = on_continue
        self._on_cancel = on_cancel
        self.title_text = self.media_item.get("title", "")
        self.size_hint = (None, None)
        self.width = dp(600)
        self.height = dp(350)
        self.auto_dismiss = False
        self.title = "Edit Filename"
        self._error_label = None
        self._build()

    def _build(self):
        layout = BoxLayout(orientation="vertical", padding=dp(10), spacing=dp(10))
        # Thumbnail
        if self.media_item.get("thumbnail"):
            thumb = AsyncImage(
                source=self.media_item["thumbnail"], size_hint=(1, None), height=dp(120)
            )
        else:
            thumb = Label(text="[No thumbnail]", size_hint=(1, None), height=dp(120))
        layout.add_widget(thumb)

        # Title input
        self.title_input = TextInput(
            text=self.title_text,
            multiline=False,
            size_hint=(1, None),
            height=dp(40),
            font_size=20,
            unfocus_on_touch=False,
        )
        layout.add_widget(self.title_input)

        # Actions
        actions = BoxLayout(
            orientation="horizontal", size_hint_y=None, height=dp(40), spacing=dp(10)
        )
        cont = Button(text="Continue", on_release=self._continue)
        cancel = Button(text="Cancel", on_release=self._cancel)
        actions.add_widget(cont)
        actions.add_widget(cancel)
        layout.add_widget(actions)

        self.content = layout

    def _continue(self, _):
        new_title = self.title_input.text[:100]
        # Simple sanitization (filesystem-safe)
        sanitized = self._sanitize_filename(new_title)
        valid, formatted = self._validate_title_format(sanitized)
        if not valid:
            if self._error_label is None:
                self._error_label = Label(
                    text=formatted, color=(1, 0, 0, 1), size_hint_y=None, height=dp(20)
                )
                self.content.add_widget(self._error_label)
            else:
                self._error_label.text = formatted
            return
        self.dismiss()
        self._on_continue(self.media_type, self.media_item, formatted)

    def _cancel(self, _):
        self.dismiss()
        self._on_cancel()

    def _sanitize_filename(self, title: str) -> str:
        invalid = '<>:"/\\|?*'
        for ch in invalid:
            title = title.replace(ch, "_")
        title = " ".join(title.split())
        if len(title) > 100:
            title = title[:100]
        return title

    def _validate_title_format(self, title):
        # Must contain exactly one dash, with non-empty sides
        if title.count("-") != 1:
            return False, "Title must be in format: Artist Name - Title"
        left, right = [part.strip() for part in title.split("-", 1)]
        if not left or not right:
            return False, "Both artist and title must be non-empty"
        if "-" in left or "-" in right:
            return False, "Only a single dash is allowed"
        return True, f"{left} - {right}"
