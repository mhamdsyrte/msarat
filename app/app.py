#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مسارات (مسارات) — أداة محلية لفحص وتحميل فيديوهات وقوائم تشغيل يوتيوب

تعرض كل الصيغ المتوفرة لأي رابط يوتيوب: جودات الفيديو، مسارات الصوت
(الأصلي + كل الدبلجات المتوفرة)، الترجمات (الرسمية والتلقائية)،
والصورة المصغرة — وتحمّل الاختيار مباشرة لمجلد التحميلات بالجهاز.
تدعم أيضاً تحميل قوائم التشغيل كاملة مع اختيار جودة ولغة صوت مفضّلة.

التشغيل:
    pip install yt-dlp flask --break-system-packages
    python app.py
    افتح المتصفح على: http://127.0.0.1:5000
"""

import json
import os
import shutil
import threading
import uuid

from flask import Flask, render_template, request, jsonify

try:
    import yt_dlp
except ImportError:
    raise SystemExit(
        "yt-dlp مو مثبت. شغّل: pip install yt-dlp --break-system-packages"
    )

app = Flask(__name__)

APP_NAME = "مسارات"
APP_VERSION = "2.0.0"
GITHUB_URL = "https://github.com/mhamdsyrte/msarat"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_PATH = os.path.join(BASE_DIR, "settings.json")

_ANDROID_DOWNLOADS = os.path.expanduser("~/storage/downloads")  # ترمكس (Termux)
_ANDROID_APP_DOWNLOADS = os.environ.get("ANDROID_DOWNLOAD_DIR")  # نسخة APK عبر buildozer/webview

if _ANDROID_APP_DOWNLOADS:
    try:
        os.makedirs(_ANDROID_APP_DOWNLOADS, exist_ok=True)
    except Exception:
        pass

if _ANDROID_APP_DOWNLOADS and os.path.isdir(_ANDROID_APP_DOWNLOADS):
    _DEFAULT_DOWNLOAD_DIR = _ANDROID_APP_DOWNLOADS
elif os.path.isdir(_ANDROID_DOWNLOADS):
    _DEFAULT_DOWNLOAD_DIR = _ANDROID_DOWNLOADS
else:
    _DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
    if not os.path.isdir(_DEFAULT_DOWNLOAD_DIR):
        _DEFAULT_DOWNLOAD_DIR = os.path.expanduser("~")

DEFAULT_SETTINGS = {
    "download_dir": _DEFAULT_DOWNLOAD_DIR,
    "language": None,   # None = يحدد تلقائياً من لغة النظام بالواجهة
    "theme": "dark",
}

_settings_lock = threading.Lock()

# حالة تقدّم تحميلات قوائم التشغيل (بالذاكرة، لكل جلسة تحميل معرّف عشوائي)
_playlist_jobs = {}
_jobs_lock = threading.Lock()


def load_settings():
    with _settings_lock:
        if os.path.isfile(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                merged = {**DEFAULT_SETTINGS, **data}
                return merged
            except Exception:
                pass
        return dict(DEFAULT_SETTINGS)


def save_settings(new_values):
    with _settings_lock:
        current = dict(DEFAULT_SETTINGS)
        if os.path.isfile(SETTINGS_PATH):
            try:
                with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                    current.update(json.load(f))
            except Exception:
                pass
        current.update(new_values)
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(current, f, ensure_ascii=False, indent=2)
        return current


def get_download_dir():
    return load_settings().get("download_dir") or DEFAULT_SETTINGS["download_dir"]


def ffmpeg_location():
    """يدعم تحديد مسار ffmpeg مخصص (مثلاً على أندرويد عبر متغير بيئة)"""
    env_path = os.environ.get("MASARAT_FFMPEG_PATH")
    if env_path and os.path.isfile(env_path):
        return env_path
    return shutil.which("ffmpeg")


def human_size(num_bytes):
    if not num_bytes:
        return None
    size = float(num_bytes)
    for unit in ("بايت", "كيلوبايت", "ميجا", "جيجا"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} تيرا"


def format_duration(seconds):
    if not seconds:
        return None
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def subs_dict(raw):
    out = {}
    for lang, tracks in (raw or {}).items():
        if not tracks:
            continue
        out[lang] = tracks[0].get("name") or lang
    return out


def _format_single_video_info(info):
    formats = info.get("formats", []) or []
    video_formats, audio_formats = [], []

    for f in formats:
        vcodec = f.get("vcodec") or "none"
        acodec = f.get("acodec") or "none"
        fmt_id = f.get("format_id")
        if not fmt_id:
            continue
        size = f.get("filesize") or f.get("filesize_approx")
        protocol = "m3u8" if "m3u8" in (f.get("protocol") or "") else "https"

        is_video_only = vcodec != "none" and acodec == "none"
        is_audio_only = acodec != "none" and vcodec == "none"
        is_progressive = vcodec != "none" and acodec != "none"  # فيديو+صوت بملف واحد

        if is_video_only or is_progressive:
            video_formats.append({
                "id": fmt_id,
                "height": f.get("height") or 0,
                "fps": f.get("fps") or 0,
                "ext": f.get("ext"),
                "protocol": protocol,
                "size": human_size(size),
                "has_audio": is_progressive,
            })
        if is_audio_only:
            note = f.get("format_note") or ""
            lang = f.get("language") or "und"
            audio_formats.append({
                "id": fmt_id,
                "lang": lang,
                "ext": f.get("ext"),
                "protocol": protocol,
                "size": human_size(size),
                "is_original": "original" in note.lower(),
                "abr": round(f.get("abr") or 0),
            })

    video_formats.sort(key=lambda x: (-x["height"], x["protocol"] != "https"))
    audio_formats.sort(key=lambda x: (not x["is_original"], x["protocol"] != "https", -x["abr"]))

    return {
        "type": "video",
        "title": info.get("title") or "بدون عنوان",
        "thumbnail": info.get("thumbnail"),
        "duration": format_duration(info.get("duration")),
        "uploader": info.get("uploader"),
        "video_formats": video_formats,
        "audio_formats": audio_formats,
        "subtitles": subs_dict(info.get("subtitles")),
        "auto_captions": subs_dict(info.get("automatic_captions")),
    }


def extract_video_info(url):
    """يجيب معلومات رابط يوتيوب — يتعرف تلقائياً إذا كان فيديو مفرد أو قائمة تشغيل"""
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # أول محاولة: فيديو مفرد بدون توسيع القائمة (أسرع)
        info = ydl.extract_info(url, download=False, process=False)

    if info.get("_type") in ("playlist", "multi_video"):
        entries_raw = list(info.get("entries") or [])
        if not entries_raw:
            raise ValueError("ما قدرت ألقى فيديوهات بهالقائمة")
        entries = []
        for e in entries_raw:
            if not e:
                continue
            vid = e.get("id")
            entries.append({
                "id": vid,
                "title": e.get("title") or vid,
                "url": e.get("url") or f"https://www.youtube.com/watch?v={vid}",
                "thumbnail": e.get("thumbnail") or (
                    f"https://i.ytimg.com/vi/{vid}/mqdefault.jpg" if vid else None
                ),
                "duration": format_duration(e.get("duration")),
            })
        return {
            "type": "playlist",
            "title": info.get("title") or "قائمة تشغيل",
            "entries": entries,
        }

    # فيديو مفرد: لازم نعيد الاستخراج بمعالجة كاملة عشان نحصل الصيغ
    ydl_opts_full = dict(ydl_opts)
    ydl_opts_full["noplaylist"] = True
    with yt_dlp.YoutubeDL(ydl_opts_full) as ydl:
        info_full = ydl.extract_info(url, download=False)
    if info_full.get("_type") == "playlist":
        entries = info_full.get("entries") or []
        if not entries:
            raise ValueError("ما قدرت ألقى فيديو بهالرابط")
        info_full = entries[0]
    return _format_single_video_info(info_full)


@app.route("/")
def index():
    return render_template(
        "index.html",
        app_name=APP_NAME,
        app_version=APP_VERSION,
        github_url=GITHUB_URL,
    )


@app.route("/api/settings", methods=["GET"])
def api_get_settings():
    return jsonify(load_settings())


@app.route("/api/settings", methods=["POST"])
def api_set_settings():
    body = request.get_json(silent=True) or {}
    allowed = {}
    if "download_dir" in body:
        path = (body["download_dir"] or "").strip()
        if path and not os.path.isdir(path):
            return jsonify({"error": "المجلد غير موجود"}), 400
        if path:
            allowed["download_dir"] = path
    if "language" in body:
        allowed["language"] = body["language"]
    if "theme" in body and body["theme"] in ("light", "dark"):
        allowed["theme"] = body["theme"]
    updated = save_settings(allowed)
    return jsonify(updated)


@app.route("/api/meta")
def api_meta():
    return jsonify({
        "app_name": APP_NAME,
        "app_version": APP_VERSION,
        "github_url": GITHUB_URL,
        "ffmpeg_available": bool(ffmpeg_location()),
    })


@app.route("/api/info", methods=["POST"])
def api_info():
    url = (request.get_json(silent=True) or {}).get("url", "").strip()
    if not url:
        return jsonify({"error": "حط رابط الفيديو"}), 400
    try:
        return jsonify(extract_video_info(url))
    except yt_dlp.utils.DownloadError:
        return jsonify({"error": "ما قدرت أفتح الرابط — تأكد إنه صحيح ومتاح"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download", methods=["POST"])
def api_download():
    ff = ffmpeg_location()
    if not ff:
        return jsonify({"error": "ffmpeg مو مثبت"}), 400

    body = request.get_json(silent=True) or {}
    url = (body.get("url") or "").strip()
    video_id = body.get("video_id")
    audio_id = body.get("audio_id")
    sub_lang = body.get("sub_lang")
    sub_kind = body.get("sub_kind")
    save_thumb = bool(body.get("save_thumbnail"))

    if not url or not video_id:
        return jsonify({"error": "بيانات ناقصة"}), 400

    fmt = f"{video_id}+{audio_id}" if audio_id else video_id
    result_holder = {}

    def pp_hook(d):
        if d.get("postprocessor") == "Merger" and d.get("status") == "finished":
            result_holder["path"] = d.get("info_dict", {}).get("filepath")

    ydl_opts = {
        "format": fmt,
        "outtmpl": os.path.join(get_download_dir(), "%(title)s [%(id)s].%(ext)s"),
        "merge_output_format": "mp4",
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "postprocessor_hooks": [pp_hook],
        "writethumbnail": save_thumb,
        "ffmpeg_location": ff,
    }

    if sub_lang and sub_kind:
        ydl_opts["subtitleslangs"] = [sub_lang]
        ydl_opts["writesubtitles"] = sub_kind == "manual"
        ydl_opts["writeautomaticsub"] = sub_kind == "auto"
        ydl_opts["embedsubtitles"] = True
        ydl_opts.setdefault("postprocessors", []).append({"key": "FFmpegEmbedSubtitle"})

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            final_path = result_holder.get("path") or ydl.prepare_filename(info)
        return jsonify({
            "success": True,
            "filename": os.path.basename(final_path),
            "folder": get_download_dir(),
        })
    except yt_dlp.utils.DownloadError:
        return jsonify({"error": "صار خطأ بالتحميل — جرب صيغة ثانية"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _quality_selector(quality, lang):
    """يبني معيار اختيار صيغة yt-dlp حسب الجودة المطلوبة ولغة الصوت المفضلة"""
    height = "" if quality == "best" else f"[height<=?{quality}]"
    if lang and lang != "any":
        return (
            f"bestvideo{height}+bestaudio[language={lang}]/"
            f"bestvideo{height}+bestaudio/best{height}"
        )
    return f"bestvideo{height}+bestaudio/best{height}"


def _run_playlist_job(job_id, entries, quality, lang, sub_lang, sub_kind, save_thumb):
    ff = ffmpeg_location()
    total = len(entries)
    with _jobs_lock:
        job = _playlist_jobs[job_id]
        job["total"] = total

    for idx, entry in enumerate(entries, start=1):
        with _jobs_lock:
            job["current_index"] = idx
            job["current_title"] = entry.get("title")
        try:
            ydl_opts = {
                "format": _quality_selector(quality, lang),
                "outtmpl": os.path.join(get_download_dir(), "%(title)s [%(id)s].%(ext)s"),
                "merge_output_format": "mp4",
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "writethumbnail": save_thumb,
                "ffmpeg_location": ff,
            }
            if sub_lang and sub_kind:
                ydl_opts["subtitleslangs"] = [sub_lang]
                ydl_opts["writesubtitles"] = sub_kind == "manual"
                ydl_opts["writeautomaticsub"] = sub_kind == "auto"
                ydl_opts["embedsubtitles"] = True
                ydl_opts.setdefault("postprocessors", []).append({"key": "FFmpegEmbedSubtitle"})

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.extract_info(entry["url"], download=True)
            with _jobs_lock:
                job["done"].append({"title": entry.get("title"), "ok": True})
        except Exception as e:
            with _jobs_lock:
                job["done"].append({"title": entry.get("title"), "ok": False, "error": str(e)})

    with _jobs_lock:
        job["finished"] = True


@app.route("/api/download_playlist", methods=["POST"])
def api_download_playlist():
    ff = ffmpeg_location()
    if not ff:
        return jsonify({"error": "ffmpeg مو مثبت"}), 400

    body = request.get_json(silent=True) or {}
    entries = body.get("entries") or []  # [{id, title, url}]
    quality = str(body.get("quality") or "best")
    lang = body.get("audio_lang") or "any"
    sub_lang = body.get("sub_lang")
    sub_kind = body.get("sub_kind")
    save_thumb = bool(body.get("save_thumbnail"))

    if not entries:
        return jsonify({"error": "ما فيه فيديوهات محددة"}), 400

    job_id = uuid.uuid4().hex
    with _jobs_lock:
        _playlist_jobs[job_id] = {
            "total": len(entries),
            "current_index": 0,
            "current_title": None,
            "done": [],
            "finished": False,
        }

    t = threading.Thread(
        target=_run_playlist_job,
        args=(job_id, entries, quality, lang, sub_lang, sub_kind, save_thumb),
        daemon=True,
    )
    t.start()

    return jsonify({"job_id": job_id})


@app.route("/api/download_playlist/status")
def api_download_playlist_status():
    job_id = request.args.get("job_id")
    with _jobs_lock:
        job = _playlist_jobs.get(job_id)
        if not job:
            return jsonify({"error": "job غير موجود"}), 404
        return jsonify(dict(job))


if __name__ == "__main__":
    print(f"افتح المتصفح على: http://127.0.0.1:5000")
    print(f"مجلد الحفظ: {get_download_dir()}")
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
