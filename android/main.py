#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نقطة الدخول لنسخة أندرويد — تُبنى عبر buildozer باستخدام bootstrap = webview
(هذا يخلي python-for-android يعرض تطبيق الويب مباشرة بمكوّن WebView بدون
الحاجة لكتابة كود Kivy). يشغّل هذا الملف خادم Flask، ثم p4a webview
يفتح http://127.0.0.1:5000 تلقائياً.

⚠️ ملاحظة مهمة عن ffmpeg على أندرويد:
python-for-android ما يوفر ffmpeg افتراضياً. لازم ترفق ثنائي ffmpeg الثابت
لمعمارية أندرويد (arm64-v8a / armeabi-v7a) داخل مجلد android/ffmpeg_bin/
قبل البناء (شوف android/README.md للتفاصيل)، أو تستخدم مكتبة
ffmpeg-kit-android كبديل أكثر ثباتاً (يحتاج تعديل بايثون-جافا bridge).
بدون ffmpeg، تحميل الفيديو مع الصوت بجودة عالية (تحتاج دمج) لن يعمل —
بس تحميل صيغ فيها فيديو+صوت بملف واحد (progressive) هيشتغل بدون مشاكل.
"""

import os
import sys
import threading

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APP_DIR = os.path.join(BASE_DIR, "app")
sys.path.insert(0, APP_DIR)
os.chdir(APP_DIR)

# مسار ffmpeg المرفق (إن وُجد) — شوف ملاحظة الأعلى
_bundled_ffmpeg = os.path.join(BASE_DIR, "ffmpeg_bin", "ffmpeg")
if os.path.isfile(_bundled_ffmpeg):
    os.environ["MASARAT_FFMPEG_PATH"] = _bundled_ffmpeg
    os.chmod(_bundled_ffmpeg, 0o755)

# مجلد التنزيلات على أندرويد (Termux-style path لا ينطبق هنا؛ p4a يعطينا صلاحية
# WRITE_EXTERNAL_STORAGE وتقدر تحدد المسار من داخل التطبيق عبر الإعدادات ⚙️)
os.environ.setdefault(
    "ANDROID_DOWNLOAD_DIR",
    "/storage/emulated/0/Download/Masarat",
)

from app import app as flask_app  # noqa: E402


def run():
    flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":
    threading.Thread(target=run, daemon=True).start()
    # p4a webview bootstrap يراقب المنفذ 5000 ويفتحه تلقائياً بعد إقلاع الخدمة
    while True:
        pass
