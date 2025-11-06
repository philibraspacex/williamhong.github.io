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

# ==========================================================
# DATABASE MAHASISWA (VERSI LENGKAP + IMPROVISASI NILAI)
# ==========================================================
DATA_MAHASISWA = {
    # === 3 MAHASISWA SELESAI SEMESTER 4 (Total 79 SKS) ===
    "7123001": {
        "nama": "William",
        "password": "william123", 
        "total_sks": 79,
        "transkrip_text": (
            # Semester 1 (18 SKS)
            "PAK (Pendidikan Agama Kristen): B+\n"
            "BhsInd (Bahasa Indonesia): A-\n"
            "IMK (Interaksi Manusia & Komputer): B\n"
            "TeKom (Teknologi Komputer): B+\n"
            "PrTeKom (Praktikum Teknologi Komputer): A\n"
            "MaTek (Matematika Teknik): B-\n"
            "LogMat (Logika Matematika): B\n"
            # Semester 2 (20 SKS)
            "PKN (Pendidikan Kewarganegaraan): A\n"
            "AlPro (Algoritma & Pemrograman): B\n"
            "PrAlPro (Praktikum Algoritma & Pemrograman): A-\n"
            "MaDis (Matematika Diskrit): C+\n"
            "ArOrKom (Arsitektur & Organisasi Komputer): B-\n"
            "Stat (Statistika): B\n"
            "JarKom (Jaringan Komputer): B\n"
            "PrJarKom (Praktikum Jaringan Komputer): B+\n"
            # Semester 3 (18 SKS)
            "StrukDat (Struktur Data): B\n"
            "PrStrukDat (Praktikum Struktur Data): B+\n"
            "InLAN (Internet & LAN): B-\n"
            "PrinLAN (Praktikum Internet & LAN): B+\n"
            "SBD (Sistem Basis Data): B+\n"
            "PrSBD (Praktikum Sistem Basis Data): A\n"
            "RO (Riset Operasi): D\n"
            "SO (Sistem Operasi): C+\n"
            # Semester 4 (23 SKS)
            "PP (Pancasila): A\n"
            "AI (Artificial Intelligence / Kecerdasan Buatan): B\n"
            "KaKom (Kalkulus Komputasi / Kalkulus Lanjut): C\n"
            "EtProf (Etika Profesi): B+\n"
            "ProgWeb (Pemrograman Web): B+\n"
            "PrProgWeb (Praktikum Pemrograman Web): A\n"
            "RPL-BO (Rekayasa Perangkat Lunak Berorientasi Objek): B-\n"
            "PrRPL-BO (Praktikum RPL Berorientasi Objek): B\n"
            "Desain Grafis: B" # MK Pilihan Sem 4 (3 SKS)
        )
    },
    "7123002": {
        "nama": "Jonathan",
        "password": "jonathan123", 
        "total_sks": 79,
        "transkrip_text": (
            # Semester 1 (18 SKS)
            "PAK (Pendidikan Agama Kristen): A\n"
            "BhsInd (Bahasa Indonesia): A\n"
            "IMK (Interaksi Manusia & Komputer): A-\n"
            "TeKom (Teknologi Komputer): A\n"
            "PrTeKom (Praktikum Teknologi Komputer): A\n"
            "MaTek (Matematika Teknik): A\n"
            "LogMat (Logika Matematika): A\n"
            # Semester 2 (20 SKS)
            "PKN (Pendidikan Kewarganegaraan): A\n"
            "AlPro (Algoritma & Pemrograman): A\n"
            "PrAlPro (Praktikum Algoritma & Pemrograman): A\n"
            "MaDis (Matematika Diskrit): A-\n"
            "ArOrKom (Arsitektur & Organisasi Komputer): B+\n"
            "Stat (Statistika): A\n"
            "JarKom (Jaringan Komputer): A-\n"
            "PrJarKom (Praktikum Jaringan Komputer): A\n"
            # Semester 3 (18 SKS)
            "StrukDat (Struktur Data): A\n"
            "PrStrukDat (Praktikum Struktur Data): A\n"
            "InLAN (Internet & LAN): B+\n"
            "PrinLAN (Praktikum Internet & LAN): A\n"
            "SBD (Sistem Basis Data): A\n"
            "PrSBD (Praktikum Sistem Basis Data): A\n"
            "RO (Riset Operasi): B+\n"
            "SO (Sistem Operasi): B+\n"
            # Semester 4 (23 SKS)
            "PP (Pancasila): A\n"
            "AI (Artificial Intelligence / Kecerdasan Buatan): A\n"
            "KaKom (Kalkulus Komputasi / Kalkulus Lanjut): A-\n"
            "EtProf (Etika Profesi): A\n"
            "ProgWeb (Pemrograman Web): A\n"
            "PrProgWeb (Praktikum Pemrograman Web): A\n"
            "RPL-BO (Rekayasa Perangkat Lunak Berorientasi Objek): A-\n"
            "PrRPL-BO (Praktikum RPL Berorientasi Objek): A\n"
            "Machine Learning: A-" # MK Pilihan Sem 4 (3 SKS)
        )
    },
    "7123003": {
        "nama": "steven",
        "password": "steven123", 
        "total_sks": 79,
        "transkrip_text": (
            # Semester 1 (18 SKS)
            "PAK (Pendidikan Agama Kristen): B\n"
            "BhsInd (Bahasa Indonesia): B+\n"
            "IMK (Interaksi Manusia & Komputer): B-\n"
            "TeKom (Teknologi Komputer): B\n"
            "PrTeKom (Praktikum Teknologi Komputer): B+\n"
            "MaTek (Matematika Teknik): C\n"
            "LogMat (Logika Matematika): B-\n"
            # Semester 2 (20 SKS)
            "PKN (Pendidikan Kewarganegaraan): B+\n"
            "AlPro (Algoritma & Pemrograman): C+\n"
            "PrAlPro (Praktikum Algoritma & Pemrograman): B\n"
            "MaDis (Matematika Diskrit): C\n"
            "ArOrKom (Arsitektur & Organisasi Komputer): C+\n"
            "Stat (Statistika): B-\n"
            "JarKom (Jaringan Komputer): C+\n"
            "PrJarKom (Praktikum Jaringan Komputer): B-\n"
            # Semester 3 (18 SKS)
            "StrukDat (Struktur Data): C+\n"
            "PrStrukDat (Praktikum Struktur Data): B\n"
            "InLAN (Internet & LAN): C\n"
            "PrinLAN (Praktikum Internet & LAN): C+\n"
            "SBD (Sistem Basis Data): C+\n"
            "PrSBD (Praktikum Sistem Basis Data): B+\n"
            "RO (Riset Operasi): C-\n"
            "SO (Sistem Operasi): C\n"
            # Semester 4 (23 SKS)
            "PP (Pancasila): A-\n"
            "AI (Artificial Intelligence / Kecerdasan Buatan): C+\n"
            "KaKom (Kalkulus Komputasi / Kalkulus Lanjut): C\n"
            "EtProf (Etika Profesi): B\n"
            "ProgWeb (Pemrograman Web): B-\n"
            "PrProgWeb (Praktikum Pemrograman Web): B\n"
            "RPL-BO (Rekayasa Perangkat Lunak Berorientasi Objek): C+\n"
            "PrRPL-BO (Praktikum RPL Berorientasi Objek): B-\n"
            "Manajemen Basis Data: B-" # MK Pilihan Sem 4 (3 SKS)
        )
    },

    # === 2 MAHASISWA SELESAI SEMESTER 5 (Total 100 SKS) ===
    "7122001": {
        "nama": "bio",
        "password": "bio123", 
        "total_sks": 100,
        "transkrip_text": (
            # Semester 1 (18 SKS)
            "PAK (Pendidikan Agama Kristen): A\n"
            "BhsInd (Bahasa Indonesia): A-\n"
            "IMK (Interaksi Manusia & Komputer): A-\n"
            "TeKom (Teknologi Komputer): B+\n"
            "PrTeKom (Praktikum Teknologi Komputer): A\n"
            "MaTek (Matematika Teknik): B+\n"
            "LogMat (Logika Matematika): A\n"
            # Semester 2 (20 SKS)
            "PKN (Pendidikan Kewarganegaraan): A\n"
            "AlPro (Algoritma & Pemrograman): A\n"
            "PrAlPro (Praktikum Algoritma & Pemrograman): A\n"
            "MaDis (Matematika Diskrit): B+\n"
            "ArOrKom (Arsitektur & Organisasi Komputer): B+\n"
            "Stat (Statistika): A-\n"
            "JarKom (Jaringan Komputer): B+\n"
            "PrJarKom (Praktikum Jaringan Komputer): A\n"
            # Semester 3 (18 SKS)
            "StrukDat (Struktur Data): A\n"
            "PrStrukDat (Praktikum Struktur Data): A\n"
            "InLAN (Internet & LAN): B+\n"
            "PrinLAN (Praktikum Internet & LAN): A\n"
            "SBD (Sistem Basis Data): A\n"
            "PrSBD (Praktikum Sistem Basis Data): A\n"
            "RO (Riset Operasi): B\n"
            "SO (Sistem Operasi): A-\n"
            # Semester 4 (23 SKS)
            "PP (Pancasila): A\n"
            "AI (Artificial Intelligence / Kecerdasan Buatan): A\n"
            "KaKom (Kalkulus Komputasi / Kalkulus Lanjut): B+\n"
            "EtProf (Etika Profesi): A\n"
            "ProgWeb (Pemrograman Web): A-\n"
            "PrProgWeb (Praktikum Pemrograman Web): A\n"
            "RPL-BO (Rekayasa Perangkat Lunak Berorientasi Objek): B+\n"
            "PrRPL-BO (Praktikum RPL Berorientasi Objek): A\n"
            "Machine Learning: A" # MK Pilihan Sem 4 (3 SKS)
            # --- Semester 5 (21 SKS) ---
            "ManPro (Manajemen Proyek): B+\n" # Wajib Sem 5
            "Data Mining: A\n" # Pilihan
            "Data Warehouse: B+\n" # Pilihan
            "Natural Language Processing: A-\n" # Pilihan
            "Jaringan Syaraf Tiruan: B+\n" # Pilihan
            "Computer Vision: A-\n" # Pilihan
            "Sistem Temu Balik Informasi: B" # Pilihan
        )
    },
    "7122002": {
        "nama": "antony",
        "password": "antony123", 
        "total_sks": 100,
        "transkrip_text": (
            # Semester 1 (18 SKS)
            "PAK (Pendidikan Agama Kristen): B+\n"
            "BhsInd (Bahasa Indonesia): A-\n"
            "IMK (Interaksi Manusia & Komputer): B\n"
            "TeKom (Teknologi Komputer): B\n"
            "PrTeKom (Praktikum Teknologi Komputer): B+\n"
            "MaTek (Matematika Teknik): C+\n"
            "LogMat (Logika Matematika): B+\n"
            # Semester 2 (20 SKS)
            "PKN (Pendidikan Kewarganegaraan): A\n"
            "AlPro (Algoritma & Pemrograman): B+\n"
            "PrAlPro (Praktikum Algoritma & Pemrograman): A\n"
            "MaDis (Matematika Diskrit): B\n"
            "ArOrKom (Arsitektur & Organisasi Komputer): C+\n"
            "Stat (Statistika): B-\n"
            "JarKom (Jaringan Komputer): B-\n"
            "PrJarKom (Praktikum Jaringan Komputer): B\n"
            # Semester 3 (18 SKS)
            "StrukDat (Struktur Data): B\n"
            "PrStrukDat (Praktikum Struktur Data): A-\n"
            "InLAN (Internet & LAN): B-\n"
            "PrinLAN (Praktikum Internet & LAN): B\n"
            "SBD (Sistem Basis Data): B+\n"
            "PrSBD (Praktikum Sistem Basis Data): A\n"
            "RO (Riset Operasi): C+\n"
            "SO (Sistem Operasi): B-\n"
            # Semester 4 (23 SKS)
            "PP (Pancasila): A\n"
            "AI (Artificial Intelligence / Kecerdasan Buatan): C+\n"
            "KaKom (Kalkulus Komputasi / Kalkulus Lanjut): C\n"
            "EtProf (Etika Profesi): B+\n"
            "ProgWeb (Pemrograman Web): A-\n"
            "PrProgWeb (Praktikum Pemrograman Web): A\n"
            "RPL-BO (Rekayasa Perangkat Lunak Berorientasi Objek): B\n"
            "PrRPL-BO (Praktikum RPL Berorientasi Objek): B+\n"
            "Pengujian Perangkat Lunak: B" # MK Pilihan Sem 4 (3 SKS)
            # --- Semester 5 (21 SKS) ---
            "ManPro (Manajemen Proyek): A-\n" # Wajib Sem 5
            "Pemrograman Perangkat Bergerak: B+\n" # Pilihan
            "Pemrograman Web Lanjut: A-\n" # Pilihan
            "Arsitektur Perangkat Lunak: B\n" # Pilihan
            "Keamanan Perangkat Lunak: B-\n" # Pilihan
            "Cloud Computing: B+\n" # Pilihan
            "DevOps: B" # Pilihan
        )
    }
}
# ==========================================================
# AKHIR DARI DATABASE
# ==========================================================


