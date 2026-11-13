"""
CakraAegis v3 - Asisten keamanan suara ala Jarvis/Alexa (Desktop)

Jalur deteksi ancaman: (1) LOG server real-time, (2) KODE proyek, (3) LAYAR (opsional).

Instalasi:
    pip install customtkinter SpeechRecognition pyttsx3 pyaudio mss pillow google-genai gTTS pygame
API key Gemini: set env GEMINI_API_KEY, ATAU klik tombol "🔑 API key" di aplikasi.
Jalankan:  python cakraaegis.py
"""

import array
import collections
import datetime
import difflib
import faulthandler
import io
import math
import json
import os
import queue
import random
import re
import subprocess
import sys
import tempfile
import threading
import time
import traceback
from pathlib import Path
from tkinter import filedialog
from urllib.parse import unquote

os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import customtkinter as ctk
import mss
import pyttsx3
import speech_recognition as sr
from google import genai
from google.genai import types
from PIL import Image, ImageChops, ImageStat

# ============================ KONFIGURASI ============================
FALLBACK_MODELS = ["gemini-3.8-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-2.5-flash"]
# Model dicari otomatis dari akun Anda (client.models.list). Paksa model tertentu: isi "model" di cakra_config.json
LANG_STT = "id-ID"
CAPTURE_INTERVAL = 2   # detik antar tangkapan layar (Live screen)
WATCH_INTERVAL = 12    # jeda minimum antar analisis otomatis layar (detik)
CONVO_WINDOW = 45         # detik tetap aktif setelah dipanggil/menjawab
MIC_RETRY_DELAY = 1.2     # jeda sebelum menyambung ulang mic yang terputus (detik)
SILENCE_END = 0.6         # detik hening sebelum ucapan dianggap selesai (makin kecil = makin cepat menjawab)
BATCH_WAIT, ANALYSIS_GAP = 6, 20   # jeda pengumpulan event & jarak minimum antar analisis ancaman (detik)
BYE_WORDS = ("sudah dulu", "cukup", "terima kasih", "tidur dulu", "makasih")
CFG_FILE = Path("cakra_config.json")
try:                                   # panggilan ke pengguna; ubah via "panggilan" di cakra_config.json (mis. "Ndan")
    CALL = json.loads(CFG_FILE.read_text()).get("panggilan") or "Komandan"
except Exception:
    CALL = "Komandan"
TTS_VOICE = "id-ID-ArdiNeural"         # suara cowok natural (cewek: id-ID-GadisNeural)
TTS_RATE, TTS_PITCH = "+6%", "-2Hz"    # kecepatan & nada: sedikit lebih cepat dan berat supaya terdengar tegas
PRONOUNCE = {"SQL": "es kiu el", "XSS": "eks es es", "DDoS": "di dos", "DoS": "dos", "IP": "ai pi", "API": "ei pi ai",
             "URL": "yu er el", "PHP": "pe ha pe", "HTTP": "ha te te pe", "HTTPS": "ha te te pe es", "CSRF": "si es er ef",
             "JWT": "je dobel yu ti", "SSH": "es es ha", "VPS": "vi pi es", "AI": "ei ai", "CVE": "si vi i", "WAF": "waf"}
REPORT_DIR = Path("cakra_reports")
ID_VOICE_KEYS = ("id-id", "id_id", "idid", "indones", "andika", "damayanti")

CODE_EXTS = {".py", ".js", ".ts", ".jsx", ".tsx", ".php", ".java", ".go", ".rb", ".cs",
             ".html", ".vue", ".sql", ".yml", ".yaml", ".conf"}
SKIP_DIRS = {"node_modules", ".git", "venv", ".venv", "dist", "build", "__pycache__", "vendor", ".next"}
MAX_FILES, MAX_FILE_BYTES = 1500, 40_000

SYSTEM_PROMPT = f"""Kamu adalah CakraAegis, asisten AI pelindung keamanan siber bergaya Jarvis.
Bicara Bahasa Indonesia yang hangat, tenang, dan natural seperti asisten suara modern (bukan kaku/baku berlebihan), panggil
pengguna "{CALL}" secukupnya, tidak di setiap kalimat. Saat ngobrol,
jawab SANGAT singkat (maksimal 2 kalimat pendek, di bawah 35 kata, langsung ke inti tanpa basa-basi
pembuka) karena dibacakan lewat suara; baru panjang jika diminta detail atau kode. Untuk perbaikan kode, tulis dalam
blok kode markdown (kodenya tidak dibacakan). Kamu hanya melindungi aset MILIK pengguna:
berikan panduan defensif (deteksi, mitigasi, patch, hardening), bukan exploit atau cara
menyerang pihak lain. Jangan mengarang: jika bukti kurang, katakan dan minta data tambahan."""

THREAT_PROMPT = """Berikut event serangan hasil deteksi lokal dari log server pengguna, beserta kode
proyek yang kemungkinan terkait. Tugasmu:
1. Baris pertama: "RINGKAS: <1-2 kalimat lisan: jenis serangan, tingkat bahaya, apakah kode rentan>".
2. Nilai apakah serangan berpotensi berhasil. Tunjuk file/fungsi/baris rentan (jika kode terlihat).
3. Beri KODE PERBAIKAN (sebelum -> sesudah) dalam blok kode markdown.
4. Langkah respons cepat: blokir IP, rate limit, aturan WAF, rotasi kredensial bila perlu.
Jika kode terkait tidak tersedia/tidak cukup, katakan jelas dan beri mitigasi umum."""

AUDIT_PROMPT = """Audit keamanan kode berikut (milik pengguna). Cari: SQL injection, XSS, command injection,
path traversal, auth/session lemah, IDOR, upload tidak aman, secret hardcoded, CSRF, misconfig.
Baris pertama: "RINGKAS: <jumlah temuan & yang paling kritis>". Lalu tiap temuan:
[SEVERITY] file:baris - jenis - penjelasan singkat, diikuti blok kode perbaikan.
Setiap baris kode diawali nomor baris asli dengan format "nomor| kode": pakai nomor itu pada file:baris, dan JANGAN
menyertakan awalan nomor itu pada kode perbaikan. Jika sebuah file dibagi beberapa bagian, audit semua bagian yang diberikan.
Jika tidak ada temuan jelas, katakan jujur. Jangan mengarang baris yang tidak ada."""

SCREEN_PROMPT = """Analisis screenshot ini sebagai analis keamanan: cari indikasi serangan atau misconfig yang
TERLIHAT (log, dashboard WAF, DevTools, terminal). Awali dengan "RINGKAS: ...", lalu temuan dan langkah penanganan."""

WATCH_PROMPT = """Kamu memantau layar pengguna SECARA LIVE sambil ngobrol dengannya. Ini frame terbaru.
ABAIKAN jendela aplikasi CakraAegis sendiri (sidebar, bubble chat, tombol): itu bukan target pemantauan.
Balas dengan format ini saja:
STATUS: AMAN | WASPADA | BAHAYA
RINGKAS: <1 kalimat lisan tentang apa yang terlihat/terdeteksi>
DETAIL: (hanya jika WASPADA/BAHAYA) temuan, bukti yang terlihat, langkah penanganan singkat, kode perbaikan dalam blok kode bila relevan.
Tandai WASPADA/BAHAYA hanya jika ADA indikasi serangan, misconfig, atau secret terekspos yang TERLIHAT jelas di layar.
Selain itu STATUS: AMAN dan RINGKAS menjelaskan singkat apa yang sedang ditampilkan."""

C = {"bg": "#0b1118", "panel": "#131b25", "user": "#1f6feb", "ai": "#202a36",
     "ok": "#2ea043", "warn": "#d29922", "bad": "#f85149", "muted": "#8b949e"}


# ============================ UTIL ============================
def load_cfg():
    try:
        cfg = json.loads(CFG_FILE.read_text())
    except Exception:
        cfg = {}
    cfg.setdefault("project_dir", "")
    cfg.setdefault("log_files", [])
    return cfg


CFG_LOCK = threading.Lock()


def save_cfg(cfg):
    with CFG_LOCK:
        CFG_FILE.write_text(json.dumps(cfg, indent=2))


def speakable(text, limit=420, pron=True):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"[*#`_>|\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    if pron:                                           # ejaan istilah teknis agar terdengar natural
        text = re.sub(r"\b(" + "|".join(PRONOUNCE) + r")\b", lambda m: PRONOUNCE[m.group(1)], text)
    return text if len(text) <= limit else text[:limit].rsplit(" ", 1)[0] + ". Detail lengkap ada di layar."


def grab_screen():
    with mss.mss() as sct:
        s = sct.grab(sct.monitors[1])
        return Image.frombytes("RGB", s.size, s.bgra, "raw", "BGRX")


def jpeg(img, max_w=1600):
    if img.width > max_w:
        img = img.resize((max_w, int(img.height * max_w / img.width)))
    buf = io.BytesIO()
    img.convert("RGB").save(buf, "JPEG", quality=80)
    return buf.getvalue()


def find_wake(text):
    """Deteksi nama 'CakraAegis' secara fuzzy (Google STT sering salah tulis: Chakra, Kakra, dst).
    Return (terpanggil?, teks_perintah_tanpa_nama)."""
    words = re.findall(r"\w+", text)
    sim = lambda a, b: difflib.SequenceMatcher(None, a.lower(), b).ratio()
    for i, w in enumerate(words):
        if len(w) >= 5 and max(sim(w, "cakra"), sim(w, "cakraaegis"), sim(w, "cakraegis")) >= 0.78:
            j = i + 1
            if j < len(words) and sim(words[j], "aegis") >= 0.6:
                j += 1
            return True, " ".join(words[:i] + words[j:]).strip()
    return False, text.strip()


def windows_mic_privacy():
    """Baca pengaturan privasi mikrofon Windows (hanya di Windows). Return teks masalah, atau None bila tidak ada."""
    try:
        import winreg
    except ImportError:
        return None
    base = r"Software\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\microphone"
    problems = []
    for sub, label in (("", "Akses mikrofon (global)"), ("\\NonPackaged", "Izinkan aplikasi desktop")):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, base + sub) as k:
                v, _ = winreg.QueryValueEx(k, "Value")
                if str(v).lower() != "allow":
                    problems.append(f"{label}: {v} (harus Allow)")
        except OSError:
            pass
    return "; ".join(problems) or None


# ============================ TTS (Indonesia, suara natural) ============================
WAKE_REPLY = f"Ya {CALL}, saya di sini. Ada yang bisa dibantu?"
BYE_REPLY = f"Siap {CALL}. Saya tetap berjaga. Panggil saja kalau perlu."
FIXED_PHRASES = [WAKE_REPLY, BYE_REPLY]


