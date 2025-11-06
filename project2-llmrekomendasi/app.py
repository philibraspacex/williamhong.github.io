import streamlit as st
import os
import json
import re
from operator import itemgetter
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import JsonOutputParser




DATA_MAHASISWA = {
    "7123001": {
        "nama": "William",
        "password": "william123", 
        "transkrip_text": (
            "Pendidikan Agama Kristen: B+\nBahasa Indonesia: A-\nInteraksi Manusia dan Komputer: B\nTeknologi Komputer: B+\nPraktikum Teknologi Komputer: A\nMatematika Teknik: B-\nLogika Matematika: B\nPendidikan Kewarganegaraan: A\nAlgoritma dan Pemrograman: B\nPraktikum Algoritma dan Pemrograman: A-\nMatematika Diskrit: C+\nArsitektur dan Organisasi Komputer: B-\nStatistik: B\nJaringan Komputer: B\nPraktikum Jaringan Komputer: B+\nStruktur Data: B\nPraktikum Struktur Data: B+\nInfrastruktur LAN: B-\nPraktikum Infrastruktur LAN: B+\nSistem Basis Data: B+\nPraktikum Sistem Basis Data: A\nRiset Operasi: D\nSistem Operasi: C+\nPendidikan Pancasila: A\nKecerdasan Buatan: B\nKeamanan Komputer: C\nEtika Profesi Teknologi Informasi: B+\nPemrograman Web: B+\nPraktikum Pemrograman Web: A\nRekayasa Perangkat Lunak Berorientasi Obyek: B-\nPraktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B\n"
        )
    },
    "7123002": {
        "nama": "Jonathan",
        "password": "jonathan123", 
        "transkrip_text": (
            "Pendidikan Agama Kristen: A\nBahasa Indonesia: A\nInteraksi Manusia dan Komputer: A-\nTeknologi Komputer: A\nPraktikum Teknologi Komputer: A\nMatematika Teknik: A\nLogika Matematika: A\nPendidikan Kewarganegaraan: A\nAlgoritma dan Pemrograman: A\nPraktikum Algoritma dan Pemrograman: A\nMatematika Diskrit: A-\nArsitektur dan Organisasi Komputer: B+\nStatistik: A\nJaringan Komputer: A-\nPraktikum Jaringan Komputer: A\nStruktur Data: A\nPraktikum Struktur Data: A\nInfrastruktur LAN: B+\nPraktikum Infrastruktur LAN: A\nSistem Basis Data: A\nPraktikum Sistem Basis Data: A\nRiset Operasi: B+\nSistem Operasi: B+\nPendidikan Pancasila: A\nKecerdasan Buatan: A\nKeamanan Komputer: A-\nEtika Profesi Teknologi Informasi: A\nPemrograman Web: A\nPraktikum Pemrograman Web: A\nRekayasa Perangkat Lunak Berorientasi Obyek: A-\nPraktikum Rekayasa Perangkat Lunak Berorientasi Obyek: A\nMachine Learning: A-\n"
        )
    },
    "7123003": {
        "nama": "steven",
        "password": "steven123", 
        "transkrip_text": (
            "Pendidikan Agama Kristen: B\nBahasa Indonesia: B+\nInteraksi Manusia dan Komputer: B-\nTeknologi Komputer: B\nPraktikum Teknologi Komputer: B+\nMatematika Teknik: C\nLogika Matematika: B-\nPendidikan Kewarganegaraan: B+\nAlgoritma dan Pemrograman: C+\nPraktikum Algoritma dan Pemrograman: B\nMatematika Diskrit: C\nArsitektur dan Organisasi Komputer: C+\nStatistik: B-\nJaringan Komputer: C+\nPraktikum Jaringan Komputer: B-\nStruktur Data: C+\nPraktikum Struktur Data: B\nInfrastruktur LAN: C\nPraktikum Infrastruktur LAN: C+\nSistem Basis Data: C+\nPraktikum Sistem Basis Data: B+\nRiset Operasi: C-\nSistem Operasi: C\nPendidikan Pancasila: A-\nKecerdasan Buatan: C+\nKeamanan Komputer: C\nEtika Profesi Teknologi Informasi: B\nPemrograman Web: B-\nPraktikum Pemrograman Web: B\nRekayasa Perangkat Lunak Berorientasi Obyek: C+\nPraktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B-\nAdministrasi Basis Data: B-\n"
        )
    },
    "7122001": {
        "nama": "bio",
        "password": "bio123", 
        "transkrip_text": (
            "Pendidikan Agama Kristen: A\nBahasa Indonesia: A-\nInteraksi Manusia dan Komputer: A-\nTeknologi Komputer: B+\nPraktikum Teknologi Komputer: A\nMatematika Teknik: B+\nLogika Matematika: A\nPendidikan Kewarganegaraan: A\nAlgoritma dan Pemrograman: A\nPraktikum Algoritma dan Pemrograman: A\nMatematika Diskrit: B+\nArsitektur dan Organisasi Komputer: B+\nStatistik: A-\nJaringan Komputer: B+\nPraktikum Jaringan Komputer: A\nStruktur Data: A\nPraktikum Struktur Data: A\nInfrastruktur LAN: B+\nPraktikum Infrastruktur LAN: A\nSistem Basis Data: A\nPraktikum Sistem Basis Data: A\nRiset Operasi: B\nSistem Operasi: A-\nPendidikan Pancasila: A\nKecerdasan Buatan: A\nKeamanan Komputer: B+\nEtika Profesi Teknologi Informasi: A\nPemrograman Web: A-\nPraktikum Pemrograman Web: A\nRekayasa Perangkat Lunak Berorientasi Obyek: B+\nPraktikum Rekayasa Perangkat Lunak Berorientasi Obyek: A\nMachine Learning: A\nManajemen Proyek Teknologi Informasi: B+\nData Warehouse: B+\nPemrosesan Bahasa Natural: A-\nJaringan Syaraf Tiruan: B+\nPemrosesan Citra Digital: A-\n"
        )
    },
    "7122002": {
        "nama": "antony",
        "password": "antony123", 
        "transkrip_text": (
            "Pendidikan Agama Kristen: B+\nBahasa Indonesia: A-\nInteraksi Manusia dan Komputer: B\nTeknologi Komputer: B\nPraktikum Teknologi Komputer: B+\nMatematika Teknik: C+\nLogika Matematika: B+\nPendidikan Kewarganegaraan: A\nAlgoritma dan Pemrograman: B+\nPraktikum Algoritma dan Pemrograman: A\nMatematika Diskrit: B\nArsitektur dan Organisasi Komputer: C+\nStatistik: B-\nJaringan Komputer: B-\nPraktikum Jaringan Komputer: B\nStruktur Data: B\nPraktikum Struktur Data: A-\nInfrastruktur LAN: B-\nPraktikum Infrastruktur LAN: B\nSistem Basis Data: B+\nPraktikum Sistem Basis Data: A\nRiset Operasi: C+\nSistem Operasi: B-\nPendidikan Pancasila: A\nKecerdasan Buatan: C+\nKeamanan Komputer: C\nEtika Profesi Teknologi Informasi: B+\nPemrograman Web: A-\nPraktikum Pemrograman Web: A\nRekayasa Perangkat Lunak Berorientasi Obyek: B\nPraktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B+\nTest Engineering: B\nManajemen Proyek Teknologi Informasi: A-\nPemrograman Perangkat Bergerak Berbasis Android: B+\nPemrograman Web Lanjut: A-\nPemodelan Proses Bisnis: B\nPola Desain Antarmuka Pengguna: B+\nDesain dan Evaluasi Antarmuka: B\nUX Writing dan Storytelling: A-\n"
        )
    },
    
    # ==========================================================
    # --- 4 PERSONA BARU UNTUK TESTING AI ---
    # ==========================================================

    # --- 1. PERSONA: PUTRA (JAGO PSD) ---
    "7122101": {
        "nama": "Putra PSD",
        "password": "putra123", 
        "transkrip_text": (
            # Sem 1 (PSD Bagus, Lainnya Cukup)
            "Pendidikan Agama Kristen: B\nBahasa Indonesia: B+\n"
            "Interaksi Manusia dan Komputer: A\n" # <-- FONDASI PSD (NILAI A)
            "Teknologi Komputer: C+\n"
            "Praktikum Teknologi Komputer: B-\n"
            "Matematika Teknik: B-\n"
            "Logika Matematika: A-\n" # <-- FONDASI PSD
            
            # Sem 2 (PSD Bagus, Lainnya Cukup)
            "Pendidikan Kewarganegaraan: B+\n"
            "Algoritma dan Pemrograman: A\n" # <-- FONDASI PSD (NILAI A)
            "Praktikum Algoritma dan Pemrograman: A\n" # <-- FONDASI PSD (NILAI A)
            "Matematika Diskrit: B\n"
            "Arsitektur dan Organisasi Komputer: C\n"
            "Statistik: C+\n" # <-- Fondasi AI/DMS (Nilai Cukup)
            "Jaringan Komputer: C\n" # <-- Fondasi INFRA (Nilai Cukup)
            "Praktikum Jaringan Komputer: B-\n"
            
            # Sem 3 (PSD Bagus, Lainnya Cukup)
            "Struktur Data: A\n" # <-- FONDASI PSD (NILAI A)
            "Praktikum Struktur Data: A\n"
            "Infrastruktur LAN: C+\n"
            "Praktikum Infrastruktur LAN: B-\n"
            "Sistem Basis Data: B\n" # <-- Fondasi DMS (Nilai Cukup)
            "Praktikum Sistem Basis Data: B+\n"
            "Riset Operasi: B-\n"
            "Sistem Operasi: B\n"
            
            # Sem 4 (PSD Bagus, Lainnya Cukup)
            "Pendidikan Pancasila: A-\n"
            "Rekayasa Perangkat Lunak Berorientasi Obyek: A\n" # <-- FONDASI PSD (NILAI A)
            "Praktikum Rekayasa Perangkat Lunak Berorientasi Obyek: A\n" # <-- FONDASI PSD (NILAI A)
            "Pemrograman Web: A-\n" # <-- FONDASI PSD (NILAI A)
            "Praktikum Pemrograman Web: A\n"
            "Kecerdasan Buatan: C+\n" # <-- Fondasi AI (Nilai Cukup)
            "Keamanan Komputer: C+\n"
            "Etika Profesi Teknologi Informasi: B+\n"
            
            # Sem 5 (Ambil Pilihan PSD)
            "Manajemen Proyek Teknologi Informasi: B+\n"
            "Test Engineering: A\n" # Pilihan PSD
            "Pola Desain Antarmuka Pengguna: A-\n" # Pilihan PSD
            "Pemodelan Proses Bisnis: A\n" # Pilihan PSD
            "Pemrograman Web Lanjut: A\n" # Pilihan PSD
            "UX Writing dan Storytelling: A-\n" # Pilihan PSD
            "Kriptografi: B+\n" # Pilihan PSD
        )
    },

    # --- 2. PERSONA: ANI (JAGO AI) ---
    "7122102": {
        "nama": "Ani AI",
        "password": "ani123", 
        "transkrip_text": (
            # Sem 1 (AI Bagus, Lainnya Cukup)
            "Pendidikan Agama Kristen: B\nBahasa Indonesia: B\n"
            "Interaksi Manusia dan Komputer: C+\n" # <-- Fondasi PSD (Nilai Cukup)
            "Teknologi Komputer: B\n"
            "Praktikum Teknologi Komputer: B+\n"
            "Matematika Teknik: A\n"
            "Logika Matematika: A\n" # <-- FONDASI AI (NILAI A)
            
            # Sem 2 (AI Bagus, Lainnya Cukup)
            "Pendidikan Kewarganegaraan: B\n"
            "Algoritma dan Pemrograman: A-\n" # <-- FONDASI AI (NILAI A)
            "Praktikum Algoritma dan Pemrograman: A\n"
            "Matematika Diskrit: A-\n"
            "Arsitektur dan Organisasi Komputer: B+\n"
            "Statistik: A\n" # <-- FONDASI AI (NILAI A)
            "Jaringan Komputer: C+\n" # <-- Fondasi INFRA (Nilai Cukup)
            "Praktikum Jaringan Komputer: B\n"
            
            # Sem 3 (AI Bagus, Lainnya Cukup)
            "Struktur Data: A\n" # <-- FONDASI AI (NILAI A)
            "Praktikum Struktur Data: A\n"
            "Infrastruktur LAN: B-\n"
            "Praktikum Infrastruktur LAN: B\n"
            "Sistem Basis Data: B-\n" # <-- Fondasi DMS (Nilai Cukup)
            "Praktikum Sistem Basis Data: B\n"
            "Riset Operasi: A-\n"
            "Sistem Operasi: C+\n"
            
            # Sem 4 (AI Bagus, Lainnya Cukup)
            "Pendidikan Pancasila: A-\n"
            "Rekayasa Perangkat Lunak Berorientasi Obyek: B-\n" # <-- Fondasi PSD (Nilai Cukup)
            "Praktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B\n"
            "Pemrograman Web: C+\n" # <-- Fondasi PSD (Nilai Cukup)
            "Praktikum Pemrograman Web: B\n"
            "Kecerdasan Buatan: A\n" # <-- FONDASI AI (NILAI A)
            "Keamanan Komputer: B-\n"
            "Etika Profesi Teknologi Informasi: B\n"
            
            # Sem 5 (Ambil Pilihan AI)
            "Manajemen Proyek Teknologi Informasi: B\n"
            "Machine Learning: A\n" # Pilihan AI
            "Jaringan Syaraf Tiruan: A\n" # Pilihan AI
            "Pemrosesan Bahasa Natural: A-\n" # Pilihan AI
            "Deep Learning: A\n" # Pilihan AI
            "Sistem Pakar: A-\n" # Pilihan AI
            "Algoritma Graf: B+\n" # Pilihan AI
        )
    },

    # --- 3. PERSONA: DODI (JAGO DMS) ---
    "7122103": {
        "nama": "Dodi DMS",
        "password": "dodi123", 
        "transkrip_text": (
            # Sem 1 (DMS Bagus, Lainnya Cukup)
            "Pendidikan Agama Kristen: B+\nBahasa Indonesia: B\n"
            "Interaksi Manusia dan Komputer: C+\n" # <-- Fondasi PSD (Nilai Cukup)
            "Teknologi Komputer: B-\n"
            "Praktikum Teknologi Komputer: B\n"
            "Matematika Teknik: A-\n"
            "Logika Matematika: B\n"
            
            # Sem 2 (DMS Bagus, Lainnya Cukup)
            "Pendidikan Kewarganegaraan: B\n"
            "Algoritma dan Pemrograman: B\n" 
            "Praktikum Algoritma dan Pemrograman: B+\n"
            "Matematika Diskrit: B-\n"
            "Arsitektur dan Organisasi Komputer: C+\n"
            "Statistik: A\n" # <-- FONDASI DMS (NILAI A)
            "Jaringan Komputer: C+\n"
            "Praktikum Jaringan Komputer: B-\n"
            
            # Sem 3 (DMS Bagus, Lainnya Cukup)
            "Struktur Data: B\n"
            "Praktikum Struktur Data: B+\n"
            "Infrastruktur LAN: C\n"
            "Praktikum Infrastruktur LAN: C+\n"
            "Sistem Basis Data: A\n" # <-- FONDASI DMS (NILAI A)
            "Praktikum Sistem Basis Data: A\n" # <-- FONDASI DMS (NILAI A)
            "Riset Operasi: B\n"
            "Sistem Operasi: C+\n"
            
            # Sem 4 (DMS Bagus, Lainnya Cukup)
            "Pendidikan Pancasila: A-\n"
            "Rekayasa Perangkat Lunak Berorientasi Obyek: C+\n" # <-- Fondasi PSD (Nilai Cukup)
            "Praktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B\n"
            "Pemrograman Web: C+\n"
            "Praktikum Pemrograman Web: B\n"
            "Kecerdasan Buatan: C\n" # <-- Fondasi AI (Nilai Cukup)
            "Keamanan Komputer: B-\n"
            "Etika Profesi Teknologi Informasi: B\n"
            
            # Sem 5 (Ambil Pilihan DMS)
            "Manajemen Proyek Teknologi Informasi: B\n"
            "Administrasi Basis Data: A\n" # Pilihan DMS
            "Data Warehouse: A\n" # Pilihan DMS
            "Basis Data Terdistribusi: A-\n" # Pilihan DMS
            "Keamanan Basis Data: A\n" # Pilihan DMS
            "Analisis Data Statistik: A-\n" # Pilihan DMS/AI
            "Praktikum Keahlian Khusus – SAP (Lab): B+\n" # Pilihan DMS
        )
    },

    # --- 4. PERSONA: INDAH (JAGO INFRA) ---
    "7122104": {
        "nama": "Indah INFRA",
        "password": "indah123", 
        "transkrip_text": (
            # Sem 1 (INFRA Bagus, Lainnya Cukup)
            "Pendidikan Agama Kristen: B\nBahasa Indonesia: B+\n"
            "Interaksi Manusia dan Komputer: C\n" # <-- Fondasi PSD (Nilai Cukup)
            "Teknologi Komputer: A\n" # <-- FONDASI INFRA (NILAI A)
            "Praktikum Teknologi Komputer: A\n" # <-- FONDASI INFRA (NILAI A)
            "Matematika Teknik: B-\n"
            "Logika Matematika: B\n"
            
            # Sem 2 (INFRA Bagus, Lainnya Cukup)
            "Pendidikan Kewarganegaraan: B+\n"
            "Algoritma dan Pemrograman: B-\n" 
            "Praktikum Algoritma dan Pemrograman: B\n"
            "Matematika Diskrit: C+\n"
            "Arsitektur dan Organisasi Komputer: B+\n"
            "Statistik: C\n" # <-- Fondasi AI/DMS (Nilai Cukup)
            "Jaringan Komputer: A\n" # <-- FONDASI INFRA (NILAI A)
            "Praktikum Jaringan Komputer: A\n" # <-- FONDASI INFRA (NILAI A)
            
            # Sem 3 (INFRA Bagus, Lainnya Cukup)
            "Struktur Data: C+\n"
            "Praktikum Struktur Data: B\n"
            "Infrastruktur LAN: A\n" # <-- FONDASI INFRA (NILAI A)
            "Praktikum Infrastruktur LAN: A\n" # <-- FONDASI INFRA (NILAI A)
            "Sistem Basis Data: C+\n" # <-- Fondasi DMS (Nilai Cukup)
            "Praktikum Sistem Basis Data: B\n"
            "Riset Operasi: C\n"
            "Sistem Operasi: A-\n" # <-- FONDASI INFRA (NILAI A)
            
            # Sem 4 (INFRA Bagus, Lainnya Cukup)
            "Pendidikan Pancasila: A-\n"
            "Rekayasa Perangkat Lunak Berorientasi Obyek: C\n" # <-- Fondasi PSD (Nilai Cukup)
            "Praktikum Rekayasa Perangkat Lunak Berorientasi Obyek: B-\n"
            "Pemrograman Web: C\n"
            "Praktikum Pemrograman Web: B-\n"
            "Kecerdasan Buatan: C\n" # <-- Fondasi AI (Nilai Cukup)
            "Keamanan Komputer: A\n" # <-- FONDASI INFRA (NILai A)
            "Etika Profesi Teknologi Informasi: B\n"
            
            # Sem 5 (Ambil Pilihan INFRA)
            "Manajemen Proyek Teknologi Informasi: B\n"
            "Cloud Infrastructure: A\n" # Pilihan INFRA
            "Enterprise Network: A\n" # Pilihan INFRA
            "Pengantar Keamanan Jaringan: A-\n" # Pilihan INFRA
            "Jaringan Nir Kabel: A\n" # Pilihan INFRA
            "Otomasi Jaringan: B+\n" # Pilihan INFRA
            "Internet of Things: B+\n" # Pilihan AI/INFRA
        )
    }
}
# ==========================================================
# AKHIR DARI DATABASE
# ==========================================================



