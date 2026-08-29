const langName = (code) => TRACK_LANG_NAMES[code] || code;

const els = {
  htmlRoot: document.getElementById('html-root'),
  urlInput: document.getElementById('url-input'),
  fetchBtn: document.getElementById('fetch-btn'),
  fetchStatus: document.getElementById('fetch-status'),
  result: document.getElementById('result'),
  thumb: document.getElementById('thumb'),
  vTitle: document.getElementById('v-title'),
  vSub: document.getElementById('v-sub'),
  videoOptions: document.getElementById('video-options'),
  audioOptions: document.getElementById('audio-options'),
  subSelect: document.getElementById('sub-select'),
  thumbCheckbox: document.getElementById('thumb-checkbox'),
  downloadBtn: document.getElementById('download-btn'),
  downloadStatus: document.getElementById('download-status'),

  playlistResult: document.getElementById('playlist-result'),
  plTitle: document.getElementById('pl-title'),
  plBadge: document.getElementById('pl-badge'),
  plEntries: document.getElementById('pl-entries'),
  plSelectAll: document.getElementById('pl-select-all'),
  plDeselectAll: document.getElementById('pl-deselect-all'),
  plQuality: document.getElementById('pl-quality-select'),
  plLang: document.getElementById('pl-lang-select'),
  plSubSelect: document.getElementById('pl-sub-select'),
  plThumbCheckbox: document.getElementById('pl-thumb-checkbox'),
  plDownloadBtn: document.getElementById('pl-download-btn'),
  plProgress: document.getElementById('pl-progress'),
  plProgressFill: document.getElementById('pl-progress-fill'),
  plProgressText: document.getElementById('pl-progress-text'),

  settingsBtn: document.getElementById('settings-btn'),
  aboutBtn: document.getElementById('about-btn'),
  settingsModal: document.getElementById('settings-modal'),
  aboutModal: document.getElementById('about-modal'),
  downloadDirInput: document.getElementById('download-dir-input'),
  downloadDirSave: document.getElementById('download-dir-save'),
  languageSelect: document.getElementById('language-select'),
  themeLightBtn: document.getElementById('theme-light-btn'),
  themeDarkBtn: document.getElementById('theme-dark-btn'),

  splash: document.getElementById('splash'),
};

// اسم التطبيق ثابت دايماً (براندنج) — نلقطه من الـ HTML الأصلي قبل أي ترجمة
const APP_BRAND_NAME = document.getElementById('t-app-title').textContent;

const state = {
  url: '', selectedVideo: null, selectedAudio: null,
  lang: 'ar', theme: 'dark',
  playlistEntries: [], selectedPlaylistIds: new Set(),
};

// ================== i18n ==================

function applyTranslations() {
  const lang = state.lang;
  const dir = RTL_LANGS.has(lang) ? 'rtl' : 'ltr';
  els.htmlRoot.setAttribute('lang', lang);
  els.htmlRoot.setAttribute('dir', dir);

  document.querySelectorAll('[id^="t-"]').forEach(el => {
    const key = el.id.replace(/^t-/, '').replace(/-/g, '_').replace(/_opt$/, '');
    if (el.id.endsWith('-opt')) return; // معالجة خاصة أدناه
    el.textContent = t(lang, key);
  });
  document.getElementById('t-no-sub-opt').textContent = t(lang, 'no_sub');
  document.getElementById('t-pl-no-sub-opt').textContent = t(lang, 'no_sub');

  document.querySelectorAll('[id-text]').forEach(el => {
    el.textContent = t(lang, el.getAttribute('id-text'));
  });

  document.getElementById('t-app-title').textContent = APP_BRAND_NAME; // نستعيد الاسم الأصلي بدل النسخة المترجمة

  els.themeLightBtn.textContent = t(lang, 'theme_light');
  els.themeDarkBtn.textContent = t(lang, 'theme_dark');
  renderPlaylistSubtitleOptions();
  els.plSelectAll.textContent = t(lang, 'playlist_select_all');
  els.plDeselectAll.textContent = t(lang, 'playlist_deselect_all');
  els.plDownloadBtn.textContent = t(lang, 'playlist_download_btn');

  // قائمة اللغات بالإعدادات
  els.languageSelect.innerHTML = '';
  const autoOpt = document.createElement('option');
  autoOpt.value = '';
  autoOpt.textContent = lang === 'ar' ? 'تلقائي (لغة الجهاز)' : 'Auto (system language)';
  els.languageSelect.appendChild(autoOpt);
  SUPPORTED_LANGS.forEach(code => {
    const opt = document.createElement('option');
    opt.value = code;
    opt.textContent = LANG_LABELS[code];
    els.languageSelect.appendChild(opt);
  });
  els.languageSelect.value = state.langOverride || '';
}

