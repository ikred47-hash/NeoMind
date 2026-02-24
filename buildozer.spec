[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Critical Python Libraries
requirements = python3, kivy==2.3.0, requests, urllib3, certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a

# Full permissions for the Brain folder
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.manifest.largeHeap = True

# API versions required for NPU Hardware Acceleration
android.api = 33
android.minapi = 24
android.ndk = 25b

# Snapdragon ONNX integration
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.22.0

# The Fixes: Forcing the correct Java wrapper
p4a.branch = master
android.bootstrap = sdl2
log_level = 2