def parse_mk_lulus(text_input):
    """Mengubah text area input 'MK: Nilai' jadi dictionary (key jadi lowercase)."""
    mk_dict = {}
    for line in text_input.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            # --- UBAH INI: .strip() jadi .strip().lower() ---
            mk_name = parts[0].strip().lower() 
            nilai = parts[1].strip().upper().split()[0]
            if mk_name and nilai:
                mk_dict[mk_name] = nilai
    return mk_dict

# ==========================================================
# BAGIAN CACHING: LOAD MODEL & DATABASE
# ==========================================================

@st.cache_resource
def load_llm():
    """Load LLM Groq dari st.secrets dan cache."""
    try:
        groq_api_key = st.secrets["GROQ_API_KEY"]
        if not groq_api_key or groq_api_key == "gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
            st.error("GROQ_API_KEY tidak ditemukan/belum diganti di `.streamlit/secrets.toml`!")
            return None
            
        llm = ChatGroq(
            groq_api_key=groq_api_key,
            model_name="llama-3.3-70b-versatile", # Update ke model terbaru
            temperature=0.1
        )
        print(">>> [SUKSES] LLM Groq berhasil dimuat!")
        return llm
    except Exception as e:
        st.error(f"Gagal memuat LLM Groq: {e}")
        return None