// ================== Theme ==================

function applyTheme(theme) {
  state.theme = theme;
  document.documentElement.setAttribute('data-theme', theme);
  els.themeLightBtn.classList.toggle('active', theme === 'light');
  els.themeDarkBtn.classList.toggle('active', theme === 'dark');
}

// ================== Settings ==================

async function loadSettings() {
  try {
    const res = await fetch('/api/settings');
    const data = await res.json();
    els.downloadDirInput.value = data.download_dir || '';
    applyTheme(data.theme || 'dark');
    state.langOverride = data.language || '';
    state.lang = state.langOverride || detectSystemLang();
    applyTranslations();
  } catch (e) {
    state.lang = detectSystemLang();
    applyTranslations();
  }
}

async function saveSetting(patch) {
  try {
    const res = await fetch('/api/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(patch),
    });
    return await res.json();
  } catch (e) {
    return null;
  }
}

function openModal(el) { el.classList.remove('hidden'); }
function closeModal(el) { el.classList.add('hidden'); }

els.settingsBtn.addEventListener('click', () => openModal(els.settingsModal));
els.aboutBtn.addEventListener('click', () => openModal(els.aboutModal));
document.querySelectorAll('.modal-close').forEach(btn => {
  btn.addEventListener('click', () => closeModal(document.getElementById(btn.dataset.close)));
});
document.querySelectorAll('.modal-overlay').forEach(overlay => {
  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeModal(overlay); });
});

els.downloadDirSave.addEventListener('click', async () => {
  const dir = els.downloadDirInput.value.trim();
  if (!dir) return;
  const result = await saveSetting({ download_dir: dir });
  if (result && result.error) alert(result.error);
});

els.languageSelect.addEventListener('change', async () => {
  const val = els.languageSelect.value;
  state.langOverride = val;
  state.lang = val || detectSystemLang();
  await saveSetting({ language: val || null });
  applyTranslations();
});

els.themeLightBtn.addEventListener('click', async () => { applyTheme('light'); await saveSetting({ theme: 'light' }); });
els.themeDarkBtn.addEventListener('click', async () => { applyTheme('dark'); await saveSetting({ theme: 'dark' }); });

// ================== Single video rendering ==================

function miniWave(intensity) {
  const heights = [4, 8, 12].map(h => Math.max(4, Math.round(h * (0.4 + intensity * 0.6))));
  return `<span class="mini-wave">${heights.map(h => `<span style="height:${h}px"></span>`).join('')}</span>`;
}

function setStatus(el, text, type) {
  el.textContent = text || '';
  el.className = 'status-text' + (type ? ' ' + type : '');
}

