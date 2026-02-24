from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import os
import threading
import requests

class NeoMindApp(App):
    def build(self):
        self.title = "NeoMind AI"
        self.model_path = "/sdcard/Download/NeoMind_Models/inswapper_128.onnx"
        
        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        root.add_widget(Label(text="NEOMIND AI SUITE", font_size='28sp', bold=True, size_hint_y=None, height=60))
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        content.bind(minimum_height=content.setter('height'))

        # --- DOWNLOAD SECTION ---
        content.add_widget(Label(text="[ AI MODEL MANAGER ]", bold=True, color=(0, 0.8, 1, 1)))
        self.dl_status = Label(text="Checking for Brain File...", size_hint_y=None, height=40)
        content.add_widget(self.dl_status)

        self.dl_btn = Button(text="DOWNLOAD INSWAPPER (500MB)", size_hint_y=None, height=100)
        self.dl_btn.bind(on_press=self.start_download)
        content.add_widget(self.dl_btn)

        # --- AI ACTIONS ---
        content.add_widget(Label(text="[ NPU ACCELERATED ACTIONS ]", bold=True, color=(1, 0.5, 0, 1)))
        self.swap_btn = Button(text="START FACE SWAP (UNRESTRICTED)", size_hint_y=None, height=120, background_color=(0.5, 0, 0, 1))
        content.add_widget(self.swap_btn)

        scroll.add_widget(content)
        root.add_widget(scroll)
        return root

    def start_download(self, instance):
        self.dl_btn.disabled = True
        threading.Thread(target=self.download_logic, daemon=True).start()

    def download_logic(self):
        url = "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
        try:
            r = requests.get(url, stream=True)
            total = int(r.headers.get('content-length', 0))
            done = 0
            with open(self.model_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024*1024):
                    if chunk:
                        f.write(chunk)
                        done += len(chunk)
                        percent = int((done/total)*100)
                        Clock.schedule_once(lambda dt, p=percent: self.update_ui(f"Downloading: {p}%"))
            Clock.schedule_once(lambda dt: self.update_ui("SUCCESS: Brain Loaded!"))
        except Exception as e:
            Clock.schedule_once(lambda dt: self.update_ui(f"Error: {str(e)}"))

    def update_ui(self, text):
        self.dl_status.text = text

if __name__ == '__main__':
    NeoMindApp().run()
