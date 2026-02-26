[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# FIXED: Version-locked requirements to prevent NumPy linker errors
requirements = python3, kivy==2.3.0, numpy==1.26.4, onnxruntime==1.17.0, tokenizers==0.15.2, requests, certifi, urllib3, pyjnius

orientation = portrait
android.archs = arm64-v8a
android.allow_backup = True

# Storage Permissions for the Dedicated Vault
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# NPU and API specific targeting
android.api = 33
android.minapi = 24
android.ndk = 25b
android.enable_androidx = True

# Java/Gradle bindings for hardware acceleration
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.17.0
android.manifest.largeHeap = True
android.bootstrap = sdl2
