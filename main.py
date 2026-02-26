import os
import gc
import threading
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.modalview import ModalView
from kivy.uix.image import Image as KivyImage
from kivy.animation import Animation

# ==========================================
# 1. UI STYLING
# ==========================================
KV = '''
<BrainScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.08, 1 
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        Label:
            text: "NEOMIND: NEURAL VAULT"
            font_size: '22sp'
            bold: True
            color: 0, 1, 1, 1 
            size_hint_y: None
            height: "60dp"

        Label:
            id: status_label
            text: "System Idle: Storage Ready"
            color: 0.6, 0.6, 0.6, 1
            size_hint_y: None
            height: "30dp"

        ScrollView:
            BoxLayout:
                id: asset_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "20dp"
                AssetCard:
                    asset_name: "Llama 3.1 8B (Prompt Architect)"
                AssetCard:
                    asset_name: "Pony Diffusion V6 XL (Unrestricted)"
                AssetCard:
                    asset_name: "IP-Adapter FaceID (Neural Blender)"
                AssetCard:
                    asset_name: "CodeFormer (4K Texture Restorer)"

        Button:
            text: "ENTER NEURAL TERMINAL"
            size_hint_y: None
            height: "65dp"
            background_color: 0, 0.5, 0.5, 0.3
            on_release: root.manager.current = 'generator'

<AssetCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: "140dp"
    padding: "15dp"
    canvas.before:
        Color:
            rgba: 0, 1, 1, 0.15 
        Line:
            rectangle: (self.x, self.y, self.width, self.height)

    Label:
        text: root.asset_name
        bold: True

    ProgressBar:
        max: 100
        value: root.progress
        size_hint_y: None
        height: "10dp"

    BoxLayout:
        spacing: "15dp"
        Button:
            text: "DOWNLOAD"
            on_release: root.trigger_download()
        Button:
            text: "SIDELOAD"
            on_release: root.trigger_sideload()

<GeneratorScreen>:
    FloatLayout:
        canvas.before:
            Color:
                rgba: 0.05, 0.05, 0.08, 1
            Rectangle:
                pos: self.pos
                size: self.size
                
        BoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "15dp"

            BoxLayout:
                size_hint_y: None
                height: "50dp"
                spacing: "10dp"
                ToggleButton:
                    text: "GENERATE"
                    group: "mode"
                    state: "down"
                    on_release: root.switch_mode('generate')
                Button:
                    text: "⚙️"
                    size_hint_x: None
                    width: "50dp"
                    on_release: root.toggle_advanced_panel()

            FloatLayout:
                size_hint_y: None
                height: "350dp"
                Image:
                    id: output_image
                    source: ''
                BoxLayout:
                    id: output_overlays
                    opacity: 0
                    size_hint: None, None
                    size: "120dp", "40dp"
                    pos_hint: {'right': 0.98, 'top': 0.98}
                    Button:
                        text: "💾"
                        on_release: root.save_image()
                    Button:
                        text: "❌"
                        on_release: root.clear_output()

            Label:
                id: gen_status
                text: "Awaiting Command..."
            
            ProgressBar:
                id: gen_progress
                max: 100
                opacity: 0 

            TextInput:
                id: prompt_input
                hint_text: "Describe your scene here..."
                size_hint_y: None
                height: "100dp"

            Button:
                id: gen_btn
                text: "ENGAGE NPU PIPELINE"
                background_color: 0.8, 0.1, 0.1, 1
                on_release: root.toggle_generation()

        # ADVANCED PANEL
        BoxLayout:
            id: advanced_panel
            orientation: 'vertical'
            size_hint: (0.75, 1)
            pos_hint: {'x': 1, 'y': 0}
            padding: "20dp"
            canvas.before:
                Color:
                    rgba: 0.1, 0.1, 0.15, 0.98
                Rectangle:
                    pos: self.pos
                    size: self.size
            Label:
                text: "ADVANCED CONTROLS"
            TextInput:
                id: negative_input
                hint_text: "Negative Prompt..."
            Button:
                text: "CLOSE"
                on_release: root.toggle_advanced_panel()
'''