class TTSWorker:
    """Pipeline: teks -> sintesis (thread A) -> putar (thread B); kalimat berikutnya disintesis saat kalimat
    sebelumnya masih diputar. Engine berurutan: Microsoft Edge Neural (natural) -> Google TTS -> voice lokal."""

    def __init__(self, voice=None):
        self.q, self.play_q = queue.Queue(), queue.Queue(maxsize=4)
        self.enabled, self.quiet_until, self.last_play_start = True, 0.0, 0.0
        self.mode, self.voice_id, self.notices, self.engines = None, None, [], []
        self.voice = voice or TTS_VOICE
        self.pending, self.gen, self.cache, self._lock = 0, 0, {}, threading.Lock()
        self.edge_block_until, self._need_prewarm, self.edge_down, self._notice_t = 0.0, False, False, {}
        threading.Thread(target=self._synth_loop, daemon=True).start()
        threading.Thread(target=self._play_loop, daemon=True).start()

    @property
    def speaking(self):
        return self.pending > 0

    def _done(self):
        with self._lock:
            self.pending = max(0, self.pending - 1)

    def say(self, text):
        if self.enabled and text and text.strip():
            with self._lock:
                self.pending += 1
            self.q.put((self.gen, text))

    def set_voice(self, voice):
        self.voice = voice
        self.cache.clear()
        self._need_prewarm = True

    def stop(self):
        """Hentikan suara yang sedang diputar dan kosongkan antrean."""
        self.gen += 1
        for q in (self.q, self.play_q):
            while True:
                try:
                    q.get_nowait()
                    self._done()
                except queue.Empty:
                    break

    @staticmethod
    def _com():
        try:
            import comtypes
            comtypes.CoInitialize()          # perlu untuk SAPI5 Windows di dalam thread
        except Exception:
            pass

    def _ensure(self, mods, pips, notice=None):
        """Pastikan modul ada; jika belum, pasang otomatis lewat pip (sekali saja)."""
        import importlib

        def ok():
            importlib.invalidate_caches()
            try:
                for m in mods:
                    importlib.import_module(m)
                return True
            except ImportError:
                return False

        if ok():
            return True
        marker, key = Path(tempfile.gettempdir()) / "cakra_pip_attempt.json", ",".join(pips)
        try:
            tried = json.loads(marker.read_text())
        except Exception:
            tried = {}
        if time.time() - tried.get(key, 0) < 86400:      # sudah dicoba <24 jam lalu: jangan pip install tiap dibuka
            return False
        if notice:
            self.notices.append(notice)
        tried[key] = time.time()
        try:
            marker.write_text(json.dumps(tried))
        except OSError:
            pass
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", *pips], capture_output=True, timeout=300)
        except Exception as e:
            print("Auto-install gagal:", e)
        return ok()

    def _notice_once(self, key, text, every=300):
        if time.time() - self._notice_t.get(key, 0) > every:
            self._notice_t[key] = time.time()
            self.notices.append(text)

    def _probe(self):
        if self._ensure(("edge_tts", "pygame"), ["edge-tts", "pygame"],
                        "📦 Memasang suara natural (edge-tts & pygame), sekali saja sekitar 1 menit…"):
            self.engines.append("edge")
        if self._ensure(("gtts", "pygame"), ["gTTS", "pygame"]):
            self.engines.append("gtts")
        try:
            eng = pyttsx3.init()
            for v in eng.getProperty("voices"):
                if any(k in f"{v.id} {v.name} {v.languages}".lower() for k in ID_VOICE_KEYS):
                    self.voice_id = v.id
                    break
            eng.stop()
        except Exception as e:
            print("TTS probe error:", e)
        self.mode = self.engines[0] if self.engines else "pyttsx3"
        if "edge" in self.engines:
            self.notices.append("✅ Suara natural aktif: Microsoft Neural (Ardi, cowok). Butuh internet.")
        elif "gtts" in self.engines:
            self.notices.append("ℹ️ Suara natural (Edge) belum tersedia, memakai Google TTS yang lebih kaku. "
                                "Coba: python -m pip install edge-tts lalu restart.")
        else:
            self.notices.append("⚠️ Suara natural belum terpasang. Jalankan:  python -m pip install edge-tts pygame  "
                                "lalu restart aplikasi.")

    def _synth_edge(self, text, path):
        import asyncio
        import edge_tts

        async def go():
            await asyncio.wait_for(
                edge_tts.Communicate(text, self.voice, rate=TTS_RATE, pitch=TTS_PITCH).save(path), 10)

        asyncio.run(go())

    @staticmethod
    def _synth_gtts(text, path):
        from gtts import gTTS
        gTTS(text=text, lang="id").save(path)

    def _synth(self, text):
        key = (self.voice, text)
        hit = self.cache.get(key)
        if hit and os.path.exists(hit):
            return hit
        path = os.path.join(tempfile.gettempdir(), f"cakra_{abs(hash(key))}_{int(time.time() * 1000)}.mp3")
        last, done = None, False
        for eng in self.engines:
            if eng == "edge":
                if time.time() < self.edge_block_until:
                    continue                              # Edge baru gagal: istirahat sebentar, pakai cadangan
                err = None
                for _ in range(2):                        # coba 2x sebelum menyerah (gangguan jaringan sesaat)
                    try:
                        self._synth_edge(text, path)
                        err = None
                        break
                    except Exception as e:
                        err = e
                if err is None:
                    if self.edge_down:
                        self.edge_down = False
                        self.notices.append("✅ Suara natural (Ardi) kembali aktif.")
                    done = True
                    break
                last, self.edge_down, self.edge_block_until = err, True, time.time() + 45
                print("TTS edge gagal:", err)
                self._notice_once("edge", f"⚠️ Suara natural (Edge) gagal: {str(err)[:120]}. Sementara dipakai suara cadangan "
                                          "yang terdengar BERBEDA. Solusi: python -m pip install -U edge-tts lalu restart.")
            else:
                try:
                    self._synth_gtts(text, path)
                    done = True
                    break
                except Exception as e:
                    last = e
                    print("TTS gtts gagal:", e)
        if not done:
            raise RuntimeError(str(last) if last else "tidak ada engine suara online")
        if len(text) <= 80:                               # frasa pendek disimpan agar berikutnya instan
            self.cache[key] = path
        return path

    def _prewarm(self):
        self._need_prewarm = False
        for p in FIXED_PHRASES:
            try:
                self._synth(p)
            except Exception:
                pass

    def _synth_loop(self):
        self._com()
        self._probe()
        self._prewarm()
        while True:
            gen, text = self.q.get()
            if gen != self.gen:
                self._done()
                continue
            if self._need_prewarm:
                self._prewarm()
            item = ("text", None, text)
            if self.engines:
                try:
                    item = ("file", self._synth(text), text)
                except Exception as e:
                    print("Sintesis gagal, pakai voice lokal:", e)
            self.play_q.put((gen, item))

    def _speak_local(self, text):
        """Voice lokal hanya dipakai bila ada voice INDONESIA. Kalau tidak, lebih baik diam daripada beraksen Inggris."""
        if not self.voice_id:
            self._notice_once("nolocal", "⚠️ Suara online sedang tidak tersedia dan tidak ada voice Indonesia lokal, jadi jawaban "
                                         "hanya ditampilkan (tidak dibacakan agar tidak beraksen Inggris).")
            return
        self._speak_pyttsx3(text)

    def _speak_pyttsx3(self, text):
        eng = pyttsx3.init()
        eng.setProperty("rate", 178)
        if self.voice_id:
            eng.setProperty("voice", self.voice_id)
        eng.say(text)
        eng.runAndWait()
        eng.stop()

    def _play_file(self, path, gen):
        import pygame
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy() and gen == self.gen:
            time.sleep(0.02)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()

    def _play_loop(self):
        self._com()
        while True:
            gen, (kind, path, text) = self.play_q.get()
            try:
                if gen == self.gen:
                    self.last_play_start = time.time()
                    if kind == "file":
                        try:
                            self._play_file(path, gen)
                        except Exception as e:
                            print("Putar file gagal, pakai voice lokal:", e)
                            self._speak_local(text)
                    else:
                        self._speak_local(text)
            except Exception as e:
                print("TTS error:", e)
            finally:
                if kind == "file" and path not in self.cache.values():
                    try:
                        os.remove(path)
                    except OSError:
                        pass
                self._done()
                self.quiet_until = time.time() + 0.5   # cegah AI mendengar suaranya sendiri


class SentenceSpeaker:
    """Memecah teks yang mengalir (streaming) menjadi kalimat dan langsung dibacakan. Kode tidak dibacakan."""
    END = re.compile(r"(?<=[.!?])\s+|\n+")

    def __init__(self, tts, limit=420):
        self.tts, self.buf, self.spoken, self.limit, self.cut = tts, "", 0, limit, False

    def feed(self, delta):
        self.buf += delta
        if self.buf.count("```") % 2:                      # sedang di dalam blok kode, tunggu sampai tertutup
            return
        self.buf = re.sub(r"```.*?```", " ", self.buf, flags=re.S)
        parts = self.END.split(self.buf)
        self.buf = parts.pop()                              # sisa kalimat yang belum selesai
        for p in parts:
            self._say(p)

    def finish(self):
        if self.buf.count("```") % 2:
            self.buf = self.buf.split("```")[0]
        self.buf = re.sub(r"```.*?```", " ", self.buf, flags=re.S)
        self._say(self.buf)
        self.buf = ""

    def _say(self, s):
        s = speakable(s, limit=10_000)
        if not s or self.cut:
            return
        if self.spoken + len(s) > self.limit:
            self.cut = True
            self.tts.say("Detail lengkapnya ada di layar.")
            return
        self.spoken += len(s)
        self.tts.say(s)


# ============================ OTAK AI ============================
TRANSIENT = ("503", "unavailable", "429", "resource_exhausted", "500", "internal", "deadline",
             "overloaded", "timed out", "timeout", "connection", "respons kosong")
THINK_VARIANTS = ("budget0", "minimal", "low", "none")      # cara mematikan/meminimalkan "thinking" agar cepat
EXCLUDE_WORDS = ("tts", "image", "audio", "live", "native", "embedding", "robotics", "computer")