# --- [GANTI FUNGSI INI] ---
@st.cache_resource
def load_retriever():
    """Load model embedding dan FAISS index dari folder lokal."""
    
    # --- 1. Load Model Embedding ---
    print("Memuat model embedding...")
    try:
        model_name = "BAAI/bge-large-en-v1.5"
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        embedding_model = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        print("Model embedding dimuat.")
    except Exception as e:
        st.error(f"Gagal memuat model embedding: {e}")
        return None

    # --- 2. Load FAISS Index dari Disk ---
    
    index_folder = "faiss_index_matakuliah" 
    
    print(f"Mencoba memuat index FAISS dari folder '{index_folder}'...")
    if os.path.exists(index_folder):
        try:
            vector_store = FAISS.load_local(
                index_folder,
                embedding_model,
                allow_dangerous_deserialization=True
            )
            retriever = vector_store.as_retriever(search_kwargs={'k': 20}) # Ambil 20 dokumen
            print("✅ Index FAISS berhasil dimuat dan retriever dibuat.")
            return retriever
        except Exception as e:
            st.error(f"Gagal memuat index FAISS: {e}")
            return None
    else:
        st.error(f"❌ Folder index '{index_folder}' tidak ditemukan! Pastikan lu udah jalanin 'build_index.py' dulu.")
        return None

