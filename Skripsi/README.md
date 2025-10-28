# 🧐 Klasifikasi Gender Sidik Jari Menggunakan CNN Inception-ResNetV2

## 📖 Pendahuluan

[cite_start]Proyek ini adalah implementasi skripsi S1 berjudul **"Klasifikasi Gender Pada Sidik Jari Menggunakan Convolutional Neural Network Dengan Implementasi Model Arsitektur Inception-ResNetV2"**[cite: 1, 2, 3]. [cite_start]Tujuannya adalah untuk mengembangkan dan mengevaluasi model *deep learning* yang mampu mengklasifikasikan jenis kelamin (pria/wanita) berdasarkan citra sidik jari[cite: 131, 164, 177].

[cite_start]Penelitian ini dilatarbelakangi oleh potensi sidik jari sebagai data biometrik yang tidak hanya unik untuk identifikasi individu, tetapi juga mungkin mengandung informasi tentang karakteristik lain seperti gender[cite: 156]. [cite_start]Kemampuan untuk mengidentifikasi gender dari sidik jari dapat berkontribusi signifikan dalam berbagai bidang, terutama keamanan dan analisis forensik[cite: 157, 180].

---

## 🎯 Masalah & Tujuan

* [cite_start]**Masalah:** Pengenalan pola sidik jari secara manual memakan waktu dan subjektif[cite: 200]. [cite_start]Metode klasifikasi gender dari sidik jari yang ada sebelumnya mungkin belum mencapai akurasi optimal[cite: 158, 160, 162].
* **Tujuan:**
    1.  [cite_start]Menghasilkan sistem klasifikasi gender dari citra sidik jari dengan akurasi tinggi[cite: 177].
    2.  [cite_start]Mengimplementasikan dan mengevaluasi model CNN dengan arsitektur Inception-ResNetV2 untuk tugas ini[cite: 171, 178].

---

## ✨ Solusi & Metode

[cite_start]Solusi yang diimplementasikan adalah model klasifikasi gambar menggunakan **Convolutional Neural Network (CNN)** dengan arsitektur **Inception-ResNetV2**, memanfaatkan teknik *transfer learning*[cite: 132, 164, 192, 606].

**Alur Kerja Utama:**
1.  **Pengumpulan Data:** Menggunakan dua dataset publik:
    * [cite_start]**Sokoto Coventry Fingerprint (SOCOFing):** Dataset sidik jari dari 600 subjek Afrika[cite: 136, 186, 614].
    * [cite_start]**NIST Special Database 4 (SD 4):** Dataset sidik jari berkualitas tinggi dari NIST[cite: 136, 187, 617].
2.  **Pra-pemrosesan & Pembagian Data:**
    * [cite_start]Mengubah ukuran gambar menjadi 299x299 piksel[cite: 684].
    * [cite_start]Normalisasi nilai piksel (rescale)[cite: 183, 604, 677].
    * [cite_start]Membagi dataset menjadi data latih (70%), validasi (20%), dan uji (10%)[cite: 190, 602, 639].
    * (Pada beberapa skenario) [cite_start]Menggunakan *Fingerprint Enhancer*[cite: 138, 625].
3.  [cite_start]**Implementasi Model:** Membangun model CNN menggunakan Keras dengan *base model* Inception-ResNetV2 (pre-trained di ImageNet), menambahkan layer `GlobalAveragePooling2D`, `Dropout`, dan `Dense` (output 2 kelas: pria/wanita) [cite: 192, 645, 647, 649, 910, 913-916].
4.  [cite_start]**Kompilasi Model:** Menggunakan *optimizer* Adam (dan diuji coba dengan SGD, RMSprop), *loss function* `binary_crossentropy`, dan metrik `accuracy`[cite: 607, 652, 692, 716, 919].
5.  [cite_start]**Pelatihan Model:** Melatih model selama beberapa epoch (contoh: 20 epoch) menggunakan data latih dan divalidasi dengan data validasi[cite: 193, 608, 659]. [cite_start]Menggunakan *callbacks* `EarlyStopping` dan `ReduceLROnPlateau` [cite: 923-926].
6.  [cite_start]**Evaluasi Model:** Menguji performa model final pada data uji menggunakan metrik: Akurasi, Presisi, Recall, dan F1-Score[cite: 195, 433, 610, 666].

---

## 🛠️ Tools & Teknologi

* **Perangkat Keras:**
    * [cite_start]Laptop: Acer Nitro AN515-15 [cite: 544]
    * [cite_start]Processor: Intel® Core™ i5-10300H CPU @ 2.50GHz [cite: 546]
    * [cite_start]RAM: 16GB [cite: 549]
* **Perangkat Lunak:**
    * [cite_start]Sistem Operasi: Windows 11 Home Single Language 64-bit [cite: 556]
    * [cite_start]IDE: Pycharm [cite: 557]
* **Framework & Library:**
    * [cite_start]Bahasa Pemrograman: Python [cite: 185, 559]
    * [cite_start]Deep Learning: Tensorflow [cite: 185, 560][cite_start], Keras [cite: 192, 561] (termasuk `ImageDataGenerator`, `InceptionResNetV2`)
    * [cite_start]Machine Learning Utilities: Sklearn (Scikit-learn) [cite: 562] (untuk metrik evaluasi & confusion matrix)
    * [cite_start]Numerik: Numpy [cite: 565, 868]
    * [cite_start]Plotting: Matplotlib [cite: 564, 866][cite_start], Seaborn [cite: 874]
    * [cite_start]Enhancement: Fingerprint Enhancer [cite: 138, 566, 625]
    * [cite_start]Lainnya: OS [cite: 855][cite_start], Tensorflow Hub [cite: 857] (disebutkan dalam kode)

---

## 📊 Hasil Ringkas

* [cite_start]Model yang dilatih dengan dataset **NIST** cenderung **lebih baik** daripada SOCOFing[cite: 139, 150].
* [cite_start]Penggunaan **data augmentasi** efektif pada dataset yang lebih besar/beragam (NIST, Gabungan)[cite: 793, 815].
* [cite_start]**Batch size 32** memberikan keseimbangan performa yang baik[cite: 800, 816].
* [cite_start]**Learning rate 0.001** menunjukkan hasil paling optimal dalam eksperimen[cite: 805, 817].
* [cite_start]Optimizer **Adam** secara konsisten memberikan performa terbaik dibandingkan SGD dan RMSprop[cite: 809, 818].

*(Untuk detail akurasi spesifik tiap skenario, silakan merujuk ke Bab IV dalam dokumen skripsi.)*

---

## 🚀 Potensi Aplikasi

Penelitian ini menunjukkan potensi penggunaan CNN Inception-ResNetV2 untuk klasifikasi gender dari sidik jari, yang dapat diaplikasikan lebih lanjut dalam bidang:
* [cite_start]Keamanan & Verifikasi Identitas [cite: 157, 180]
* [cite_start]Analisis Forensik [cite: 157, 180]
* Penelitian Biometrik

---

* [cite_start]**Penulis:** William Hong (71200617) [cite: 7, 8]
* [cite_start]**Institusi:** Program Studi Informatika, Fakultas Teknologi Informasi, Universitas Kristen Duta Wacana, Yogyakarta [cite: 9, 10, 11]
* [cite_start]**Tahun:** 2024 [cite: 12]
