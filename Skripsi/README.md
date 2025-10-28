# 🧐 Klasifikasi Gender Sidik Jari Menggunakan CNN Inception-ResNetV2

## 📖 Pendahuluan

Proyek ini adalah implementasi skripsi S1 berjudul **"Klasifikasi Gender Pada Sidik Jari Menggunakan Convolutional Neural Network Dengan Implementasi Model Arsitektur Inception-ResNetV2"**. Tujuannya adalah untuk mengembangkan dan mengevaluasi model *deep learning* yang mampu mengklasifikasikan jenis kelamin (pria/wanita) berdasarkan citra sidik jari.

Penelitian ini dilatarbelakangi oleh potensi sidik jari sebagai data biometrik yang tidak hanya unik untuk identifikasi individu, tetapi juga mungkin mengandung informasi tentang karakteristik lain seperti gender. Kemampuan untuk mengidentifikasi gender dari sidik jari dapat berkontribusi signifikan dalam berbagai bidang, terutama keamanan dan analisis forensik.

---

## 🎯 Masalah & Tujuan

* **Masalah:** Pengenalan pola sidik jari secara manual memakan waktu dan subjektif. Metode klasifikasi gender dari sidik jari yang ada sebelumnya mungkin belum mencapai akurasi optimal.
* **Tujuan:**
    1.  Menghasilkan sistem klasifikasi gender dari citra sidik jari dengan akurasi tinggi.
    2.  Mengimplementasikan dan mengevaluasi model CNN dengan arsitektur Inception-ResNetV2 untuk tugas ini.

---

## ✨ Solusi & Metode

Solusi yang diimplementasikan adalah model klasifikasi gambar menggunakan **Convolutional Neural Network (CNN)** dengan arsitektur **Inception-ResNetV2**, memanfaatkan teknik *transfer learning*.

**Alur Kerja Utama:**
1.  **Pengumpulan Data:** Menggunakan dua dataset publik:
    * **Sokoto Coventry Fingerprint (SOCOFing):** Dataset sidik jari dari 600 subjek Afrika.
    * **NIST Special Database 4 (SD 4):** Dataset sidik jari berkualitas tinggi dari NIST.
2.  **Pra-pemrosesan & Pembagian Data:**
    * Mengubah ukuran gambar menjadi 299x299 piksel.
    * Normalisasi nilai piksel (rescale).
    * Membagi dataset menjadi data latih (70%), validasi (20%), dan uji (10%).
    * (Pada beberapa skenario) Menggunakan *Fingerprint Enhancer*.
3.  **Implementasi Model:** Membangun model CNN menggunakan Keras dengan *base model* Inception-ResNetV2 (pre-trained di ImageNet), menambahkan layer `GlobalAveragePooling2D`, `Dropout`, dan `Dense` (output 2 kelas: pria/wanita).
4.  **Kompilasi Model:** Menggunakan *optimizer* Adam (dan diuji coba dengan SGD, RMSprop), *loss function* `binary_crossentropy`, dan metrik `accuracy`.
5.  **Pelatihan Model:** Melatih model selama beberapa epoch (contoh: 20 epoch) menggunakan data latih dan divalidasi dengan data validasi. Menggunakan *callbacks* `EarlyStopping` dan `ReduceLROnPlateau`.
6.  **Evaluasi Model:** Menguji performa model final pada data uji menggunakan metrik: Akurasi, Presisi, Recall, dan F1-Score.

---

## 🛠️ Tools & Teknologi

* **Perangkat Keras:**
    * Laptop: Acer Nitro AN515-15
    * Processor: Intel® Core™ i5-10300H CPU @ 2.50GHz
    * RAM: 16GB
* **Perangkat Lunak:**
    * Sistem Operasi: Windows 11 Home Single Language 64-bit
    * IDE: Pycharm
* **Framework & Library:**
    * Bahasa Pemrograman: Python
    * Deep Learning: Tensorflow, Keras (termasuk `ImageDataGenerator`, `InceptionResNetV2`)
    * Machine Learning Utilities: Sklearn (Scikit-learn) (untuk metrik evaluasi & confusion matrix)
    * Numerik: Numpy
    * Plotting: Matplotlib, Seaborn
    * Enhancement: Fingerprint Enhancer
    * Lainnya: OS, Tensorflow Hub (disebutkan dalam kode)

---

## 📊 Hasil Ringkas

* Model yang dilatih dengan dataset **NIST** cenderung **lebih baik** daripada SOCOFing.
* Penggunaan **data augmentasi** efektif pada dataset yang lebih besar/beragam (NIST, Gabungan).
* **Batch size 32** memberikan keseimbangan performa yang baik.
* **Learning rate 0.001** menunjukkan hasil paling optimal dalam eksperimen.
* Optimizer **Adam** secara konsisten memberikan performa terbaik dibandingkan SGD dan RMSprop.

*(Untuk detail akurasi spesifik tiap skenario, silakan merujuk ke Bab IV dalam dokumen skripsi.)*

---

## 🚀 Potensi Aplikasi

Penelitian ini menunjukkan potensi penggunaan CNN Inception-ResNetV2 untuk klasifikasi gender dari sidik jari, yang dapat diaplikasikan lebih lanjut dalam bidang:
* Keamanan & Verifikasi Identitas
* Analisis Forensik
* Penelitian Biometrik

---

* **Penulis:** William Hong (71200617)
* **Institusi:** Program Studi Informatika, Fakultas Teknologi Informasi, Universitas Kristen Duta Wacana, Yogyakarta
* **Tahun:** 2024
* 
