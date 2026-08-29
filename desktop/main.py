#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
غلاف سطح المكتب لتطبيق مسارات — يشغّل خادم Flask داخلياً
ويعرضه بنافذة تطبيق حقيقية (بدون متصفح خارجي) عبر pywebview.

يُستخدم هذا الملف كنقطة الدخول عند البناء بـ PyInstaller لوندوز/لينكس.
"""

import os
import sys
import threading
import time

# يضيف مجلد app/ لمسار الاستيراد (يعمل بنفس الشكل من المصدر ومن الملف المبني)
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS  # مجلد الملفات المرفقة داخل الملف التنفيذي (PyInstaller)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

APP_DIR = os.path.join(BASE_DIR, "app")
sys.path.insert(0, APP_DIR)

os.chdir(APP_DIR)  # عشان Flask يلقى templates/ و static/ بشكل صحيح

# إذا كان ffmpeg مرفق جوا الحزمة (ffmpeg_bin/) نستخدمه، وإلا نعتمد على النظام
_bundled_ffmpeg = os.path.join(
    BASE_DIR, "ffmpeg_bin", "ffmpeg.exe" if sys.platform == "win32" else "ffmpeg"
)
if os.path.isfile(_bundled_ffmpeg):
    os.environ["MASARAT_FFMPEG_PATH"] = _bundled_ffmpeg

import webview  # noqa: E402
from app import app as flask_app, APP_NAME, get_download_dir  # noqa: E402


def run_flask():
    flask_app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


def main():
    t = threading.Thread(target=run_flask, daemon=True)
    t.start()
    time.sleep(0.6)  # مهلة بسيطة لضمان جاهزية الخادم قبل فتح النافذة

    icon_path = os.path.join(APP_DIR, "static", "logo.png")
    window_kwargs = dict(
        title=APP_NAME,
        url="http://127.0.0.1:5000",
        width=480,
        height=800,
        min_size=(380, 600),
    )
    webview.create_window(**window_kwargs)
    webview.start()


if __name__ == "__main__":
    main()