class Brain:
    def __init__(self, key=None, forced_model=None):
        key = key or os.getenv("GEMINI_API_KEY")
        if not key:
            raise RuntimeError("API key Gemini belum diisi.")
        self.client = genai.Client(api_key=key, http_options=types.HttpOptions(api_version="v1beta", timeout=20000))
        self.history, self.screen_note, self.lock = [], "", threading.Lock()
        self.forced, self.cands, self.tv, self.dead = forced_model, None, 0, set()
        self.model = {"fast": None, "deep": None}      # model yang terakhir berhasil, per mode

    # ---- pemilihan model ----
    def _candidates(self):
        """Cari model flash yang tersedia untuk API key ini. fast = flash-lite dulu (cepat, untuk ngobrol),
        deep = flash biasa (untuk analisis kode/log/layar)."""
        if self.cands is None:
            if self.forced:
                self.cands = {"fast": [self.forced], "deep": [self.forced]}
                return self.cands
            found = []
            try:
                for m in self.client.models.list():
                    name = (m.name or "").replace("models/", "")
                    if "generateContent" in (getattr(m, "supported_actions", None) or ["generateContent"]):
                        found.append(name)
            except Exception as e:
                print("Gagal mengambil daftar model:", e)
            normal, lite = [], []
            for n in found:
                if any(w in n for w in EXCLUDE_WORDS):
                    continue
                m = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-flash(-lite)?(-preview.*)?", n)
                if m:
                    key = (1 if m.group(3) else 0, -float(m.group(1)), n)
                    (lite if m.group(2) else normal).append(key)
                elif n == "gemini-flash-latest":
                    normal.append((0.5, 0, n))
            normal = [k[2] for k in sorted(normal)]
            lite = [k[2] for k in sorted(lite)]
            deep = (normal + lite) or list(FALLBACK_MODELS)
            self.cands = {"fast": (lite + normal) or list(FALLBACK_MODELS), "deep": deep}
        return self.cands

    def _order(self, mode):
        cur, c = self.model[mode], [m for m in self._candidates()[mode] if m not in self.dead]
        return ([cur] + [m for m in c if m != cur]) if cur in c else list(c)

    def _config(self):
        kw = {"system_instruction": SYSTEM_PROMPT}
        v = THINK_VARIANTS[self.tv]
        if v == "budget0":
            kw["thinking_config"] = types.ThinkingConfig(thinking_budget=0)
        elif v == "minimal":
            kw["thinking_config"] = types.ThinkingConfig(thinking_level="MINIMAL")
        elif v == "low":
            kw["thinking_config"] = types.ThinkingConfig(thinking_level="LOW")
        return types.GenerateContentConfig(**kw)

    @staticmethod
    def _code(s, code):
        """Kode HTTP sebagai angka utuh (agar '400' di dalam '14003ms' tidak salah dikira)."""
        return re.search(rf"(?<!\d){code}(?!\d)", s) is not None

    @classmethod
    def _is_quota(cls, e):
        s = str(e)
        low = s.lower()
        return cls._code(s, 429) or "resource_exhausted" in low or ("quota" in low and "exceed" in low)

    @classmethod
    def _reason(cls, e):
        """Ringkas error API jadi alasan singkat yang mudah dipahami."""
        s = str(e)
        low = s.lower()
        if cls._is_quota(e):
            return "kuota/batas permintaan habis (429)"
        if cls._code(s, 503) or "unavailable" in low or "overloaded" in low or "high demand" in low:
            return "server sedang sibuk (503)"
        if cls._code(s, 404) or "not_found" in low:
            return "model tidak tersedia/sudah dihentikan (404)"
        if "timeout" in low or "timed out" in low:
            return "timeout"
        if "respons kosong" in low:
            return "respons kosong"
        return s[:90]

    def _classify(self, e, retry, model=None):
        """Tentukan langkah setelah error: again (ganti varian thinking), retry, next (model lain), raise."""
        s = str(e)
        low = s.lower()
        quota = self._is_quota(e)
        if (not quota and self.tv < len(THINK_VARIANTS) - 1
                and ("thinking" in low or "budget" in low or "invalid_argument" in low or self._code(s, 400))):
            self.tv += 1                 # kemungkinan pengaturan thinking tidak didukung model ini: coba varian lain
            return "again"
        if self._code(s, 404) or "not_found" in low:
            if model and not self.forced:
                self.dead.add(model)     # model sudah dihentikan: jangan dicoba lagi
            return "next"
        if quota:
            return "next"                # kuota habis: mengulang di model yang sama percuma
        transient = (any(self._code(s, c) for c in (503, 500))
                     or any(w in low for w in ("unavailable", "internal", "deadline", "overloaded", "timed out",
                                               "timeout", "connection", "respons kosong")))
        if transient:
            return "retry" if retry == 0 else "next"
        return "raise"

    def _fail(self, fails):
        """Pesan gagal yang menyebut alasan SETIAP model (bukan hanya error terakhir)."""
        detail = "; ".join(f"{m}: {r}" for m, r in fails)
        reasons = " ".join(r for _, r in fails)
        if "429" in reasons:
            tip = "Kemungkinan kuota API gratis habis: tunggu ±1 menit (atau sampai besok), atau cek pemakaian di aistudio.google.com."
        elif "503" in reasons or "timeout" in reasons:
            tip = "Server Google sedang padat. Coba lagi beberapa detik lagi."
        else:
            tip = "Periksa API key, koneksi internet, dan nama model."
        return RuntimeError(f"Semua model Gemini gagal → {detail}. {tip}")

    # ---- panggilan ke model ----
    def _gen(self, contents, mode="deep"):
        fails, deadline = [], time.time() + 20
        for m in self._order(mode)[:5]:
            if time.time() > deadline:
                break
            retry = 0
            while True:
                try:
                    r = self.client.models.generate_content(model=m, contents=contents, config=self._config())
                    text = (r.text or "").strip()
                    if not text:
                        raise RuntimeError("503 respons kosong")
                    self.model[mode] = m
                    return text
                except Exception as e:
                    act = self._classify(e, retry, m)
                    if act == "again":
                        continue
                    if act == "retry":
                        retry += 1
                        time.sleep(0.6)
                        continue
                    fails.append((m, self._reason(e)))
                    if act == "next":
                        break
                    raise
        raise self._fail(fails)

    @staticmethod
    def _parts(text, image=None):
        p = [types.Part.from_text(text=text)]
        if image is not None:
            p.append(types.Part.from_bytes(data=jpeg(image), mime_type="image/jpeg"))
        return p

    def _contents(self, text, image):
        if image is None and self.screen_note:
            text += f"\n\n[Pengamatan layar terakhir: {self.screen_note}]"
        with self.lock:
            hist = list(self.history[-14:])
        contents = [types.Content(role=r, parts=[types.Part.from_text(text=t)]) for r, t in hist]
        contents.append(types.Content(role="user", parts=self._parts(text, image)))
        return contents

    def chat_stream(self, text, image=None, on_delta=None):
        """Obrolan streaming: teks keluar kata demi kata (tampil & dibacakan segera, tanpa menunggu selesai)."""
        contents = self._contents(text, image)
        mode = "deep" if image is not None else "fast"
        full, fails, deadline = "", [], time.time() + 20
        for m in self._order(mode)[:5]:
            if time.time() > deadline:
                break
            retry = 0
            while True:
                try:
                    for ch in self.client.models.generate_content_stream(model=m, contents=contents,
                                                                         config=self._config()):
                        d = getattr(ch, "text", None) or ""
                        if d:
                            full += d
                            if on_delta:
                                on_delta(d)
                    if not full.strip():
                        raise RuntimeError("503 respons kosong")
                    break
                except Exception as e:
                    if full.strip():                 # sudah ada teks yang tampil: pakai apa adanya
                        break
                    act = self._classify(e, retry, m)
                    if act == "again":
                        continue
                    if act == "retry":
                        retry += 1
                        time.sleep(0.6)
                        continue
                    fails.append((m, self._reason(e)))
                    if act == "next":
                        break
                    raise
            if full.strip():
                self.model[mode] = m
                with self.lock:
                    self.history += [("user", text), ("model", full.strip())]
                return full.strip()
        raise self._fail(fails)

    def once(self, prompt, image=None, mode="deep"):
        return self._gen([types.Content(role="user", parts=self._parts(prompt, image))], mode)

    def remember(self, report):
        with self.lock:
            self.history += [("user", "[Laporan keamanan otomatis yang baru kamu buat]\n" + report[:3500]),
                             ("model", f"Baik {CALL}, laporan itu saya ingat.")]


# ============================ JALUR 1: LOG ============================
class ThreatEngine:
    PATTERNS = {
        "SQL Injection": r"(?i)(union(\s|\+|%20)+select|(\s|\+|%20)or(\s|\+|%20)+1(=|%3d)1|sleep\(\d+\)|information_schema|%27(\s|\+|%20)*or|' ?or ?'1)",
        "XSS": r"(?i)(<script|%3cscript|onerror=|onload=|javascript:|alert\()",
        "Path Traversal": r"(?i)(\.\./|%2e%2e%2f|\.\.%2f|/etc/passwd|win\.ini)",
        "Command Injection": r"(?i)((;|\|\||&&|%3b)\s*(cat|ls|wget|curl|nc|bash|sh)\b|\$\(|cmd=|exec\()",
        "Scanner/Bot": r"(?i)(sqlmap|nikto|nmap|masscan|acunetix|wpscan|dirbuster|gobuster|nuclei)",
        "Probing file sensitif": r"(?i)(/\.env|/\.git/|phpmyadmin|/\.aws/|id_rsa|backup\.sql|wp-config)",
    }
    IP_RE = re.compile(r"^(\d{1,3}(?:\.\d{1,3}){3}|[0-9a-fA-F:]{6,})")
    STATUS_RE = re.compile(r'"\s(\d{3})\s')
    REQ_RE = re.compile(r'"(?:GET|POST|PUT|DELETE|PATCH|HEAD)\s+(\S+)')
    FAIL_RE = re.compile(r"(?i)failed password|authentication failure|invalid user")
    HIST_CAP = 8

    def __init__(self, on_event, on_info, on_offsets=None):
        self.on_event, self.on_info, self.on_offsets = on_event, on_info, on_offsets
        self.pos = {}                       # posisi baca terakhir per file (tetap ada saat engine di-restart)
        self.rx = {k: re.compile(v) for k, v in self.PATTERNS.items()}
        self.files, self.running, self.gen = [], False, 0
        self.stats = collections.defaultdict(int)
        self.req = collections.defaultdict(collections.deque)
        self.fail = collections.defaultdict(collections.deque)
        self.cool, self.hist_mode, self.hist_found, self.hist_skipped = {}, False, 0, 0

    def start(self, files, offsets=None, scan_first=()):
        """offsets = posisi baca tersimpan dari sesi sebelumnya. File yang BARU ditambahkan (scan_first) dipindai ekornya
        sekali; file lama hanya dibaca baris barunya, sehingga isi lama tidak terdeteksi ulang tiap aplikasi dibuka."""
        self.files = [f for f in files if os.path.exists(f)]
        known = {f: p for f, p in (offsets or {}).items() if f in self.files}
        known.update({f: p for f, p in self.pos.items() if f in self.files})
        self.pos = {f: p for f, p in self.pos.items() if f in self.files}     # lupakan log yang sudah dihapus
        self.running, self.gen = True, self.gen + 1
        threading.Thread(target=self._loop, args=(self.gen, known, set(scan_first)), daemon=True).start()

    def forget(self, f):
        self.pos.pop(f, None)
        self.stats.pop(f, None)

    def _flush(self):
        if self.on_offsets:
            self.on_offsets(dict(self.pos))

    def stop(self):
        self.running = False

    @staticmethod
    def _decode(raw):
        # .replace("\x00") agar log UTF-16 (hasil `echo >>` PowerShell) tetap terbaca
        return raw.decode("utf-8", "ignore").replace("\x00", "")

    def _scan(self, f, start, end, first):
        """Pindai byte [start, end) sebagai data lama (tanpa deteksi laju). first=True: file baru ditambahkan."""
        start = max(start, end - 262_144)
        with open(f, "rb") as fh:
            fh.seek(start)
            lines = self._decode(fh.read(end - start)).splitlines()[-2000:]
        self.hist_mode, self.hist_found, self.hist_skipped = True, 0, 0
        for line in lines:
            self._inspect(line, rate=False)
        self.hist_mode = False
        self.stats[f] += len(lines)
        if not lines and not first:
            return
        extra = f" (+{self.hist_skipped} lainnya disembunyikan)" if self.hist_skipped else ""
        what = "baris terakhir dipindai" if first else "baris baru sejak aplikasi terakhir dibuka dipindai"
        self.on_info(f"📄 {os.path.basename(f)}: {len(lines)} {what}, "
                     f"{self.hist_found} pola serangan ditemukan{extra}. Pemantauan real-time aktif.")

    def _loop(self, gen, known, scan_first):
        for f in self.files:
            try:
                size = os.path.getsize(f)
                if f in scan_first:
                    self._scan(f, 0, size, True)
                elif f in known:
                    saved = known[f] if known[f] <= size else 0     # log di-rotate/dikosongkan saat aplikasi tertutup
                    if size > saved:
                        self._scan(f, saved, size, False)           # hanya baris yang muncul sejak terakhir dibuka
                self.pos[f] = size                                  # file tanpa catatan posisi: mulai dari sekarang
            except OSError as e:
                self.on_info(f"⚠️ Gagal membaca {f}: {e}")
        self._flush()
        while self.running and gen == self.gen:
            changed = False
            for f in [x for x in list(self.pos) if x in self.files]:
                try:
                    size, cur = os.path.getsize(f), self.pos.get(f)
                    if cur is None:
                        continue
                    if size < cur:
                        cur = 0                                      # log di-rotate
                    if size > cur:
                        with open(f, "rb") as fh:
                            fh.seek(cur)
                            data = self._decode(fh.read(size - cur))
                        if gen != self.gen or f not in self.pos:     # engine di-restart / log dihapus saat membaca
                            continue
                        self.pos[f] = size
                        changed = True
                        for line in data.splitlines():
                            self.stats[f] += 1
                            self._inspect(line)
                    elif f in self.pos:
                        self.pos[f] = cur
                except OSError:
                    pass
            if changed:
                self._flush()
            time.sleep(1)

    def _emit(self, kind, ip, line, count=1):
        now = time.time()
        if now - self.cool.get((kind, ip), 0) < 120:      # anti-spam per jenis+IP
            return
        if self.hist_mode:
            if self.hist_found >= self.HIST_CAP:
                self.hist_skipped += 1
                return
            self.hist_found += 1
        self.cool[(kind, ip)] = now
        m = self.REQ_RE.search(line)
        self.on_event({"type": kind, "ip": ip, "line": line[:400], "count": count,
                       "path": unquote(m.group(1)) if m else ""})

    def _inspect(self, line, rate=True):
        m = self.IP_RE.match(line)
        ip = m.group(1) if m else "?"
        for kind, rx in self.rx.items():
            if rx.search(line):
                self._emit(kind, ip, line)
        if not rate or ip == "?":
            return                                        # deteksi laju hanya untuk baris live
        now, st = time.time(), self.STATUS_RE.search(line)
        q = self.req[ip]
        q.append(now)
        while q and now - q[0] > 60:
            q.popleft()
        if len(q) >= 300:
            self._emit("Flood/DDoS", ip, line, len(q))
        if (st and st.group(1) in ("401", "403")) or self.FAIL_RE.search(line):
            f = self.fail[ip]
            f.append(now)
            while f and now - f[0] > 60:
                f.popleft()
            if len(f) >= 10:
                self._emit("Brute Force Login", ip, line, len(f))