# ==========================================================
# BAGIAN RAG CHAIN (PROMPT & LOGIC)
# ==========================================================
prompt_text = """<|system|>
Anda adalah Penasihat Akademik AI yang sangat teliti untuk Program Studi Informatika UKDW.
Misi Anda adalah memberikan rekomendasi mata kuliah yang personal, akurat, dan patuh pada aturan prasyarat serta distribusi SKS kurikulum.

ATURAN PERBANDINGAN NILAI (PENTING!):
Gunakan hirarki nilai ini: A > A- > B+ > B > B- > C+ > C > D > E.
- Jika nilai minimum adalah 'D', maka 'C', 'B', 'A' juga Lulus.
- Jika nilai minimum adalah 'C', maka 'D', 'E' TIDAK Lulus.

DATA KORELASI FONDASI (LOGIKA UTAMA REKOMENDASI):
Selain deskripsi biasa, beberapa mata kuliah FONDASI (MK Wajib Semester 1-4) di dalam CONTEXT sekarang memiliki "contekan" korelasi di dalam deskripsinya, dengan format:
"--- CATATAN FONDASI (PENTING) ---"
"Ini adalah mata kuliah fondasi. [Penjelasan fondasi]"
"RELEVANSI KUAT KE: [Daftar nama MK Spesialisasi]"
Gunakan ini sebagai alasan utama rekomendasi Anda jika nilai mahasiswa di MK Fondasi tersebut bagus.

DATA YANG ANDA MILIKI (KATALOG MATA KULIAH LENGKAP):
Anda memiliki akses ke seluruh katalog mata kuliah. Formatnya:
Kode: [Kode MK] Nama: [Nama Mata Kuliah] SKS: [Jumlah SKS] Kategori: [Wajib/Pilihan Wajib Profesi/dll] Prasyarat SKS Total: [Jumlah] Prasyarat MK (JSON): [String JSON] Profesi Relevan: [List Profesi] Deskripsi: [Deskripsi MK]

# Contoh literal JSON (DI-ESCAPE):
{{
    "kode": "TI0022",
    "nama": "Praktikum Teknologi Komputer",
    "kategori": "Wajib",
    ...
}}

ATURAN REKOMENDASI BARU (WAJIB DIIKUTI SECARA BERURUTAN):

Anda harus membangun daftar rekomendasi dengan target total **18 hingga 24 SKS**.
Ikuti 3 langkah prioritas ini untuk mengisi SKS tersebut:

1.  **PRIORITAS 1: MATA KULIAH WAJIB YANG TERTINGGAL**
    - Pertama, cek SELURUH mata kuliah dengan "Kategori: Wajib" (dari Semester 1-8) di CONTEXT.
    - Bandingkan dengan `mk_lulus` mahasiswa.
    - Jika ada MK Wajib yang belum diambil (tidak ada di `mk_lulus`) DAN semua prasyaratnya (dijelaskan di ATURAN PRASYARAT) sudah terpenuhi, maka MK Wajib tersebut **HARUS** dimasukkan ke dalam rekomendasi. Ini adalah prioritas utama.

2.  **PRIORITAS 2: PILIHAN WAJIB PROFESI (SESUAI MINAT)**
    - Setelah MK Wajib terpenuhi, isi sisa SKS dengan mata kuliah dari "Kategori: Pilihan Wajib Profesi".
    - Fokus HANYA pada MK yang `profesi_relevan`-nya cocok dengan `minat_user`.
    - Gunakan `CATATAN FONDASI` sebagai panduan utama untuk memilih.
    - Pastikan ATURAN PRASYARAT terpenuhi.

3.  **PRIORITAS 3: PILIHAN BEBAS PRODI (SESUAI MINAT)**
    - Jika SKS masih belum penuh (belum 18 SKS) setelah mengambil Wajib dan Pilihan Wajib Profesi,
    - Isi sisa SKS dengan mata kuliah dari "Kategori: Pilihan Bebas Prodi".
    - Fokus HANYA pada MK yang `profesi_relevan`-nya cocok dengan `minat_user`.
    - Gunakan `CATATAN FONDASI` sebagai panduan.
    - Pastikan ATURAN PRASYARAT terpenuhi.

ATURAN PRASYARAT (BERLAKU UNTUK SEMUA REKOMENDASI):
Sebuah mata kuliah (MK Rekomendasi) HANYA BOLEH direkomendasikan jika SEMUA kondisi berikut terpenuhi:
    a. MK Rekomendasi belum ada di `mk_lulus`.
    b. `total_sks_lulus` mahasiswa >= `prasyarat_sks_total` MK Rekomendasi.
    c. Untuk SETIAP prasyarat di `Prasyarat MK (JSON)`:
        i.   (Anda harus mem-parsing string JSON ini). Ambil info: kode MK prasyarat, nilai minimum yang dibutuhkan, dan apakah boleh diambil bersamaan.
        ii.  Cek `mk_lulus`: Apakah kode MK prasyarat ada di `mk_lulus` DAN nilainya >= nilai minimum yang dibutuhkan?
        iii. Cek `mk_sedang_ambil`: Jika info 'boleh diambil bersamaan' adalah `true`, cek apakah kode MK prasyarat ada di `mk_sedang_ambil`.
        iv.  Kondisi prasyarat terpenuhi jika (ii) ATAU (iii) bernilai benar.
        v.   Jika `Prasyarat MK (JSON)` kosong (`[]`), prasyarat ini otomatis terpenuhi.

ATURAN PENGECUALIAN:
- Jangan merekomendasikan MK dari "Kategori: Pilihan Bebas Non-Prodi" kecuali diminta.
- Jangan merekomendasikan MK dengan catatan "[CATATAN: ... MBKM ...]" di deskripsinya kecuali diminta.

FORMAT JSON OUTPUT YANG WAJIB DIIKUTI:
- "rekomendasi": (Sebuah list)
  - Setiap item di list adalah obyek dengan key: "nama_mk", "sks", "tentang_mk", "alasan_rekomendasi", "wawasan_nilai".
- "wawasan_performa": (Sebuah string)
- "rekomendasi_alternatif": (Sebuah string, atau string kosong)

INPUT DATA MAHASISWA:
minat_user: List profesi (e.g., ["AI", "PSD"]).
mk_lulus: Dictionary. Key: Nama/Kode MK. Value: Nilai huruf.
mk_sedang_ambil: List. Key: Nama/Kode MK. (e.g., ["Sistem Basis Data"])
total_sks_lulus: Integer.
CONTEXT (Katalog Mata Kuliah Lengkap):
{context}
<|end_system|> <|user|> 
Berikan rekomendasi mata kuliah berdasarkan data di atas, dengan memperhatikan aturan distribusi SKS kurikulum dan prasyarat.
Minat User (List Profesi): {minat_user}
Mata Kuliah Lulus & Nilai: {mk_lulus}
Mata Kuliah Sedang Diambil: {mk_sedang_ambil}
Total SKS Lulus: {total_sks_lulus}
<|end_user|> <|assistant|>
"""


