import os
import time
import threading
import gc
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock
from kivy.utils import platform

# ==========================================
# 1. UI STYLING (Embedded KV String)
# ==========================================
KV = '''
<BrainScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.1, 1 
        Rectangle:
            pos: self.pos
            size: self.size

    BoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        Label:
            text: "NEOMIND: BRAIN MANAGEMENT"
            font_size: '24sp'
            bold: True
            color: 0, 1, 1, 1 
            size_hint_y: None
            height: "60dp"

        Label:
            id: status_label
            text: "System Idle: Dedicated 300GB Ready"
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: "30dp"

        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: asset_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "20dp"

                AssetCard:
                    asset_name: "Pony Diffusion V6 XL (Unrestricted Engine)"
                AssetCard:
                    asset_name: "IP-Adapter FaceID (Native Blending)"
                AssetCard:
                    asset_name: "Mistral-7B (Local Architect)"

        Button:
            text: "ENTER NEURAL TERMINAL"
            size_hint_y: None
            height: "60dp"
            background_color: 0.1, 0.1, 0.2, 1
            color: 0, 1, 1, 1
            bold: True
            on_release: root.manager.current = 'generator'

<AssetCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: "140dp"
    padding: "10dp"
    canvas.before:
        Color:
            rgba: 0, 1, 1, 0.2
        Line:
            width: 1.2
            rectangle: (self.x, self.y, self.width, self.height)

    Label:
        text: root.asset_name
        halign: 'left'
        text_size: self.size
        bold: True
        color: 1, 1, 1, 1

    ProgressBar:
        max: 100
        value: root.progress
        size_hint_y: None
        height: "15dp"

    BoxLayout:
        spacing: "10dp"
        size_hint_y: None
        height: "50dp"
        Button:
            text: "DOWNLOAD"
            background_color: 0.2, 0.6, 1, 1
            on_release: self.parent.parent.trigger_download()
        Button:
            text: "SIDELOAD"
            background_color: 0.2, 0.2, 0.3, 1
            on_release: self.parent.parent.trigger_sideload()

<GeneratorScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    BoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"
        
        Label:
            text: "NEOMIND: UNRESTRICTED TERMINAL"
            font_size: '22sp'
            bold: True
            color: 0, 1, 1, 1
            size_hint_y: None
            height: "40dp"
            
        # The space where your generated image will appear
        Image:
            id: output_image
            source: '' 
            allow_stretch: True
            keep_ratio: True
            canvas.before:
                Color:
                    rgba: 0.1, 0.1, 0.15, 1
                Rectangle:
                    pos: self.pos
                    size: self.size
                    
        Label:
            id: gen_status
            text: "Awaiting Command..."
            color: 0.5, 0.5, 0.5, 1
            size_hint_y: None
            height: "30dp"

        # Text input for your casual commands
        TextInput:
            id: prompt_input
            hint_text: "Describe your scene here..."
            multiline: True
            size_hint_y: None
            height: "100dp"
            background_color: 0.1, 0.1, 0.2, 1
            foreground_color: 0, 1, 1, 1
            cursor_color: 0, 1, 1, 1
            padding: ["10dp", "10dp"]

        Button:
            id: gen_btn
            text: "ENGAGE NPU"
            size_hint_y: None
            height: "60dp"
            background_color: 0.8, 0.1, 0.1, 1
            color: 1, 1, 1, 1
            bold: True
            on_release: root.start_generation()

        Button:
            text: "BACK TO BRAIN MANAGEMENT"
            size_hint_y: None
            height: "50dp"
            background_color: 0.2, 0.2, 0.3, 1
            on_release: root.manager.current = 'brain_mgmt'
'''

# ==========================================
# 2. THE UNRESTRICTED ENGINE (RAM MANAGER)
# ==========================================
class UnrestrictedEngine:
    def __init__(self, status_callback):
        self.update_status = status_callback
        self.llm_session = None
        self.image_session = None

    def process_request(self, raw_text, completion_callback):
        # Phase 1: LLM Translation
        self.update_status("Allocating RAM: Waking Mistral-7B...")
        self.llm_session = "Mock_LLM_Loaded"
        time.sleep(1)
        
        self.update_status("Architecting Master Prompt...")
        time.sleep(1.5)
        master_prompt = f"(masterpiece, 8k, highly detailed), {raw_text}, volumetric lighting"
        
        # Phase 2: RAM Flush (Protecting your 16GB limit)
        self.update_status("Command Processed. Flushing LLM from RAM...")
        self.llm_session = None
        gc.collect()
        time.sleep(0.5)

        # Phase 3: Image Generation via NPU
        self.update_status("Allocating RAM: Engaging Snapdragon NPU...")
        self.image_session = "Mock_SDXL_Loaded"
        time.sleep(1)
        
        self.update_status(f"Generating: {master_prompt[:30]}...")
        time.sleep(3) # Simulating heavy NPU workload
        
        # Phase 4: Final RAM Flush
        self.update_status("Image Complete. Flushing Generator from RAM...")
        self.image_session = None
        gc.collect()
        
        # Signal the UI that we are done
        Clock.schedule_once(lambda dt: completion_callback())

