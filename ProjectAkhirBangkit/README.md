# 💆‍♀️ Aplikasi SkinCareku: Deteksi & Rekomendasi Perawatan Kulit Wajah

## 📖 Pendahuluan

**SkinCareku** adalah sebuah aplikasi mobile inovatif yang dirancang untuk membantu pengguna mendeteksi kondisi kesehatan kulit wajah mereka dan memberikan rekomendasi perawatan atau produk *skincare* yang sesuai. Seiring meningkatnya kesadaran akan pentingnya kesehatan kulit, tidak hanya di kalangan wanita tetapi juga pria, aplikasi ini hadir sebagai solusi. Kondisi cuaca di Indonesia yang tropis menuntut perhatian ekstra agar kulit wajah tetap cerah dan sehat.

Seringkali, pengguna mengalami ketidakcocokan antara produk *skincare* dengan tipe kulit mereka, yang mengakibatkan pemborosan biaya karena mencoba berbagai macam produk. Dengan SkinCareku, kami berharap dapat membantu pengguna mengidentifikasi masalah kulit mereka secara lebih akurat dan mendapatkan rekomendasi *skincare* yang tepat sasaran.

Proyek ini merupakan bagian dari **Capstone Project Bangkit Academy 2023**.

---

## 🎯 Masalah yang Dipecahkan

* **Kesulitan Identifikasi Masalah Kulit:** Banyak orang awam kesulitan mengenali jenis masalah kulit wajah mereka secara akurat (misalnya, membedakan jenis jerawat atau komedo).
* **Ketidakcocokan Produk Skincare:** Pemilihan produk yang tidak sesuai dengan tipe dan masalah kulit sering terjadi, menyebabkan iritasi atau tidak memberikan hasil yang diharapkan.
* **Biaya Trial-and-Error:** Mencoba berbagai produk *skincare* untuk menemukan yang cocok memakan biaya yang tidak sedikit.
* **Kebutuhan Perawatan Spesifik:** Kondisi iklim tropis di Indonesia memerlukan perawatan kulit yang tepat untuk menjaga kesehatan dan kecerahan kulit.

---

## ✨ Solusi Kami: Aplikasi SkinCareku

SkinCareku menawarkan solusi berbasis teknologi:

1.  **Deteksi Kondisi Kulit:** Menggunakan model *Machine Learning* (TensorFlow Lite) yang dilatih untuk mengklasifikasikan gambar wajah pengguna ke dalam kategori: **Jerawat (Acne)**, **Kulit Bersih (Clear Skin)**, atau **Komedo (Comedo)**.
2.  **Rekomendasi Produk Personal:** Berdasarkan hasil deteksi, aplikasi memberikan rekomendasi produk *skincare* atau perawatan yang sesuai, dengan kemampuan *filter* berdasarkan kandungan bahan.
3.  **Informasi Produk:** Menyediakan daftar produk yang tersedia beserta detailnya melalui API.
4.  **Pengalaman Pengguna Mobile:** Aplikasi *user-friendly* dengan koneksi *real-time* (Firebase) dan mekanisme *buffer data* saat koneksi internet tidak tersedia.

---

## 🚀 Fitur Utama

* **Klasifikasi Gambar Kulit Wajah:** Menganalisis foto wajah untuk mendeteksi kondisi kulit (Jerawat, Bersih, Komedo).
* **Rekomendasi Skincare:** Memberikan saran produk berdasarkan hasil analisis.
* **Katalog Produk:** Menampilkan daftar produk *skincare* yang dapat difilter berdasarkan jenis atau kandungan.
* **Autentikasi Pengguna:** Sistem login aman menggunakan Firebase Authentication (Email & Password).
* **Profil Pengguna:** Menyimpan riwayat atau preferensi pengguna (via Firestore).
* **Konektivitas Handal:** Tetap berfungsi sebagian meskipun koneksi internet terputus sementara.
* **(Implied) Aplikasi Admin:** Kemungkinan adanya aplikasi terpisah untuk mengelola data produk.

---

## 🛠️ Teknologi yang Digunakan

Proyek ini dibangun menggunakan kombinasi teknologi dari berbagai bidang:

**1. Machine Learning (ML):**
    * **Model:** TensorFlow Lite untuk klasifikasi gambar.
    * **Training Platform:** Kaggle.
    * **Dataset:** Dataset gambar wajah (Acne, Clear Skin, Comedo).
    * **Tugas:** Klasifikasi Gambar.

**2. Mobile Development (MD):**
    * **Platform:** Android (asumsi, bisa disesuaikan).
    * **Deployment ML:** Integrasi model TensorFlow Lite ke dalam aplikasi.
    * **Backend As A Service (BaaS):** Firebase (Realtime Database/Firestore, Authentication).
    * **Fitur:** Koneksi *real-time*, *Data buffer* offline.

**3. Cloud Computing (CC):**
    * **Platform:** Google Cloud Platform (GCP).
    * **API Backend:**
        * API Autentikasi Pengguna.
        * API Produk (List, Rekomendasi, Filter).
    * **Deployment:**
        * Cloud Run (untuk API Firestore).
        * Compute Engine (untuk API Model ML).
    * **Database:** Firestore (Profil Pengguna, Data Produk).
    * **Autentikasi:** Firebase Authentication (Email/Password).
    * **Manajemen Akses:** Cloud IAM (Konfigurasi *policy* untuk tim & *Service Account*).
    * **Dokumentasi API:** Swagger UI.

---

## 🔗 Tautan Proyek

Berikut adalah tautan terkait proyek SkinCareku:

* **Dataset:**
    * [Face Skin Disease Dataset](https://www.kaggle.com/datasets/philibraspacex/faceskin-dataset)
    * [Skincare Product Dataset](https://www.kaggle.com/datasets/philibraspacex/skincareproductdataset)
* **Machine Learning:**
    * [Notebook Klasifikasi Gambar (Kaggle)](https://www.kaggle.com/code/philibraspacex/notebookb56ae0a974)
* **Kode Sumber:**
    * [Repositori GitHub](https://github.com/AlvonJ/skincareku-project)
* **Presentasi:**
    * [Video Presentasi 10 Menit (YouTube)](https://youtu.be/BLgqEWHeQ-Q)
    * [Slide Presentasi (Canva)](https://www.canva.com/design/DAFl3sMxaO8/nlPZn9vRw2X9J38uynP2wg/edit?utm_content=DAFl3sMxaO8&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)


---

## 🙏 Ucapan Terima Kasih

Proyek ini tidak akan terwujud tanpa bimbingan dan kesempatan yang diberikan oleh **Bangkit Academy 2023** yang didukung oleh Google, GoTo, dan Traveloka.
