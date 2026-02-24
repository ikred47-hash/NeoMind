from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
from kivy.core.window import Window
import os
import threading
import requests

# --- UNRESTRICTED BYPASS LOGIC ---
def dummy_pre_check(): return True
def dummy_analyse_content(): return False

class NeoMindApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        self.title = "NeoMind: Unrestricted AI"
        
        # Phone's public Download folder for easy manual access
        self.model_dir = "/sdcard/Download/NeoMind_Models/"
        if not os.path.exists(self.model_dir):
            try: os.makedirs(self.model_dir)
            except: pass

        root = BoxLayout(orientation='vertical', padding=20, spacing=15)
        root.add_widget(Label(text="NEOMIND AI SUITE", font_size='28sp', bold=True, size_hint_y=None, height=60))
        
        scroll = ScrollView()
        content = BoxLayout(orientation='vertical', size_hint_y=None, spacing=10)
        content.bind(minimum_height=content.setter('height'))

        # --- MODEL MANAGER (THE BRAIN DOWNLOADER) ---
        content.add_widget(Label(text="[ MODEL MANAGER ]", bold=True, color=(0, 0.8, 1, 1)))
        
        self.dl_status = Label(text="Model Status: Checking...", size_hint_y=None, height=40)
        content.add_widget(self.dl_status)

        self.dl_btn = Button(text="Download FaceSwap Brain (Inswapper)", size_hint_y=None, height=80)
        self.dl_btn.bind(on_press=self.start_download)
        content.add_widget(self.dl_btn)

        # --- FACE SWAP SECTION ---
        content.add_widget(Label(text="[ FACE MORPH STUDIO ]", bold=True, color=(1, 0.5, 0, 1)))
        swap_btn = Button(text="Start Face Swap (512x512 Boost)", size_hint_y=None, height=120, background_color=(0.5, 0, 0, 1))
        swap_btn.bind(on_press=self.swap)
        content.add_widget(swap_btn)

        self.status = Label(text="System Status: Operational", size_hint_y=None, height=50)
        content.add_widget(self.status)

        scroll.add_widget(content)
        root.add_widget(scroll)
        
        self.check_local_models()
        return root

    def check_local_models(self):
        target_file = os.path.join(self.model_dir, "inswapper_128.onnx")
        if os.path.exists(target_file):
            self.dl_status.text = "Brain is loaded and ready!"
            self.dl_btn.disabled = True
        else:
            self.dl_status.text = "Model missing. Tap to Download."

    def start_download(self, instance):
        self.dl_btn.disabled = True
        self.dl_status.text = "Connecting to Hugging Face..."
        threading.Thread(target=self.download_model, daemon=True).start()

    def download_model(self):
        url = "https://huggingface.co/ezioruan/inswapper_128.onnx/resolve/main/inswapper_128.onnx"
        filepath = os.path.join(self.model_dir, "inswapper_128.onnx")
        
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024 * 1024 # 1MB chunks
            count = 0
            
            with open(filepath, 'wb') as file:
                for data in response.iter_content(block_size):
                    file.write(data)
                    count += len(data)
                    percent = int((count / total_size) * 100) if total_size > 0 else 0
                    Clock.schedule_once(lambda dt, p=percent: self.set_dl_status(f"Downloading: {p}%"))
            
            Clock.schedule_once(lambda dt: self.download_complete(True))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self.download_complete(False, err))

    def set_dl_status(self, text):
        self.dl_status.text = text

    def download_complete(self, success, error=""):
        if success:
            self.dl_status.text = "Download complete! Brain is ready."
        else:
            self.dl_status.text = f"Download failed: {error}"
            self.dl_btn.disabled = False

    def swap(self, instance):
        target_file = os.path.join(self.model_dir, "inswapper_128.onnx")
        if not os.path.exists(target_file):
            self.status.text = "Error: Please download the model first!"
            return
        self.status.text = "Processing Swap (Unrestricted Mode)..."

if __name__ == '__main__':
    NeoMindApp().run()
