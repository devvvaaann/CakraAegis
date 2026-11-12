<a id="top"></a>

<div align="center">

<!-- <img src="assets/banner-cakraaegis.png" alt="Banner CakraAegis" width="100%"> -->

<h1>🛡️ CakraAegis</h1>

<p><b>AI-Driven Live Screen-Aware &amp; Voice-Activated Cyber Security Assistant</b></p>

<p><i>Asisten pertahanan siber ala Jarvis: mendengar, melihat, dan menjaga sistem Anda secara real-time.</i></p>

<p>
  <img src="https://img.shields.io/badge/Python-3.12.9-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python 3.12.9">
  <img src="https://img.shields.io/badge/CustomTkinter-Desktop%20UI-1F6FEB?style=for-the-badge" alt="CustomTkinter">
  <img src="https://img.shields.io/badge/Kartika%20Cyber%20Hackathon-2026-B22222?style=for-the-badge" alt="Kartika Cyber Hackathon 2026">
 
</p>

<p>
  <a href="#tentang-proyek">Tentang</a> •
  <a href="#fitur-dan-menu-utama">Fitur</a> •
  <a href="#arsitektur-dan-alur-kerja">Arsitektur</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#skenario-demo">Demo</a> •
  <a href="#instalasi-dan-quick-start">Instalasi</a> •
  <a href="#panduan-penggunaan">Penggunaan</a> •
  <a href="#catatan-keamanan-dan-batasan">Catatan</a>
</p>

</div>

---

## Daftar Isi

