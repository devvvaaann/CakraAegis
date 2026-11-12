<div align="center">

  <!-- Hapus tanda komentar HTML di bawah ini jika sudah meng-upload gambar banner/thumbnail ke folder assets/ -->
  <!-- <img src="assets/banner-cakraaegis.png" alt="CakraAegis Banner" width="100%" /> -->

  <h1>🛡️ CakraAegis</h1>
  <p><b>AI-Driven Live Screen-Aware & Voice-Activated Cyber Security Assistant</b></p>

  <!-- Badges Status Proyek -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.12.9-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/AI-Google%20Gemini-FF6F00?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API">
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-2EA043?style=for-the-badge" alt="CustomTkinter">
    <img src="https://img.shields.io/badge/Hackathon-Kartika%20Cyber%202026-D73A49?style=for-the-badge" alt="Hackathon">
  </p>

  <!-- Menu Navigasi Cepat -->
  <p>
    <a href="#-tentang-proyek">🚀 Tentang Proyek</a> •
    <a href="#-fitur--menu-utama-aplikasi">✨ Fitur & Menu</a> •
    <a href="#-arsitektur--alur-kerja-sistem">⚙️ Arsitektur Sistem</a> •
    <a href="#-tech-stack--library-utama">🛠️ Tech Stack</a> •
    <a href="#-panduan-instalasi--pemasangan-quick-start">📋 Cara Instalasi</a> •
    <a href="#-panduan-penggunaan--daftar-perintah">🎮 Cara Pakai</a>
  </p>
</div>

---

