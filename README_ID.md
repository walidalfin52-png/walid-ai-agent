# WALID AI OFFICE — Paket deploy online

Aplikasi web berbahasa Indonesia dengan dashboard Owner, 8 peran karyawan AI, manajemen tugas, draf hasil AI, persetujuan Owner, riwayat aktivitas, dan database SQLite.

## Deploy online melalui Render
1. Buat akun Render dan akun GitHub jika belum punya.
2. Unggah folder proyek ini ke repository GitHub pribadi.
3. Di Render pilih **New → Blueprint**, lalu hubungkan repository. Render membaca `render.yaml`.
4. Isi `OWNER_PASSWORD` dengan password kuat dan `OPENAI_API_KEY` dengan API key dari akun OpenAI Anda pada pengaturan Environment. Jangan bagikan API key di chat atau repository.
5. Jalankan deploy. Setelah layanan berstatus Live, buka alamat `.onrender.com` yang disediakan Render.

Blueprint menyiapkan persistent disk untuk database SQLite. Pembuatan akun hosting, pengisian rahasia, dan penerbitan URL publik memerlukan login serta persetujuan Anda; paket ini belum terpasang ke akun hosting Anda.

## Uji coba lokal
Gunakan Python 3.11+. Jalankan `pip install -r requirements.txt`, atur environment `OWNER_PASSWORD`, `SECRET_KEY`, dan `OPENAI_API_KEY`, lalu jalankan `python app.py`. Buka `http://localhost:8080`.

## Keamanan dan batasan
- Ganti password Owner sebelum aplikasi dibuka ke internet.
- API key hanya disimpan di Environment Variables hosting.
- Hasil AI berstatus draf sampai Owner menyetujuinya.
- Biaya API OpenAI terpisah sesuai penggunaan akun API.
- Versi awal belum mengirim email/WhatsApp, mengakses kalender, menerima pembayaran, atau menjalankan tindakan eksternal otomatis.