def parse_mk_lulus(text_input):
    """Mengubah text area input 'MK: Nilai' jadi dictionary."""
    mk_dict = {}
    for line in text_input.split('\n'):
        if ':' in line:
            parts = line.split(':', 1)
            mk_name = parts[0].strip()
            # Ambil nilai, bersihkan, dan pastikan uppercase
            nilai = parts[1].strip().upper().split()[0] # Ambil kata pertama (misal 'A' dari 'A (Lulus)')
            if mk_name and nilai:
                mk_dict[mk_name] = nilai
    return mk_dict

# --- [TAMBAHKAN FUNGSI INI] ---
def parse_mk_sedang_ambil(text_input):
    """Mengubah text area input 'MK Sedang Diambil' jadi list."""
    mk_list = [line.strip() for line in text_input.split('\n') if line.strip()]
    return mk_list
# ==========================================================
# BAGIAN CACHING: LOAD MODEL & DATABASE (BIAR NGGAK LEMOT)
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
    
    # [IMPROVISASI] Ganti hardcoded path ke relative path
    # Pastikan folder 'faiss_index_matakuliah' ada di folder yg sama dgn app.py
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

# --- [GANTI TOTAL BLOK INI DENGAN KODE DI BAWAH] ---
# Ini adalah prompt_text FINAL, semua kata 'kode_mk', 'nilai_min', dll. 
# yang bikin error udah diganti jadi bahasa Indonesia.

