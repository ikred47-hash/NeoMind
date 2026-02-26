import os
import threading
import requests
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty, NumericProperty
from kivy.clock import Clock

# ==========================================
# 1. UI STYLING (Embedded KV String)
# ==========================================
KV = '''
<BrainScreen>:
    canvas.before:
        Color:
            rgba: 0.05, 0.05, 0.1, 1 # Deep dark blue/Cyberpunk background
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
            color: 0, 1, 1, 1 # Cyan Neon
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

                # Your core No-Refusal assets
                AssetCard:
                    asset_name: "Pony Diffusion V6 XL (Unrestricted)"
                AssetCard:
                    asset_name: "Inswapper 128 (Identity)"
                AssetCard:
                    asset_name: "RealVisXL V4.0 (Photo-Real)"
                AssetCard:
                    asset_name: "Mistral-7B (Local Architect)"

        Button:
            text: "GO TO GENERATOR"
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
        Label:
            text: "Unrestricted Generator UI\\n(Pending Implementation)"
            color: 0, 1, 1, 1
            bold: True
            text_size: self.size
            halign: 'center'
            valign: 'middle'
        Button:
            text: "BACK TO BRAIN MANAGEMENT"
            size_hint_y: None
            height: "60dp"
            background_color: 0.1, 0.1, 0.2, 1
            on_release: root.manager.current = 'brain_mgmt'
'''

# ==========================================
# 2. BACKEND LOGIC (Downloads & Storage)
# ==========================================
class BrainManagerLogic:
    def __init__(self, status_label):
        self.status_label = status_label
        # Targeted directly at your iQOO Neo 10 internal storage
        self.brain_path = "/sdcard/NeoMind/Models/"
        try:
            if not os.path.exists(self.brain_path):
                os.makedirs(self.brain_path)
        except Exception as e:
            self._update_status(f"Storage Error: Check Permissions")

    def download_model(self, name, url, progress_callback):
        self._update_status(f"Connecting to {name}...")
        # Uses threading so the UI doesn't freeze or "squash" during download
        threading.Thread(target=self._run_download, args=(name, url, progress_callback), daemon=True).start()

    def _run_download(self, name, url, progress_callback):
        try:
            response = requests.get(url, stream=True, verify=False)
            total_size = int(response.headers.get('content-length', 0))
            bytes_downloaded = 0
            
            # Formats the name to a valid filename
            safe_name = name.split(" ")[0] + ".safetensors"
            path = os.path.join(self.brain_path, safe_name)
            
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bytes_downloaded += len(chunk)
                        if total_size > 0:
                            progress = (bytes_downloaded / total_size) * 100
                            # Schedule Kivy UI updates on the main thread
                            Clock.schedule_once(lambda dt, p=progress: progress_callback(p))
            
            Clock.schedule_once(lambda dt: self._update_status(f"LOADED: {name}"))
        except Exception as e:
            Clock.schedule_once(lambda dt, err=str(e): self._update_status(f"ERROR: {err}"))

    def _update_status(self, text):
        if self.status_label:
            self.status_label.text = text

# ==========================================
# 3. UI COMPONENTS (Card Logic)
# ==========================================
class AssetCard(BoxLayout):
    asset_name = StringProperty()
    progress = NumericProperty(0)

    def trigger_download(self):
        # Placeholder HuggingFace link structure - we will update these later
        url = "https://huggingface.co/dummy_link_for_now" 
        app = App.get_running_app()
        if app.brain_logic:
            app.brain_logic.download_model(self.asset_name, url, self.update_progress)

    def update_progress(self, val):
        self.progress = val

    def trigger_sideload(self):
        # Native Android Picker call (Requires pyjnius in buildozer.spec)
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
# 4. APP & SCREEN ROUTING
# ==========================================
class BrainScreen(Screen):
    pass

class GeneratorScreen(Screen):
    pass

class NeoMindApp(App):
    def build(self):
        self.title = "NeoMind Unrestricted Suite"
        self.brain_logic = None 
        
        # Load the KV string layout
        Builder.load_string(KV)
        
        # Setup Screen Manager
        sm = ScreenManager()
        sm.add_widget(BrainScreen(name='brain_mgmt'))
        sm.add_widget(GeneratorScreen(name='generator'))
        
        # Initialize the backend logic after the UI is built
        Clock.schedule_once(self._init_logic)
        return sm

    def _init_logic(self, dt):
        # Find the status label in the BrainScreen to update it during downloads
        screen = self.root.get_screen('brain_mgmt')
        status_lbl = screen.ids.status_label
        self.brain_logic = BrainManagerLogic(status_lbl)

if __name__ == '__main__':
    NeoMindApp().run()
