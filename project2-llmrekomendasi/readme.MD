# 🎓 Penasihat Akademik AI (Prodi Informatika UKDW)

Sebuah aplikasi web berbasis Streamlit yang berfungsi sebagai penasihat akademik pribadi untuk mahasiswa. Aplikasi ini menggunakan arsitektur RAG (Retrieval-Augmented Generation) canggih untuk menganalisis transkrip nilai mahasiswa dan memberikan rekomendasi mata kuliah yang personal dan akurat untuk semester depan.

## 🚀 Fitur Utama

* **Sistem Login Mahasiswa:** Simulasi halaman login menggunakan NIM dan password dengan data mahasiswa yang telah ditentukan.
* **Dashboard Akademik Interaktif:**
    * Menggunakan **Tab** (`st.tabs`) untuk memisahkan 4 kategori utama (Wajib, Pilihan Wajib Profesi, Pilihan Bebas Prodi, Pilihan Bebas Non-Prodi).
    * Menampilkan **seluruh** mata kuliah dalam kurikulum, dilengkapi penanda visual ("Sudah diambil (Nilai: A)" atau "Belum diambil").
    * Mata kuliah yang sudah diambil otomatis diurutkan ke bagian atas untuk visibilitas.
* **Pengelompokan Mata Kuliah Cerdas:**
    * **Wajib:** Dikelompokkan berdasarkan semester (Semester 1-8).
    * **Pilihan Wajib Profesi:** Dikelompokkan berdasarkan profesi (PSD, AI, DMS, INFRA, dll).
    * **Pilihan Bebas Prodi:** Dikelompokkan secara logis menjadi "MBKM" dan "Lainnya" (dengan *tagging* profesi) untuk menghindari duplikasi data.
* **Sistem Rekomendasi AI yang Cerdas:**
    * **Deteksi Minat Otomatis:** Menganalisis transkrip untuk mendeteksi profesi yang paling cocok berdasarkan nilai-nilai fondasi.
    * **Logika Prompt Prioritas 3 Lapis:** Memaksa AI untuk merekomendasikan mata kuliah berdasarkan urutan kepentingan: 1. MK Wajib -> 2. Pilihan Wajib Profesi -> 3. Pilihan Bebas Prodi.
    * **Target SKS:** AI diinstruksikan untuk mengisi KRS hingga penuh (target 18-24 SKS).
    * **Alasan yang Kontekstual:** AI memberikan alasan rekomendasi berdasarkan *korelasi konseptual* ("Karena nilai Statistik Anda A, yang merupakan fondasi kuat untuk Machine Learning...").

---

## 🧠 Arsitektur & Konsep AI (Penjelasan Sederhana)

Kecerdasan buatan (AI) dalam proyek ini dirancang untuk tidak sekadar "menebak". AI ini dibekali pemahaman konseptual tentang kurikulum.

### 1. Tantangan Awal: AI Tanpa Konteks

Jika kita hanya memberikan AI sebuah "kamus" berisi 130+ mata kuliah (file `matakuliah.json`), AI tersebut hanya akan taat pada deskripsi. Dia bisa membaca deskripsi "Statistik" dan "Machine Learning", tapi dia **tidak mengerti** bahwa kedua mata kuliah itu *berhubungan erat* secara konseptual.

Hasilnya, rekomendasi akan bersifat "abu-abu", hanya berdasarkan kemiripan kata dalam deskripsi.

### 2. Solusi: Arsitektur Dua Basis Data

Untuk mengatasi ini, kita menggunakan dua sumber data:

**A. `matakuliah.json` (Basis Data Faktual / "Kamus")**
* **Isi:** 130+ mata kuliah lengkap (deskripsi, SKS, prasyarat, kategori).
* **Fungsi:** Sebagai "kamus" fakta. AI menggunakan ini untuk mengecek prasyarat dan SKS.

**B. `korelasi_mk.json` (Basis Pengetahuan / "Otak")**
* **Isi:** HANYA 10 mata kuliah **Fondasi** (MK Wajib Semester 1-4) yang paling krusial.
* **Fungsi:** Sebagai "otak" atau *knowledge base* yang berisi wawasan ahli (seperti dosen). File ini memetakan hubungan konseptual antara MK Fondasi dan MK Spesialisasi.
* **Contoh Isi:**
    ```json
    {
      "kode_mk": "TI0113", // Statistik
      "notes": "Fondasi WAJIB untuk jalur Data/AI...",
      "topik_terkait": [
        "TI6043", // Machine Learning
        "TI3033"  // Data Warehouse
      ]
    }
    ```
* **Hasil:** Dengan "otak" ini, AI tidak lagi menebak. Dia tahu *fakta* bahwa nilai bagus di `Statistik` adalah sinyal kuat untuk mengambil `Machine Learning`.

### 3. Tahap Pra-Proses: "Pencangkokan" Konteks (build_index.py)

* "Otak" (`korelasi_mk.json`) tidak bisa diberikan langsung ke AI. Kita harus "mencangkokkannya" ke dalam "Kamus" (`matakuliah.json`).
* Script `build_index.py` melakukan proses ini. Script akan "menyuntikkan" catatan korelasi ke dalam deskripsi MK Fondasi.
* **Contoh Teks yang Dihasilkan untuk "Statistik":**
    ```
    Nama: Statistik
    Deskripsi: Memberikan pemahaman tentang metode statistika...
    
    --- CATATAN FONDASI (PENTING) --- 
    Ini adalah mata kuliah fondasi. Fondasi WAJIB untuk jalur Data/AI...
    RELEVANSI KUAT KE: Machine Learning, Data Warehouse...
    ```
* Teks yang sudah digabung inilah yang kemudian diubah menjadi vektor dan disimpan di database **FAISS**.

### 4. Tahap Eksekusi: AI yang "Cerdas" (app.py)

Saat Anda menekan tombol "Berikan Rekomendasi":

1.  **Konteks Penuh:** Aplikasi tidak mencari 20 MK teratas. Aplikasi mengambil **SELURUH 130+ MK** dari database FAISS dan memberikannya kepada AI.
2.  **Aturan Tegas:** AI diberikan 3 aturan prioritas yang ketat melalui *prompt*:
    1.  **Prioritas 1:** "Selesaikan dulu MK WAJIB yang belum diambil."
    2.  **Prioritas 2:** "Lalu, isi SKS dengan Pilihan Wajib Profesi menggunakan 'CATATAN FONDASI' sebagai panduan utama."
    3.  **Prioritas 3:** "Jika SKS belum penuh (target 18-24 SKS), isi sisanya dengan Pilihan Bebas Prodi."

**Intinya:** AI tidak lagi *menebak* berdasarkan kemiripan deskripsi, melainkan *mengikuti* 3 aturan prioritas menggunakan basis pengetahuan korelasi yang sudah kita tanamkan.

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

5.  **Build Basis Pengetahuan AI (Wajib!):**
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