# ============================ JALUR 2: KODE ============================
class CodeGuard:
    SECRET_RE = re.compile(r"""(?i)((?:api[_-]?key|secret|passwd|password|token|private[_-]?key)\s*[:=]\s*)(['"])[^'"\n]{6,}\2""")
    KEY_RE = re.compile(r"AIza[0-9A-Za-z_\-]{30,}|AKIA[0-9A-Z]{16}")
    STOP = {"php", "html", "www", "com", "http", "https", "index", "api", "get", "post", "the", "css", "png", "jpg"}
    SENSITIVE = ("login", "auth", "upload", "query", "db", "user", "admin", "session")

    def __init__(self):
        self.files, self.cache, self.last_truncated = {}, {}, 0

    def load(self, root):
        files, dirs = {}, 0
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d not in SKIP_DIRS]
            dirs += 1
            for f in fn:
                p = Path(dp) / f
                if p.suffix.lower() in CODE_EXTS and not f.startswith(".env"):
                    try:
                        if p.stat().st_size <= MAX_FILE_BYTES:
                            files[str(p.relative_to(root))] = p
                    except OSError:
                        pass
                if len(files) >= MAX_FILES:
                    break
            if len(files) >= MAX_FILES or dirs > 5000:       # folder raksasa: jangan telusuri selamanya
                break
        self.files, self.cache = files, {}
        return len(files)

    def read(self, rel):
        if rel not in self.cache:
            try:
                t = self.files[rel].read_text(errors="ignore")
            except OSError:
                t = ""
            t = self.SECRET_RE.sub(r"\1\2***REDACTED***\2", t)       # rahasia tidak dikirim ke AI
            self.cache[rel] = self.KEY_RE.sub("***REDACTED***", t)
        return self.cache[rel]

    @staticmethod
    def _chunks(txt, n=6000):
        """Pecah teks per baris menjadi potongan <= n karakter. Return [(nomor_baris_awal, teks)]."""
        parts, cur, size, start = [], [], 0, 1
        for no, line in enumerate(txt.splitlines(keepends=True), 1):
            while len(line) > n:                              # baris sangat panjang (mis. file minified)
                if cur:
                    parts.append((start, "".join(cur)))
                    cur, size = [], 0
                parts.append((no, line[:n]))
                line = line[n:]
            if cur and size + len(line) > n:
                parts.append((start, "".join(cur)))
                cur, size = [], 0
            if not cur:
                start = no
            cur.append(line)
            size += len(line)
        if cur:
            parts.append((start, "".join(cur)))
        return parts or [(1, "")]

    def relevant(self, paths, n=3, cap=7000):
        kws = {k.lower() for p in paths for k in re.findall(r"[A-Za-z_]{3,}", p)} - self.STOP
        scored = []
        for rel in self.files:
            txt, name = self.read(rel).lower(), rel.lower()
            s = sum(txt.count(k) for k in kws) + 5 * sum(k in name for k in kws) + sum(w in name for w in self.SENSITIVE)
            scored.append((s, rel))
        top = [r for s, r in sorted(scored, reverse=True)[:n] if s > 0]
        out = []
        for r in top:                                         # ambil potongan yang paling banyak memuat kata kunci serangan
            best = max(self._chunks(self.read(r), cap), key=lambda ch: sum(ch[1].lower().count(k) for k in kws))
            out.append(f"### FILE: {r} (mulai baris {best[0]})\n{best[1]}")
        return "\n\n".join(out) or "(tidak ada file yang cocok)"

    def batches(self, cap=14000, limit=6):
        """Seluruh isi tiap file diaudit (dipecah per 6000 karakter), baris diberi nomor asli agar laporan akurat."""
        out, cur, size = [], [], 0
        for rel in sorted(self.files, key=lambda r: not any(w in r.lower() for w in self.SENSITIVE)):
            chunks = self._chunks(self.read(rel))
            for k, (start, txt) in enumerate(chunks, 1):
                numbered = "".join(f"{start + i}| {ln}" for i, ln in enumerate(txt.splitlines(keepends=True)))
                label = f"### FILE: {rel}" + (f" (bagian {k}/{len(chunks)})" if len(chunks) > 1 else "")
                if cur and size + len(numbered) > cap:
                    out.append(cur)
                    cur, size = [], 0
                cur.append(f"{label}\n{numbered}")
                size += len(numbered)
        if cur:
            out.append(cur)
        self.last_truncated = max(0, len(out) - limit)
        return ["\n\n".join(b) for b in out[:limit]]


# ============================ SUARA (MIKROFON + WAKE WORD) ============================
class MicEngine:
    """Rekam mic terus-menerus, deteksi suara sendiri (VAD), kirim ke Google STT.
    Punya meter level + sensitivitas supaya mudah didiagnosis."""
    CHUNK = 1024
    DEAD_SECONDS = 1.5      # keheningan total (level 0) selama ini = mic tidak mengirim suara sama sekali

    def __init__(self, app):
        self.app, self.thread, self.running, self.rate = app, None, False, 16000
        self.cur, self.channels, self.auto_pick = (None, 0, 1), 1, None
        self.min_rms, self.noise, self.level, self.thr = 250.0, 150.0, 0.0, 250.0
        self.manual_until = 0.0
        self.q, self.rec = queue.Queue(), sr.Recognizer()
        threading.Thread(target=self._recognize_loop, daemon=True).start()

    @staticmethod
    def list_devices():
        """Semua perangkat input (MME/DirectSound/WASAPI; host API default dulu). Return [(index, nama, host, rate, kanal)]."""
        import pyaudio
        pa, out = pyaudio.PyAudio(), []
        try:
            default_host = pa.get_default_host_api_info()["index"]
            for i in range(pa.get_device_count()):
                d = pa.get_device_info_by_index(i)
                if d.get("maxInputChannels", 0) <= 0:
                    continue
                host = pa.get_host_api_info_by_index(d["hostApi"])["name"]
                if "WDM" in host:                    # WDM-KS sering tidak stabil
                    continue
                out.append((d["hostApi"] != default_host, i, d["name"], host, int(d.get("defaultSampleRate", 0) or 0),
                            int(d.get("maxInputChannels", 1) or 1)))
            out.sort()
        finally:
            pa.terminate()
        return [(i, n, h, r, ch) for _, i, n, h, r, ch in out]

    def start(self, device_index=None, rate=None, channels=None):
        self.stop()
        import pyaudio
        pa = pyaudio.PyAudio()
        if device_index is None:
            try:
                device_index = pa.get_default_input_device_info()["index"]
            except Exception:
                device_index = None
        try:
            info = pa.get_device_info_by_index(device_index)
        except Exception:
            info = {}
        max_ch = int(info.get("maxInputChannels", 1) or 1)
        rates = [rate] if rate else [16000, int(info.get("defaultSampleRate", 0) or 44100)]
        chans = [channels] if channels else sorted({1, min(2, max_ch)})     # mic array laptop kadang wajib 2 kanal
        stream, last = None, None
        for r in rates:
            for ch in chans:
                try:
                    stream = pa.open(format=pyaudio.paInt16, channels=ch, rate=r, input=True,
                                     frames_per_buffer=self.CHUNK, input_device_index=device_index)
                    self.rate, self.channels = r, ch
                    break
                except Exception as e:
                    last = e
            if stream is not None:
                break
        if stream is None:
            pa.terminate()
            raise RuntimeError(str(last))
        self.cur, self.running = (device_index, self.rate, self.channels), True
        self.thread = threading.Thread(target=self._capture_loop, args=(stream, pa), daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.5)
        self.thread, self.level = None, 0.0

    @staticmethod
    def _mono(data, ch):
        """Ubah audio multi-kanal jadi mono: ambil kanal yang paling keras (kanal lain pada mic array bisa kosong)."""
        if ch <= 1:
            return data
        s = array.array("h", data)
        return max((s[k::ch] for k in range(ch)), key=lambda c: sum(abs(x) for x in c)).tobytes()

    @staticmethod
    def _rms(data):
        s = array.array("h", data)
        return math.sqrt(sum(x * x for x in s) / len(s)) if s else 0.0

    def _capture_loop(self, stream, pa):
        tts, rate, nch = self.app.tts, self.rate, self.channels
        pre = collections.deque(maxlen=6)
        frames, speaking, start, last_voice, manual, zeros, alive = [], False, 0.0, 0.0, False, 0, 0
        try:
            while self.running:
                data = self._mono(stream.read(self.CHUNK, exception_on_overflow=False), nch)
                rms, now = self._rms(data), time.time()
                self.level = rms
                zeros = zeros + 1 if rms == 0 else 0
                alive = alive + 1 if rms > 0 else 0
                if alive >= 8 and self.auto_pick:                         # mic pilihan otomatis terbukti menghasilkan suara
                    name, self.auto_pick = self.auto_pick, None
                    self.app.ui(lambda n=name: self.app._mic_confirm(n))
                if zeros * self.CHUNK / rate > self.DEAD_SECONDS:     # hening total: mic tidak mengirim suara
                    self.running = False
                    self.app.ui(self.app.on_mic_dead)
                    break
                if tts.speaking or now < tts.quiet_until:      # jangan dengar suara sendiri
                    pre.clear()
                    frames, speaking = [], False
                    continue
                self.thr = max(self.noise * 2.5, self.min_rms)
                if rms > self.thr:
                    if not speaking:
                        speaking, frames, start = True, list(pre), now
                        manual = now < self.manual_until
                    last_voice = now
                elif not speaking:
                    self.noise = min(0.95 * self.noise + 0.05 * rms, 2000.0)
                if speaking:
                    frames.append(data)
                    if now - last_voice > SILENCE_END or now - start > 15:
                        if last_voice - start >= 0.25:
                            self.q.put((b"".join(frames), manual, rate, last_voice))
                        frames, speaking = [], False
                else:
                    pre.append(data)
        except Exception as e:
            was_running, self.running = self.running, False
            if was_running:                       # mis. headset dicabut saat dipakai
                self.app.ui(lambda m=str(e): self.app.on_mic_error(m))
        finally:
            try:
                stream.stop_stream()
                stream.close()
                pa.terminate()
            except Exception:
                pass

    def _recognize_loop(self):
        while True:
            raw, manual, rate, t_end = self.q.get()
            try:
                t0 = time.time()
                text = self.rec.recognize_google(sr.AudioData(raw, rate, 2), language=LANG_STT)
                stt = time.time() - t0
                self.app.ui(lambda t=text, m=manual, te=t_end, d=stt: self.app.handle_speech(t, m, te, d))
            except sr.UnknownValueError:
                self.app.ui(lambda: self.app.set_heard("(ada suara, tapi tidak jelas dikenali — coba lebih dekat/jelas)"))
            except sr.RequestError as e:
                self.app.ui(lambda m=str(e): self.app.set_heard(f"⚠️ STT gagal, cek internet: {m}"))
            except Exception as e:
                self.app.ui(lambda m=str(e): self.app.set_heard(f"⚠️ STT error: {m}"))


