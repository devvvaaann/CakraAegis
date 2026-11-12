<div align="center">

  <!-- Hapus tanda komentar di bawah jika sudah meng-upload banner/thumbnail ke folder assets/ -->
  <!-- <img src="assets/banner-cakraaegis.png" alt="CakraAegis Banner" width="100%" /> -->

  <h1>🛡️ CakraAegis</h1>
  <p><b>AI-Driven Live Screen-Aware & Voice-Activated Cyber Security Assistant</b></p>

  <!-- Badges Status Proyek -->
  <p>
    <img src="https://img.shields.io/badge/Python-3.12.9-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/AI-Google%20Gemini-orange?style=for-the-badge&logo=google&logoColor=white" alt="Gemini API">
    <img src="https://img.shields.io/badge/GUI-CustomTkinter-green?style=for-the-badge" alt="CustomTkinter">
    <img src="https://img.shields.io/badge/Hackathon-Kartika%20Cyber%202026-red?style=for-the-badge" alt="Hackathon">
  </p>

  <!-- Navigasi Cepat (Bisa Diklik) -->
  <p>
    <a href="#-tentang-proyek">Tentang Proyek</a> •
    <a href="#-fitur-unggulan">Fitur Unggulan</a> •
    <a href="#-arsitektur--alur-kerja-sistem">Arsitektur Sistem</a> •
    <a href="#-tech-stack--library">Tech Stack</a> •
    <a href="#-panduan-instalasi--menjalankan-quick-start">Cara Instalasi</a>
  </p>
</div>

---

## 📖 Daftar Isi Interaktif
Klik bagian di bawah ini untuk langsung melompat ke dokumentasi yang diinginkan:
1. [🚀 Tentang Proyek](#-tentang-proyek)
2. [✨ Fitur Unggulan](#-fitur-unggulan)
3. [⚙️ Arsitektur & Alur Kerja Sistem](#%EF%B8%8F-arsitektur--alur-kerja-sistem)
4. [🛠️ Tech Stack & Library](#%EF%B8%8F-tech-stack--library)
5. [📸 Preview & Demo Aplikasi](#-preview--demo-aplikasi)
6. [📋 Panduan Instalasi & Menjalankan (Quick Start)](#-panduan-instalasi--menjalankan-quick-start)

---

## 🚀 Tentang Proyek

**CakraAegis** adalah asisten pertahanan siber cerdas (*Guardian AI*) bergaya *Jarvis* yang dirancang untuk memantau, mendeteksi, dan mengamankan aset aplikasi secara *real-time*. 

Menggabungkan kemampuan **Live Screen-Aware**, **Real-Time Log Monitoring**, dan interaksi suara **Hands-Free**, CakraAegis membantu pengembang mendeteksi potensi celah keamanan (seperti SQL Injection, XSS, Path Traversal, hingga kebocoran *API Key*) sekaligus memberikan rekomendasi perbaikan kode (*Code Remediation*) secara instan.

---

## ✨ Fitur Unggulan

| Fitur | Deskripsi |
| :--- | :--- |
| 🎙️ **Hands-Free Voice Control** | Aktif otomatis saat dipanggil menggunakan *wake word* **`"CakraAegis"`** dan merespons balik dengan suara natural (TTS). |
| 👁️ **Live Screen-Aware AI** | Memantau layar kerja secara *real-time* untuk mendeteksi misconfig, potensi ancaman, atau *secret* yang tidak sengaja terekspos. |
| 📜 **Real-Time Log Threat Engine** | Membaca file log server (`access.log`, `error.log`, `auth.log`) secara langsung untuk mendeteksi pola serangan siber lokal. |
| 🔒 **CodeGuard & Auto-Redaction** | Memindai kode proyek dari kerentanan **OWASP Top 10** dan otomatis menyamarkan (*redact*) *password* atau *API Key* sebelum dikirim ke AI. |
| 🧪 **Attack Simulator** | Fitur simulasi serangan bawaan untuk menguji ketangguhan deteksi sistem secara aman. |

---

## ⚙️ Arsitektur & Alur Kerja Sistem

<details open>
<summary><b>🔽 Klik untuk buka/tutup detail Alur Kerja & Arsitektur Sistem</b></summary>
<br>

CakraAegis bekerja melalui **3 jalur utama secara paralel (*multi-threading*)** agar antarmuka tetap ringan, responsif, dan tidak mengalami *freeze* saat memproses suara maupun layar:

```text
[Mikrofon / User] ──(SpeechRecognition)──> [Teks Perintah]
                                                 │
[File Log Server] ──(ThreatEngine Regex)──> [Brain / Gemini AI] ──> [Output Chat GUI]
                                                 │                         │
[Layar Aktif / Kode] ──(MSS & CodeGuard)─────────┘                         └──> [TTS Worker (Suara)]
