# 🎓 Penasihat Akademik AI (Prodi Informatika UKDW)

Sebuah aplikasi web berbasis Streamlit yang berfungsi sebagai penasihat akademik pribadi untuk mahasiswa. Aplikasi ini menggunakan arsitektur RAG (Retrieval-Augmented Generation) canggih untuk menganalisis transkrip nilai mahasiswa dan memberikan rekomendasi mata kuliah yang personal dan "gacor" untuk semester depan.

## 🚀 Fitur Utama

* **Sistem Login Mahasiswa:** Simulasi login menggunakan NIM dan password dengan *database* mahasiswa *hardcoded* (`DATA_MAHASISWA`).
* **Dashboard Akademik Interaktif:**
    * Menggunakan **Tab** (`st.tabs`) untuk memisahkan 4 kategori utama (Wajib, Pilihan Wajib Profesi, Pilihan Bebas Prodi, Pilihan Bebas Non-Prodi).
    * Menampilkan **semua** mata kuliah di kurikulum, dengan penanda visual ("Sudah diambil (Nilai: A)" atau "Belum diambil").
    * Mata kuliah yang sudah diambil otomatis diurutkan ke atas.
* **Grouping Mata Kuliah Cerdas:**
    * **Wajib:** Dikelompokkan per semester (Semester 1-8).
    * **Pilihan Wajib Profesi:** Dikelompokkan per profesi (PSD, AI, DMS, INFRA, Pemrograman Bersama).
    * **Pilihan Bebas Prodi:** Dikelompokkan secara cerdas menjadi "MBKM" dan "Pilihan Bebas Prodi Lainnya" (dengan *tagging* profesi untuk menghindari duplikasi).
* **Sistem Rekomendasi AI "Gacor":**
    * **Deteksi Minat Otomatis:** Menganalisis transkrip untuk mendeteksi profesi yang paling cocok (misal: "Minat terdeteksi: PSD 💻").
    * **Logika Prompt Prioritas 3 Lapis:** Memaksa AI untuk merekomendasikan berdasarkan urutan: MK Wajib -> Pilihan Wajib Profesi -> Pilihan Bebas Prodi.
    * **Target SKS:** AI diinstruksikan untuk mengisi KRS hingga penuh (target 18-24 SKS).
    * **Alasan "Gacor":** AI memberikan alasan rekomendasi berdasarkan *korelasi konseptual* ("Karena nilai Statistik kamu A, yang merupakan fondasi AI...").

---

## 🧠 Arsitektur & Konsep AI (Penjelasan Detail)

Ini adalah inti dari proyek ini. AI bisa "gacor" karena kita tidak mengandalkan RAG murni (yang sering "abu-abu"). Kita menggunakan **Sistem RAG yang Diperkaya Korelasi Konseptual**.

Sistem ini memiliki 3 tahap utama:

### 1. Data Pengetahuan (Knowledge Base)

AI ini tidak belajar dari satu "buku", tapi dari dua sumber data yang berbeda fungsi:

#### A. `matakuliah.json` (Sang "Kamus")
* **Isi:** 130+ mata kuliah lengkap dengan deskripsi, SKS, prasyarat, kategori, dan profesi relevan.
* **Tujuan:** Sebagai "kamus" fakta. AI menggunakan ini untuk mengecek prasyarat, jumlah SKS, dan deskripsi dasar.
* **Kelemahan:** "Kamus" ini "bodoh". Dia tidak tahu kalau `Statistik` punya hubungan konseptual dengan `Machine Learning`. Dia hanya tahu deskripsi masing-masing.

#### B. `korelasi_mk.json` (Sang "Otak")
* **Isi:** HANYA 10 mata kuliah **Fondasi** (MK Wajib Semester 1-4) yang paling krusial.
* **Tujuan:** Sebagai "otak" atau "buku contekan" yang berisi *insight* dosen. File ini memetakan hubungan konseptual antara MK Fondasi dan MK Spesialisasi.
* **Contoh Isi:**
    ```json
    {
      "kode_mk": "TI0113", // Statistik
      "notes": "Fondasi WAJIB untuk jalur Data/AI...",
      "topik_terkait": [
        "TI6043", // Machine Learning
        "TI3033", // Data Warehouse
        "TI9023"  // Analisis Data Statistik
      ]
    }
    ```
* **Kekuatan:** Dengan "otak" ini, AI tidak lagi menebak-nebak. Dia tahu *fakta* bahwa nilai bagus di `Statistik` adalah sinyal kuat untuk mengambil `Machine Learning`.

---

### 2. Pembangunan Index (Operasi "Cangkok Otak")

Sebelum aplikasi bisa dijalankan, kita harus "mencangkokkan" sang "Otak" (`korelasi_mk.json`) ke dalam sang "Kamus" (`matakuliah.json`). Proses ini dilakukan oleh script `build_index.py`.

