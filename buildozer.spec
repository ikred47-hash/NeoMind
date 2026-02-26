[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Added pyjnius for the Android Sideload File Picker
requirements = python3, kivy==2.3.0, requests, certifi, urllib3, pyjnius

orientation = portrait
android.archs = arm64-v8a

# Critical Permissions for your 300GB Dedicated Storage
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# API limits adjusted to support ONNX NPU Acceleration
android.api = 33
android.minapi = 24
android.ndk = 25b

# Hardware Acceleration via Gradle
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.22.0
android.manifest.largeHeap = True
android.bootstrap = sdl2
