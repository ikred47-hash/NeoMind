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
from kivy.core.window import Window

# Magic Bullet for Android Keyboards
Window.softinput_mode = 'below_target' 

# ==========================================
# 1. UI STYLING (Embedded KV String)
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
            halign: 'center'
            valign: 'middle'

        Label:
            id: status_label
            text: "System Idle: Dedicated Storage Ready"
            color: 0.6, 0.6, 0.6, 1
            font_size: '14sp'
            size_hint_y: None
            height: "30dp"
            text_size: self.size
            halign: 'center'

        ScrollView:
            do_scroll_x: False
            BoxLayout:
                id: asset_list
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                spacing: "20dp"
                padding: [0, 10, 0, 10]

                # The Absolute Peak Asset Roster
                AssetCard:
                    asset_name: "Llama 3.1 8B (Prompt Architect)"
                AssetCard:
                    asset_name: "Pony Diffusion V6 XL (Unrestricted)"
                AssetCard:
                    asset_name: "FLUX.1 Quantized (Experimental SOTA)"
                AssetCard:
                    asset_name: "IP-Adapter FaceID (Neural Blender)"
                AssetCard:
                    asset_name: "CodeFormer (4K Texture Restorer)"

        Button:
            text: "ENTER NEURAL TERMINAL"
            size_hint_y: None
            height: "65dp"
            background_normal: ''
            background_color: 0, 0.5, 0.5, 0.3
            color: 0, 1, 1, 1
            bold: True
            font_size: '16sp'
            on_release: root.manager.current = 'generator'

<AssetCard>:
    orientation: 'vertical'
    size_hint_y: None
    height: "140dp"
    padding: "15dp"
    spacing: "5dp"
    canvas.before:
        Color:
            rgba: 0, 1, 1, 0.15 
        Line:
            width: 1.2
            rectangle: (self.x, self.y, self.width, self.height)

    Label:
        text: root.asset_name
        halign: 'left'
        valign: 'middle'
        text_size: self.size
        bold: True
        color: 0.9, 0.9, 0.9, 1

    ProgressBar:
        max: 100
        value: root.progress
        size_hint_y: None
        height: "10dp"

    BoxLayout:
        spacing: "15dp"
        size_hint_y: None
        height: "45dp"
        Button:
            text: "DOWNLOAD"
            background_normal: ''
            background_color: 0.1, 0.4, 0.8, 1
            bold: True
            on_release: self.parent.parent.trigger_download()
        Button:
            text: "SIDELOAD"
            background_normal: ''
            background_color: 0.2, 0.2, 0.25, 1
            bold: True
            on_release: self.parent.parent.trigger_sideload()

<GeneratorScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.08, 1
        Rectangle:
            pos: self.pos
            size: self.size
            
    ScrollView:
        do_scroll_x: False
        BoxLayout:
            orientation: 'vertical'
            padding: "20dp"
            spacing: "15dp"
            size_hint_y: None
            height: self.minimum_height 
            
            # --- THE DYNAMIC MODE SELECTOR ---
            BoxLayout:
                size_hint_y: None
                height: "50dp"
                spacing: "5dp"
                
                ToggleButton:
                    text: "GENERATE"
                    group: "mode"
                    state: "down"
                    background_normal: ''
                    background_color: (0, 0.5, 0.5, 1) if self.state == 'down' else (0.1, 0.1, 0.15, 1)
                    bold: True
                    on_release: root.switch_mode('generate')
                    
                ToggleButton:
                    text: "FACE SWAP"
                    group: "mode"
                    background_normal: ''
                    background_color: (0, 0.5, 0.5, 1) if self.state == 'down' else (0.1, 0.1, 0.15, 1)
                    bold: True
                    on_release: root.switch_mode('swap')
                    
                ToggleButton:
                    text: "AI EDIT"
                    group: "mode"
                    background_normal: ''
                    background_color: (0, 0.5, 0.5, 1) if self.state == 'down' else (0.1, 0.1, 0.15, 1)
                    bold: True
                    on_release: root.switch_mode('edit')

            # Image Display Area
            BoxLayout:
                size_hint_y: None
                height: "350dp"
                padding: "2dp"
                canvas.before:
                    Color:
                        rgba: 0.2, 0.2, 0.25, 1 
                    Line:
                        width: 1
                        rectangle: (self.x, self.y, self.width, self.height)
                    Color:
                        rgba: 0.08, 0.08, 0.1, 1 
                    Rectangle:
                        pos: self.x+2, self.y+2
                        size: self.width-4, self.height-4
                Image:
                    id: output_image
                    source: '' 
                    allow_stretch: True
                    keep_ratio: True
            
            Button:
                id: save_btn
                text: "SAVE TO DEVICE GALLERY"
                size_hint_y: None
                height: "50dp"
                background_normal: ''
                background_color: 0, 0.7, 0.3, 1
                color: 1, 1, 1, 1
                bold: True
                opacity: 0
                disabled: True
                on_release: root.save_image()

            Label:
                id: gen_status
                text: "Awaiting Command..."
                color: 0.6, 0.6, 0.6, 1
                size_hint_y: None
                height: "30dp"
                bold: True

            ProgressBar:
                id: gen_progress
                max: 100
                value: 0
                size_hint_y: None
                height: "15dp"
                opacity: 0 

            # --- DYNAMIC INPUT PANELS ---
            
            # Panel for Face Swap & Edit Image Selection
            BoxLayout:
                id: upload_panel
                orientation: 'horizontal'
                size_hint_y: None
                height: "0dp" 
                opacity: 0
                spacing: "10dp"
                
                Button:
                    id: btn_upload_1
                    text: "Upload Source"
                    background_normal: ''
                    background_color: 0.2, 0.2, 0.3, 1
                    on_release: root.open_gallery('source')
                    
                Button:
                    id: btn_upload_2
                    text: "Upload Target"
                    background_normal: ''
                    background_color: 0.2, 0.2, 0.3, 1
                    on_release: root.open_gallery('target')

            # Text Input Panel
            TextInput:
                id: prompt_input
                hint_text: "Describe your scene here..."
                multiline: True
                size_hint_y: None
                height: "120dp" 
                background_color: 0.15, 0.15, 0.2, 1
                foreground_color: 0, 1, 1, 1
                cursor_color: 0, 1, 1, 1
                padding: ["12dp", "12dp"]
                font_size: '15sp'

            Button:
                id: gen_btn
                text: "ENGAGE NPU PIPELINE"
                size_hint_y: None
                height: "65dp"
                background_normal: ''
                background_color: 0.8, 0.1, 0.1, 1
                color: 1, 1, 1, 1
                bold: True
                font_size: '18sp'
                on_release: root.start_generation()

            Button:
                text: "ACCESS NEURAL VAULT"
                size_hint_y: None
                height: "50dp"
                background_normal: ''
                background_color: 0.2, 0.2, 0.25, 1
                bold: True
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

    def process_request(self, current_mode, raw_text, source_img, target_img, completion_callback):
        self.update_status(f"Pipeline Initiated: {current_mode.upper()} MODE", 5)
        time.sleep(1)

        self.update_status("Allocating RAM: Waking Llama 3.1 8B...", 15)
        self.llm_session = "Mock_LLM_Loaded"
        time.sleep(1)
        
        self.update_status("LLM Architecting NPU Instructions...", 25)
        time.sleep(1.5)
        
        self.update_status("Analysis Complete. Flushing LLM from RAM...", 35)
        self.llm_session = None
        gc.collect()
        time.sleep(0.5)

        self.update_status(f"NPU Waking... Loading Main Checkpoints", 50)
        self.image_session = "Mock_SDXL_Loaded"
        time.sleep(1)
        
        for i in range(60, 100, 10):
            self.update_status(f"NPU Rendering Tensor Step {i//10}/10...", i)
            time.sleep(0.5) 
        
        self.update_status("Process Complete. Flushing Memory...", 100)
        self.image_session = None
        gc.collect()
        
        Clock.schedule_once(lambda dt: completion_callback())

# ==========================================
# 3. BACKEND LOGIC (Downloads & Storage)
# ==========================================
class BrainManagerLogic:
    def __init__(self, status_label):
        self.status_label = status_label
        self.brain_path = self.get_safe_storage_path()
        try:
            if not os.path.exists(self.brain_path):
                os.makedirs(self.brain_path)
        except Exception as e:
            self._update_status(f"Storage Error: {str(e)}")

    def get_safe_storage_path(self):
        if platform == 'android':
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            context = PythonActivity.mActivity
            external_dir = context.getExternalFilesDir(None)
            if external_dir:
                return os.path.join(external_dir.getAbsolutePath(), "NeoMind_Models")
        return os.path.join(os.path.expanduser("~"), "NeoMind_Models")

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
                app.brain_logic._update_status("Sideload only works on Android")

# ==========================================
# 5. APP & SCREEN ROUTING
# ==========================================
class BrainScreen(Screen):
    pass

