import json
import os
import shutil
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- 1. Konfigurasi ---
INDEX_FOLDER = "faiss_index_matakuliah"
MODEL_NAME = "BAAI/bge-large-en-v1.5" # Pastikan ini model yg sama dgn di app.py

def load_json_file(filename):
    """Helper untuk load file JSON."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"--- ERROR: File '{filename}' tidak ditemukan! ---")
        return None
    except json.JSONDecodeError:
        print(f"--- ERROR: File '{filename}' bukan JSON yang valid! ---")
        return None

def build_faiss_index():
    """
    Fungsi utama untuk membangun index FAISS
    dengan data korelasi yang sudah disuntik.
    """
    
    # --- 2. Load Kedua Database ---
    print(">>> [INFO] Memuat database...")
    data_matakuliah = load_json_file('matakuliah.json')
    data_korelasi = load_json_file('korelasi_mk.json')

    if data_matakuliah is None or data_korelasi is None:
        print(">>> [GAGAL] Proses dihentikan. Pastikan kedua file JSON ada.")
        return

    # --- 3. Buat Lookup Table untuk Korelasi ---
    # Mengubah list korelasi jadi dictionary biar gampang dicari
    # Hasilnya: {"TI0073": {...}, "TI0113": {...}, ...}
    korelasi_lookup = {item['kode_mk']: item for item in data_korelasi}
    print(">>> [INFO] Database korelasi berhasil dimuat.")

    # --- 4. Proses dan Gabungkan Data ---
    print(">>> [INFO] Memproses dan menggabungkan data...")
    all_documents = []
    
    for mk in data_matakuliah:
        kode_mk = mk.get("kode")
        deskripsi_asli = mk.get("deskripsi", "")
        
        teks_korelasi = "" # Default-nya kosong
        
        # --- 5. INI BAGIAN UTAMA "PENYUNTIKAN" ---
        # Cek apakah MK ini adalah salah satu MK Fondasi
        if kode_mk in korelasi_lookup:
            korelasi_item = korelasi_lookup[kode_mk]
            
            # Cari nama MK terkait berdasarkan kodenya
            nama_topik_terkait = []
            for kode_terkait in korelasi_item.get("topik_terkait", []):
                # Loop di data_matakuliah untuk cari nama
                for mk_ref in data_matakuliah:
                    if mk_ref.get("kode") == kode_terkait:
                        nama_topik_terkait.append(mk_ref.get("nama"))
                        break
            
            # Buat "contekan" yang akan disuntikkan ke AI
            teks_korelasi = (
                f"\n\n--- CATATAN FONDASI (PENTING) --- \n"
                f"Ini adalah mata kuliah fondasi. {korelasi_item.get('notes', '')}\n"
                f"RELEVANSI KUAT KE: {', '.join(nama_topik_terkait)}"
            )
            print(f">>> [INFO] Menyuntikkan korelasi untuk: {kode_mk} ({mk.get('nama')})")

        # Gabungkan deskripsi asli + contekan korelasi
        combined_page_content = (
            f"Nama: {mk.get('nama', '')}\n"
            f"Deskripsi: {deskripsi_asli}"
            f"{teks_korelasi}" # Disuntik di sini
        )
        
        # --- 6. Siapkan Metadata ---
        # Ini penting agar app.py bisa baca prasyarat, sks, dll.
        metadata = {
            "kode": kode_mk,
            "nama": mk.get("nama"),
            "sks": mk.get("sks"),
            "semester_umum": mk.get("semester_umum"),
            "kategori": mk.get("kategori"), # Tambahkan kategori
            "prasyarat_sks_total": mk.get("prasyarat_sks_total"),
            "prasyarat_mk_json": json.dumps(mk.get("prasyarat_mk", [])), # Wajib ada
            "profesi_relevan": mk.get("profesi_relevan", []),
            "deskripsi": deskripsi_asli # Simpan deskripsi asli
        }
        
        # Buat Document object (format standar LangChain)
        all_documents.append(
            Document(page_content=combined_page_content, metadata=metadata)
        )
        
    print(f">>> [INFO] Selesai memproses {len(all_documents)} mata kuliah.")
    
    # --- 7. Load Model Embedding ---
    print(f">>> [INFO] Memuat model embedding: {MODEL_NAME}...")
    try:
        model_kwargs = {'device': 'cpu'}
        encode_kwargs = {'normalize_embeddings': True}
        embedding_model = HuggingFaceEmbeddings(
            model_name=MODEL_NAME,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
    except Exception as e:
        print(f">>> [GAGAL] Gagal memuat model embedding: {e}")
        return

    print(">>> [INFO] Model embedding berhasil dimuat.")
    
    # --- 8. Hapus Index Lama (Jika Ada) ---
    if os.path.exists(INDEX_FOLDER):
        print(f">>> [INFO] Menghapus folder index lama: {INDEX_FOLDER}...")
        shutil.rmtree(INDEX_FOLDER)
        print(">>> [INFO] Folder lama berhasil dihapus.")

    # --- 9. Buat dan Simpan Index FAISS Baru ---
    print(">>> [INFO] Mulai membuat index FAISS... (Ini mungkin butuh waktu)")
    
    # (Text splitting tidak diperlukan karena data kita sudah terstruktur per dokumen)
    vector_store = FAISS.from_documents(
        documents=all_documents,
        embedding=embedding_model
    )
    
    vector_store.save_local(INDEX_FOLDER)
    
    print(f"\n--- [SUKSES] ---")
    print(f"Index FAISS baru dengan 'otak' korelasi berhasil dibuat!")
    print(f"Folder index disimpan di: {INDEX_FOLDER}")
    print("-------------------")


if __name__ == "__main__":
    build_faiss_index()