1. [Tentang Proyek](#tentang-proyek)
2. [Fitur dan Menu Utama](#fitur-dan-menu-utama)
3. [Arsitektur dan Alur Kerja](#arsitektur-dan-alur-kerja)
4. [Tech Stack](#tech-stack)
5. [Skenario Demo](#skenario-demo)
6. [Instalasi dan Quick Start](#instalasi-dan-quick-start)
7. [Panduan Penggunaan](#panduan-penggunaan)
8. [Catatan Keamanan dan Batasan](#catatan-keamanan-dan-batasan)

---

## Tentang Proyek

**CakraAegis** merupakan asisten siber berbasis AI interaktif yang bekerja secara real-time untuk mengamankan perimeter aplikasi web. CakraAegis memiliki kemampuan unik untuk memantau jendela kerja secara langsung (live screen-aware), mendeteksi kerentanan kode berdasarkan standar OWASP Top 10, serta mengukur tingkat keparahan (urgency severity rating) secara otomatis. Tak hanya mendeteksi, sistem ini juga dapat diajak berdialog secara komunikatif untuk memberikan rekomendasi perbaikan kode (code remediation) secara instan.

<table>
  <tr>
    <td align="center" width="25%"><h3>🎙️</h3><b>Mendengar</b><br><sub>Kontrol hands-free dengan wake word "CakraAegis" dan suara natural berbahasa Indonesia</sub></td>
    <td align="center" width="25%"><h3>👁️</h3><b>Melihat</b><br><sub>Live Screen-Aware: AI ikut membaca layar Anda saat ngobrol</sub></td>
    <td align="center" width="25%"><h3>📡</h3><b>Memantau</b><br><sub>Log server dibaca real-time dan dicocokkan dengan pola serangan</sub></td>
    <td align="center" width="25%"><h3>🛠️</h3><b>Memperbaiki</b><br><sub>Menunjuk kode yang rentan dan memberi perbaikan sebelum/sesudah</sub></td>
  </tr>
</table>

<p align="right"><a href="#top">⬆ kembali ke atas</a></p>

---

## Fitur dan Menu Utama

<table>
  <thead>
    <tr>
      <th>Kategori</th>
      <th>Menu / Tombol</th>
      <th>Fungsi</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3"><b>🎙️ Kontrol Suara dan Audio</b></td>
      <td><code>Selalu mendengarkan</code></td>
      <td>Mikrofon aktif terus dengan wake word <b>"CakraAegis"</b> (toleran terhadap salah-eja pengenalan suara seperti "Chakra" atau "Kakra"). Setelah dipanggil, asisten tetap aktif sekitar 45 detik sehingga bisa ngobrol tanpa menyebut nama lagi. Tersedia pilihan mikrofon, meter level, dan slider sensitivitas.</td>
    </tr>
    <tr>
      <td><code>Suara CakraAegis</code></td>
      <td>Jawaban dibacakan dengan Microsoft Edge Neural TTS, pilihan suara <b>Ardi</b> (cowok, bawaan) atau <b>Gadis</b> (cewek), dibaca per kalimat agar cepat. Ada cadangan Google TTS dan pyttsx3, serta tombol <code>Hentikan suara</code>.</td>
    </tr>
    <tr>
      <td><code>Bicara sekarang</code></td>
      <td>Mode bicara langsung selama 8 detik tanpa perlu menyebut wake word. Berguna untuk tes mikrofon.</td>
    </tr>
    <tr>
      <td rowspan="2"><b>👁️ Live Screen</b></td>
      <td><code>AI melihat layar saat ngobrol</code></td>
      <td>Layar ditangkap berkala dan frame terbaru otomatis dilampirkan ke setiap pertanyaan, jadi Anda cukup bertanya "ini kenapa?".</td>
    </tr>
    <tr>
      <td><code>Deteksi ancaman layar otomatis</code></td>
      <td>Saat layar berubah, AI menganalisisnya di background, paralel dengan percakapan. Jika berstatus WASPADA atau BAHAYA, muncul peringatan visual dan suara.</td>
    </tr>
    <tr>
      <td rowspan="3"><b>⚙️ Setup Proyek</b></td>
      <td><code>API key Gemini</code></td>
      <td>Memasukkan API key Google Gemini lewat dialog (atau lewat environment variable). Model Flash dipilih otomatis dari daftar model yang tersedia di akun Anda.</td>
    </tr>
    <tr>
      <td><code>Pilih folder proyek</code></td>
      <td>Mengindeks kode sumber proyek yang dilindungi. Password, token, dan API key disamarkan otomatis (<b>auto-redaction</b>), dan file <code>.env</code> dilewati, sebelum apa pun dikirim ke AI.</td>
    </tr>
    <tr>
      <td><code>Tambah file log</code></td>
      <td>Memantau <code>access.log</code>, <code>error.log</code>, <code>auth.log</code>, atau log aplikasi secara real-time. Isi lama tidak dipindai ulang saat aplikasi dibuka. Daftar bisa dikelola lewat <code>Hapus file log</code> dan <code>Kosongkan daftar log</code>.</td>
    </tr>
    <tr>
      <td rowspan="3"><b>⚡ Aksi Cepat</b></td>
      <td><code>Tes simulasi serangan</code></td>
      <td>Menulis satu baris log uji (pola SQL Injection) agar seluruh jalur deteksi sampai analisis AI bisa dites tanpa menyerang apa pun.</td>
    </tr>
    <tr>
      <td><code>Audit kode proyek</code></td>
      <td>Audit keamanan statis berkelompok terhadap kode proyek: SQL Injection, XSS, command injection, path traversal, autentikasi/sesi lemah, IDOR, upload tidak aman, secret hardcoded, CSRF, dan misconfiguration (selaras dengan kategori OWASP Top 10), lengkap dengan kode perbaikan.</td>
    </tr>
    <tr>
      <td><code>Analisis layar sekarang</code></td>
      <td>Analisis sekali jalan terhadap tampilan layar saat ini, berisi status, temuan, dan langkah penanganan.</td>
    </tr>
  </tbody>
</table>

**Pola serangan yang dideteksi pada log:** SQL Injection • XSS • Path Traversal • Command Injection • Scanner/Bot (sqlmap, nikto, dll.) • Probing file sensitif (<code>.env</code>, <code>.git</code>, dll.) • Brute Force Login • Flood/DDoS.

<p align="right"><a href="#top">⬆ kembali ke atas</a></p>

---

## Arsitektur dan Alur Kerja

<details>
<summary><b>🧩 Klik untuk membuka diagram alur dan penjelasan multi-threading</b></summary>

<br>

<pre><code> ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
 │  Mikrofon   │  │    Layar    │  │ Log server  │  │ Folder kode │
 └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
        ▼                ▼                ▼                ▼
 ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
 │ MicEngine   │  │ LiveScreen  │  │ThreatEngine │  │ CodeGuard   │
 │ VAD + STT   │  │ capture     │  │ regex + laju│  │ indeks +    │
 │ wake word   │  │ tiap 2 dtk  │  │ posisi baca │  │ auto-redact │
 └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘
        └────────────────┴───────┬────────┴────────────────┘
                                 ▼
                   ┌───────────────────────────┐
                   │ Brain (Google Gemini API) │
                   │ streaming, pilih model    │
                   │ otomatis, retry + fallback│
                   └─────────────┬─────────────┘
                                 ▼
       ┌─────────────────────────┼─────────────────────────┐
       ▼                         ▼                         ▼
 ┌─────────────┐          ┌─────────────┐          ┌─────────────┐
 │ Chat UI     │          │ TTS Worker  │          │cakra_reports│
 │ CustomTk    │          │ Edge Neural │          │ laporan .md │
 │ kode+Salin  │          │ gTTS, lokal │          └─────────────┘
 └─────────────┘          └─────────────┘</code></pre>

**Tiga jalur utama yang berjalan paralel (multi-threading):**

1. **Voice Loop dan TTS Worker.** Satu thread merekam mikrofon dan mendeteksi ucapan sendiri (VAD), thread lain mengirimnya ke Google Speech-to-Text. Setelah wake word cocok, pertanyaan dikirim ke Gemini dengan streaming. Jawaban dibacakan kalimat demi kalimat lewat dua thread TTS (sintesis dan pemutaran berjalan paralel), dan mikrofon otomatis diabaikan saat asisten bicara agar tidak mendengar suaranya sendiri.
2. **Threat Engine (Log Regex).** Satu thread membaca log yang terus bertambah, lalu mencocokkan baris dengan pola serangan dan menghitung laju (brute force dan flood) per IP. Setiap jenis serangan per IP punya jeda anti-spam, dan posisi baca disimpan agar isi lama tidak terdeteksi ulang. Event dikumpulkan, lalu dikirim ke Gemini bersama potongan kode yang relevan.
3. **CodeGuard (Auto-Redaction).** Kode proyek diindeks di background. Saat ada serangan, file dipilih berdasarkan kata kunci dari URL serangan. Sebelum dikirim ke AI, password, token, dan API key disamarkan, dan file <code>.env</code> tidak pernah dibaca.

Semua thread berkomunikasi dengan antarmuka lewat antrean (queue) yang aman, sehingga UI tidak membeku. Operasi berat seperti mikrofon, pemindaian folder, dan pemanggilan AI tidak berjalan di thread utama.

</details>

---

## Tech Stack

<details>
<summary><b>🧰 Klik untuk melihat teknologi dan library yang dipakai</b></summary>

<br>

| Komponen | Peran |
|---|---|
| **Python 3.12.9** | Bahasa pemrograman utama |
| **google-genai** | Klien Google Gemini API (analisis ancaman, audit kode, obrolan streaming) |
| **CustomTkinter** | Antarmuka desktop modern bertema gelap |
| **SpeechRecognition** | Speech-to-Text untuk bahasa Indonesia |
| **PyAudio** | Akses dan perekaman mikrofon |
| **Edge-TTS** | Suara natural Microsoft Neural (Ardi dan Gadis) |
| **pyttsx3** | Text-to-Speech lokal sebagai cadangan |
| **Pygame** | Memutar audio hasil sintesis suara |
| **MSS** | Penangkapan layar untuk Live Screen |
| **Pillow** | Pengolahan gambar (deteksi perubahan layar dan kompresi) |
| **gTTS** | Cadangan Text-to-Speech Google |

</details>

---

## Skenario Demo

<details>
<summary><b>🎬 Klik untuk melihat alur demo dalam 4 langkah</b></summary>

<br>

Alur ini bisa dicoba dalam beberapa menit tanpa menyerang sistem apa pun.

| Langkah | Yang dilakukan | Yang terjadi |
|:---:|---|---|
| **1** | Jalankan aplikasi, pilih folder proyek, lalu klik <code>Tes simulasi serangan</code> | Satu baris log uji ditulis. Muncul peringatan merah <b>SQL Injection</b> dan asisten membacakan peringatan |
| **2** | Tunggu beberapa detik | AI menganalisis serangan bersama kode proyek yang terkait, lalu menampilkan bagian yang rentan, <b>kode perbaikan</b> (bisa disalin), dan langkah respons cepat seperti blokir IP dan aturan WAF |
| **3** | Ucapkan: <i>"CakraAegis, bagaimana cara memperbaikinya?"</i> | Asisten menjawab dengan suara dan mengingat laporan tadi, jadi percakapan tetap nyambung |
| **4** | Nyalakan <code>AI melihat layar saat ngobrol</code>, buka terminal atau dashboard log, lalu tanya <i>"ini kenapa?"</i> | AI membaca isi layar dan menjelaskan temuan atau langkah penanganannya |

</details>

---

## Instalasi dan Quick Start

<details>
<summary><b>🚀 Klik untuk melihat langkah instalasi</b></summary>

<br>

<ol>
  <li>
    <b>Siapkan prasyarat:</b> Python 3.12.9, Git, mikrofon, koneksi internet, dan API key Google Gemini dari
    <a href="https://aistudio.google.com/apikey">Google AI Studio</a>.
    Pengembangan dan pengujian dilakukan di Windows. Di Linux/macOS aplikasi seharusnya bisa jalan, tetapi belum diuji penuh dan membutuhkan PortAudio serta izin mikrofon/layar.
<pre><code>Linux (Debian/Ubuntu)
sudo apt install portaudio19-dev python3-tk flac

macOS
brew install portaudio</code></pre>
  </li>
  <li>
    <b>Clone repository:</b>
<pre><code>git clone https://github.com/devvvaaann/CakraAegis.git
cd CakraAegis</code></pre>
  </li>
  <li>
    <b>Buat dan aktifkan virtual environment:</b>
<pre><code>Windows
python -m venv venv
venv\Scripts\activate

Linux / macOS
python3 -m venv venv
source venv/bin/activate</code></pre>
  </li>
  <li>
    <b>Pasang dependencies:</b>
<pre><code>pip install customtkinter SpeechRecognition pyaudio pyttsx3 mss pillow google-genai edge-tts gTTS pygame</code></pre>
  </li>
  <li>
    <b>(Opsional) Set API key lewat environment variable.</b> Bisa juga diisi lewat tombol <code>API key Gemini</code> di aplikasi.
<pre><code>Windows
setx GEMINI_API_KEY "kunci_anda"

Linux / macOS
export GEMINI_API_KEY="kunci_anda"</code></pre>
    Setelah <code>setx</code>, tutup dan buka ulang terminal.
  </li>
  <li>
    <b>Jalankan aplikasi:</b>
<pre><code>python CakraAegis.py</code></pre>
    Jika <code>edge-tts</code>, <code>gTTS</code>, atau <code>pygame</code> belum terpasang, aplikasi mencoba memasangnya otomatis saat pertama dijalankan.
  </li>
</ol>

</details>

---

## Panduan Penggunaan

<details>
<summary><b>📘 Klik untuk melihat panduan penggunaan dan daftar perintah</b></summary>

<br>

**Langkah awal di antarmuka:**

1. **Masukkan API key.** Saat pertama dibuka, dialog API key muncul otomatis. Jika terlewat, klik <code>API key Gemini</code> di sidebar. Tunggu pesan "Terhubung ke Gemini".
2. **Muat folder proyek.** Klik <code>Pilih folder proyek</code> dan arahkan ke kode website atau aplikasi yang ingin dilindungi.
3. **Tambah file log.** Klik <code>Tambah file log</code> dan pilih <code>access.log</code>, <code>error.log</code>, atau <code>auth.log</code> milik Anda. Untuk mencoba tanpa log asli, klik <code>Tes simulasi serangan</code>.
4. **Atur mikrofon.** Pilih mikrofon di sidebar, lalu bicara dan perhatikan meter level. Jika batang tidak bergerak, ganti perangkat atau tekan tombol segarkan.
5. **Nyalakan Live Screen** (opsional) jika ingin AI ikut melihat layar Anda.

**Contoh perintah suara dengan wake word "CakraAegis":**

| Ucapan | Hasil |
|---|---|
| "CakraAegis" | Asisten menjawab dan siap mendengarkan |
| "CakraAegis, jelaskan serangan terakhir tadi" | Menjelaskan laporan ancaman terakhir yang dihasilkan otomatis |
| "CakraAegis, bagaimana cara memperbaiki celah itu? Berikan kodenya" | Kode perbaikan tampil di layar dan bisa disalin (kode tidak dibacakan) |
| "CakraAegis, audit kode" | Menjalankan audit keamanan terhadap folder proyek |
| "CakraAegis, cek layar" | Menganalisis tampilan layar saat ini |
| "CakraAegis, ini kenapa?" | Dengan Live Screen aktif, AI menjawab berdasarkan layar Anda |
| "Terima kasih" atau "sudah dulu" | Asisten kembali ke mode siaga |

Panggilan ke pengguna bawaannya "Komandan". Untuk mengubahnya (misalnya menjadi "Ndan"), tambahkan <code>"panggilan": "Ndan"</code> di <code>cakra_config.json</code>, lalu restart aplikasi.

**Pemecahan masalah cepat:**

- **Mikrofon tidak terdeteksi:** pilih mikrofon lain di dropdown lalu tekan tombol segarkan. Pastikan izin mikrofon Windows menyala (<i>Privacy &amp; security</i> lalu <i>Microphone</i>, termasuk "Let desktop apps access your microphone").
- **Suara berubah atau terdengar kaku:** suara natural gagal dan aplikasi memakai cadangan. Coba <code>python -m pip install -U edge-tts</code> lalu restart.
- **Error 429 atau 503 dari Gemini:** kuota API habis atau server sedang padat. Tunggu sebentar. Pesan error menyebut alasan tiap model.
- **Aplikasi macet:** berkas <code>cakra_hang.log</code> terisi otomatis dan membantu diagnosis.

**Berkas yang dihasilkan aplikasi.** Tambahkan ke <code>.gitignore</code> agar tidak ikut ter-commit:

<pre><code>cakra_config.json
cakra_test.log
cakra_hang.log
cakra_reports/</code></pre>

</details>

---

## Catatan Keamanan dan Batasan

> [!WARNING]
> Gunakan CakraAegis **hanya pada aset milik Anda sendiri**. Aplikasi ini ditujukan untuk pertahanan (deteksi, mitigasi, dan perbaikan), bukan untuk menyerang pihak lain.

- **Data yang dikirim ke layanan eksternal:** pertanyaan teks, potongan kode proyek (secret sudah disamarkan), baris log yang terdeteksi, dan screenshot jika Live Screen aktif, semuanya ke Google Gemini. Audio dikirim ke Google Speech-to-Text, dan teks jawaban ke layanan Edge TTS. Jangan menampilkan data sensitif di layar saat Live Screen menyala.
- **API key** yang diisi lewat aplikasi tersimpan sebagai teks biasa di <code>cakra_config.json</code>. Jangan commit atau bagikan berkas tersebut.
- **Bukan pengganti WAF, IDS/IPS, atau SIEM.** CakraAegis adalah lapisan deteksi dan penasihat. Hasil AI bisa keliru, jadi verifikasi sebelum diterapkan. Patch tidak diterapkan otomatis.
- **Live Screen bukan video streaming:** layar ditangkap berkala dan dianalisis saat berubah, sehingga bersifat near real-time.
- **Edge-TTS** memakai layanan baca-nyaring Edge secara tidak resmi, sehingga sewaktu-waktu bisa berubah. Aplikasi otomatis memakai suara cadangan dan memberi tahu di chat.

---

<div align="center">

**Dibuat oleh [@devvvaaann](https://github.com/devvvaaann) - Kartika Cyber Hackathon 2026**

<a href="#top">⬆ Kembali ke atas</a>

</div>
