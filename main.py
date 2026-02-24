from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import Image
from kivy.clock import Clock
import os

class NeoMindApp(App):
    def build(self):
        self.title = "NeoMind AI Suite"
        # The file you already downloaded
        self.model_path = "/sdcard/Download/NeoMind_Models/inswapper_128.onnx"
        
        # Main Layout with proper spacing
        root = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Header
        root.add_widget(Label(text="NEOMIND AI SUITE", font_size='32sp', bold=True, size_hint_y=None, height=100))
        
        # Status Area
        self.status = Label(text="Brain Loaded: Ready to Swap", color=(0, 1, 0, 1), size_hint_y=None, height=50)
        root.add_widget(self.status)

        # Action Buttons
        btn_layout = BoxLayout(orientation='vertical', spacing=15)
        
        self.btn_src = Button(text="SELECT SOURCE FACE", size_hint_y=None, height=120, background_color=(0.2, 0.6, 1, 1))
        self.btn_src.bind(on_press=self.select_source)
        btn_layout.add_widget(self.btn_src)

        self.btn_tgt = Button(text="SELECT TARGET IMAGE", size_hint_y=None, height=120, background_color=(0.2, 0.6, 1, 1))
        self.btn_tgt.bind(on_press=self.select_target)
        btn_layout.add_widget(self.btn_tgt)

        self.swap_btn = Button(text="START FACE SWAP", size_hint_y=None, height=150, background_color=(0.8, 0.1, 0.1, 1), bold=True)
        self.swap_btn.bind(on_press=self.run_swap)
        btn_layout.add_widget(self.swap_btn)

        root.add_widget(btn_layout)
        
        # Preview Placeholder
        self.preview = Label(text="Image Previews will appear here")
        root.add_widget(self.preview)

        return root

    def select_source(self, instance):
        self.status.text = "Opening Gallery for Source..."
        # Logic for Android Gallery picker goes here next

    def select_target(self, instance):
        self.status.text = "Opening Gallery for Target..."

    def run_swap(self, instance):
        if not os.path.exists(self.model_path):
            self.status.text = "ERROR: Model file missing!"
            return
        self.status.text = "SWAPPING... (NPU ACCELERATED)"
        # This is where we call the ONNX runtime

if __name__ == '__main__':
    NeoMindApp().run()