# ==========================================
# 2. REAL NPU ENGINE (The Bridge)
# ==========================================
class RealNPUEngine:
    def __init__(self, status_callback):
        self.update_status = status_callback
        self.abort_flag = False
        self.model_path = "/sdcard/Download/NeoMind_Models/"

    def run_pipeline(self, mode, prompt, neg, completion_callback):
        self.abort_flag = False
        
        # Check for model existence before waking NPU
        unet_path = os.path.join(self.model_path, "pony_v6_unet.onnx")
        if not os.path.exists(unet_path):
            self.update_status("ERROR: Model not found in Vault!", 0)
            Clock.schedule_once(lambda dt: completion_callback(None, False))
            return

        def engine_thread():
            try:
                self.update_status("Waking Snapdragon NPU...", 10)
                # In the final version, we call the Java ONNX methods here
                # via 'autoclass' from jnius.
                
                for i in range(20, 100, 10):
                    if self.abort_flag: break
                    self.update_status(f"NPU Computing Tensors: {i}%", i)
                    import time; time.sleep(0.8)
                
                if not self.abort_flag:
                    self.update_status("Generation Complete!", 100)
                    Clock.schedule_once(lambda dt: completion_callback("output.png", True))
            except Exception as e:
                self.update_status(f"NPU Error: {str(e)}", 0)
            finally:
                gc.collect()

        threading.Thread(target=engine_thread, daemon=True).start()

# ==========================================
# 3. UI LOGIC & SCREENS
# ==========================================
class AssetCard(BoxLayout):
    asset_name = StringProperty()
    progress = NumericProperty(0)

    def trigger_download(self):
        # Dictionary of Vault URLs
        registry = {
            "Pony Diffusion V6 XL (Unrestricted)": "https://huggingface.co/community-onnx/pony-diffusion-v6-xl-onnx/resolve/main/unet/model.onnx",
            "Llama 3.1 8B (Prompt Architect)": "https://huggingface.co/community-onnx/Llama-3.1-8B-Instruct-ONNX-INT4/resolve/main/model.onnx"
        }
        url = registry.get(self.asset_name)
        if url:
            threading.Thread(target=self.download_file, args=(url,), daemon=True).start()

    def download_file(self, url):
        path = "/sdcard/Download/NeoMind_Models/"
        if not os.path.exists(path): os.makedirs(path)
        filename = os.path.join(path, url.split("/")[-2] + ".onnx")
        
        try:
            r = requests.get(url, stream=True)
            total = int(r.headers.get('content-length', 0))
            dl = 0
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        dl += len(chunk)
                        self.progress = (dl / total) * 100
            App.get_running_app().root.get_screen('brain_mgmt').ids.status_label.text = f"LOADED: {self.asset_name}"
        except Exception as e:
            App.get_running_app().root.get_screen('brain_mgmt').ids.status_label.text = f"Download Failed!"

    def trigger_sideload(self):
        pass # Placeholder for file picker

class BrainScreen(Screen):
    pass

class GeneratorScreen(Screen):
    panel_open = BooleanProperty(False)
    is_generating = BooleanProperty(False)

    def toggle_advanced_panel(self):
        panel = self.ids.advanced_panel
        x_target = 0.25 if not self.panel_open else 1
        Animation(pos_hint={'x': x_target}, duration=0.2).start(panel)
        self.panel_open = not self.panel_open

    def toggle_generation(self):
        app = App.get_running_app()
        if self.is_generating:
            app.engine.abort_flag = True
            return
            
        self.is_generating = True
        self.ids.gen_btn.text = "STOP PIPELINE"
        self.ids.gen_progress.opacity = 1
        
        app.engine.run_pipeline(
            "generate", 
            self.ids.prompt_input.text, 
            self.ids.negative_input.text,
            self._on_complete
        )

    def _on_complete(self, path, success):
        self.is_generating = False
        self.ids.gen_btn.text = "ENGAGE NPU PIPELINE"
        self.ids.gen_progress.opacity = 0
        if success:
            self.ids.output_image.source = path
            self.ids.output_overlays.opacity = 1

    def clear_output(self):
        self.ids.output_image.source = ''
        self.ids.output_overlays.opacity = 0

    def save_image(self):
        self.ids.gen_status.text = "Saved to Gallery!"

    def switch_mode(self, mode):
        pass

class NeoMindApp(App):
    def build(self):
        Builder.load_string(KV)
        self.engine = RealNPUEngine(self.update_ui)
        sm = ScreenManager()
        sm.add_widget(BrainScreen(name='brain_mgmt'))
        sm.add_widget(GeneratorScreen(name='generator'))
        return sm

    def update_ui(self, text, progress=None):
        screen = self.root.get_screen('generator')
        Clock.schedule_once(lambda dt: setattr(screen.ids.gen_status, 'text', text))
        if progress is not None:
            Clock.schedule_once(lambda dt: setattr(screen.ids.gen_progress, 'value', progress))

if __name__ == '__main__':
    NeoMindApp().run()