prompt_text = """<|system|>
Anda adalah Penasihat Akademik AI yang sangat teliti untuk Program Studi Informatika UKDW.
Misi Anda adalah memberikan rekomendasi mata kuliah yang personal, akurat, dan patuh pada aturan prasyarat.

ATURAN PERBANDINGAN NILAI (PENTING!):
Gunakan hirarki nilai ini: A > A- > B+ > B > B- > C+ > C > D > E.
- Jika nilai minimum adalah 'D', maka 'C', 'B', 'A' juga Lulus.
- Jika nilai minimum adalah 'C', maka 'D', 'E' TIDAK Lulus.
- Jika nilai minimum adalah 'E', maka 'E', 'D', 'C', 'B', 'A' Lulus.

DATA YANG ANDA MILIKI (KATALOG MATA KULIAH LENGKAP):
Anda memiliki akses ke seluruh katalog mata kuliah. Formatnya:
Kode: [Kode MK] Nama: [Nama Mata Kuliah] SKS: [Jumlah SKS] Prasyarat SKS Total: [Jumlah SKS Lulus Minimal] Prasyarat MK (JSON): [Ini adalah string JSON dari list prasyarat] Profesi Relevan: [List Profesi] Deskripsi: [Deskripsi MK]


ATURAN WAJIB YANG HARUS DIIKUTI (VERSI BARU):

1.  Sumber Data: Gunakan HANYA informasi dari KATALOG (CONTEXT).
2.  Filter Prasyarat: Sebuah mata kuliah (MK Rekomendasi) HANYA BOLEH direkomendasikan jika SEMUA kondisi berikut terpenuhi:
    a. MK Rekomendasi belum ada di `mk_lulus`.
    b. `total_sks_lulus` mahasiswa >= `prasyarat_sks_total` MK Rekomendasi.
    c. Untuk SETIAP prasyarat di `Prasyarat MK (JSON)`:
        i.   (Anda harus mem-parsing string JSON ini di pikiran Anda). Ambil info: kode MK prasyarat, nilai minimum yang dibutuhkan, dan apakah boleh diambil bersamaan.
        ii.  Cek `mk_lulus`: Apakah kode MK prasyarat ada di `mk_lulus` DAN nilainya >= nilai minimum yang dibutuhkan (sesuai ATURAN PERBANDINGAN NILAI)?
        iii. Cek `mk_sedang_ambil`: Jika info 'boleh diambil bersamaan' adalah `true`, cek apakah kode MK prasyarat ada di `mk_sedang_ambil`.
        iv.  Kondisi prasyarat terpenuhi jika (ii) ATAU (iii) bernilai benar.
        v.   Jika `Prasyarat MK (JSON)` kosong (`[]`), prasyarat ini otomatis terpenuhi.
3.  Jumlah Rekomendasi: Berikan hingga 10 mata kuliah rekomendasi yang paling relevan.
4.  Filter Relevansi: Prioritaskan MK yang cocok dengan `minat_user`.
5.  Aturan Khusus MBKM: Mata kuliah dengan catatan "[CATATAN: ... MBKM ...]" di deskripsinya JANGAN direkomendasikan kecuali user secara spesifik memintanya.
6.  Format Output: Anda WAJIB menghasilkan output dalam format JSON yang valid. TIDAK BOLEH ada teks lain sebelum atau sesudah blok JSON.

INPUT DATA MAHASISWA:
minat_user: List profesi (e.g., ["AI", "PSD"]).
mk_lulus: Dictionary. Key: Nama/Kode MK. Value: Nilai huruf.
mk_sedang_ambil: List. Key: Nama/Kode MK. (e.g., ["Sistem Basis Data"])
total_sks_lulus: Integer.

FORMAT JSON OUTPUT YANG WAJIB DIIKUTI:
Anda harus membuat JSON dengan struktur berikut:
- "rekomendasi": (Sebuah list)
  - Setiap item di list adalah obyek dengan key: "nama_mk", "sks", "tentang_mk", "alasan_rekomendasi", "wawasan_nilai".
- "wawasan_performa": (Sebuah string)
- "rekomendasi_alternatif": (Sebuah string, atau string kosong)

Pastikan output Anda adalah JSON valid.
<|end_system|> <|user|> Berikan rekomendasi mata kuliah.
Minat User (List Profesi): {minat_user}
Mata Kuliah Lulus & Nilai: {mk_lulus}
Mata Kuliah Sedang Diambil: {mk_sedang_ambil}
Total SKS Lulus: {total_sks_lulus}
CONTEXT (Katalog Mata Kuliah Lengkap):
{context}
<|end_user|> <|assistant|>
"""

