[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,onnx,tflite
version = 1.0

# Critical AI Requirements
requirements = python3, kivy==2.3.0, numpy, pillow, onnxruntime-android, mediapipe

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Hardware & RAM Access
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.manifest.largeHeap = True
android.api = 33
android.ndk = 25b

# Performance settings
p4a.branch = master
android.entrypoint = main.py
log_level = 2
