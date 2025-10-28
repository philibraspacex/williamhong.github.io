# config.py
import os
from dotenv import load_dotenv

# Load variabel dari file .env di folder yang sama
load_dotenv()

# --- API Keys & Model IDs ---
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
# Pilih salah satu model LLM (rekomendasi: llama atau mixtral)
LLM_MODEL_NAME = "llama-3.3-70b-versatile"
# LLM_MODEL_NAME = "mixtral-8x7b-32768"
# LLM_MODEL_NAME = "openai/llama-3-70b" # Kurang stabil

EMBEDDING_MODEL_ID = "BAAI/bge-large-en-v1.5" # Model embedding RAG
# RERANKER_MODEL_ID = "BAAI/bge-reranker-large" # Jika nanti pakai re-ranking

# Validasi API Key saat import
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file or environment variables.")
else:
    # Set ke os.environ jika belum (kadang diperlukan library lain)
    os.environ["GROQ_API_KEY"] = GROQ_API_KEY
    print(">>> [Config] GROQ_API_KEY dimuat.")

# --- Paths RAG ---
# Menggunakan path relatif dari file config.py ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data") # Asumsi folder 'data' sejajar config.py
INDEX_PATH_T1 = os.path.join(DATA_DIR, "writingtask1ragdataset/faiss_index") # Path ke folder index T1
INDEX_PATH_T2 = os.path.join(DATA_DIR, "writingtask2ragdataset/faiss_index") # Path ke folder index T2

# --- Parameter RAG ---
RETRIEVER_K = 5 # Jumlah dokumen yang diambil retriever awal
RERANKER_TOP_N = 3 # Jumlah dokumen setelah re-ranking (jika dipakai)

# --- Lain-lain ---
# Nonaktifkan parallelism tokenizer (opsional)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

print(">>> [Config] Konfigurasi aplikasi dimuat.")
print(f"    LLM Model: {LLM_MODEL_NAME}")
print(f"    Embedding Model: {EMBEDDING_MODEL_ID}")
print(f"    Index T1 Path: {INDEX_PATH_T1}")
print(f"    Index T2 Path: {INDEX_PATH_T2}")
