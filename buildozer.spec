[app]

title = CSOI Live Indicator
package.name = csoiliveindicator
package.domain = org.csoi

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json,txt
source.include_patterns = icons/*.png

version = 1.0

requirements = python3==3.11.6,kivy==2.3.0
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

orientation = portrait
fullscreen = 0

# Izin yang dibutuhkan aplikasi: akses internet (untuk konek ke ESP32-S3-CAM)
# dan status jaringan.
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# PENTING: aplikasi ini terhubung ke ESP32-S3-CAM lewat HTTP biasa (bukan
# HTTPS) di jaringan lokal/WiFi. Android modern (API 28+) memblokir koneksi
# HTTP secara default. Baris ini mengizinkan koneksi HTTP tetap berjalan.
android.manifest.uses_cleartext_traffic = True

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
