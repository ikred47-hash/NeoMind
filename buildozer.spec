[app]
title = NeoMind
package.name = neomind
package.domain = org.unrestricted
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# --- THE ENGINE UPDATE ---
# Added numpy, onnxruntime, and tokenizers to empower the NPU bridge
requirements = python3, kivy==2.3.0, requests, certifi, urllib3, pyjnius, numpy, onnxruntime, tokenizers

orientation = portrait
android.archs = arm64-v8a

# Storage Permissions for the 300GB Dedicated Vault
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# NPU and API specific targeting
android.api = 33
android.minapi = 24
android.ndk = 25b

# Java/Gradle bindings to wake the hardware acceleration
android.gradle_dependencies = com.microsoft.onnxruntime:onnxruntime-android:1.22.0
android.manifest.largeHeap = True
android.bootstrap = sdl2