prompt_template = PromptTemplate(
    template=prompt_text,
    input_variables=["minat_user", "mk_lulus", "mk_sedang_ambil", "total_sks_lulus", "context"]
)



# CARI FUNGSI INI DI app.py
def format_docs(docs):
    """Menggabungkan page_content dan metadata dari list Dokumen jadi satu string."""
    formatted_context = "\n\n---\n\n".join([
        f"Kode: {doc.metadata.get('kode', 'N/A')}\n"
        f"Nama: {doc.metadata.get('nama', 'N/A')}\n"
        f"SKS: {doc.metadata.get('sks', 0)}\n"
        # --- [TAMBAHKAN BARIS INI] ---
        f"Kategori: {doc.metadata.get('kategori', 'N/A')}\n" 
        # --- [AKHIR TAMBAHAN] ---
        f"Semester Umum: {doc.metadata.get('semester_umum', 'N/A')}\n"
        f"Prasyarat SKS Total: {doc.metadata.get('prasyarat_sks_total', 0)}\n"
        f"Prasyarat MK (JSON): {doc.metadata.get('prasyarat_mk_json', '[]')}\n"
        f"Profesi Relevan: {doc.metadata.get('profesi_relevan', 'N/A')}\n"
        f"Deskripsi: {doc.page_content.split('Deskripsi: ')[1] if 'Deskripsi: ' in doc.page_content else doc.page_content}"
        for doc in docs
    ])
    return formatted_context



@st.cache_resource
def get_rag_chain(_llm, _retriever):
    """Buat dan cache RAG chain (dengan output JSON).
    VERSI BARU: Menggunakan FULL CONTEXT, BUKAN RETRIEVER.
    """
    print(">>> Membuat RAG chain (Full Context)...")
    
    # 1. Ambil SEMUA dokumen dari docstore
    try:
        # Akses docstore internal FAISS
        all_docs = list(_retriever.vectorstore.docstore._dict.values())
        if not all_docs:
            raise Exception("Docstore kosong atau _dict tidak ditemukan.")
        print(f">>> [INFO] Berhasil memuat {len(all_docs)} dokumen dari docstore.")
    except Exception as e:
        print(f">>> [ERROR] Gagal mengambil dari docstore: {e}. Mencoba fallback...")

        try:
            
            _retriever_all = _retriever.vectorstore.as_retriever(search_kwargs={'k': 150}) # Ambil 150+ MK
           
            all_docs = _retriever_all.invoke("mata kuliah") 
            print(f">>> [INFO] Fallback K=150 berhasil, memuat {len(all_docs)} dokumen.")
        except Exception as e2:
            print(f">>> [GAGAL] Fallback K=150 gagal: {e2}.")
            st.error(f"Gagal total memuat context: {e2}")
            return None


    full_context_string = format_docs(all_docs)
    if not full_context_string:
         print(">>> [GAGAL] format_docs mengembalikan string kosong.")
         return None
    print(">>> [INFO] String context penuh (full context) berhasil dibuat.")

    # 3. Buat chain yang MENGABAIKAN retriever-based query
    setup_chain = RunnableParallel(
        {
            # "context" tidak lagi diambil dari retriever, tapi disuntik statis
            "context": lambda x: full_context_string, 
            "minat_user": RunnableLambda(lambda x: str(x["minat_user"])), 
            "mk_lulus": RunnableLambda(lambda x: x["mk_lulus"]),
            "mk_sedang_ambil": RunnableLambda(lambda x: x["mk_sedang_ambil"]), 
            "total_sks_lulus": RunnableLambda(lambda x: x["total_sks_lulus"])
        }
    )

    rag_chain = (
        setup_chain
        | prompt_template
        | _llm
        | JsonOutputParser() 
    )
    print("✅ RAG Chain (Full Context) siap.")
    return rag_chain

# --- AKHIR BLOK PENGGANTI ---

# ==========================================================
# BAGIAN UTAMA: TAMPILAN UI STREAMLIT (DENGAN LOGIN)
# ==========================================================