# ==========================================
# 3. BACKEND LOGIC (Downloads & Storage)
# ==========================================
class BrainManagerLogic:
    def __init__(self, status_label):
        self.status_label = status_label
        self.brain_path = "/sdcard/Download/NeoMind_Models/"
        try:
            if not os.path.exists(self.brain_path):
                os.makedirs(self.brain_path)
        except Exception as e:
            self._update_status(f"Storage Error: {str(e)}")

    def download_model(self, name, url, progress_callback):
        self._update_status(f"Connecting to {name}...")
        threading.Thread(target=self._run_download, args=(name, url, progress_callback), daemon=True).start()

    def _run_download(self, name, url, progress_callback):
        try:
            response = requests.get(url, stream=True, verify=False)
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            
            safe_name = name.split(" ")[0] + ".safetensors"
            path = os.path.join(self.brain_path, safe_name)
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        if total_size > 0:
                            progress = (bytes_downloaded / total_size) * 100
                            Clock.schedule_once(lambda dt, p=progress: progress_callback(p))
            
            Clock.schedule_once(lambda dt: self._update_status(f"LOADED: {name}"))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._update_status(f"ERROR: {err}"))

    def _update_status(self, text):
        if self.status_label:
            self.status_label.text = text

# ==========================================
# 4. UI COMPONENTS (Card Logic)
# ==========================================
class AssetCard(BoxLayout):
    asset_name = StringProperty()
    progress = NumericProperty(0)

    def trigger_download(self):
        url = "https://huggingface.co/dummy_link_for_now" 
        app = App.get_running_app()
        if app.brain_logic:
            app.brain_logic.download_model(self.asset_name, url, self.update_progress)

    def update_progress(self, val):
        self.progress = val

    def trigger_sideload(self):
        app = App.get_running_app()
        try:
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("*/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            PythonActivity.mActivity.startActivityForResult(intent, 102)
            app.brain_logic._update_status("Opening Device Storage...")
        except Exception as e:
            if app.brain_logic:
                app.brain_logic._update_status("Sideload only works on Android Device")

# ==========================================
# 5. APP & SCREEN ROUTING
# ==========================================
class BrainScreen(Screen):
    pass

class GeneratorScreen(Screen):
    def start_generation(self):
        prompt_text = self.ids.prompt_input.text
        if not prompt_text.strip():
            self.ids.gen_status.text = "Error: Please describe a scene first."
            self.ids.gen_status.color = (1, 0, 0, 1)
            return

        self.ids.gen_btn.disabled = True
        self.ids.gen_btn.text = "PROCESSING..."
        
        # Pass the request to our Engine in a background thread
        app = App.get_running_app()
        threading.Thread(
            target=app.ai_engine.process_request, 
            args=(prompt_text, self._on_generation_complete), 
            daemon=True
        ).start()

    def _on_generation_complete(self):
        self.ids.gen_status.text = "Generation Complete."
        self.ids.gen_status.color = (0, 1, 0, 1)
        self.ids.gen_btn.disabled = False
        self.ids.gen_btn.text = "ENGAGE NPU"

class NeoMindApp(App):
    def build(self):
        self.title = "NeoMind Unrestricted Suite"
        self.brain_logic = None 
        self.ai_engine = None
        
        Builder.load_string(KV)
        
        sm = ScreenManager()
        sm.add_widget(BrainScreen(name='brain_mgmt'))
        sm.add_widget(GeneratorScreen(name='generator'))
        
        Clock.schedule_once(self._init_logic)
        return sm

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])

    def _init_logic(self, dt):
        screen = self.root.get_screen('brain_mgmt')
        status_lbl = screen.ids.status_label
        
        self.brain_logic = BrainManagerLogic(status_lbl)
        
        # Link the Generator UI's status label to the AI Engine
        gen_screen = self.root.get_screen('generator')
        gen_status_lbl = gen_screen.ids.gen_status
        
        def update_gen_ui(text):
            # Safely update the UI from the background thread
            Clock.schedule_once(lambda dt: setattr(gen_status_lbl, 'text', text))
            
        self.ai_engine = UnrestrictedEngine(update_gen_ui)

if __name__ == '__main__':
    NeoMindApp().run()