prompt_template = PromptTemplate(
    template=prompt_text,
    input_variables=["minat_user", "mk_lulus", "mk_sedang_ambil", "total_sks_lulus", "context"]
)

# --- [AKHIR DARI BLOK PENGGANTI] ---


# --- Fungsi Bantuan RAG (Copy-paste dari kode lu) ---
def format_docs(docs):
    """Menggabungkan page_content dan metadata dari list Dokumen jadi satu string."""
    formatted_context = "\n\n---\n\n".join([
        f"Kode: {doc.metadata.get('kode', 'N/A')}\n"
        f"Nama: {doc.metadata.get('nama', 'N/A')}\n"
        f"SKS: {doc.metadata.get('sks', 0)}\n"
        f"Semester Umum: {doc.metadata.get('semester_umum', 'N/A')}\n"
        f"Prasyarat SKS Total: {doc.metadata.get('prasyarat_sks_total', 0)}\n"
        # [UPGRADE] Baca 'prasyarat_mk_json' dari metadata
        f"Prasyarat MK (JSON): {doc.metadata.get('prasyarat_mk_json', '[]')}\n"
        f"Profesi Relevan: {doc.metadata.get('profesi_relevan', 'N/A')}\n"
        f"Deskripsi: {doc.page_content.split('Deskripsi: ')[1] if 'Deskripsi: ' in doc.page_content else doc.page_content}"
        for doc in docs
    ])
    return formatted_context

