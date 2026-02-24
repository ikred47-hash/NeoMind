[app]
title = Unrestricted AI
package.name = unrestrictedai
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,onnx
version = 1.0

# --- PERFORMANCE REQUIREMENTS ---
# We include onnxruntime for NPU use and mediapipe for generation
requirements = python3, kivy, numpy, pillow, onnxruntime-android, mediapipe

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# --- HARDWARE & RAM ACCESS ---
# Permissions for your gallery and massive 32GB RAM pool
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.manifest.largeHeap = True
android.api = 33
android.ndk = 25b

# --- GRAPHICS ACCELERATION ---
# This forces the app to use the Adreno GPU/Hexagon NPU
p4a.branch = master
android.entrypoint = main.py
