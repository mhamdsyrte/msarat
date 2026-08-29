# مسارات (مسارات)

أداة مفتوحة المصدر لفحص وتحميل فيديوهات وقوائم تشغيل يوتيوب — كل الجودات،
الدبلجات، الترجمات، وقوائم التشغيل كاملة. متوفرة كتطبيق ويب محلي، تطبيق
سطح مكتب (وندوز/لينكس)، وتطبيق أندرويد (APK).

> ⚠️ **تنويه**: هذا الكود يستخدم [yt-dlp](https://github.com/yt-dlp/yt-dlp) وهو
> مخصص للاستخدام الشخصي (أرشفة، محتواك الخاص، محتوى مرخّص أو ضمن الاستخدام
> العادل). احترم شروط استخدام يوتيوب وحقوق الملكية الفكرية لأي محتوى تحمّله.

---

## 🧩 بنية المشروع

```
app/            الكود المشترك (Flask + yt-dlp + الواجهة) — يُستخدم بكل النسخ
desktop/        غلاف تطبيق سطح المكتب (pywebview) + ملفات PyInstaller
android/        مشروع أندرويد (buildozer + python-for-android webview)
.github/workflows/build.yml   بناء تلقائي لكل النسخ عبر GitHub Actions
```

## ✨ الميزات

- فحص أي رابط يوتيوب: جودات فيديو، مسارات صوت (أصلي + دبلجات)، ترجمات رسمية وتلقائية
- **تحميل قوائم تشغيل كاملة** مع اختيار جودة مستهدفة ولغة صوت مفضّلة
- إعدادات: تغيير مجلد الحفظ، تبديل اللغة، تبديل الثيم (فاتح/غامق)
- **11 لغة واجهة** (عربي، إنجليزي، فرنسي، إسباني، ألماني، تركي، أردو، فارسي،
  روسي، صيني، هندي) — تُختار تلقائياً حسب لغة الجهاز إن كانت مدعومة
- شاشة بداية (splash) وشاشة "حول التطبيق" بالعلامة التجارية

## 🚀 التشغيل من المصدر (اختبار سريع)

```bash
cd app
pip install -r ../desktop/requirements.txt --break-system-packages
python app.py
# افتح: http://127.0.0.1:5000
```

يحتاج `ffmpeg` مثبت على النظام لدمج الفيديو والصوت (لتحميل الجودات العالية).

## 🖥️ بناء نسخة وندوز/لينكس (يدوياً)

```bash
cd desktop
pip install -r requirements.txt --break-system-packages   # على لينكس
# أو: pip install -r requirements.txt                      # على وندوز
pyinstaller masarat.spec --noconfirm
```

الناتج بمجلد `desktop/dist/Masarat/`.

## 📱 بناء نسخة أندرويد (APK)

راجع [`android/README.md`](android/README.md) للتفاصيل والقيود المعروفة
(خصوصاً موضوع ffmpeg على أندرويد).

## 🤖 البناء التلقائي عبر GitHub Actions (موصى به لجهاز ضعيف)

بمجرد ما ترفع المشروع على GitHub:

1. أي push على `main` يبني تلقائياً نسخة وندوز، لينكس، وAPK أندرويد
   ويحطها بـ **Actions → أحدث تشغيلة → Artifacts** (تقدر تنزلها من هناك).
2. لعمل **إصدار رسمي (Release)** بكل الملفات جاهزة للتحميل:
   ```bash
   git tag v2.0.0
   git push origin v2.0.0
   ```
   بعد ما يخلص البناء، بتلاقي الملفات بصفحة Releases بالمستودع.

لا تحتاج أي بناء محلي على جهازك — كل شي يصير على سيرفرات GitHub المجانية.

## ⚙️ الحالة الحالية للبراندنج

- ✅ رابط GitHub: `https://github.com/mhamdsyrte/msarat`
- ✅ WhatsApp: `963995385471`
- ✅ Instagram: `mhamd.tresh`
- ✅ الشعار (`app/static/logo.svg` و`logo.png`, وأيقونات سطح المكتب/أندرويد): نهائي — تصميم "مسارات" (3 خطوط فيديو/صوت/ترجمة تتجمع بسهم تحميل واحد)
- ✅ شاشة بداية بمرحلتين: بطاقة المطوّر `hamziwy-py` أولاً ثم شعار التطبيق

## 📱 التشغيل من ترمكس (Termux) خطوة بخطوة

```bash
pkg update -y && pkg upgrade -y
pkg install git -y

# فك ضغط المشروع (بعد نقل ملف الـ zip لمجلد التنزيلات بالهاتف)
termux-setup-storage
cd ~/storage/downloads
unzip masarat.zip -d ~/masarat-project
cd ~/masarat-project/masarat

# إعداد Git (مرة وحدة فقط)
git config --global user.name "hamziwy-py"
git config --global user.email "your-email@example.com"

git init
git branch -M main
git add -A
git commit -m "مسارات v2.0.0"

# اربطه بمستودعك على GitHub (لازم تكون سويت المستودع فاضي من موقع GitHub مسبقاً)
git remote add origin https://github.com/mhamdsyrte/msarat.git
```

**تسجيل الدخول من ترمكس**: GitHub ما يقبل كلمة السر العادية من التيرمينال —
لازم Personal Access Token:
1. من متصفح الهاتف: GitHub → Settings → Developer settings →
   Personal access tokens → Generate new token (صلاحية `repo` كافية)
2. عند الدفع أول مرة، استخدم اسم المستخدم + التوكن بدل كلمة السر:
```bash
git push -u origin main
# Username: hamziwy-py
# Password: (الصق التوكن هنا، مو كلمة سر حسابك)
```

**تشغيل البناء التلقائي** (يبني وندوز + لينكس + APK أندرويد تلقائياً):
البناء يشتغل تلقائياً بمجرد الـ push. لعمل إصدار رسمي (Release) فيه كل
الملفات جاهزة للتحميل مباشرة:
```bash
git tag v2.0.0
git push origin v2.0.0
```

بعد 15-25 دقيقة تقريباً (وقت بناء APK أطول من الباقي)، روح لصفحة المستودع
على GitHub → تبويب **Actions** لمتابعة التقدم، أو تبويب **Releases** بعد
الانتهاء لتحميل ملف الـ APK مباشرة (متوافق مع أجهزة 32-بت و64-بت بنفس الملف).

## 📄 الرخصة

MIT — شوف [`LICENSE`](LICENSE). المشروع مفتوح المصدر بالكامل.

---
تطوير: **hamziwy-py**
