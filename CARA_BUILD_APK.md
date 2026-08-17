# Cara Mengubah CSOI Jadi APK & Membagikannya ke Banyak Orang

Pydroid 3 hanya bisa MENJALANKAN Python, bukan membuat file APK. Untuk
menghasilkan APK, kita memakai **GitHub Actions** — server milik GitHub
yang meng-compile-kan APK untuk kita secara GRATIS, tanpa perlu laptop
Linux atau Android Studio.

Total waktu: sekitar 20-30 menit (kebanyakan cuma menunggu build selesai).

---

## BAGIAN 1 - Menyiapkan Repository GitHub

1. Buat akun di https://github.com kalau belum punya (gratis).
2. Klik tombol hijau **"New"** untuk membuat repository baru.
   - Nama repo bebas, misalnya `csoi-live-indicator`
   - Pilih **Public** (biar Actions gratis penuh; kalau Private juga
     tetap gratis untuk akun personal, hanya ada batas menit/bulan)
   - Centang "Add a README file" (boleh, nanti ditimpa)
3. Setelah repo dibuat, klik **"Add file" -> "Upload files"**.
4. Upload SEMUA isi folder zip yang saya kirim, dengan struktur PERSIS
   seperti ini (jangan sampai ada yang tertinggal atau salah folder):

   ```
   main.py
   csoi_logo.png
   icon.png
   presplash.png
   requirements.txt
   buildozer.spec
   icons/
     camera.png
     chip.png
     clock.png
     droplet.png
     gauge.png
     gear.png
     grid.png
     home.png
     info.png
     people.png
     thermometer.png
     train.png
   .github/
     workflows/
       build-apk.yml
   .gitignore
   ```

   Tips: kalau upload lewat browser HP susah menjaga struktur folder,
   pakai aplikasi GitHub resmi, atau upload dari laptop/warnet sekali
   saja (setelah ini semua proses build otomatis, tidak perlu upload
   lagi tiap kali).

5. Commit / simpan perubahan (tombol hijau "Commit changes").

---

## BAGIAN 2 - Build APK Otomatis

1. Begitu file `.github/workflows/build-apk.yml` ter-upload dan ter-commit,
   GitHub OTOMATIS mulai proses build.
2. Buka tab **"Actions"** di repo kamu, akan ada proses "Build CSOI APK"
   sedang berjalan (ikon kuning berputar).
3. Tunggu sampai selesai (biasanya 10-20 menit untuk build pertama kali,
   build berikutnya lebih cepat karena ada cache).
4. Kalau ikonnya jadi **centang hijau** -> build BERHASIL.
   Kalau **silang merah** -> build GAGAL, klik untuk lihat log error,
   atau kirim screenshot log-nya ke saya, saya bantu perbaiki.
5. Klik hasil build yang sukses -> scroll ke bawah -> ada bagian
   **"Artifacts"** -> download **"CSOI-Live-Indicator-APK"** (file .zip
   berisi file .apk di dalamnya).

---

## BAGIAN 3 - Coba di HP Sendiri Dulu

1. Ekstrak zip hasil download, akan ada file `.apk`.
2. Pindahkan ke HP Android, buka file-nya.
3. Kalau muncul peringatan "Install dari sumber tidak dikenal" -> izinkan
   (Setelan -> Keamanan -> Instal aplikasi tidak dikenal -> aktifkan untuk
   aplikasi file manager/browser yang kamu pakai).
4. Install & coba jalankan seperti biasa. Pastikan bisa connect ke
   ESP32-S3-CAM dengan lancar (sudah saya set supaya koneksi HTTP ke IP
   lokal diizinkan, lihat catatan di buildozer.spec).

---

## BAGIAN 4 - Membagikan ke Banyak Orang

Ada 2 jalur, pilih sesuai kebutuhan:

### A. Cara Cepat (bagikan APK langsung) - PALING PRAKTIS
Cocok untuk dibagikan ke rekan kerja, komunitas, atau publik terbatas
tanpa proses review dari Google.

- Upload file .apk ke Google Drive -> set "Anyone with the link can view"
  -> bagikan link-nya.
- ATAU upload sebagai **GitHub Release** (di repo kamu: Releases -> Draft
  a new release -> upload file .apk) -> dapat link download publik yang
  rapi dan permanen.
- Orang lain tinggal download & install manual (perlu izinkan "sumber
  tidak dikenal" sekali di HP mereka, seperti langkah di atas).

### B. Cara Resmi (rilis ke Google Play Store) - untuk jangkauan luas & terpercaya
Lebih ribet tapi orang bisa install lewat Play Store seperti aplikasi
pada umumnya, dan Google Play Protect tidak akan menandainya mencurigakan.

1. Daftar Google Play Console: https://play.google.com/console
   (biaya pendaftaran sekali bayar sekitar USD 25).
2. APK dari langkah di atas masih versi **debug** (belum ditandatangani
   untuk rilis) - Play Store butuh versi **release** yang di-sign dengan
   keystore sendiri. Ganti perintah di `build-apk.yml` dari
   `buildozer android debug` menjadi `buildozer android release`, lalu
   siapkan keystore (buildozer akan memandu / ada dokumentasi resmi
   Buildozer soal signing).
3. Google Play juga mewajibkan format **.aab** (Android App Bundle),
   bukan .apk, untuk rilis baru - buildozer mendukung ini juga
   (`buildozer android release` bisa menghasilkan .aab tergantung
   konfigurasi terbaru; cek dokumentasi Buildozer terkini kalau perlu).
4. Lengkapi juga: ikon & screenshot untuk listing, deskripsi aplikasi,
   kebijakan privasi (privacy policy - wajib walau aplikasi sederhana),
   rating konten, dan lolos tahap "closed testing" dulu sebelum rilis
   publik penuh (ketentuan Google Play saat ini).

Saran saya: **mulai dari cara A dulu** (bagikan APK langsung) untuk
menyebarkan ke pengguna awal / komunitas CSOI. Kalau responnya bagus dan
ingin jangkauan lebih luas & resmi, baru lanjut ke cara B (Play Store).

---

## Catatan Teknis Penting

- **package.name** dan **package.domain** di `buildozer.spec` sebaiknya
  kamu ubah jadi unik milikmu sendiri (misal `org.namakamu`) sebelum
  benar-benar dipublikasikan luas, supaya tidak bentrok dengan aplikasi
  lain.
- **version** di `buildozer.spec` (saat ini `1.0`) perlu dinaikkan setiap
  kali kamu update aplikasi dan build ulang.
- File `.apk` hasil build pertama ukurannya cukup besar (~30-50 MB)
  karena sudah termasuk seluruh runtime Python + Kivy - ini normal untuk
  aplikasi Kivy.
- Kalau build GAGAL di GitHub Actions, log errornya biasanya jelas
  menyebutkan penyebabnya (versi paket, permission, dsb) - kirim
  screenshot/teks log itu ke saya kapan saja, saya bantu telusuri.
