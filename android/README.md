# نسخة أندرويد — مسارات

يستخدم هذا المشروع [python-for-android](https://python-for-android.readthedocs.io/)
عبر [buildozer](https://buildozer.readthedocs.io/) مع **bootstrap = webview**،
وهي طريقة رسمية تخلي p4a يشغّل تطبيق الويب (Flask) ويعرضه مباشرة بمكوّن
WebView أندرويد — بدون الحاجة لإعادة كتابة الواجهة بـ Kivy.

## البناء عبر GitHub Actions (الطريقة الموصى بها)

مضبوط تلقائياً بـ `.github/workflows/build.yml` (job: `build-android`).
فقط ادفع (push) للمستودع أو فعّل الـ workflow يدوياً من تبويب **Actions**،
وبعد ما يخلص البناء حمّل الـ APK من **Artifacts**.

## البناء يدوياً (لينكس فقط — buildozer ما يدعم وندوز مباشرة)

```bash
pip install buildozer cython --break-system-packages
cp -r ../app ./app          # ينسخ الكود المشترك جوا مجلد android/
buildozer android debug
# الناتج: android/bin/*.apk
```

أول بناء بياخذ وقت طويل (يحمّل Android SDK/NDK — عدة جيجات).

## ⚠️ القيود المعروفة (لازم تُحل قبل نشر نهائي)

### 1. ffmpeg غير مرفق افتراضياً
`python-for-android` ما يوفر `ffmpeg` جاهز. بدون ffmpeg:
- ✅ الصيغ المدمجة (فيديو+صوت بملف واحد، عادة حتى 360p/720p القديمة) تشتغل عادي
- ❌ دمج فيديو عالي الجودة + صوت منفصل (اللي يحتاجه yt-dlp لمعظم صيغ 1080p+) **مو هيشتغل**

**الحل**: نزّل ثنائي `ffmpeg` ثابت (static build) لمعمارية أندرويد
(`arm64-v8a` و`armeabi-v7a`) من مصدر موثوق، وحطه بمسار:
```
android/ffmpeg_bin/ffmpeg
```
`main.py` بيكتشفه تلقائياً ويمرره لـ yt-dlp عبر `MASARAT_FFMPEG_PATH`.
بديل أكثر ثباتاً على المدى الطويل: التكامل مع مكتبة
[ffmpeg-kit](https://github.com/arthenica/ffmpeg-kit) (يحتاج جسر Java/Python
إضافي — تطوير مستقبلي).

### 2. صلاحيات التخزين على أندرويد 11+
أندرويد الحديث يقيّد الوصول المباشر لمجلدات النظام. التطبيق حالياً يحفظ
بمسار `/storage/emulated/0/Download/Masarat` (يحتاج صلاحية التخزين ممنوحة
من المستخدم عند أول تشغيل). لتخصيص المسار من التطبيق نفسه، استخدم شاشة
⚙️ الإعدادات — تقدر تكتب أي مسار يقدر التطبيق يوصله.

### 3. حجم APK
تضمين `yt-dlp` + Python كامل يخلي حجم الـ APK كبير نسبياً (30-60 ميجا).
هذا طبيعي لهذا النوع من التطبيقات (مقارنة بتطبيقات Kivy الخفيفة).

## اختبار سريع بدون بناء APK كامل

قبل ما تبني APK، جرّب نفس كود `app/` على المتصفح (`python app.py`) للتأكد
كل الميزات تشتغل صح، لأن دورة بناء APK بتاخذ وقت.