## 📖 Daftar Isi Interaktif
Klik salah satu menu di bawah ini untuk langsung melompat ke bagian dokumentasi[cite: 3]:
1. [🚀 Tentang Proyek](#-tentang-proyek)
2. [✨ Fitur & Menu Utama Aplikasi](#-fitur--menu-utama-aplikasi)
3. [⚙️ Arsitektur & Alur Kerja Sistem](#%EF%B8%8F-arsitektur--alur-kerja-sistem)
4. [🛠️ Tech Stack & Library Utama](#%EF%B8%8F-tech-stack--library-utama)
5. [📸 Preview & Demo Aplikasi](#-preview--demo-aplikasi)
6. [📋 Panduan Instalasi & Pemasangan (Quick Start)](#-panduan-instalasi--pemasangan-quick-start)
7. [🎮 Panduan Penggunaan & Daftar Perintah](#-panduan-penggunaan--daftar-perintah)

---

## 🚀 Tentang Proyek

**CakraAegis** adalah asisten pertahanan siber cerdas (*Guardian AI*) bergaya *Jarvis* berbasis desktop yang dirancang untuk membantu pengembang memantau, mendeteksi, dan mengamankan aset aplikasi secara *real-time*[cite: 2].

Menggabungkan kemampuan **Hands-Free Voice Control**, **Live Screen-Aware AI**, dan **Real-Time Log Threat Engine**, CakraAegis mampu mengidentifikasi pola serangan siber (seperti *SQL Injection*, *XSS*, *Path Traversal*, hingga kebocoran kredensial/*API Key*) serta memberikan rekomendasi perbaikan kode (*Code Remediation*) secara instan[cite: 2].

---

## ✨ Fitur & Menu Utama Aplikasi

Berikut adalah rincian menu kontrol yang tersedia di panel samping (*sidebar*) dan area utama aplikasi **CakraAegis**[cite: 2]:

<table>
  <thead>
    <tr>
      <th>Kategori Menu</th>
      <th>Fitur / Tombol</th>
      <th>Fungsi Utama</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td rowspan="3"><b>🎙️ Kontrol Suara & Audio</b></td>
      <td><code>Selalu mendengarkan</code></td>
      <td>Mengaktifkan mode <i>standby</i> mikrofon yang otomatis aktif saat dipanggil <i>wake word</i> <b><code>"CakraAegis"</code></b>[cite: 2].</td>
    </tr>
    <tr>
      <td><code>Suara CakraAegis</code></td>
      <td>Mengaktifkan/mematikan respons suara natural (<i>Text-to-Speech</i> dengan pilihan suara Ardi/Gadis)[cite: 2].</td>
    </tr>
    <tr>
      <td><code>🎤 Bicara sekarang</code></td>
      <td>Tombol pemicu perintah suara langsung tanpa perlu mengucapkan <i>wake word</i>[cite: 2].</td>
    </tr>
    <tr>
      <td rowspan="2"><b>👁️ Live Screen</b></td>
      <td><code>AI melihat layar saat ngobrol</code></td>
      <td>Mengizinkan CakraAegis melihat jendela layar aktif untuk membantu analisis konteks saat berdiskusi[cite: 2].</td>
    </tr>
    <tr>
      <td><code>Deteksi ancaman layar otomatis</code></td>
      <td>Memindai layar secara berkala dan memberi peringatan jika ada <i>misconfig</i> atau <i>secret</i> terekspos[cite: 2].</td>
    </tr>
    <tr>
      <td rowspan="3"><b>⚙️ Setup Proyek</b></td>
      <td><code>🔑 API key Gemini</code></td>
      <td>Mengatur dan menyimpan kunci API Google Gemini secara lokal dan aman[cite: 2].</td>
    </tr>
    <tr>
      <td><code>📁 Pilih folder proyek</code></td>
      <td>Mengindeks file kode sumber proyek sekaligus menyamarkan (<i>redact</i>) <i>password/API key</i> otomatis[cite: 2].</td>
    </tr>
    <tr>
      <td><code>📄 Tambah file log</code></td>
      <td>Memantau file log server (<code>access.log</code>, <code>error.log</code>, <code>auth.log</code>) secara <i>real-time</i>[cite: 2].</td>
    </tr>
    <tr>
      <td rowspan="3"><b>⚡ Aksi Cepat</b></td>
      <td><code>🧪 Tes simulasi serangan</code></td>
      <td>Menjalankan simulasi log serangan <i>SQL Injection</i> lokal untuk menguji respon deteksi sistem[cite: 2].</td>
    </tr>
    <tr>
      <td><code>🔍 Audit kode proyek</code></td>
      <td>Melakukan pemindaian menyeluruh pada folder proyek terhadap kerentanan standar <b>OWASP Top 10</b>[cite: 2].</td>
    </tr>
    <tr>
      <td><code>🖥️ Analisis layar sekarang</code></td>
      <td>Mengambil tangkapan layar seketika dan menganalisis potensi ancaman yang terlihat[cite: 2].</td>
    </tr>
  </tbody>
</table>

---

## ⚙️ Arsitektur & Alur Kerja Sistem

<details open>
<summary><b>🔽 Klik untuk buka/tutup detail Arsitektur & Alur Kerja Sistem</b></summary>
<br>

<p>CakraAegis berjalan menggunakan arsitektur <b>Multi-Threading</b> agar proses perekaman suara, pemantauan file log, dan pemanggilan AI berjalan paralel tanpa membuat antarmuka pengguna (<i>GUI</i>) mengalami <i>lag</i> atau <i>freeze</i>[cite: 2]:</p>

<pre><code>┌─────────────────────────┐
│   Mikrofon / Pengguna   │──(SpeechRecognition STT)──┐
└─────────────────────────┘                           ▼
┌─────────────────────────┐                  ┌─────────────────┐     ┌────────────────────┐
│  File Log Server (Tail) │──(Regex Engine)─▶│  Brain (Gemini) │────▶│  Chat GUI & Salin  │
└─────────────────────────┘                  └─────────────────┘     └────────────────────┘
┌─────────────────────────┐                           ▲                        │
│ Layar & Kode (CodeGuard)│──(MSS + Redact)───────────┘                        ▼
└─────────────────────────┘                                          ┌────────────────────┐
                                                                     │ TTS Worker (Suara) │
                                                                     └────────────────────┘</code></pre>

<ol>
  <li><b>Jalur Interaksi Suara (<i>Voice Loop & TTS Worker</i>)</b>: Menangkap perintah suara → diterjemahkan ke teks via <code>SpeechRecognition</code> → diproses oleh model Gemini → ditampilkan di ruang obrolan dan dibacakan secara ringkas via <code>Edge-TTS</code> / <code>pyttsx3</code> (blok kode otomatis dilewati saat dibacakan)[cite: 2].</li>
  <li><b>Jalur Deteksi Log (<i>Threat Engine</i>)</b>: Memantau baris log baru secara langsung dengan pola <i>Regex</i> (SQLi, XSS, Brute Force, Scanner) → mencocokkan <i>path</i> serangan dengan file kode di folder proyek → memberikan analisis tingkat bahaya dan kode perbaikan[cite: 2].</li>
  <li><b>Jalur Keamanan Kode (<i>CodeGuard Auto-Redaction</i>)</b>: Sebelum file kode dikirim ke AI untuk diaudit, sistem otomatis menyensor kredensial sensitif menjadi <code>***REDACTED***</code> demi menjaga kerahasiaan data pengguna[cite: 2].</li>
</ol>

</details>

---

## 🛠️ Tech Stack & Library Utama

<details>
<summary><b>🔽 Klik untuk melihat rincian Teknologi & Library Python</b></summary>
<br>

<ul>
  <li><b>Bahasa Pemrograman:</b> Python <code>v3.12.9</code>[cite: 2]</li>
  <li><b>Otak Kecerdasan Buatan:</b> Google Gemini API (<code>google-genai</code>)[cite: 2]</li>
  <li><b>Antarmuka Grafis (GUI):</b> <code>CustomTkinter</code> (Modern Dark Theme)[cite: 2]</li>
  <li><b>Speech-to-Text (STT):</b> <code>SpeechRecognition</code> & <code>PyAudio</code>[cite: 2]</li>
  <li><b>Text-to-Speech (TTS):</b> <code>Edge-TTS</code>, <code>pyttsx3</code>, & <code>Pygame</code>[cite: 2]</li>
  <li><b>Screen Capture & Image Processing:</b> <code>MSS</code> & <code>Pillow (PIL)</code>[cite: 2]</li>
</ul>

</details>

---

## 📸 Preview & Demo Aplikasi

> 💡 **Catatan:** Untuk menampilkan gambar *screenshot* atau animasi GIF di sini, buat folder `assets/` di repository ini, unggah gambar dengan nama `screenshot-ui.png`, lalu hapus tanda komentar HTML (`<!--` dan `-->`) pada baris di bawah[cite: 2, 3].

<div align="center">
  <!-- <img src="assets/screenshot-ui.png" alt="Antarmuka Utama CakraAegis" width="85%" /> -->
  <p><i>Tampilan Antarmuka Utama CakraAegis: Panel Kontrol Sidebar & Ruang Diskusi Threat Intel</i></p>
</div>

---

## 📋 Panduan Instalasi & Pemasangan (Quick Start)

<details open>
<summary><b>🔽 Klik untuk buka/tutup Langkah Instalasi di Komputer Lokal</b></summary>
<br>

<p>Ikuti langkah-langkah berikut di terminal (CMD / PowerShell / VS Code Terminal) untuk menginstal dan menjalankan <b>CakraAegis</b>[cite: 2]:</p>

<ol>
  <li>
    <b>Clone Repository GitHub</b>
    <pre><code>git clone https://github.com/devvvaaann/CakraAegis.git
cd CakraAegis</code></pre>
  </li>
  <li>
    <b>Buat &amp; Aktifkan Virtual Environment <i>(Direkomendasikan Python 3.12.9)</i></b>
    <pre><code>python -m venv venv</code></pre>
    <p>Untuk pengguna <b>Windows (CMD / PowerShell)</b>:</p>
    <pre><code>venv\Scripts\activate</code></pre>
    <p>Untuk pengguna <b>Linux / macOS</b>:</p>
    <pre><code>source venv/bin/activate</code></pre>
  </li>
  <li>
    <b>Instal Semua Library yang Dibutuhkan</b>
    <pre><code>pip install customtkinter SpeechRecognition pyttsx3 pyaudio mss pillow google-genai edge-tts pygame</code></pre>
  </li>
  <li>
    <b>Jalankan Aplikasi</b>
    <pre><code>python CakraAegis.py</code></pre>
  </li>
</ol>

</details>

---

## 🎮 Panduan Penggunaan & Daftar Perintah

<details>
<summary><b>🔽 Klik untuk melihat Cara Penggunaan & Contoh Perintah Suara</b></summary>
<br>

<ol>
  <li><b>Konfigurasi API Key:</b> Saat aplikasi terbuka, klik tombol <b><code>🔑 API key Gemini</code></b> di sidebar kiri lalu tempelkan API Key Google Gemini Anda[cite: 2].</li>
  <li><b>Muat Proyek &amp; Log:</b> Klik <b><code>📁 Pilih folder proyek</code></b> untuk mengindeks kode Anda dan <b><code>📄 Tambah file log</code></b> untuk mulai memantau file log[cite: 2].</li>
  <li><b>Contoh Perintah Suara (Panggil <code>"CakraAegis"</code> terlebih dahulu):</b>[cite: 2]
    <ul>
      <li><i>"CakraAegis, tolong audit kode proyek saya."</i>[cite: 2]</li>
      <li><i>"CakraAegis, cek layar saya sekarang apakah ada celah keamanan."</i>[cite: 2]</li>
      <li><i>"CakraAegis, jelaskan cara mencegah serangan SQL Injection."</i></li>
      <li><i>"CakraAegis, terima kasih / sudah dulu."</i> <i>(untuk mengembalikan asisten ke mode Standby)</i>[cite: 2]</li>
    </ul>
  </li>
  <li><b>Uji Coba Cepat:</b> Klik tombol <b><code>🧪 Tes simulasi serangan</code></b> di sidebar untuk melihat bagaimana CakraAegis mendeteksi serangan secara <i>real-time</i> dan memberikan kode perbaikannya[cite: 2].</li>
</ol>

</details>

---

<div align="center">
  <p>Dibuat untuk <b>Kartika Cyber Hackathon 2026</b> • Kategori: <i>Penangkalan</i>[cite: 2]</p>
</div>
