from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
import os

class NeoMindApp(App):
    def build(self):
        self.root = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.label = Label(text="NEOMIND SUITE\n[Status: Standby]", halign="center", font_size='20sp')
        self.root.add_widget(self.label)
        
        self.btn = Button(text="INITIALIZE SYSTEM", size_hint_y=None, height='100dp', background_color=(0, 0.5, 0, 1))
        self.btn.bind(on_press=self.setup_storage)
        self.root.add_widget(self.btn)
        return self.root

    def setup_storage(self, instance):
        # The public Downloads folder on your iQOO
        path = "/sdcard/Download/NeoMind_Models"
        try:
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            self.label.text = "SUCCESS!\nBrain Folder created in Downloads.\nReady for NPU Modules."
            self.label.color = (0, 1, 0, 1)
            self.btn.text = "SYSTEM ACTIVE"
            self.btn.disabled = True
        except Exception as e:
            self.label.text = f"CRITICAL ERROR:\n{str(e)}\n\nDid you grant 'All Files' permission?"
            self.label.color = (1, 0, 0, 1)

if __name__ == '__main__':
    NeoMindApp().run()
