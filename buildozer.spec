[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Added requests and urllib3 for the Brain Downloader
requirements = python3, kivy==2.3.0, numpy, pillow, requests, urllib3, certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Full permissions to read/write the downloaded models to /sdcard/
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.manifest.largeHeap = True
android.api = 33
android.ndk = 25b

# NPU Hardware Acceleration bridge
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.22.0

p4a.branch = master
android.entrypoint = main.py
log_level = 2
