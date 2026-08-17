CSOI V2 - Pydroid 3 FIX9 (tampilan dirapikan sesuai contoh)

1. Ekstrak ZIP ke satu folder, misalnya /storage/emulated/0/Download/CSOI_Pydroid_FIX/
2. PENTING: folder "icons" HARUS ikut ter-ekstrak di folder yang sama dengan
   main.py (bukan dipindah/dihapus). Struktur folder harus seperti ini:
     CSOI_Pydroid_FIX/
       main.py
       csoi_logo.png
       requirements.txt
       icons/
         camera.png, chip.png, clock.png, droplet.png, dst.
3. Di Pydroid 3, buka main.py dari folder tersebut.
4. Jalankan main.py.

Login:
Password = CSOI2026

PERUBAHAN TAMPILAN (FIX9):
- Semua ikon sekarang gambar PNG asli (dibuat khusus, bukan karakter font
  atau titik polos) yang diberi warna sesuai tema tiap kartu: orang
  (penumpang/status), termometer (suhu), tetes air (kelembapan), gauge
  (tekanan), kamera, chip (BME280), grid (MAX7219), kereta, jam, gear
  (pengaturan), rumah (dashboard), info (about).
- Kartu PENUMPANG/OKUPANSI/STATUS sekarang punya lingkaran besar di
  tengah (ikon di dalamnya untuk Penumpang/Status, angka persen di
  dalamnya untuk Okupansi) -- seperti pada contoh referensi.
- Baris STATUS SISTEM sekarang 3 kotak terpisah dengan ikon kotak
  hijau + label + status OK/--, bukan satu baris teks panjang.
- Kotak KAPASITAS KERETA & UPDATE TERAKHIR sekarang punya ikon kereta
  dan jam. Waktu update terakhir otomatis terisi jam:menit:detik saat
  data terbaru diterima.
- Menu bawah (DASHBOARD/PENGATURAN/ABOUT) sekarang punya ikon di atas
  tulisan.
- Status ONLINE/OFFLINE/CONNECTING di header sekarang disertai titik
  bulat warna (hijau/merah/oranye) di sebelah kiri teks.

Semua ikon digambar dengan grafis vektor (Ellipse/RoundedRectangle) atau
gambar PNG yang di-tint warna -- TIDAK memakai kivy.graphics.Line sama
sekali (karena versi Kivy di HP ini bermasalah dengan Line, lihat FIX7)
dan TIDAK memakai karakter simbol/emoji dari font (karena font di HP ini
tidak mendukungnya, lihat FIX8).

Perbaikan-perbaikan sebelumnya yang tetap dipertahankan:
- Import ScrollView yang sebelumnya hilang (FIX3)
- Animation(value=100) -> Animation(progress=100) di splash screen (FIX4)
- Semua penggunaan Line() dihapus total (FIX7)
- Akses app.user_data_dir dibungkus try/except dengan fallback ke folder skrip
- Jaring pengaman: kalau ada error lain, ditampilkan langsung di layar
  (bukan diam-diam mati) - lihat class CSOIApp.build()

Catatan:
ESP32-S3-CAM harus menyediakan endpoint HTTP:
http://IP_ESP32/data
dan mengembalikan JSON.