# ============================ LIVE SCREEN ============================
class LiveScreen:
    """Layar ditangkap terus-menerus di background. Frame terbaru selalu siap dilampirkan ke obrolan,
    dan (mode Watch) dianalisis otomatis saat layar berubah, paralel dengan percakapan."""

    def __init__(self, app):
        self.app, self.frame, self.ts, self.prev = app, None, 0.0, None
        self.running, self.changed, self.last_analysis = False, False, 0.0

    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self._capture, daemon=True).start()
            threading.Thread(target=self._watch, daemon=True).start()

    def stop(self):
        self.running = False

    def _capture(self):
        with mss.mss() as sct:
            while self.running:
                try:
                    s = sct.grab(sct.monitors[1])
                    img = Image.frombytes("RGB", s.size, s.bgra, "raw", "BGRX")
                    small = img.resize((96, 54)).convert("L")
                    if self.prev is None or ImageStat.Stat(ImageChops.difference(small, self.prev)).mean[0] > 1.5:
                        self.changed = True
                    self.prev, self.frame, self.ts = small, img, time.time()
                except Exception as e:
                    print("Capture error:", e)
                    time.sleep(3)
                time.sleep(CAPTURE_INTERVAL)

    def _watch(self):
        app = self.app
        while self.running:
            time.sleep(1)
            if (not app.watch_sw.get() or not app.brain or app.watch_busy or not self.changed
                    or self.frame is None or time.time() - self.last_analysis < WATCH_INTERVAL):
                continue
            self.changed, self.last_analysis, app.watch_busy = False, time.time(), True
            try:
                res = app.brain.once(WATCH_PROMPT, self.frame)
                app.ui(lambda r=res: app.on_watch_result(r))
            except Exception as e:
                app.ui(lambda m=str(e)[:100]: app.watch_lbl.configure(text=f"⚠️ analisis gagal: {m}"))
            finally:
                app.watch_busy = False


