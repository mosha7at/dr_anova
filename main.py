import os
import threading
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.lang import Builder
from kivy.uix.filechooser import FileChooserListView
import yt_dlp

# Setup yt-dlp options
def download_media(url, save_path='downloads/', media_type='audio', video_quality=None, progress_callback=None):
    if media_type == 'audio':
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '0',
            }],
            'progress_hooks': [progress_callback] if progress_callback else [],
        }
    elif media_type == 'video':
        format_map = {
            '144p': '144p',
            '240p': '240p',
            '360p': '360p',
            '480p': '480p',
            '720p': '720p',
            '1080p': '1080p',
        }
        if video_quality not in format_map:
            return "Invalid video quality choice."
        
        selected_quality = format_map[video_quality]
        ydl_opts = {
            'format': f'bestvideo[height={selected_quality}]+bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_callback] if progress_callback else [],
        }
    else:
        return "Please choose 'audio' or 'video' only."

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

# Update progress bar
def update_progress(d):
    if d['status'] == 'downloading':
        try:
            percent = int(d['_percent_str'].strip('%'))
            app.root.ids.progress_bar.value = percent
            app.root.ids.progress_label.text = f"{percent}%"
        except ValueError:
            pass

# Main application class
class DownloadApp(App):
    def build(self):
        self.title = "Media Downloader"
        Builder.load_string(kv_design)
        return RootWidget()

    # Start download function
    def start_download(self):
        url = self.root.ids.url_input.text
        media_type = 'audio' if self.root.ids.radio_audio.state == 'down' else 'video'
        
        # Check which quality button is selected
        quality_choice = None
        for quality in ['144p', '240p', '360p', '480p', '720p', '1080p']:
            toggle_button = self.root.ids[f"quality_{quality.replace('p', '')}"]
            if toggle_button.state == 'down':
                quality_choice = quality
                break
        
        if not url:
            self.show_popup("Error", "Please enter a valid URL.")
            return

        if not quality_choice:
            self.show_popup("Error", "Please select a video quality.")
            return

        save_path = self.root.ids.save_path.text
        if not save_path:
            self.show_popup("Error", "Please select a save location.")
            return

        def download_thread():
            try:
                result = download_media(url, save_path=save_path, media_type=media_type,
                                        video_quality=quality_choice, progress_callback=update_progress)
                if isinstance(result, str):  # If there's an error message
                    self.show_popup("Error", result)
                else:
                    self.show_popup("Success", "File downloaded successfully!")
            except Exception as e:
                self.show_popup("Error", f"An error occurred during download: {e}")

        threading.Thread(target=download_thread).start()

    # Show popup message
    def show_popup(self, title, message):
        popup = Popup(title=title, content=Label(text=message), size_hint=(None, None), size=(400, 200))
        popup.open()

    # Open file chooser dialog
    def open_file_chooser(self):
        content = BoxLayout(orientation='vertical')
        file_chooser = FileChooserListView(path=os.getcwd(), dirselect=True)
        confirm_button = Button(text="Confirm", size_hint_y=None, height=50)
        cancel_button = Button(text="Cancel", size_hint_y=None, height=50)

        content.add_widget(file_chooser)
        buttons_layout = BoxLayout(size_hint_y=None, height=50)
        buttons_layout.add_widget(confirm_button)
        buttons_layout.add_widget(cancel_button)
        content.add_widget(buttons_layout)

        popup = Popup(title="Choose Save Location", content=content, size_hint=(0.9, 0.9))

        def on_confirm(instance):
            selected_path = file_chooser.path
            self.root.ids.save_path.text = selected_path
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        confirm_button.bind(on_release=on_confirm)
        cancel_button.bind(on_release=on_cancel)

        popup.open()

# Kivy Design
kv_design = """
#:kivy 2.1.0

<RootWidget>:
    orientation: 'vertical'
    padding: 20
    spacing: 10
    background_color: (1, 1, 1, 1)  # White background

    # Dr Anova Logo
    Label:
        text: "Dr Anova"
        font_size: '32sp'
        color: (0.2, 0.6, 1, 1)  # Blue color
        bold: True
        size_hint_y: None
        height: self.texture_size[1]

    Label:
        text: "Enter URL:"
        font_size: '16sp'
        color: (0, 0, 0, 1)  # Black text
        size_hint_y: None
        height: self.texture_size[1]

    TextInput:
        id: url_input
        hint_text: "https://www.example.com"
        multiline: False
        font_size: '16sp'
        background_color: (0.95, 0.95, 0.95, 1)  # Light gray background
        foreground_color: (0, 0, 0, 1)  # Black text

    Label:
        text: "Select Media Type:"
        font_size: '16sp'
        color: (0, 0, 0, 1)  # Black text
        size_hint_y: None
        height: self.texture_size[1]

    BoxLayout:
        orientation: 'horizontal'
        spacing: 10

        ToggleButton:
            id: radio_audio
            text: "Audio"
            group: 'media_type'
            state: 'down'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: radio_video
            text: "Video"
            group: 'media_type'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

    Label:
        text: "Select Video Quality:"
        font_size: '16sp'
        color: (0, 0, 0, 1)  # Black text
        size_hint_y: None
        height: self.texture_size[1]

    BoxLayout:
        orientation: 'horizontal'
        spacing: 10

        ToggleButton:
            id: quality_144
            text: "144p"
            group: 'quality'
            state: 'down'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: quality_240
            text: "240p"
            group: 'quality'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: quality_360
            text: "360p"
            group: 'quality'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: quality_480
            text: "480p"
            group: 'quality'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: quality_720
            text: "720p"
            group: 'quality'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

        ToggleButton:
            id: quality_1080
            text: "1080p"
            group: 'quality'
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1) if self.state == 'down' else (0.8, 0.8, 0.8, 1)
            background_normal: ''
            background_down: ''

    Label:
        text: "Save Location:"
        font_size: '16sp'
        color: (0, 0, 0, 1)  # Black text
        size_hint_y: None
        height: self.texture_size[1]

    BoxLayout:
        orientation: 'horizontal'
        spacing: 10

        TextInput:
            id: save_path
            hint_text: "/sdcard/Download/"
            multiline: False
            font_size: '16sp'
            background_color: (0.95, 0.95, 0.95, 1)  # Light gray background
            foreground_color: (0, 0, 0, 1)  # Black text

        Button:
            text: "Choose Location"
            font_size: '16sp'
            background_color: (0, 0.5, 1, 1)  # Blue button
            background_normal: ''
            on_release: app.open_file_chooser()

    ProgressBar:
        id: progress_bar
        max: 100
        value: 0
        size_hint_y: None
        height: 30
        background_color: (0.8, 0.8, 0.8, 1)  # Light gray background
        canvas.before:
            Color:
                rgba: (0, 0.5, 1, 1)  # Blue progress bar
            Rectangle:
                pos: self.pos
                size: self.size

    Label:
        id: progress_label
        text: "0%"
        font_size: '16sp'
        color: (0, 0, 0, 1)  # Black text
        size_hint_y: None
        height: self.texture_size[1]

    Button:
        text: "Start Download"
        font_size: '18sp'
        background_color: (0, 0.5, 1, 1)  # Blue button
        background_normal: ''
        on_release: app.start_download()
"""

class RootWidget(BoxLayout):
    pass

if __name__ == '__main__':
    app = DownloadApp()
    app.run()
