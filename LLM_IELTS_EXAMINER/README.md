# 🤖 AI Pelatih Menulis IELTS

[![Aplikasi Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://url-aplikasi-streamlit-lu.streamlit.app) 
## 📝 Pengantar

**AI Pelatih Menulis IELTS** adalah aplikasi web yang dirancang untuk membantu kandidat IELTS meningkatkan keterampilan Menulis Task 1 (General Training - Surat) dan Task 2 (Esai). Dengan memanfaatkan kekuatan *Large Language Models* (LLM) melalui Groq, *Retrieval-Augmented Generation* (RAG) dengan FAISS, dan kerangka kerja LangChain, alat ini memberikan umpan balik dan penilaian instan yang mendetail berdasarkan deskriptor band resmi IELTS.

Dibangun dengan Streamlit, aplikasi ini menawarkan antarmuka yang interaktif dan ramah pengguna untuk evaluasi yang mudah.

---

## ✨ Fitur Utama

* **Klasifikasi Tugas:** Secara otomatis mendeteksi apakah input adalah Task 1 atau Task 2.
* **Evaluasi Berbasis AI:** Memberikan skor tulisan berdasarkan empat kriteria IELTS:
    * *Task Achievement* (Task 1) / *Task Response* (Task 2)
    * *Coherence & Cohesion* (Koherensi & Kohesi)
    * *Lexical Resource* (Kosakata)
    * *Grammatical Range & Accuracy* (Rentang Tata Bahasa & Akurasi)
* **Umpan Balik Mendetail:** Memberikan komentar spesifik untuk setiap kriteria, menyoroti kelebihan dan kekurangan.
* **Saran yang Dapat Ditindaklanjuti:** Menawarkan tips konkret tentang cara memperbaiki tulisan.
* **Koreksi (Proofreading):** Mengidentifikasi dan menyarankan perbaikan untuk kesalahan tata bahasa dan frasa yang kaku.
* **Revisi Otomatis:** Memungkinkan pengguna meminta AI untuk menulis ulang esai mereka agar mencapai target skor band yang lebih tinggi.
* **Integrasi RAG:** Menggunakan *vector store* FAISS lokal yang berisi konteks IELTS yang relevan untuk meningkatkan akurasi dan relevansi evaluasi.
* **Inferensi Cepat:** Didukung oleh Mesin Inferensi LPU Groq untuk analisis yang cepat.

---

## 🛠️ Teknologi yang Digunakan

* **Kerangka Kerja:** [LangChain](https://www.langchain.com/)
* **Penyedia LLM:** [Groq](https://groq.com/) (menggunakan model seperti Llama 3.3 70B)
* **UI:** [Streamlit](https://streamlit.io/)
* **Vector Store:** [FAISS](https://faiss.ai/) (CPU)
* **Embeddings:** [BAAI/bge-large-en-v1.5](https://huggingface.co/BAAI/bge-large-en-v1.5) (atau model pilihan Anda)
* **Library Inti:** `python-dotenv`, `streamlit`, `langchain`, `langchain-groq`, `faiss-cpu`, `sentence-transformers`

---

## 🚀 Cara Penggunaan

1.  **Akses Aplikasi:** Kunjungi aplikasi yang sudah di-*deploy* [di sini](https://url-aplikasi-streamlit-lu.streamlit.app). 
    2.  **Input:** Tempel (paste) soal IELTS Writing Task 1 atau Task 2 Anda di area teks pertama.
3.  **Submit:** Tempel jawaban esai/surat Anda di area teks kedua.
4.  **Evaluasi:** Klik tombol "🚀 Evaluasi Sekarang!".
5.  **Tinjau:** Analisis umpan balik mendetail, skor, saran, dan koreksi yang diberikan oleh AI di panel hasil.
6.  **(Opsional) Revisi:** Gunakan fitur "Opsi Revisi Otomatis" untuk melihat bagaimana AI akan menulis ulang esai Anda ke band yang lebih tinggi.

---

## 🔧 Menjalankan Secara Lokal (Opsional)

1.  **Clone:** `git clone https://github.com/nama-pengguna-lu/nama-repo-lu.git`
2.  **Navigasi:** `cd nama-repo-lu/LLM_IELTS_EXAMINER`
3.  **Instal:** `pip install -r requirements.txt`
4.  **Rahasia (Secrets):** Buat file `.env` dan tambahkan `GROQ_API_KEY="kunci_api_groq_lu"` di dalamnya.
5.  **Jalankan:** `streamlit run app.py`

---

*Penafian: Skor dan umpan balik yang diberikan oleh alat AI ini adalah perkiraan berdasarkan deskriptor band IELTS dan sebaiknya digunakan hanya untuk tujuan latihan. Hasil ini bukan pengganti evaluasi oleh penguji IELTS bersertifikat.*