function renderVideoOptions(list) {
  els.videoOptions.innerHTML = '';
  state.selectedVideo = null;
  list.forEach((f, i) => {
    const card = document.createElement('label');
    card.className = 'option-card' + (i === 0 ? ' selected' : '');
    const audioTag = f.has_audio ? `<span class="tag">${t(state.lang, 'original')}+${t(state.lang, 'section_audio')}</span>` : '';
    card.innerHTML = `
      <input type="radio" name="video" value="${f.id}" ${i === 0 ? 'checked' : ''}>
      <div class="option-main">
        <div class="option-title">${f.height}p${f.fps > 30 ? f.fps : ''} ${audioTag}</div>
        <div class="option-sub">${f.ext} · ${f.size || t(state.lang, 'size_unknown')}</div>
      </div>`;
    card.querySelector('input').addEventListener('change', () => {
      state.selectedVideo = f.id;
      state.selectedVideoHasAudio = !!f.has_audio;
      els.videoOptions.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
    if (i === 0) { state.selectedVideo = f.id; state.selectedVideoHasAudio = !!f.has_audio; }
    els.videoOptions.appendChild(card);
  });
}

function renderAudioOptions(list) {
  els.audioOptions.innerHTML = '';
  state.selectedAudio = null;
  if (!list.length) return;
  const maxAbr = Math.max(1, ...list.map(f => f.abr || 0));
  list.forEach((f, i) => {
    const card = document.createElement('label');
    card.className = 'option-card' + (i === 0 ? ' selected' : '');
    const tag = f.is_original ? `<span class="tag">${t(state.lang, 'original')}</span>` : `<span class="tag">${t(state.lang, 'dub')}</span>`;
    card.innerHTML = `
      <input type="radio" name="audio" value="${f.id}" ${i === 0 ? 'checked' : ''}>
      ${miniWave((f.abr || 20) / maxAbr)}
      <div class="option-main">
        <div class="option-title">${langName(f.lang)}${tag}</div>
        <div class="option-sub">${f.ext} · ${f.abr ? f.abr + 'kbps' : '؟'} · ${f.size || t(state.lang, 'size_unknown')}</div>
      </div>`;
    card.querySelector('input').addEventListener('change', () => {
      state.selectedAudio = f.id;
      els.audioOptions.querySelectorAll('.option-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
    });
    if (i === 0) state.selectedAudio = f.id;
    els.audioOptions.appendChild(card);
  });
}

function renderSubtitles(manual, auto) {
  els.subSelect.innerHTML = `<option value="">${t(state.lang, 'no_sub')}</option>`;
  const addGroup = (label, dict, kind) => {
    const codes = Object.keys(dict || {});
    if (!codes.length) return;
    const group = document.createElement('optgroup');
    group.label = label;
    codes.forEach(code => {
      const opt = document.createElement('option');
      opt.value = `${kind}:${code}`;
      opt.textContent = langName(code);
      group.appendChild(opt);
    });
    els.subSelect.appendChild(group);
  };
  addGroup(t(state.lang, 'sub_manual'), manual, 'manual');
  addGroup(t(state.lang, 'sub_auto'), auto, 'auto');
}

// قائمة الترجمة لقوائم التشغيل: ما نعرف مسبقاً ترجمة كل فيديو بالقائمة (نجيبها
// فقط عند الفحص المفرد)، فنعرض مجموعة لغات شائعة — السيرفر يتجاهل أي لغة
// غير متوفرة لفيديو معيّن تلقائياً بدون خطأ.
const COMMON_SUB_CODES = ['ar', 'en', 'fr', 'es', 'de', 'tr', 'ur', 'fa', 'ru', 'zh', 'hi', 'pt', 'it', 'ja', 'ko'];

function renderPlaylistSubtitleOptions() {
  if (!els.plSubSelect) return;
  els.plSubSelect.innerHTML = `<option value="">${t(state.lang, 'no_sub')}</option>`;
  const addGroup = (label, kind) => {
    const group = document.createElement('optgroup');
    group.label = label;
    COMMON_SUB_CODES.forEach(code => {
      const opt = document.createElement('option');
      opt.value = `${kind}:${code}`;
      opt.textContent = langName(code);
      group.appendChild(opt);
    });
    els.plSubSelect.appendChild(group);
  };
  addGroup(t(state.lang, 'sub_manual'), 'manual');
  addGroup(t(state.lang, 'sub_auto'), 'auto');
}

// ================== Playlist rendering ==================

function renderPlaylist(data) {
  state.playlistEntries = data.entries;
  state.selectedPlaylistIds = new Set(data.entries.map(e => e.id));

  els.plTitle.textContent = data.title;
  els.plBadge.textContent = `${data.entries.length} ${t(state.lang, 'playlist_count')}`;
  els.plEntries.innerHTML = '';

  data.entries.forEach(entry => {
    const row = document.createElement('label');
    row.className = 'pl-entry';
    row.innerHTML = `
      <input type="checkbox" checked data-id="${entry.id}">
      <img src="${entry.thumbnail || ''}" alt="">
      <span class="pl-entry-title">${entry.title}</span>
      <span class="muted">${entry.duration || ''}</span>`;
    row.querySelector('input').addEventListener('change', (e) => {
      if (e.target.checked) state.selectedPlaylistIds.add(entry.id);
      else state.selectedPlaylistIds.delete(entry.id);
    });
    els.plEntries.appendChild(row);
  });
}

els.plSelectAll.addEventListener('click', () => {
  state.selectedPlaylistIds = new Set(state.playlistEntries.map(e => e.id));
  els.plEntries.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = true);
});
els.plDeselectAll.addEventListener('click', () => {
  state.selectedPlaylistIds = new Set();
  els.plEntries.querySelectorAll('input[type="checkbox"]').forEach(cb => cb.checked = false);
});

async function pollPlaylistJob(jobId) {
  els.plProgress.classList.remove('hidden');
  while (true) {
    await new Promise(r => setTimeout(r, 1200));
    try {
      const res = await fetch(`/api/download_playlist/status?job_id=${jobId}`);
      const job = await res.json();
      if (job.error) break;
      const pct = job.total ? Math.round((job.done.length / job.total) * 100) : 0;
      els.plProgressFill.style.width = pct + '%';
      els.plProgressText.textContent = `${t(state.lang, 'playlist_progress')} ${job.current_index}/${job.total} — ${job.current_title || ''}`;
      if (job.finished) {
        const okCount = job.done.filter(d => d.ok).length;
        els.plProgressText.textContent = `✅ ${okCount}/${job.total}`;
        break;
      }
    } catch (e) { break; }
  }
  els.plDownloadBtn.disabled = false;
}

els.plDownloadBtn.addEventListener('click', async () => {
  const entries = state.playlistEntries.filter(e => state.selectedPlaylistIds.has(e.id));
  if (!entries.length) return;
  els.plDownloadBtn.disabled = true;
  const [plSubKind, plSubLang] = (els.plSubSelect.value || '').split(':');
  try {
    const res = await fetch('/api/download_playlist', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        entries,
        quality: els.plQuality.value,
        audio_lang: els.plLang.value,
        sub_kind: plSubKind || null,
        sub_lang: plSubLang || null,
        save_thumbnail: els.plThumbCheckbox.checked,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || t(state.lang, 'error_generic'));
    pollPlaylistJob(data.job_id);
  } catch (err) {
    els.plDownloadBtn.disabled = false;
    alert(err.message);
  }
});

// ================== Fetch / Download (single) ==================

els.fetchBtn.addEventListener('click', async () => {
  const url = els.urlInput.value.trim();
  if (!url) return;
  state.url = url;
  els.fetchBtn.disabled = true;
  setStatus(els.fetchStatus, t(state.lang, 'checking'), '');
  els.result.classList.add('hidden');
  els.playlistResult.classList.add('hidden');

  try {
    const res = await fetch('/api/info', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || t(state.lang, 'error_generic'));

    if (data.type === 'playlist') {
      renderPlaylist(data);
      els.playlistResult.classList.remove('hidden');
    } else {
      els.thumb.src = data.thumbnail || '';
      els.vTitle.textContent = data.title;
      els.vSub.textContent = [data.uploader, data.duration].filter(Boolean).join(' · ');
      renderVideoOptions(data.video_formats || []);
      renderAudioOptions(data.audio_formats || []);
      renderSubtitles(data.subtitles, data.auto_captions);
      els.result.classList.remove('hidden');
    }
    setStatus(els.fetchStatus, '', '');
  } catch (err) {
    setStatus(els.fetchStatus, err.message, 'error');
  } finally {
    els.fetchBtn.disabled = false;
  }
});

els.downloadBtn.addEventListener('click', async () => {
  if (!state.selectedVideo) return;
  const [subKind, subLang] = (els.subSelect.value || '').split(':');

  els.downloadBtn.disabled = true;
  setStatus(els.downloadStatus, t(state.lang, 'downloading'), '');

  try {
    const res = await fetch('/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        url: state.url,
        video_id: state.selectedVideo,
        audio_id: state.selectedVideoHasAudio ? null : state.selectedAudio,
        sub_kind: subKind || null,
        sub_lang: subLang || null,
        save_thumbnail: els.thumbCheckbox.checked,
      }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || t(state.lang, 'error_generic'));
    setStatus(els.downloadStatus, `✅ ${data.filename} — ${data.folder}`, 'success');
  } catch (err) {
    setStatus(els.downloadStatus, err.message, 'error');
  } finally {
    els.downloadBtn.disabled = false;
  }
});

// ================== Init ==================

function playIntroSplash() {
  const dev = document.getElementById('splash-dev');
  const appStage = document.getElementById('splash-app');
  const splash = els.splash;

  // مرحلة 1: بطاقة المطوّر تدخل
  requestAnimationFrame(() => dev.classList.add('stage-visible'));

  // مرحلة 1 تخرج → مرحلة 2 (شعار التطبيق) تدخل
  setTimeout(() => {
    dev.classList.remove('stage-visible');
    setTimeout(() => {
      dev.classList.add('hidden');
      appStage.classList.remove('hidden');
      requestAnimationFrame(() => appStage.classList.add('stage-visible'));
    }, 450);
  }, 1100);

  // إخفاء الشاشة بالكامل وإزالتها
  setTimeout(() => {
    splash.classList.add('splash-hide');
    setTimeout(() => splash.remove(), 500);
  }, 2900);
}

(async function init() {
  await loadSettings();
  playIntroSplash();
})();