def show_login_screen():
    """Menampilkan halaman login."""
    st.set_page_config(page_title="Login", layout="centered")
    st.title("🔒 Login")
    st.markdown("Silakan login menggunakan NIM dan password Anda.")

    # === TAMBAHAN: Tampilkan Info Login Untuk Simulasi ===
    with st.expander("ℹ️ Akun Simulasi"):
        info_text = ""
        for nim, data in DATA_MAHASISWA.items():
            info_text += f"* **NIM:** `{nim}` | **Password:** `{data['password']}` ({data['nama']})\n"
        st.markdown(info_text)
    # === AKHIR TAMBAHAN ===

    with st.form("login_form"):
        nim = st.text_input("NIM (Contoh: 7123001, 7123002, ...)")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login", type="primary", use_container_width=True)

        if submitted:
            # Cek ke "database"
            if nim in DATA_MAHASISWA and DATA_MAHASISWA[nim]["password"] == password:
                # Jika berhasil, simpan status di session
                st.session_state['logged_in'] = True
                st.session_state['nim'] = nim
                st.session_state['student_data'] = DATA_MAHASISWA[nim]
                st.rerun() # Muat ulang halaman
            else:
                st.error("NIM atau Password salah!")

def run_recommender_app(student_data):
    """
    Menjalankan aplikasi utama setelah login berhasil.
    (VERSI BARU: Grup UI + Minat Terdeteksi pindah ke Filter)
    """
    st.set_page_config(page_title="🎓 Recommender Akademik AI", layout="wide")

    left_space, main_col, right_space = st.columns([1, 2, 1])
    with main_col:
        
        # [LANGKAH 1: KALKULASI DATA DI AWAL]
        
        
        mk_lulus_dict = parse_mk_lulus(student_data["transkrip_text"])
        
        kategori_user_data = {"Wajib": [], "Pilihan Wajib Profesi": [], "Pilihan Bebas Prodi": [], "Pilihan Bebas Non-Prodi": []}
        kategori_user_diambil = {"Wajib": [], "Pilihan Wajib Profesi": [], "Pilihan Bebas Prodi": [], "Pilihan Bebas Non-Prodi": []}
        profesi_count_kalkulasi = {}
        total_sks_lulus_kalkulasi = 0

        target_sks = {"Wajib": 97, "Pilihan Wajib Profesi": 6, "Pilihan Bebas Prodi": 32, "Pilihan Bebas Non-Prodi": 9}
        
        try:
            with open("matakuliah.json", "r", encoding="utf-8") as f:
                katalog_data = json.load(f)
            
            for mk in katalog_data:
                kategori = mk.get("kategori", "Lainnya")
                if kategori not in kategori_user_data:
                    continue 
                
                nama_mk = mk.get("nama", "N/A")
                nama_mk_lower = nama_mk.lower()
                
                nilai_mhs = mk_lulus_dict.get(nama_mk_lower, None)
                
                mk_data_lengkap = {
                    "nama": nama_mk, "kode": mk.get("kode"), "sks": mk.get("sks", 0),
                    "semester": mk.get("semester_umum", 0), "nilai": nilai_mhs,
                    "profesi": mk.get("profesi_relevan", []), "deskripsi": mk.get("deskripsi", "")
                }
                
                kategori_user_data[kategori].append(mk_data_lengkap)
                
                if nilai_mhs is not None:
                    kategori_user_diambil[kategori].append(mk_data_lengkap)
                    total_sks_lulus_kalkulasi += mk.get("sks", 0)
                    profesi_list = mk.get("profesi_relevan", [])
                    if isinstance(profesi_list, list):
                        for prof in profesi_list:
                            profesi_count_kalkulasi[prof] = profesi_count_kalkulasi.get(prof, 0) + 1

        except FileNotFoundError:
            st.error("❌ Gagal menemukan file 'matakuliah.json'. Pastikan file ada di folder yang sama.")
            return
        except Exception as e:
            st.error(f"⚠️ Gagal memuat data kategori dari katalog: {e}")
            return
        
        
        # =======================================================
        # [LANGKAH 2: RENDER UI DENGAN GRUP]
        # =======================================================

        # --- GRUP 1: Header & Profil ---
        st.title("🎓 Penasihat Akademik AI")
        with st.container(border=True):
            col_prof_1, col_prof_2 = st.columns([3, 1])
            with col_prof_1:
                st.header(f"👋 Halo, {student_data['nama']}!")
                st.caption(f"NIM: {st.session_state['nim']}")
                # --- [DIHAPUS] Teks Minat Terdeteksi dihapus dari sini ---
            with col_prof_2:
                st.empty() 
                st.empty()
                if st.button("Logout", use_container_width=True, type="secondary"):
                    st.session_state['logged_in'] = False
                    st.session_state['nim'] = None
                    st.session_state['student_data'] = None
                    st.rerun()
        
        st.empty() # Kasih spasi antar grup

        # --- GRUP 2: Dashboard Akademik ---
        with st.container(border=True):
            st.header("📚 Mata Kuliah Berdasarkan Kategori")
            st.caption(f"Total SKS Lulus Terhitung: **{total_sks_lulus_kalkulasi} SKS**")

            category_names = list(kategori_user_data.keys())
            tab_objects = st.tabs(category_names)
            
            for tab, (kategori, daftar_mk_lengkap) in zip(tab_objects, kategori_user_data.items()):
                
                with tab:
                    daftar_mk_diambil = kategori_user_diambil[kategori]
                    total_sks_diambil = sum(mk["sks"] for mk in daftar_mk_diambil) 
                    target = target_sks.get(kategori, total_sks_diambil or 1)
                    persentase = min(total_sks_diambil / target, 1.0) if target else 1.0
                    total_mk_kategori = len(daftar_mk_lengkap) 
                    
                    cat_title_meta = f"({len(daftar_mk_diambil)}/{total_mk_kategori} MK, {total_sks_diambil}/{target} SKS)"
                    st.markdown(f"<div style='text-align: right; color: #aaa; padding-top: 0px;'>{cat_title_meta}</div>", unsafe_allow_html=True)
                    st.progress(persentase)
                    st.divider()

                    # =======================================================
                    # 1. KATEGORI "WAJIB" (Per Semester)
                    # =======================================================
                    if kategori == "Wajib":
                        semester_groups = {}
                        for mk in daftar_mk_lengkap: 
                            sem = mk.get("semester", 0)
                            if sem not in semester_groups: semester_groups[sem] = []
                            semester_groups[sem].append(mk)
                        
                        for sem in sorted(semester_groups.keys()):
                            if sem == 0 or sem > 8: continue
                            mk_list_per_sem = semester_groups[sem]
                            mk_list_per_sem.sort(key=lambda mk: mk['nilai'] is not None, reverse=True)
                            mk_diambil_sem = [m for m in mk_list_per_sem if m['nilai']]
                            sem_title = f"📚 Semester {sem} ({len(mk_diambil_sem)}/{len(mk_list_per_sem)} MK)"
                            
                            with st.expander(sem_title, expanded=False):
                                for i in range(0, len(mk_list_per_sem), 2):
                                    col1, col2 = st.columns(2)
                                    mk1 = mk_list_per_sem[i]
                                    status_html_1 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk1['nilai']}</b></span>" if mk1['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                    with col1:
                                        st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk1['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk1['sks']} SKS)</span><br> {status_html_1}</div>", unsafe_allow_html=True)
                                    
                                    if (i + 1) < len(mk_list_per_sem):
                                        mk2 = mk_list_per_sem[i+1]
                                        status_html_2 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk2['nilai']}</b></span>" if mk2['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                        with col2:
                                            st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk2['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk2['sks']} SKS)</span><br> {status_html_2}</div>", unsafe_allow_html=True)
                                    else:
                                        with col2: st.empty()

                    # =======================================================
                    # 2. KATEGORI "PILIHAN WAJIB PROFESI" (Per Profesi)
                    # =======================================================
                    elif kategori == "Pilihan Wajib Profesi":
                        SHARED_PROG_CODES = ["TI6113", "TI6123", "TI6133", "TI6143", "TI6153"]
                        profesi_groups = {"PSD": [], "AI": [], "DMS": [], "INFRA": [], "Pemrograman (Pilihan Bersama)": []}
                        for mk in daftar_mk_lengkap:
                            if mk.get("kode") in SHARED_PROG_CODES:
                                profesi_groups["Pemrograman (Pilihan Bersama)"].append(mk)
                            else:
                                for prof in mk.get("profesi", []):
                                    if prof in profesi_groups:
                                        profesi_groups[prof].append(mk)
                        
                        emoji_map = {"AI": "🤖", "PSD": "💻", "INFRA": "🌐", "DMS": "📊", "Pemrograman (Pilihan Bersama)": "📱"}
                        
                        for prof_nama, mk_list_per_prof in profesi_groups.items():
                            if not mk_list_per_prof:
                                if prof_nama == "INFRA":
                                    prof_title = f"{emoji_map[prof_nama]} {prof_nama} (0/0 MK)"
                                    with st.expander(prof_title, expanded=False):
                                        st.info(f"Tidak ada mata kuliah khusus untuk spesialisasi {prof_nama}.")
                                continue 
                            
                            mk_list_per_prof.sort(key=lambda mk: mk['nilai'] is not None, reverse=True)
                            mk_diambil_prof = [m for m in mk_list_per_prof if m['nilai']]
                            emoji = emoji_map.get(prof_nama, "💼")
                            
                            prof_title = f"{emoji} {prof_nama} ({len(mk_diambil_prof)}/{len(mk_list_per_prof)} MK)"
                            
                            with st.expander(prof_title, expanded=False):
                                for i in range(0, len(mk_list_per_prof), 2):
                                    col1, col2 = st.columns(2)
                                    mk1 = mk_list_per_prof[i]
                                    status_html_1 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk1['nilai']}</b></span>" if mk1['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                    with col1:
                                        st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk1['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk1['sks']} SKS)</span><br> {status_html_1}</div>", unsafe_allow_html=True)
                                    
                                    if (i + 1) < len(mk_list_per_prof):
                                        mk2 = mk_list_per_prof[i+1]
                                        status_html_2 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk2['nilai']}</b></span>" if mk2['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                        with col2:
                                            st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk2['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk2['sks']} SKS)</span><br> {status_html_2}</div>", unsafe_allow_html=True)
                                    else:
                                        with col2: st.empty()

                    # =======================================================
                    # 3. KATEGORI "PILIHAN BEBAS PRODI" (LOGIKA MBKM + TAG PROFESI)
                    # =======================================================
                    elif kategori == "Pilihan Bebas Prodi":
                        grup_mbkm = []
                        grup_lainnya = []
                        emoji_map = {"MBKM": "🚀", "Lainnya": "📚"}

                        for mk in daftar_mk_lengkap:
                            if "MBKM" in mk.get("deskripsi", "").upper():
                                grup_mbkm.append(mk)
                            else:
                                grup_lainnya.append(mk)

                        if grup_mbkm:
                            grup_mbkm.sort(key=lambda mk: mk['nilai'] is not None, reverse=True)
                            mk_diambil = [m for m in grup_mbkm if m['nilai']]
                            title = f"{emoji_map['MBKM']} MBKM (Merdeka Belajar) ({len(mk_diambil)}/{len(grup_mbkm)} MK)"
                            with st.expander(title, expanded=False):
                                for i in range(0, len(grup_mbkm), 2):
                                    col1, col2 = st.columns(2)
                                    mk1 = grup_mbkm[i]
                                    status_html_1 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk1['nilai']}</b></span>" if mk1['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                    with col1:
                                        st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk1['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk1['sks']} SKS)</span><br> {status_html_1}</div>", unsafe_allow_html=True)
                                    
                                    if (i + 1) < len(grup_mbkm):
                                        mk2 = grup_mbkm[i+1]
                                        status_html_2 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk2['nilai']}</b></span>" if mk2['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                        with col2:
                                            st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk2['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk2['sks']} SKS)</span><br> {status_html_2}</div>", unsafe_allow_html=True)
                                    else:
                                        with col2: st.empty()
                        
                        if grup_lainnya:
                            grup_lainnya.sort(key=lambda mk: mk['nilai'] is not None, reverse=True)
                            mk_diambil = [m for m in grup_lainnya if m['nilai']]
                            title = f"{emoji_map['Lainnya']} Pilihan Bebas Prodi Lainnya ({len(mk_diambil)}/{len(grup_lainnya)} MK)"
                            with st.expander(title, expanded=False):
                                for i in range(0, len(grup_lainnya), 2):
                                    col1, col2 = st.columns(2)
                                    
                                    mk1 = grup_lainnya[i]
                                    status_html_1 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk1['nilai']}</b></span>" if mk1['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                    prof_list_1 = [p for p in mk1.get("profesi", []) if p in ["PSD", "AI", "DMS", "INFRA"]]
                                    profesi_html_1 = ""
                                    if prof_list_1:
                                        prof_tags_1 = ", ".join(prof_list_1)
                                        profesi_html_1 = f"<span style='color:#bbb; font-size: 0.8rem; font-style: italic;'>[Profesi: {prof_tags_1}]</span>"
                                    with col1:
                                        st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 105px; font-size: 0.9rem;'> <b>{mk1['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk1['sks']} SKS)</span><br> {status_html_1}<br>{profesi_html_1}</div>", unsafe_allow_html=True)

                                    if (i + 1) < len(grup_lainnya):
                                        mk2 = grup_lainnya[i+1]
                                        status_html_2 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk2['nilai']}</b></span>" if mk2['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                        prof_list_2 = [p for p in mk2.get("profesi", []) if p in ["PSD", "AI", "DMS", "INFRA"]]
                                        profesi_html_2 = ""
                                        if prof_list_2:
                                            prof_tags_2 = ", ".join(prof_list_2)
                                            profesi_html_2 = f"<span style='color:#bbb; font-size: 0.8rem; font-style: italic;'>[Profesi: {prof_tags_2}]</span>"
                                        with col2:
                                            st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 105px; font-size: 0.9rem;'> <b>{mk2['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk2['sks']} SKS)</span><br> {status_html_2}<br>{profesi_html_2}</div>", unsafe_allow_html=True)
                                    else:
                                        with col2: st.empty()

                    # =======================================================
                    # 4. KATEGORI "PILIHAN BEBAS NON-PRODI" (Tampilkan Semua)
                    # =======================================================
                    elif kategori == "Pilihan Bebas Non-Prodi":
                        if not daftar_mk_lengkap:
                            st.info("Tidak ada mata kuliah di kategori ini.")
                        else:
                            daftar_mk_lengkap.sort(key=lambda mk: mk['nilai'] is not None, reverse=True)
                            
                            for i in range(0, len(daftar_mk_lengkap), 2):
                                col1, col2 = st.columns(2)
                                mk1 = daftar_mk_lengkap[i]
                                status_html_1 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk1['nilai']}</b></span>" if mk1['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                with col1:
                                    st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk1['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk1['sks']} SKS)</span><br> {status_html_1}</div>", unsafe_allow_html=True)
                                
                                if (i + 1) < len(daftar_mk_lengkap):
                                    mk2 = daftar_mk_lengkap[i+1]
                                    status_html_2 = f"<span style='color:#4CAF50;'>Nilai: <b>{mk2['nilai']}</b></span>" if mk2['nilai'] else "<span style='color:#aaa; font-style: italic;'>Belum diambil</span>"
                                    with col2:
                                        st.markdown(f"<div style='background-color:#1e1e1e; padding:12px 15px; margin-bottom:10px; border-radius:10px; border:1px solid #333; min-height: 90px; font-size: 0.9rem;'> <b>{mk2['nama']}</b> <span style='color:#aaa; font-size: 0.85rem;'>({mk2['sks']} SKS)</span><br> {status_html_2}</div>", unsafe_allow_html=True)
                                else:
                                    with col2: st.empty()
        
        st.empty() # Kasih spasi antar grup
        
        # --- GRUP 3: Aksi & Rekomendasi ---
        with st.container(border=True):
            st.header("📊 Dapatkan Rekomendasi")
            
            # --- [PERUBAHAN DI SINI] ---
            # 1. Logika string profesi dipindah ke sini
            if profesi_count_kalkulasi:
                profesi_teratas = max(profesi_count_kalkulasi, key=profesi_count_kalkulasi.get)
                emoji_map = {"AI": "🤖", "PSD": "💻", "INFRA": "🌐", "DMS": "📊", "MKH": "🕊️"}
                if profesi_teratas == "MKH" and len(profesi_count_kalkulasi) > 1:
                    prof_non_mkh = {k: v for k, v in profesi_count_kalkulasi.items() if k != "MKH"}
                    if prof_non_mkh:
                        profesi_teratas = max(prof_non_mkh, key=prof_non_mkh.get)
                emoji_profesi = emoji_map.get(profesi_teratas.upper(), "💡")
                # 2. Wording baru sesuai request
                profesi_teratas_str = f"Berdasarkan Mata kuliah yang sudah ditempuh dan Nilainya, Anda cocoknya di profesi: <b>{profesi_teratas}</b> {emoji_profesi}"
            else:
                profesi_teratas_str = "Berdasarkan Mata kuliah yang sudah ditempuh, minat Anda belum terdeteksi secara spesifik."
            
            # 3. Tampilkan stringnya di grup ini
            st.markdown(profesi_teratas_str, unsafe_allow_html=True)
            st.divider()
            # --- [AKHIR PERUBAHAN] ---

            MINAT_MAPPING = {"AI": "AI", "PSD": "Software Developer", "DMS": "Database", "INFRA": "Network"}
            minat_user = st.multiselect(
                "Pilih Minat/Profesi Anda:",
                options=list(MINAT_MAPPING.keys()), default=["PSD"],
                format_func=lambda k: MINAT_MAPPING[k]
            )
            
            submit_button = st.button("🚀 Berikan Rekomendasi", type="primary", use_container_width=True)
        
        # --- HASIL REKOMENDASI (Di luar grup) ---
        if submit_button:
            if not minat_user:
                st.error("❌ Harap pilih minimal 1 minat.")
            else:
                llm = load_llm()
                retriever = load_retriever()
                if llm is None or retriever is None:
                    st.error("❌ Gagal memuat komponen AI (LLM atau Retriever)...")
                    return

                rag_chain = get_rag_chain(llm, retriever)

                with st.spinner("🤖 AI sedang menganalisis transkrip dan katalog..."):
                    try:
                        input_data = {
                            "minat_user": minat_user,
                            "mk_lulus": mk_lulus_dict,
                            "mk_sedang_ambil": [], 
                            "total_sks_lulus": total_sks_lulus_kalkulasi
                        }
                        response = rag_chain.invoke(input_data)
                        
                        st.empty() 
                        st.header("🎓 Hasil Rekomendasi")
                        if "rekomendasi" not in response or not response["rekomendasi"]:
                            st.warning("AI tidak menemukan rekomendasi yang cocok saat ini.")
                        
                        for i, mk in enumerate(response.get("rekomendasi", [])):
                            title = f"{i+1}. {mk.get('nama_mk', 'N/A')} ({mk.get('sks', '?')} SKS)"
                            with st.expander(title):
                                st.info(f"**Tentang:** {mk.get('tentang_mk', '-')}")
                                st.info(f"**Alasan:** {mk.get('alasan_rekomendasi', '-')}")
                                st.info(f"**Wawasan Nilai:** {mk.get('wawasan_nilai', '-')}")

                        st.markdown("---")
                        st.subheader("📈 Wawasan Performa")
                        st.write(response.get("wawasan_performa", "Tidak ada."))

                        alternatif = response.get("rekomendasi_alternatif")
                        if alternatif:
                            st.subheader("🌱 Rekomendasi Alternatif")
                            st.write(alternatif)
                            
                    except Exception as e:
                        st.error(f"Terjadi error saat menjalankan analisis: {e}")



def main():
    """Fungsi controller utama."""
    # Inisialisasi session state jika belum ada
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['nim'] = None
        st.session_state['student_data'] = None

    # Tampilkan layar login ATAU app utama
    if not st.session_state['logged_in']:
        show_login_screen()
    else:
        # Jika sudah login, jalankan app utama
        run_recommender_app(st.session_state['student_data'])

# --- Entry point untuk menjalankan app ---
if __name__ == "__main__":
    main()