def get_query_as_string(input_dict):
    """Mengubah list minat (misal: ["AI", "PSD"]) jadi string (misal: "AI PSD") untuk retriever."""
    minat_list = input_dict.get("minat_user", [])
    return " ".join(minat_list)

# --- Gabungkan jadi RAG Chain ---
@st.cache_resource
def get_rag_chain(_llm, _retriever):
    """Buat dan cache RAG chain (dengan output JSON)."""
    print(">>> Membuat RAG chain (JSON Output)...")
    
    setup_and_retrieval = RunnableParallel(
        {
            "context": RunnableLambda(get_query_as_string) | _retriever | RunnableLambda(format_docs),
            "minat_user": RunnableLambda(lambda x: str(x["minat_user"])), 
            "mk_lulus": RunnableLambda(lambda x: x["mk_lulus"]),
            # [UPGRADE] Tambahkan input baru
            "mk_sedang_ambil": RunnableLambda(lambda x: x["mk_sedang_ambil"]), 
            "total_sks_lulus": RunnableLambda(lambda x: x["total_sks_lulus"])
        }
    )

    rag_chain = (
        setup_and_retrieval
        | prompt_template
        | _llm
        | JsonOutputParser() 
    )
    print("✅ RAG Chain (JSON) siap.")
    return rag_chain

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

