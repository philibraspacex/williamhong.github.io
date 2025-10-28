# rag_setup.py
import os
import torch 
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import config # Import konfigurasi (path, model ID, K)


def load_rag_components():
    """Memuat embedding model dan kedua retriever."""

    # --- Load Embedding Model ---
    print(f"\n>>> [RAG Setup] Memuat Embedding Model: {config.EMBEDDING_MODEL_ID}...")
    try:
        # Cek GPU
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"    Menggunakan device: {device}")

        embeddings = HuggingFaceEmbeddings(
            model_name=config.EMBEDDING_MODEL_ID,
            model_kwargs={'device': device} 
        )
        print(">>> [RAG Setup] Embedding Model dimuat.")
    except Exception as e:
        raise RuntimeError(f"Gagal memuat embedding model '{config.EMBEDDING_MODEL_ID}': {e}. Pastikan sentence-transformers terinstall.")

    # --- Load Vector Stores & Buat Retrievers ---
    retriever_t1, retriever_t2 = None, None
    print("\n>>> [RAG Setup] Memuat Vector Store LOKAL & Membuat Retriever...")

    # Load Task 1
    try:
        print(f">> Task 1 from: '{config.INDEX_PATH_T1}'...")
        if not os.path.exists(config.INDEX_PATH_T1):
            raise FileNotFoundError(f"Folder Index Task 1 tidak ditemukan: {config.INDEX_PATH_T1}. Pastikan folder ada di /data.")
        vectorstore_t1 = FAISS.load_local(
            config.INDEX_PATH_T1,
            embeddings,
            allow_dangerous_deserialization=True
        )
        # --- Retriever Logic (pilih salah satu) ---
        # 1. Retriever Biasa:
        retriever_t1 = vectorstore_t1.as_retriever(
            search_kwargs={"k": config.RETRIEVER_K}
        )
        # ------------------------------------
        print(">> [RAG Setup] Retriever Task 1 dibuat!")
    except Exception as e:
        print(f"!!! [ERROR] Gagal Task 1: {e}.")
        if 'faiss' in str(e).lower(): print("    Pastikan library 'faiss-cpu' (atau 'faiss-gpu') sudah terinstall.")

    # Load Task 2
    try:
        print(f">> Task 2 from: '{config.INDEX_PATH_T2}'...")
        if not os.path.exists(config.INDEX_PATH_T2):
            raise FileNotFoundError(f"Folder Index Task 2 tidak ditemukan: {config.INDEX_PATH_T2}. Pastikan folder ada di /data.")
        vectorstore_t2 = FAISS.load_local(
            config.INDEX_PATH_T2,
            embeddings,
            allow_dangerous_deserialization=True
        )
        # --- Retriever Logic (pilih salah satu, sama seperti T1) ---
        # 1. Retriever Biasa:
        retriever_t2 = vectorstore_t2.as_retriever(
            search_kwargs={"k": config.RETRIEVER_K}
        )
 
        # ------------------------------------
        print(">> [RAG Setup] Retriever Task 2 dibuat!")
    except Exception as e:
        print(f"!!! [ERROR] Gagal Task 2: {e}.")
        if 'faiss' in str(e).lower(): print("    Pastikan library 'faiss-cpu' (atau 'faiss-gpu') sudah terinstall.")

    # Validasi akhir
    if not retriever_t1 or not retriever_t2:
        raise RuntimeError("Gagal membuat salah satu atau kedua Retriever. Periksa path dan instalasi library.")

    print("\n>>> [RAG Setup] Komponen RAG (Embeddings, Vector Stores LOKAL, Retrievers) siap.")
    # Kembalikan hanya retriever, embeddings tidak perlu di luar file ini
    return retriever_t1, retriever_t2
