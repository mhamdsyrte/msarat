[app]
title = مسارات
package.name = masarat
package.domain = com.hamziwypy

# main.py هنا + مجلد app/ (نسخة مطابقة لـ /app بالمشروع، شوف ملاحظة بـ README)
source.dir = .
source.include_exts = py,png,jpg,jpg,svg,html,css,js,json,ttf
source.include_patterns = app/templates/*,app/static/*,ffmpeg_bin/*

version = 2.0.0

# مهم: bootstrap=webview يخلي p4a يعرض تطبيق الويب بمكوّن WebView أندرويد
# بدل الحاجة لكتابة واجهة Kivy من الصفر
p4a.bootstrap = webview

requirements = python3,flask,yt-dlp,certifi,mutagen,brotli,websockets

orientation = portrait
fullscreen = 0

icon.filename = icon.png
presplash.filename = icon.png

android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# targetSdk=28 عن قصد: أندرويد 11+ يمنع الكتابة المباشرة بمجلد Downloads
# المشترك (scoped storage) إلا لو التطبيق يستهدف API<=28 (سلوك قديم مسموح
# للتطبيقات المُثبّتة يدوياً خارج المتجر). لو رفعت الرقم لازم تضيف
# MANAGE_EXTERNAL_STORAGE + شاشة طلب صلاحية خاصة.
android.api = 28
android.minapi = 24
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