1.  **Load:** Script membaca kedua file JSON.
2.  **Suntik (Inject):** Script melakukan *looping* pada 130+ MK di "Kamus". Untuk setiap MK, script akan mengecek: "Apakah MK ini ada di dalam 'Otak'?"
3.  **Contoh Pencangkokan:**
    * Saat script memproses `TI0113` (Statistik) dari "Kamus", dia menemukannya di "Otak".
    * Script kemudian menggabungkan deskripsi aslinya dengan "contekan" dari "Otak".
    * **Teks Asli:** `"Deskripsi: Memberikan pemahaman tentang metode statistika..."`
    * **Teks Baru (Hasil Suntik):**
        ```
        Nama: Statistik
        Deskripsi: Memberikan pemahaman tentang metode statistika...

        --- CATATAN FONDASI (PENTING) --- 
        Ini adalah mata kuliah fondasi. Fondasi WAJIB untuk jalur Data/AI...
        RELEVANSI KUAT KE: Machine Learning, Data Warehouse, Analisis Data Statistik
        ```
4.  **Embedding:** Teks baru yang sudah "disuntik" inilah yang kemudian dikonversi menjadi vektor oleh model HuggingFace (`BAAI/bge-large-en-v1.5`).
5.  **Simpan:** Semua 130+ vektor (termasuk 10 yang sudah "di-boost") disimpan ke dalam database `faiss_index_matakuliah`.

Hasilnya adalah database vektor di mana MK Fondasi memiliki *kedekatan semantik* yang sangat tinggi dengan MK Spesialisasinya.

---

### 3. Logika RAG saat Runtime (Eksekusi AI)

Saat user menekan tombol "Berikan Rekomendasi" di `app.py`:

1.  **Full Context (Penglihatan Penuh):** Aplikasi **TIDAK** menjalankan *retriever* pencarian "Top-K". Sebaliknya, aplikasi mengambil **SELURUH 130+ DOKUMEN** dari database FAISS.
2.  **Format Konteks:** 130+ dokumen ini diformat menjadi satu string konteks raksasa, di mana setiap MK memiliki `Kategori:` (Wajib/Pilihan Wajib/dll).
3.  **Penyusunan Prompt:** AI (Groq) diberikan *prompt* yang berisi:
    * **Konteks Penuh:** (130+ MK yang sudah diformat).
    * **Input User:** (Transkrip `mk_lulus`, `total_sks`, dan `minat_user`).
    * **Aturan Main (Paling Penting):**
        * `ATURAN KORELASI`: "Kamu HARUS memprioritaskan rekomendasi berdasarkan `CATATAN FONDASI`..."
        * `ATURAN PRIORITAS`: "Kamu HARUS mengisi SKS dengan urutan: 1. MK Wajib yang tertinggal, 2. Pilihan Wajib Profesi, 3. Pilihan Bebas Prodi."
        * `ATURAN TARGET`: "Targetkan total SKS antara **18 hingga 24 SKS**."
4.  **Generasi Jawaban:** AI menerima "seluruh buku" (Full Context), "contekan" (Korelasi), dan "peraturan ujian" (Aturan Prompt). Dengan informasi lengkap ini, AI dipaksa untuk bertindak sebagai penasihat akademik yang patuh aturan dan cerdas, lalu mengembalikan jawaban dalam format JSON.

---

## 🛠️ Tumpukan Teknologi (Tech Stack)

* **Frontend:** Streamlit
* **Backend & Logika AI:** Python
* **Orkestrasi AI:** LangChain
* **Model LLM:** Groq (Llama 3)
* **Embeddings:** HuggingFace (`BAAI/bge-large-en-v1.5`)
* **Vector Database:** FAISS (dijalankan secara lokal)
* **Basis Data:** JSON (untuk `matakuliah.json` dan `korelasi_mk.json`)

## ⚙️ Setup & Instalasi

1.  **Clone repositori ini:**
    ```bash
    git clone [URL_REPO_ANDA]
    cd [NAMA_FOLDER_REPO]
    ```

2.  **Buat environment virtual (disarankan):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # (atau .\venv\Scripts\activate di Windows)
    ```

3.  **Install dependensi:**
    Buat file `requirements.txt` dan isi:
    ```
    streamlit
    langchain
    langchain-groq
    langchain-huggingface
    langchain-community
    faiss-cpu
    langchain-core
    ```
    Lalu install:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Setup API Key:**
    * Buat folder `.streamlit` di direktori utama.
    * Di dalamnya, buat file `secrets.toml`.
    * Isi file tersebut dengan Groq API key Anda:
        ```toml
        GROQ_API_KEY = "gsk_xxxxxxxxxxxxxxxxxxxxxxx"
        ```

5.  **Build "Otak" AI (Wajib!):**
    Pastikan `matakuliah.json` (lengkap) dan `korelasi_mk.json` ada di folder. Jalankan script `build_index.py` **satu kali**:
    ```bash
    python build_index.py
    ```
    Ini akan membuat folder `faiss_index_matakuliah` yang berisi database vektor.

6.  **Jalankan Aplikasi Streamlit:**
    ```bash
    streamlit run app.py
    ```

## 📂 Struktur File
