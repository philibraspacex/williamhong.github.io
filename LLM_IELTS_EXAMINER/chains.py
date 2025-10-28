# chains.py
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from operator import itemgetter
import config # Import konfigurasi (API Key & nama model LLM)
import prompts # Import SEMUA templates dari prompts.py

# --- Inisialisasi LLM ---
try:
    # Menggunakan nama model dari config.py
    llm = ChatGroq(
        model_name=config.LLM_MODEL_NAME,
        temperature=0.1,
        # groq_api_key=config.GROQ_API_KEY # Biasanya otomatis dari env var
    )
    print(f">>> [Chains] LLM Groq ({llm.model_name}) siap.")
except Exception as e:
    raise RuntimeError(f"Gagal inisialisasi LLM: {e}")

# --- Buat PromptTemplate Objects ---
try:
    # Menggunakan templates dari prompts.py
    prompt_evaluasi_task1 = PromptTemplate.from_template(prompts.TEMPLATE_EVALUASI_TASK1)
    prompt_evaluasi_task2 = PromptTemplate.from_template(prompts.TEMPLATE_EVALUASI_TASK2)
    prompt_saran_task1 = PromptTemplate.from_template(prompts.TEMPLATE_SARAN_TASK1)
    prompt_saran_task2 = PromptTemplate.from_template(prompts.TEMPLATE_SARAN_TASK2)
    prompt_proofread = PromptTemplate.from_template(prompts.TEMPLATE_PROOFREAD)
    prompt_rewrite_task1 = PromptTemplate.from_template(prompts.TEMPLATE_REWRITE_TASK1)
    prompt_rewrite_task2 = PromptTemplate.from_template(prompts.TEMPLATE_REWRITE_TASK2)
    prompt_classifier = PromptTemplate.from_template(prompts.TEMPLATE_CLASSIFIER)
    print(">> [Chains] PromptTemplate objects dibuat.")
except Exception as e:
     raise RuntimeError(f"Gagal membuat PromptTemplate: {e}")

# --- Fungsi untuk Membuat Semua Chains ---
# Kita buat fungsi agar retriever bisa di-pass sebagai argumen
def create_all_chains(retriever_t1, retriever_t2):
    """Membuat dan mengembalikan semua chain LangChain."""
    print(">> [Chains] Membuat semua LangChain chains...")
    if not retriever_t1 or not retriever_t2:
        raise ValueError("Retriever T1 dan T2 harus di-pass ke create_all_chains.")

    # Chain T1
    rag_chain_t1 = ( RunnableParallel(context=itemgetter("jawaban") | retriever_t1, soal_prompt=itemgetter("soal"), jawaban_essay=itemgetter("jawaban")) | prompt_evaluasi_task1 | llm | StrOutputParser() )
    chain_saran_t1 = prompt_saran_task1 | llm | StrOutputParser()
    chain_rewrite_t1 = prompt_rewrite_task1 | llm | StrOutputParser()

    # Chain T2
    rag_chain_t2 = ( RunnableParallel(context=itemgetter("jawaban") | retriever_t2, soal_prompt=itemgetter("soal"), jawaban_essay=itemgetter("jawaban")) | prompt_evaluasi_task2 | llm | StrOutputParser() )
    chain_saran_t2 = prompt_saran_task2 | llm | StrOutputParser()
    chain_rewrite_t2 = prompt_rewrite_task2 | llm | StrOutputParser()

    # Chain Umum
    chain_proofread = prompt_proofread | llm | StrOutputParser()
    chain_classifier = prompt_classifier | llm | StrOutputParser()

    print(">> [Chains] Semua chains siap.")

    # Kembalikan dalam bentuk dictionary agar mudah diakses
    return {
        "rag_t1": rag_chain_t1, "saran_t1": chain_saran_t1, "rewrite_t1": chain_rewrite_t1,
        "rag_t2": rag_chain_t2, "saran_t2": chain_saran_t2, "rewrite_t2": chain_rewrite_t2,
        "proofread": chain_proofread, "classifier": chain_classifier,
        "llm": llm # Sertakan juga instance llm jika perlu diakses langsung
    }