# ============================ APLIKASI ============================
class StreamBubble:
    """Bubble jawaban yang terisi bertahap saat teks di-stream dari AI."""

    def __init__(self, app):
        self.app = app
        self.row = ctk.CTkFrame(app.chat, fg_color="transparent")
        self.row.pack(fill="x", pady=5, padx=8)
        bubble = ctk.CTkFrame(self.row, corner_radius=14, fg_color=C["ai"])
        bubble.pack(side="left", padx=4, fill="x", expand=True)
        self.lbl = ctk.CTkLabel(bubble, text="…", wraplength=640, justify="left", anchor="w", font=("Segoe UI", 13))
        self.lbl.pack(padx=14, pady=10, anchor="w")

    def set(self, text):
        self.lbl.configure(text=text)
        self.app.after(30, lambda: self.app.chat._parent_canvas.yview_moveto(1.0))

    def finish(self, text):
        self.row.destroy()
        self.app.add_message("ai", text)


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        self.title("CakraAegis")
        self.geometry("1100x680+30+10")
        self.minsize(900, 560)
        self.configure(fg_color=C["bg"])

        self.cfg = load_cfg()
        self.ui_q, self.events_q = queue.Queue(), queue.Queue()
        self.tts, self.guard, self.brain = TTSWorker(self.cfg.get("voice")), CodeGuard(), None
        self.engine = ThreatEngine(self.on_threat, lambda m: self.ui(lambda: self.add_message("ai", m)),
                                   lambda o: self.ui(lambda: self._store_offsets(o)))
        self._fresh = set()
        self.mic, self.live = MicEngine(self), LiveScreen(self)
        self.active_until, self._log_txt, self._last_alert = 0.0, "", ""
        self.chat_busy = self.job_busy = self.watch_busy = False
        self.mic_q = queue.Queue()
        threading.Thread(target=self._mic_manager, daemon=True).start()
        self._hang_file = open("cakra_hang.log", "w")   # terisi otomatis bila aplikasi macet >15 dtk (untuk diagnosis)
        self.t_end, self.lat, self.lat_pending = None, {}, False
        self._mic_tried, self._mic_retry = set(), 0

        self._build_ui()
        self.after(100, self._tick)
        self.after(200, self._maximize)      # agar kolom input tidak keluar dari layar
        self._init_brain()
        threading.Thread(target=self._analysis_loop, daemon=True).start()

        if self.cfg.get("project_dir") and os.path.isdir(self.cfg["project_dir"]):
            self._load_project(self.cfg["project_dir"], announce=False)
        self.toggle_voice()
        self.toggle_logs()
        self.add_message("ai", "CakraAegis online. Panggil \"CakraAegis\" lalu ngobrol, atau ketik di kolom bawah. "
                               "Nyalakan 👁️ Live screen agar saya ikut melihat layar Anda sambil ngobrol. "
                               "Mic tidak merespons? Lihat meter level di sidebar dan teks \"👂 Terdengar\" di bawah chat.")

    def _maximize(self):
        try:
            self.state("zoomed")
        except Exception:
            try:
                self.attributes("-zoomed", True)
            except Exception:
                pass

    @property
    def busy(self):
        return self.chat_busy or self.job_busy

    # ---------- UI ----------
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        side = ctk.CTkScrollableFrame(self, width=270, corner_radius=0, fg_color=C["panel"])
        side.grid(row=0, column=0, sticky="ns")

        ctk.CTkLabel(side, text="🛡️ CakraAegis", font=("Segoe UI", 24, "bold")).pack(pady=(14, 0))
        ctk.CTkLabel(side, text="Guardian AI • Voice • Live Screen", text_color=C["muted"],
                     font=("Segoe UI", 11)).pack(pady=(0, 8))
        self.state_lbl = ctk.CTkLabel(side, text="● Standby", text_color=C["muted"], font=("Segoe UI", 14, "bold"))
        self.state_lbl.pack(pady=(0, 6))

        self.voice_sw = ctk.CTkSwitch(side, text="Selalu mendengarkan", command=self.toggle_voice)
        self.voice_sw.select()
        self.voice_sw.pack(padx=14, pady=4, anchor="w")
        self.tts_sw = ctk.CTkSwitch(side, text="Suara CakraAegis",
                                    command=lambda: setattr(self.tts, "enabled", bool(self.tts_sw.get())))
        self.tts_sw.select()
        self.tts_sw.pack(padx=14, pady=4, anchor="w")
        self.voice_menu = ctk.CTkOptionMenu(side, values=["Ardi (cowok)", "Gadis (cewek)"], width=240,
                                            dynamic_resizing=False, command=self._on_voice)
        self.voice_menu.set("Gadis (cewek)" if "Gadis" in self.tts.voice else "Ardi (cowok)")
        self.voice_menu.pack(padx=14, pady=(0, 4))
        self.log_sw = ctk.CTkSwitch(side, text="Pantau log real-time", command=self.toggle_logs)
        self.log_sw.select()
        self.log_sw.pack(padx=14, pady=4, anchor="w")

        self._section(side, "MIKROFON")
        self.mic_var = ctk.StringVar(value="Default sistem")
        self.mic_menu = ctk.CTkOptionMenu(side, values=["Default sistem"], variable=self.mic_var, width=240,
                                          dynamic_resizing=False, command=self._on_mic)
        self.mic_menu.pack(padx=14, pady=3)
        ctk.CTkButton(side, text="🔄 Segarkan daftar mic", fg_color="transparent", border_width=1,
                      command=self.refresh_mics).pack(padx=14, fill="x", pady=(0, 3))
        ctk.CTkButton(side, text="🔒 Buka pengaturan mic Windows", fg_color="transparent", border_width=1,
                      command=self._open_mic_settings).pack(padx=14, fill="x", pady=(0, 3))
        ctk.CTkLabel(side, text="Sensitivitas (kiri = lebih peka)", text_color=C["muted"],
                     font=("Segoe UI", 10)).pack(padx=14, anchor="w")
        self.sens = ctk.CTkSlider(side, from_=60, to=1500, command=self._on_sens)
        self.sens.set(self.cfg.get("min_rms", 250))
        self.mic.min_rms = float(self.cfg.get("min_rms", 250))
        self.sens.pack(padx=14, fill="x", pady=(2, 4))
        self.level_bar = ctk.CTkProgressBar(side, height=10)
        self.level_bar.set(0)
        self.level_bar.pack(padx=14, fill="x")
        self.level_lbl = ctk.CTkLabel(side, text="Level 0 / ambang 250", text_color=C["muted"], font=("Segoe UI", 10))
        self.level_lbl.pack(padx=14, anchor="w")
        ctk.CTkButton(side, text="🎤 Bicara sekarang (tanpa panggil nama)", command=self.listen_once).pack(padx=14, fill="x", pady=4)
        self.lat_lbl = ctk.CTkLabel(side, text="⏱️ Jeda respons: -", text_color=C["muted"], wraplength=235,
                                    justify="left", font=("Segoe UI", 10))
        self.lat_lbl.pack(padx=14, anchor="w")
        ctk.CTkButton(side, text="⏹️ Hentikan suara", fg_color="transparent", border_width=1,
                      command=self.tts.stop).pack(padx=14, fill="x", pady=4)

        self._section(side, "LIVE SCREEN")
        self.live_sw = ctk.CTkSwitch(side, text="👁️ AI melihat layar saat ngobrol", command=self._sync_live)
        self.live_sw.pack(padx=14, pady=4, anchor="w")
        self.watch_sw = ctk.CTkSwitch(side, text="Deteksi ancaman layar otomatis", command=self._sync_live)
        self.watch_sw.pack(padx=14, pady=4, anchor="w")
        self.watch_lbl = ctk.CTkLabel(side, text="👁️ Live screen mati", text_color=C["muted"], wraplength=235,
                                      justify="left", font=("Segoe UI", 10))
        self.watch_lbl.pack(padx=14, anchor="w")

        self._section(side, "SETUP")
        ctk.CTkButton(side, text="🔑 API key Gemini", command=self.set_key).pack(padx=14, fill="x", pady=3)
        ctk.CTkButton(side, text="📁 Pilih folder proyek", command=self.pick_project).pack(padx=14, fill="x", pady=3)
        self.proj_lbl = ctk.CTkLabel(side, text=self.cfg.get("project_dir") or "folder belum dipilih",
                                     text_color=C["muted"], wraplength=235, justify="left", font=("Segoe UI", 10))
        self.proj_lbl.pack(padx=14, anchor="w")
        ctk.CTkButton(side, text="📄 Tambah file log", command=self.add_log).pack(padx=14, fill="x", pady=(8, 3))
        self.log_lbl = ctk.CTkLabel(side, text="belum ada log", text_color=C["muted"], wraplength=235,
                                    justify="left", font=("Segoe UI", 10))
        self.log_lbl.pack(padx=14, anchor="w")
        self.log_menu = ctk.CTkOptionMenu(side, values=["🗑️ Hapus file log…"], width=240, dynamic_resizing=False,
                                          command=self._remove_log)
        self.log_menu.pack(padx=14, pady=(4, 0))
        ctk.CTkButton(side, text="🧹 Kosongkan daftar log", fg_color="transparent", border_width=1,
                      command=self.clear_logs).pack(padx=14, fill="x", pady=3)

        self._section(side, "AKSI CEPAT")
        for txt, cmd in (("🧪 Tes simulasi serangan", self.simulate_attack), ("🔍 Audit kode proyek", self.run_audit),
                         ("🖥️ Analisis layar sekarang", self.analyze_screen), ("🧹 Bersihkan chat", self.clear_chat)):
            ctk.CTkButton(side, text=txt, fg_color="transparent", border_width=1, command=cmd).pack(padx=14, fill="x", pady=3)
        ctk.CTkLabel(side, text="Gunakan hanya pada aset milik Anda.", text_color=C["muted"],
                     font=("Segoe UI", 10)).pack(pady=12)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.grid(row=0, column=1, sticky="nsew", padx=16, pady=16)
        main.grid_rowconfigure(0, weight=1)
        main.grid_columnconfigure(0, weight=1)
        self.chat = ctk.CTkScrollableFrame(main, fg_color=C["panel"], corner_radius=16)
        self.chat.grid(row=0, column=0, sticky="nsew")
        self.heard_lbl = ctk.CTkLabel(main, text="👂 Terdengar: -", text_color="#79c0ff", anchor="w", font=("Segoe UI", 12))
        self.heard_lbl.grid(row=1, column=0, sticky="ew", padx=8, pady=(8, 0))
        bar = ctk.CTkFrame(main, fg_color="transparent")
        bar.grid(row=2, column=0, sticky="ew", pady=(6, 0))
        bar.grid_columnconfigure(0, weight=1)
        self.entry = ctk.CTkEntry(bar, height=44, corner_radius=22, placeholder_text="Ketik pesan lalu Enter, atau panggil \"CakraAegis…\"")
        self.entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.entry.bind("<Return>", lambda e: self.send_text())
        ctk.CTkButton(bar, text="Kirim", width=90, height=44, corner_radius=22, command=self.send_text).grid(row=0, column=1)

    @staticmethod
    def _section(parent, text):
        ctk.CTkLabel(parent, text=text, text_color=C["muted"], font=("Segoe UI", 10, "bold")).pack(padx=14, pady=(14, 3), anchor="w")

    def add_message(self, role, text, color=None):
        is_user = role == "user"
        row = ctk.CTkFrame(self.chat, fg_color="transparent")
        row.pack(fill="x", pady=5, padx=8)
        bubble = ctk.CTkFrame(row, corner_radius=14, fg_color=color or (C["user"] if is_user else C["ai"]))
        if is_user:
            bubble.pack(side="right", padx=4)
        else:
            bubble.pack(side="left", padx=4, fill="x", expand=True)
        for i, seg in enumerate(re.split(r"```[\w+-]*\n?(.*?)```", text, flags=re.S)):
            seg = seg.strip("\n")
            if not seg.strip():
                continue
            if i % 2 == 0:
                ctk.CTkLabel(bubble, text=seg, wraplength=640, justify="left", anchor="w",
                             font=("Segoe UI", 13)).pack(padx=14, pady=(8, 4), anchor="w")
            else:
                box = ctk.CTkTextbox(bubble, height=min(max(seg.count("\n") + 1, 2) * 19 + 14, 340),
                                     font=("Consolas", 12), fg_color="#0d1117", wrap="none")
                box.insert("1.0", seg)
                box.configure(state="disabled")
                box.pack(fill="x", padx=12, pady=(2, 2))
                ctk.CTkButton(bubble, text="Salin kode", width=90, height=24, command=lambda s=seg: (
                    self.clipboard_clear(), self.clipboard_append(s))).pack(anchor="e", padx=12, pady=(0, 6))
        self.after(80, lambda: self.chat._parent_canvas.yview_moveto(1.0))

    def set_heard(self, text):
        self.heard_lbl.configure(text=f"👂 Terdengar: {text}")

    def clear_chat(self):
        for w in self.chat.winfo_children():
            w.destroy()
        if self.brain:
            with self.brain.lock:
                self.brain.history.clear()

    def ui(self, fn):
        self.ui_q.put(fn)

    def _tick(self):
        """Loop UI. Kebal error: satu callback gagal tidak mematikan aplikasi."""
        try:
            faulthandler.dump_traceback_later(15, file=self._hang_file)   # di-reset tiap tick; menulis jejak bila UI macet
            while True:
                try:
                    fn = self.ui_q.get_nowait()
                except queue.Empty:
                    break
                try:
                    fn()
                except Exception:
                    traceback.print_exc()
            while self.tts.notices:
                self.add_message("ai", self.tts.notices.pop(0))
            if self.busy:
                self.state_lbl.configure(text="● Berpikir…", text_color=C["warn"])
            elif not self.voice_sw.get():
                self.state_lbl.configure(text="● Mikrofon mati", text_color=C["muted"])
            elif time.time() < self.active_until:
                self.state_lbl.configure(text="● Aktif – saya mendengarkan", text_color=C["ok"])
            else:
                self.state_lbl.configure(text="● Standby – panggil “CakraAegis”", text_color=C["muted"])
            lvl, thr = self.mic.level, self.mic.thr
            self.level_bar.set(min(lvl / (thr * 2), 1.0))
            self.level_bar.configure(progress_color=C["ok"] if lvl > thr else "#1f6feb")
            self.level_lbl.configure(text=f"Level {int(lvl)} / ambang {int(thr)}" + ("  ← terdeteksi suara" if lvl > thr else ""))
            if self.lat_pending and self.t_end and self.tts.last_play_start > self.t_end:
                self.lat_pending = False
                gap = self.tts.last_play_start - self.t_end
                self.lat_lbl.configure(text=f"⏱️ Jeda sampai suara mulai: {gap:.1f} dtk\n"
                                            f"(STT {self.lat.get('stt') or 0:.1f} • AI kata pertama {self.lat.get('ai') or 0:.1f})")
            txt = "\n".join(f"• {os.path.basename(f)} ({self.engine.stats.get(f, 0)} baris dibaca)"
                            for f in self.cfg["log_files"]) or "belum ada log"
            if txt != self._log_txt:
                self._log_txt = txt
                self.log_lbl.configure(text=txt)
                self._refresh_log_menu()
        except Exception:
            traceback.print_exc()
        finally:
            self.after(200, self._tick)

    # ---------- Mic & Live screen ----------
    def _mic_index(self):
        v = self.mic_var.get()
        return int(v.split(":")[0]) if v and v[0].isdigit() else None

    def _on_mic(self, value):
        self.cfg["mic_name"] = value.split(": ", 1)[1] if value[:1].isdigit() else ""
        save_cfg(self.cfg)
        self.toggle_voice()

    def _on_voice(self, value):
        voice = "id-ID-GadisNeural" if "Gadis" in value else "id-ID-ArdiNeural"
        self.cfg["voice"] = voice
        save_cfg(self.cfg)
        self.tts.set_voice(voice)
        self.tts.say(f"Halo {CALL}, ini suara baru saya.")

    def _set_mic_menu(self, devs):
        labels = [f"{i}: {n} [{h}]" for i, n, h, _, _ in devs]
        self.mic_menu.configure(values=["Default sistem"] + labels)
        saved = self.cfg.get("mic_name", "")
        self.mic_var.set(next((lb for lb in labels if lb.split(": ", 1)[1] == saved), "Default sistem"))

    def _on_sens(self, value):
        self.mic.min_rms = float(value)
        self.cfg["min_rms"] = float(value)
        save_cfg(self.cfg)

    # ---------- Mikrofon: semua operasi PyAudio berjalan di thread terpisah (UI tidak boleh "Not Responding") ----------
    def toggle_voice(self):
        self._mic_retry = 0
        self.mic_q.put(("start",) if self.voice_sw.get() else ("stop",))

    def refresh_mics(self):
        self._mic_retry = 0
        self.voice_sw.select()
        self.mic_q.put(("start",))

    def on_mic_error(self, msg):          # dipanggil dari thread mic via ui(): stream putus (mis. headset dicabut)
        if self.voice_sw.get():
            self.mic_q.put(("error", msg))

    def on_mic_dead(self):                # mic terbuka tapi level 0 terus
        if self.voice_sw.get():
            self.mic_q.put(("dead",))

    def _mic_manager(self):
        while True:
            cmd = self.mic_q.get()
            try:
                if cmd[0] == "start":
                    self._mic_do_start()
                elif cmd[0] == "stop":
                    self.mic.stop()
                elif cmd[0] == "dead":
                    self._mic_do_dead()
                elif cmd[0] == "error":
                    self._mic_do_error(cmd[1])
            except Exception as e:
                msg = str(e)[:200]
                self.ui(lambda: self.add_message("ai", f"⚠️ Mikrofon error: {msg}"))

    def _mic_do_start(self):
        self.mic.stop()                       # tutup stream dulu supaya daftar perangkat benar-benar dibaca ulang
        self._mic_tried = set()
        self.ui(lambda: self.set_heard("⏳ Menyiapkan mikrofon…"))
        try:
            devs = MicEngine.list_devices()
        except Exception:
            devs = []
        self.ui(lambda: self._set_mic_menu(devs))
        saved = self.cfg.get("mic_name", "")
        idx = next((i for i, n, h, _, _ in devs if f"{n} [{h}]" == saved), None)    # pilihan dicocokkan berdasarkan NAMA
        try:
            self.mic.start(idx)
        except Exception as e:
            first = str(e)
            self.ui(lambda: self.set_heard("⏳ Mic pilihan gagal dibuka, mencari mic lain yang bisa dipakai…"))
            if not self._mic_open_any(idx):
                self.ui(lambda: self._mic_failed(first))
            return
        self.ui(lambda: self.set_heard("(mikrofon aktif — coba bicara, perhatikan meter level di sidebar)"))

    def _mic_open_any(self, skip_idx):
        """Mic pilihan gagal dibuka (mis. error -9999): coba 'Default sistem', lalu perangkat lain. True bila berhasil."""
        if skip_idx is not None:
            try:
                self.mic.start(None)
                self.ui(lambda: self.set_heard("⚠️ Mic pilihan gagal dibuka, memakai Default sistem."))
                return True
            except Exception:
                pass
        for n_try, (i, rate, ch, name) in enumerate(self._mic_candidates()):
            if n_try >= 12:
                break
            if i == skip_idx:
                continue
            try:
                self.mic.start(i, rate, ch)
            except Exception:
                continue
            self.mic.auto_pick = name
            self.ui(lambda: self._mic_switched(name, i, rate, ch))
            return True
        return False

    def _mic_failed(self, msg):
        self.voice_sw.deselect()
        self.set_heard("⚠️ Mikrofon gagal dibuka (lihat penjelasan di chat)")
        priv = windows_mic_privacy()
        hint = ("Error -9999 di Windows biasanya berarti akses mikrofon DITOLAK Windows, atau mic sedang dipakai aplikasi lain "
                "(Zoom/Discord/Teams/tab Chrome yang memakai mic). " if "-9999" in msg else "")
        self.add_message("ai", f"⚠️ Mikrofon tidak bisa dibuka (semua perangkat dicoba): {msg}\n{hint}"
                               + (f"Terdeteksi di Windows → {priv}\n" if priv else "")
                               + "Langkah: klik tombol 🔒 Buka pengaturan mic Windows di sidebar → pastikan \"Microphone access\" "
                                 "dan \"Let desktop apps access your microphone\" menyala; tutup aplikasi lain yang memakai mic; "
                                 "lalu nyalakan lagi \"Selalu mendengarkan\" atau tekan 🔄 Segarkan daftar mic.")

    def _open_mic_settings(self):
        opener = getattr(os, "startfile", None)
        if opener:
            try:
                opener("ms-settings:privacy-microphone")
                return
            except OSError:
                pass
        self.add_message("ai", "Tombol ini khusus Windows. Di macOS: System Settings > Privacy & Security > Microphone, lalu izinkan "
                               "Terminal/VS Code (aplikasi yang menjalankan Python). Di Linux: cek pengaturan Sound > Input.")

    def _mic_do_error(self, msg):
        self._mic_retry += 1
        n = self._mic_retry
        if n > 3:
            self.ui(lambda: (self.voice_sw.deselect(), self.add_message(
                "ai", f"⚠️ Mikrofon terputus dan gagal tersambung ulang: {msg}\nPilih mic di sidebar lalu tekan 🔄 Segarkan daftar mic.")))
            return
        self.ui(lambda: self.set_heard(f"⚠️ Mic terputus ({msg[:60]}). Menyambung ulang… ({n}/3)"))
        time.sleep(MIC_RETRY_DELAY)
        self._mic_do_start()

    def _mic_candidates(self):
        """Urutan percobaan saat mic hening total: perangkat terpilih dulu, lalu semua perangkat/rate/kanal lain."""
        try:
            devs = MicEngine.list_devices()
        except Exception:
            return []
        cur = self.mic.cur[0]
        devs.sort(key=lambda d: d[0] != cur)
        return [(i, rate, ch, f"{n} [{h}]")
                for i, n, h, r, mc in devs
                for rate in dict.fromkeys((16000, r or 44100))
                for ch in sorted({1, min(2, mc)})]

    def _mic_do_dead(self):
        """Mic hening total (level 0): coba perangkat/rate/kanal lain otomatis."""
        self._mic_tried.add(self.mic.cur)
        for idx, rate, ch, name in self._mic_candidates():
            if (idx, rate, ch) in self._mic_tried:
                continue
            try:
                self.mic.start(idx, rate, ch)
            except Exception:
                self._mic_tried.add((idx, rate, ch))
                continue
            self.mic.auto_pick = name                # disimpan permanen baru setelah terbukti ada suara
            self.ui(lambda: self._mic_switched(name, idx, rate, ch))
            return
        self.mic.stop()
        self.ui(self._mic_all_dead)

    def _mic_confirm(self, name):
        """Mic hasil pilihan otomatis terbukti menghasilkan suara: baru sekarang pilihannya disimpan."""
        self.cfg["mic_name"] = name
        save_cfg(self.cfg)

    def _mic_switched(self, name, idx, rate, ch):
        self.mic_var.set(f"{idx}: {name}")
        self.set_heard(f"⚠️ Mic sebelumnya hening total. Mencoba: {name} @ {rate} Hz, {ch} kanal …")

    def _mic_all_dead(self):
        self.voice_sw.deselect()
        priv = windows_mic_privacy()
        self.add_message("ai", "🎙️ Semua mikrofon yang saya coba hanya mengirim keheningan total (level 0), jadi suara "
                               "Anda tidak sampai ke aplikasi.\n"
                               + (f"Terdeteksi di Windows → {priv}\n" if priv else "")
                               + "Cek: (1) Settings > Privacy & security > Microphone: nyalakan \"Microphone access\" dan "
                                 "\"Let desktop apps access your microphone\"; (2) Settings > System > Sound > Input > pilih "
                                 "\"Microphone Array\": pastikan tidak di-mute, volume > 0, dan \"Allow\" (bukan Don't allow); "
                                 "(3) cek tombol/ikon mute mic di keyboard dan antivirus yang memblokir mikrofon; "
                                 "(4) tutup Zoom/Discord/Meet. Lalu nyalakan lagi \"Selalu mendengarkan\". "
                                 "Tes terpisah: python mic_test.py")
        self.tts.say(f"Mikrofon tidak mengirim suara, {CALL}. Cek izin mikrofon Windows.")

    def listen_once(self):
        """Mode tes: bicara langsung tanpa wake word. Jika ini jalan tapi 'CakraAegis' tidak, masalahnya di pengenalan nama."""
        if not self.voice_sw.get():
            self.voice_sw.select()
            self.toggle_voice()
        self.mic.manual_until = time.time() + 8
        self.set_heard("🎤 Silakan bicara sekarang… (8 detik)")

    def _sync_live(self):
        if self.live_sw.get() or self.watch_sw.get():
            self.live.start()
            self.watch_lbl.configure(text="👁️ Live screen aktif, menunggu perubahan layar…")
        else:
            self.live.stop()
            self.watch_lbl.configure(text="👁️ Live screen mati")

    def _screen_for_chat(self, text):
        if self.live_sw.get():
            if self.live.frame is not None and time.time() - self.live.ts < 30:
                return self.live.frame
            return grab_screen()
        return grab_screen() if "layar" in text.lower() else None

    def on_watch_result(self, res):
        st = re.search(r"STATUS:\s*(AMAN|WASPADA|BAHAYA)", res.upper())
        level = st.group(1) if st else "AMAN"
        rg = re.search(r"RINGKAS:\s*(.+)", res)
        ring = rg.group(1).strip() if rg else speakable(res, 140, pron=False)
        self.brain.screen_note = ring
        icon = {"AMAN": "✅", "WASPADA": "⚠️", "BAHAYA": "🚨"}[level]
        self.watch_lbl.configure(text=f"{icon} {level} • {datetime.datetime.now():%H:%M:%S}\n{ring[:110]}")
        if level == "AMAN" or difflib.SequenceMatcher(None, self._last_alert, ring).ratio() > 0.8:
            return
        self._last_alert = ring
        self._publish(res, "layar-live", f"{icon} Live screen: {level}", speak=False,
                      color={"WASPADA": "#4d3b0f", "BAHAYA": "#5a1e1e"}[level])
        self.tts.say(("Bahaya! " if level == "BAHAYA" else "Peringatan. ") + speakable(ring, 300))
        self.active_until = time.time() + CONVO_WINDOW

    # ---------- AI / API key ----------
    def _init_brain(self, prompt=True):
        try:
            self.brain = Brain(self.cfg.get("api_key"), self.cfg.get("model"))
        except Exception as e:
            self.brain = None
            self.add_message("ai", f"⚠️ {e}\nKlik tombol 🔑 API key Gemini di sidebar lalu tempel kuncinya "
                                   "(atau set env GEMINI_API_KEY lalu buka ulang terminal).")
            if prompt:
                self.after(700, self.set_key)
            return
        threading.Thread(target=self._selftest, daemon=True).start()

    def _selftest(self):
        try:
            t0 = time.time()
            self.brain.once("Balas satu kata saja: siap", mode="fast")
            dt = time.time() - t0
            self.ui(lambda: self.add_message("ai", f"✅ Terhubung ke Gemini (chat: {self.brain.model['fast']}, {dt:.1f} dtk)."))
        except Exception as e:
            msg = str(e)[:350]
            self.ui(lambda: self.add_message("ai", f"❌ Gemini error: {msg}\nPeriksa API key (🔑), kuota, dan koneksi internet."))

    def set_key(self):
        key = ctk.CTkInputDialog(text="Tempel GEMINI_API_KEY Anda:", title="API Key").get_input()
        if key and key.strip():
            self.cfg["api_key"] = key.strip()
            save_cfg(self.cfg)
            self._init_brain(prompt=False)

    def need_brain(self):
        if self.brain:
            return True
        self.say_and_show(f"AI belum siap, {CALL}. Klik tombol API key di sidebar dulu.")
        return False

    # ---------- Pengaturan sumber ----------
    def pick_project(self):
        d = filedialog.askdirectory(title="Pilih folder proyek yang dilindungi")
        if d:
            self._load_project(d)

    def _load_project(self, d, announce=True):
        self.proj_lbl.configure(text=f"{d}\n⏳ memindai folder…")
        threading.Thread(target=self._load_project_worker, args=(d, announce), daemon=True).start()

    def _load_project_worker(self, d, announce):
        try:
            n = self.guard.load(d)
        except Exception as e:
            msg = str(e)[:200]
            self.ui(lambda: self.add_message("ai", f"⚠️ Gagal membaca folder proyek: {msg}"))
            return
        self.ui(lambda: self._project_loaded(d, n, announce))

    def _project_loaded(self, d, n, announce):
        self.cfg["project_dir"] = d
        save_cfg(self.cfg)
        self.proj_lbl.configure(text=f"{d}\n({n} file kode terindeks)")
        if announce:
            self.say_and_show(f"Proyek dimuat, {n} file kode terindeks. Password dan API key di kode otomatis "
                              "disamarkan sebelum dikirim ke AI.")

    def add_log(self):
        f = filedialog.askopenfilename(title="Pilih file log (access.log, error.log, auth.log, dll)")
        if f:
            self._register_log(f)

    def _register_log(self, f):
        if f not in self.cfg["log_files"]:
            self.cfg["log_files"].append(f)
            self._fresh.add(f)                    # file baru: ekornya dipindai sekali
            save_cfg(self.cfg)
        self.log_sw.select()
        self.toggle_logs()

    def toggle_logs(self):
        if self.log_sw.get() and self.cfg["log_files"]:
            self.engine.start(self.cfg["log_files"], self.cfg.get("log_offsets", {}), self._fresh)
            self._fresh = set()
        else:
            self.engine.stop()

    def _store_offsets(self, offsets):
        """Simpan posisi baca tiap log, supaya saat aplikasi dibuka lagi isi lama tidak dipindai ulang."""
        cur = self.cfg.setdefault("log_offsets", {})
        offsets = {f: o for f, o in offsets.items() if f in self.cfg["log_files"]}   # abaikan log yang sudah dihapus dari daftar
        if cur != offsets:
            cur.clear()
            cur.update(offsets)
            save_cfg(self.cfg)

    def _refresh_log_menu(self):
        labels = [f"{i + 1}. {os.path.basename(f)}" for i, f in enumerate(self.cfg["log_files"])]
        self.log_menu.configure(values=labels or ["(tidak ada log)"])
        self.log_menu.set("🗑️ Hapus file log…")

    def _remove_log(self, choice):
        try:
            self._drop_logs([self.cfg["log_files"][int(choice.split(".")[0]) - 1]])
        except (ValueError, IndexError):
            self._refresh_log_menu()

    def clear_logs(self):
        self._drop_logs(list(self.cfg["log_files"]))

    def _drop_logs(self, paths):
        """Hapus log dari daftar pantauan. File ASLI tidak dihapus (kecuali file uji cakra_test.log buatan aplikasi ini)."""
        test_deleted = False
        for f in paths:
            if f in self.cfg["log_files"]:
                self.cfg["log_files"].remove(f)
            self.cfg.get("log_offsets", {}).pop(f, None)
            self.engine.forget(f)
            if Path(f).name == "cakra_test.log":
                try:
                    os.remove(f)
                    test_deleted = True
                except OSError:
                    pass
        save_cfg(self.cfg)
        self.toggle_logs()
        self._refresh_log_menu()
        if paths:
            self.add_message("ai", f"🗑️ {len(paths)} file log dihapus dari daftar pantauan; isi lamanya tidak akan dipindai lagi. "
                                   "File aslinya tidak dihapus" + (" (kecuali file uji cakra_test.log yang ikut dihapus)." if test_deleted else "."))

    def simulate_attack(self):
        """Tulis 1 baris log UJI (UTF-8) ke cakra_test.log agar seluruh jalur deteksi bisa dites."""
        fn = Path("cakra_test.log").resolve()
        ip = f"203.0.113.{random.randint(2, 250)}"
        ts = datetime.datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0700")
        with open(fn, "a", encoding="utf-8") as f:
            f.write(f'{ip} - - [{ts}] "GET /login.php?id=1%27%20OR%201=1-- HTTP/1.1" 200 512 "-" "Mozilla/5.0"\n')
        self.add_message("ai", f"🧪 Baris log uji ditulis ke {fn}. Seharusnya terdeteksi sebagai SQL Injection.")
        self._register_log(str(fn))

    # ---------- Percakapan ----------
    def say_and_show(self, text):
        self.add_message("ai", text)
        self.tts.say(speakable(text))

    def handle_speech(self, text, manual=False, t_end=None, stt=None):
        self.set_heard(text)
        woke, cmd = find_wake(text)
        now = time.time()
        if not (woke or manual or now < self.active_until):
            return                                   # bukan untuk CakraAegis, abaikan
        self.active_until = now + CONVO_WINDOW
        if not cmd:
            return self.say_and_show(WAKE_REPLY)
        low = cmd.lower()
        if len(low.split()) <= 5 and any(w in low for w in BYE_WORDS):
            self.active_until = 0
            return self.say_and_show(BYE_REPLY)
        if "audit" in low and "kode" in low:
            self.add_message("user", cmd)
            return self.run_audit()
        self.ask(cmd, t_end, stt)

    def send_text(self):
        t = self.entry.get().strip()
        if t:
            self.entry.delete(0, "end")
            self.active_until = time.time() + CONVO_WINDOW
            self.ask(t)

    def ask(self, text, t_end=None, stt=None):
        self.add_message("user", text)
        if self.chat_busy:
            return self.add_message("ai", f"Sebentar {CALL}, saya masih memproses pertanyaan sebelumnya.")
        if not self.need_brain():
            return
        self.chat_busy = True
        self.t_end, self.lat, self.lat_pending = t_end or time.time(), {"stt": stt}, True
        threading.Thread(target=self._ask_worker, args=(text,), daemon=True).start()

    def _ask_worker(self, text):
        """Jawaban di-stream: teks tampil kata demi kata dan kalimat pertama langsung dibacakan."""
        holder, state, t0 = {}, {"txt": "", "ui": 0.0}, time.time()
        speaker = SentenceSpeaker(self.tts)
        self.ui(lambda: holder.update(w=StreamBubble(self)))

        def on_delta(d):
            state["txt"] += d
            if "ai" not in self.lat:
                self.lat["ai"] = time.time() - t0
            speaker.feed(d)
            now = time.time()
            if now - state["ui"] > 0.08:
                state["ui"], t = now, state["txt"]
                self.ui(lambda t=t: holder["w"].set(t))

        try:
            ans = self.brain.chat_stream(text, self._screen_for_chat(text), on_delta)
            speaker.finish()
        except Exception as e:
            ans = f"⚠️ Gagal menghubungi AI: {str(e)[:300]}"
            self.lat_pending = False
            self.tts.say(f"Maaf {CALL}, AI sedang gangguan. Coba lagi sebentar.")
        finally:
            self.chat_busy = False
        self.ui(lambda: holder["w"].finish(ans))
        self.active_until = time.time() + CONVO_WINDOW + 10

    # ---------- Deteksi ancaman (log -> AI + kode) ----------
    def on_threat(self, ev):
        self.events_q.put(ev)
        msg = f"🚨 {ev['type']} dari IP {ev['ip']}" + (f" ({ev['count']}x/menit)" if ev["count"] > 1 else "")
        self.ui(lambda: self.add_message("ai", f"{msg}\n{ev['line'][:200]}", "#4a1c1c"))
        if self.tts.q.empty():
            self.tts.say(f"Peringatan. Terdeteksi {ev['type']}. Saya analisis dulu.")

    def _analysis_loop(self):
        last = 0.0
        while True:
            batch = [self.events_q.get()]
            time.sleep(max(BATCH_WAIT, ANALYSIS_GAP - (time.time() - last)))          # kumpulkan event serupa
            while not self.events_q.empty() and len(batch) < 10:
                batch.append(self.events_q.get())
            last = time.time()
            if not self.brain:
                self.ui(lambda: self.add_message("ai", "⚠️ Serangan terdeteksi tapi AI belum siap. Isi API key (🔑) dulu."))
                continue
            ctx = (self.guard.relevant([e["path"] for e in batch]) if self.guard.files
                   else "(Folder proyek belum dipilih, kode tidak tersedia.)")
            ev_txt = "\n".join(f"- [{e['type']}] IP {e['ip']} x{e['count']} :: {e['line']}" for e in batch)
            try:
                res = self.brain.once(f"{THREAT_PROMPT}\n\nEVENT LOG:\n{ev_txt}\n\nKODE TERKAIT:\n{ctx}")
            except Exception as e:
                msg = str(e)[:300]
                self.ui(lambda: self.add_message("ai", f"⚠️ Analisis gagal: {msg}"))
                continue
            self._publish(res, "ancaman", "🛡️ Analisis ancaman")

    def run_audit(self):
        if not self.guard.files:
            return self.say_and_show(f"Folder proyek belum dipilih, {CALL}. Klik tombol pilih folder proyek dulu.")
        if self.job_busy:
            return self.add_message("ai", f"Sebentar {CALL}, audit/analisis lain masih berjalan.")
        if not self.need_brain():
            return
        self.job_busy = True
        self.say_and_show("Mulai audit kode. Saya kerjakan bertahap, hasilnya muncul di layar.")
        threading.Thread(target=self._audit_worker, daemon=True).start()

    def _audit_worker(self):
        ringkas = []
        try:
            for i, b in enumerate(self.guard.batches(), 1):
                try:
                    res = self.brain.once(f"{AUDIT_PROMPT}\n\n{b}")
                except Exception as e:
                    msg = str(e)[:300]
                    self.ui(lambda i=i, msg=msg: self.add_message("ai", f"⚠️ Audit bagian {i} gagal: {msg}"))
                    continue
                m = re.search(r"RINGKAS:\s*(.+)", res)
                ringkas.append(m.group(1) if m else "")
                self._publish(res, "audit", f"🔍 Audit kode (bagian {i})", speak=False)
        finally:
            self.job_busy = False
        if self.guard.last_truncated:
            n = self.guard.last_truncated
            self.ui(lambda: self.add_message("ai", f"ℹ️ {n} bagian kode belum ikut diaudit (batas per sesi). "
                                                   "Pilih folder yang lebih kecil agar semuanya terperiksa."))
        self.tts.say("Audit selesai. " + speakable(" ".join(ringkas), 350))

    def analyze_screen(self):
        if self.job_busy:
            return self.add_message("ai", f"Sebentar {CALL}, audit/analisis lain masih berjalan.")
        if not self.need_brain():
            return
        self.add_message("ai", "🖥️ Menganalisis layar saat ini…")
        img = self.live.frame if (self.live.frame is not None and time.time() - self.live.ts < 30) else grab_screen()
        self.job_busy = True
        threading.Thread(target=self._screen_worker, args=(img,), daemon=True).start()

    def _screen_worker(self, img):
        try:
            self._publish(self.brain.once(SCREEN_PROMPT, img), "layar", "🖥️ Analisis layar")
        except Exception as e:
            msg = str(e)[:300]
            self.ui(lambda: self.add_message("ai", f"⚠️ Analisis layar gagal: {msg}"))
        finally:
            self.job_busy = False

    def _publish(self, result, kind, title, speak=True, color=None):
        self.brain.remember(result)
        REPORT_DIR.mkdir(exist_ok=True)
        fn = REPORT_DIR / f"{datetime.datetime.now():%Y%m%d_%H%M%S}_{kind}.md"
        fn.write_text(result, encoding="utf-8")
        self.ui(lambda: self.add_message("ai", f"{title}\n\n{result}", color))
        if speak:
            m = re.search(r"RINGKAS:\s*(.+)", result)
            self.tts.say(speakable(m.group(1) if m else result))
            self.active_until = time.time() + CONVO_WINDOW


if __name__ == "__main__":
    App().mainloop()
