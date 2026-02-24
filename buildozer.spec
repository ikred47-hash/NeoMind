[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Dependencies
requirements = python3, kivy==2.3.0, numpy, pillow, requests, urllib3, certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Hardware & RAM Access
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.manifest.largeHeap = True

# THE FIX: Bumping the minimum API to 24 for the NPU library
android.api = 33
android.minapi = 24
android.ndk = 25b

# NPU Hardware Acceleration bridge
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.22.0

p4a.branch = master
android.entrypoint = main.py
log_level = 2