# --- [GANTI INI] Versi UI dengan Output Dropdown ---
# --- [GANTI INI] Versi UI (Dropdown Ditutup + FIX TYPO) ---
# --- [GANTI TOTAL FUNGSI INI] ---
def run_recommender_app(student_data):
    """
    Menjalankan aplikasi utama setelah login berhasil.
    (VERSI BARU DENGAN LOGIKA PRASYARAT LENGKAP)
    """
    st.set_page_config(page_title="🎓 Recommender Akademik AI", layout="wide")

    # --- BUAT CONTAINER PALSU DI TENGAH ---
    left_space, main_col, right_space = st.columns([1, 2, 1]) 
    
    with main_col:
        
        # === BAGIAN HEADER & LOGOUT ===
        col1_head, col2_head = st.columns([2, 1])
        with col1_head:
            st.title(f"🎓 Penasihat Akademik AI")
            st.header(f"👋 Halo, {student_data['nama']}!")
            st.caption(f"NIM: {st.session_state['nim']}")
        with col2_head:
            st.empty(); st.empty() 
            if st.button("Logout", use_container_width=True, type="secondary"):
                st.session_state['logged_in'] = False
                st.session_state['nim'] = None
                st.session_state['student_data'] = None
                st.rerun()
        st.markdown("---")

        # === BAGIAN FILTER REKOMENDASI ===
        st.header("📊 Filter Rekomendasi")
        MINAT_MAPPING = {
            "AI": "AI (Artificial Intelligence)",
            "PSD": "PSD (Professional Software Developer)",
            "DMS": "DMS (Database Management System)",
            "INFRA": "INFRA (Network and Infrastructure)"
            # Hapus profesi yang tidak relevan dari list lama
        }
        list_minat_profesi_options = list(MINAT_MAPPING.keys())
        minat_user = st.multiselect(
            "Pilih Minat/Profesi Anda (Bisa > 1):",
            options=list_minat_profesi_options,
            default=["AI", "PSD"],
            format_func=lambda key: MINAT_MAPPING[key]
        )

        # === BAGIAN DATA TRANSKRIP ===
        st.header("🔒 Data Transkrip Anda")
        total_sks_lulus = st.number_input(
            "Total SKS Lulus Anda:",
            value=student_data["total_sks"],
            disabled=True
        )
        
        mk_lulus_text = st.text_area(
            "Mata Kuliah Lulus & Nilai:",
            value=student_data["transkrip_text"],
            height=300,
            disabled=True
        )

        # === [INPUT BARU] UNTUK PRASYARAT "SEDANG AMBIL" ===
        st.markdown("---")
        st.header("📝 Mata Kuliah Sedang Diambil")
        mk_sedang_ambil_text = st.text_area(
            "Masukkan MK yang sedang Anda ambil semester ini (satu per baris):",
            placeholder="Contoh:\nSistem Basis Data\nStruktur Data",
            height=100
        )
        # === AKHIR INPUT BARU ===

        st.markdown("---")
        submit_button = st.button("🚀 Berikan Rekomendasi", type="primary", use_container_width=True)

        # === AREA OUTPUT UTAMA (VERSI DROPDOWN) ===
        if submit_button:
            
            # --- Validasi Input (Sama) ---
            if not minat_user:
                st.error("❌ Harap pilih minimal 1 minat.")
                return
            
            # --- [UPGRADE] Parsing input baru ---
            mk_lulus_dict = parse_mk_lulus(mk_lulus_text)
            mk_sedang_ambil_list = parse_mk_sedang_ambil(mk_sedang_ambil_text)
            
            if not mk_lulus_dict:
                st.error("❌ Harap isi mata kuliah yang sudah lulus...")
                return

            # --- Load Model & Chain (Sama) ---
            llm = load_llm()
            retriever = load_retriever() 
            if llm is None or retriever is None:
                st.error("❌ Gagal memuat komponen AI (LLM atau Retriever)...")
                return
            rag_chain = get_rag_chain(llm, retriever) 

            # --- Panggil RAG Chain & Tampilkan Hasil (Berbeda) ---
            with st.spinner("🤖 AI sedang menganalisis transkrip dan katalog... Mohon tunggu..."):
                try:
                    # [UPGRADE] Tambahkan mk_sedang_ambil_list ke input
                    input_data = {
                        "minat_user": minat_user,
                        "mk_lulus": mk_lulus_dict,
                        "mk_sedang_ambil": mk_sedang_ambil_list,
                        "total_sks_lulus": total_sks_lulus
                    }
                    response = rag_chain.invoke(input_data)
                    
                    # --- Render Hasil JSON jadi Dropdown ---
                    st.header("🎓 Rekomendasi Mata Kuliah Semester Depan")
                    st.write(f"Berdasarkan minat pada {minat_user}, {total_sks_lulus} SKS yang telah lulus, dan riwayat nilai Anda, berikut adalah beberapa mata kuliah yang relevan:")
                    
                    for i, mk in enumerate(response.get("rekomendasi", [])):
                        title = f"{i+1}. {mk.get('nama_mk', 'N/A')} ({mk.get('sks', '?')} SKS)"
                        
                        with st.expander(title): 
                            st.markdown(f"**Tentang Mata Kuliah Ini:**")
                            st.info(f"{mk.get('tentang_mk', '-')}") 

                            st.markdown(f"**Kenapa Direkomendasikan:**")
                            st.info(f"{mk.get('alasan_rekomendasi', '-')}") 
                            
                            st.markdown(f"**Wawasan Nilai:**")
                            st.info(f"{mk.get('wawasan_nilai', '-')}")
                    
                    st.markdown("---") 

                    # Tampilkan Wawasan Performa
                    st.header("📈 Wawasan Performa & Saran Profesi")
                    st.write(response.get("wawasan_performa", "Tidak ada wawasan performa."))
                    
                    # Tampilkan Rekomendasi Alternatif (jika ada)
                    alternatif = response.get("rekomendasi_alternatif")
                    if alternatif and alternatif.strip() != "": 
                        st.header("🌱 Rekomendasi Alternatif")
                        st.write(alternatif)

                    st.markdown("---")
                    st.info("**Penting:** Rekomendasi ini adalah panduan. Selalu diskusikan dengan Dosen Wali.")
                    
                except Exception as e:
                    st.error(f"Terjadi error saat menjalankan RAG chain atau mem-parsing JSON: {e}")
                    st.exception(e) # Tampilkan traceback error
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