class GeneratorScreen(Screen):
    current_mode = StringProperty('generate')
    
    # Track the active image paths in memory
    source_img_uri = StringProperty("")
    target_img_uri = StringProperty("")
    active_picker = StringProperty("")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind Kivy's Android activity listener to catch the gallery selection
        if platform == 'android':
            from android import activity
            activity.bind(on_activity_result=self.on_activity_result)

    def switch_mode(self, mode):
        self.current_mode = mode
        upload_panel = self.ids.upload_panel
        prompt_input = self.ids.prompt_input
        btn_1 = self.ids.btn_upload_1
        btn_2 = self.ids.btn_upload_2

        # Reset image paths when switching modes
        self.source_img_uri = ""
        self.target_img_uri = ""
        btn_1.text = "Upload Source"
        btn_1.background_color = (0.2, 0.2, 0.3, 1)
        btn_2.text = "Upload Target"
        btn_2.background_color = (0.2, 0.2, 0.3, 1)

        if mode == 'generate':
            upload_panel.height = "0dp"
            upload_panel.opacity = 0
            prompt_input.height = "120dp"
            prompt_input.opacity = 1
            prompt_input.hint_text = "Describe your scene here (Unrestricted)..."
            
        elif mode == 'swap':
            upload_panel.height = "60dp"
            upload_panel.opacity = 1
            btn_1.text = "Upload Source Face"
            btn_2.text = "Upload Target Body"
            btn_2.opacity = 1
            prompt_input.height = "0dp" 
            prompt_input.opacity = 0
            
        elif mode == 'edit':
            upload_panel.height = "60dp"
            upload_panel.opacity = 1
            btn_1.text = "Upload Base Image"
            btn_2.opacity = 0 
            prompt_input.height = "80dp"
            prompt_input.opacity = 1
            prompt_input.hint_text = "What do you want to change? (e.g., make the armor black)"

    def open_gallery(self, picker_type):
        self.active_picker = picker_type
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            # Create intent strictly for image files
            intent = Intent(Intent.ACTION_GET_CONTENT)
            intent.setType("image/*")
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            
            # Fire the intent and wait for on_activity_result (Request Code 103)
            PythonActivity.mActivity.startActivityForResult(intent, 103)
        else:
            self.ids.gen_status.text = "Gallery access requires Android device."

    def on_activity_result(self, request_code, result_code, intent):
        # 103 is our custom request code for the image picker
        if request_code == 103:
            if result_code == -1 and intent is not None: # -1 means RESULT_OK in Android
                uri = intent.getDataString()
                if uri:
                    Clock.schedule_once(lambda dt: self._update_image_button(uri))

    def _update_image_button(self, uri):
        if self.active_picker == 'source':
            self.source_img_uri = uri
            self.ids.btn_upload_1.text = "Face Loaded ✓"
            self.ids.btn_upload_1.background_color = (0, 0.6, 0.3, 1) # Green for success
        elif self.active_picker == 'target':
            self.target_img_uri = uri
            self.ids.btn_upload_2.text = "Body Loaded ✓"
            self.ids.btn_upload_2.background_color = (0, 0.6, 0.3, 1)

    def start_generation(self):
        prompt_text = self.ids.prompt_input.text
        
        # Validation checks
        if self.current_mode in ['generate', 'edit'] and not prompt_text.strip():
            self.ids.gen_status.text = "Error: Text input required for this mode."
            self.ids.gen_status.color = (1, 0.3, 0.3, 1)
            return
            
        if self.current_mode == 'swap' and (not self.source_img_uri or not self.target_img_uri):
            self.ids.gen_status.text = "Error: Both Face and Body images required."
            self.ids.gen_status.color = (1, 0.3, 0.3, 1)
            return

        self.ids.gen_btn.disabled = True
        self.ids.gen_btn.text = "PROCESSING (NPU ENGAGED)..."
        self.ids.gen_btn.background_color = (0.5, 0.1, 0.1, 1)
        self.ids.save_btn.opacity = 0
        self.ids.save_btn.disabled = True
        self.ids.gen_progress.opacity = 1
        self.ids.gen_progress.value = 0
        
        app = App.get_running_app()
        threading.Thread(
            target=app.ai_engine.process_request, 
            args=(
                self.current_mode, 
                prompt_text, 
                self.source_img_uri, 
                self.target_img_uri, 
                self._on_generation_complete
            ), 
            daemon=True
        ).start()

    def _on_generation_complete(self):
        self.ids.gen_status.text = "Pipeline Complete."
        self.ids.gen_status.color = (0, 1, 0, 1)
        self.ids.gen_btn.disabled = False
        self.ids.gen_btn.text = "ENGAGE NPU PIPELINE"
        self.ids.gen_btn.background_color = (0.8, 0.1, 0.1, 1)
        self.ids.save_btn.opacity = 1
        self.ids.save_btn.disabled = False
        self.ids.gen_progress.opacity = 0

    def save_image(self):
        self.ids.gen_status.text = "Image Saved to Device Gallery."
        self.ids.gen_status.color = (0, 1, 1, 1)

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
        
        gen_screen = self.root.get_screen('generator')
        gen_status_lbl = gen_screen.ids.gen_status
        gen_progress_bar = gen_screen.ids.gen_progress
        
        def update_gen_ui(text, progress=None):
            Clock.schedule_once(lambda dt: setattr(gen_status_lbl, 'text', text))
            if progress is not None:
                Clock.schedule_once(lambda dt: setattr(gen_progress_bar, 'value', progress))
            
        self.ai_engine = UnrestrictedEngine(update_gen_ui)

if __name__ == '__main__':
    NeoMindApp().run()
