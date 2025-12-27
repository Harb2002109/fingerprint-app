[app]
title = Fingerprint Auth App
package.name = fingerprintauth
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy,plyer,sqlalchemy
orientation = portrait
fullscreen = 0
android.permissions = USE_BIOMETRIC,USE_FINGERPRINT
android.api = 30
android.minapi = 23
android.ndk = 25b
