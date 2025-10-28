import streamlit as st
import config 
from rag_setup import load_rag_components
from chains import create_all_chains
import traceback 
import re
import json
from utils import hitung_skor_keseluruhan # Ini tetap dipakai

# --- 1. Konfigurasi Halaman & Sidebar ---
st.set_page_config(
    layout="wide", 
    page_title="AI IELTS Coach",
    page_icon="🤖"
)

# --- Sidebar (Info Aplikasi) ---
with st.sidebar:
    st.title("Tentang Aplikasi")
    st.info(
        f"""
        **AI IELTS Writing Coach** ini dirancang untuk menganalisis esai Task 1 & 2 Anda menggunakan RAG dan model AI canggih.

        **Fitur Utama:**
        - Evaluasi 4 kriteria IELTS.
        - Feedback & Saran perbaikan.
        - Koreksi tata bahasa (Proofread).
        - Revisi otomatis ke target band.

        **Model LLM:** `{config.LLM_MODEL_NAME}`
        """
    )
    st.warning("Skor dari AI adalah estimasi dan BUKAN pengganti examiner resmi.")
    st.caption("Dibuat dengan LangChain, Groq, & Streamlit.")

# --- 2. Judul & Setup Aplikasi ---
st.title("🤖 AI IELTS Writing Coach") # Judul lebih general
st.caption(f"Analisis Mendalam Esai Task 1 & 2 (Powered by RAG & Groq ({config.LLM_MODEL_NAME}))")

@st.cache_resource
def setup_application():
    """Load RAG components and create chains."""
    print("--- Memulai Setup Aplikasi (hanya sekali) ---")
    try:
        retriever_t1, retriever_t2 = load_rag_components()
        all_chains = create_all_chains(retriever_t1, retriever_t2)
        print("--- Setup Aplikasi Selesai ---")
        return all_chains
    except Exception as e:
        print(f"!!! FATAL ERROR saat setup: {e}")
        st.error(f"Gagal melakukan setup awal: {e}. Cek terminal/log untuk detail.")
        print(traceback.format_exc())
        return None

all_chains = setup_application()

# --- 3. Inisialisasi Session State (Lengkap) ---
default_states = {
    'raw_evaluasi_json_str': None,  # String JSON mentah dari chain evaluasi
    'parsed_evaluasi_dict': None,   # Hasil parse JSON (dictionary)
    'saran_perbaikan': None,        # String saran dari chain saran
    'saran_proofread': None,        # String markdown dari chain proofread
    'hasil_rewrite': None,          # String esai hasil revisi
    'task_type': None,              # 'task_1' atau 'task_2'
    'word_count': 0,                # Jumlah kata esai
    'evaluasi_valid': False,        # Status apakah JSON valid
    'skor_keseluruhan_float': 0.0,  # Skor float (misal: 6.5)
    'skor_keseluruhan_display': "N/A", # Skor string (misal: "6.5")
    'target_band_selector': None,   # Untuk menyimpan pilihan user di fitur revisi
    'processing_stage': None,       # Untuk progress bar
    'processing_status': "Idle",
    'last_soal_ielts': '',      # Untuk mengingat input soal
    'last_esai_kandidat': ''    # Untuk mengingat input esai
}
for key, value in default_states.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- HELPER FUNCTIONS for UI (VERSI SIMPLE) ---

def display_band_detail_simple(kriteria_key, band_score, comments):
    """
    Menampilkan detail Band per kriteria (VERSI SIMPLE).
    Hanya menampilkan komentar, karena AI hanya menghasilkan itu.
    """
    emoji_map = {"Task": "🎯", "Coherence": "🔗", "Lexical": "📚", "Grammatical": "🖋️"}
    emoji = "📊"
    for k_emoji, v_emoji in emoji_map.items():
        if k_emoji.lower() in kriteria_key.lower(): emoji = v_emoji; break

    # Expander yang simpel, cuma nampilin skor dan komentar
    with st.expander(f"{emoji} {kriteria_key} - Band {band_score}", expanded=False):
        st.markdown(f"**Komentar AI:**")
        # Pakai st.info biar ada box-nya, lebih rapi
        st.info(comments if comments else "_Tidak ada komentar._")

# --- 4. User Interface Utama (Kolom Input & Output) ---
if all_chains:
    col_input, col_output = st.columns([0.4, 0.6]) # Input 40%, output 60%

    # === KOLOM 1: INPUT PENGGUNA (Soal & Esai) ===
    with col_input:
        st.subheader("📝 Masukkan Tulisan Anda")
        
        with st.form(key="evaluasi_form", clear_on_submit=False): 
            
            # --- [FIX 1] ---
            # Mengembalikan Text Area untuk Soal
            soal_ielts = st.text_area(
                "Tempel Soal IELTS (Task 1 atau 2):", 
                value=st.session_state.last_soal_ielts, # Ingat input terakhir
                height=150, 
                placeholder="Contoh: Some people believe that..."
            )
            # --- [AKHIR FIX 1] ---
            
            esai_kandidat = st.text_area(
                "Tempel Jawaban/Esai Anda:", 
                value=st.session_state.last_esai_kandidat, # Ingat input terakhir
                height=450, 
                placeholder="Tulis esai lengkap Anda di sini..."
            )
            
            word_count_input = len(esai_kandidat.split())
            st.caption(f"Word count: {word_count_input}")

            submit_button = st.form_submit_button(
                label="Submit Writing ✨", 
                use_container_width=True, 
                type="primary"
            )
        
    # === KOLOM 2: LOGIKA PROSES & TAMPILAN HASIL ===
    with col_output:
        st.subheader("🔍 Analisis & Feedback")
        
        # --- [A] LOGIKA PROSES (Hanya jalan saat tombol form ditekan) ---
        if submit_button:
            if not esai_kandidat.strip() or not soal_ielts.strip(): # Validasi pakai soal_ielts
                st.error("Soal dan Jawaban esai tidak boleh kosong.")
            else:
                st.session_state.last_soal_ielts = soal_ielts # Simpan input
                st.session_state.last_esai_kandidat = esai_kandidat # Simpan input
                
                for key in default_states:
                    if key not in ['last_soal_ielts', 'last_esai_kandidat']:
                        st.session_state[key] = default_states[key]
                
                st.session_state.word_count = word_count_input
                
                with st.container(border=True):
                    st.markdown("### 🤖 Menganalisis esai Anda...")
                    st.info("Ini mungkin butuh 10-30 detik untuk analisis komprehensif.")
                    
                    progress_bar = st.progress(0, text="Memulai analisis...")
                    status_text = st.empty()

                    try:
                        # --- Proses 1: Klasifikasi Task ---
                        st.session_state.processing_status = "Mendeteksi Tipe Task..."
                        progress_bar.progress(10, text=st.session_state.processing_status)
                        status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
                        task_type_result = all_chains["classifier"].invoke({"soal": soal_ielts}).strip().lower().replace("'", "")
                        st.session_state.task_type = task_type_result
                        
                        if st.session_state.task_type not in ['task_1', 'task_2']:
                            st.error(f"Tidak bisa menentukan jenis task ('{st.session_state.task_type}'). Coba perjelas soal.")
                            st.stop()

                        # --- Pilih chain ---
                        if st.session_state.task_type == 'task_1':
                            eval_chain, saran_chain, rewrite_chain = all_chains["rag_t1"], all_chains["saran_t1"], all_chains["rewrite_t1"]
                        else: # task_2
                            eval_chain, saran_chain, rewrite_chain = all_chains["rag_t2"], all_chains["saran_t2"], all_chains["rewrite_t2"]

                        # --- Proses 2: Evaluasi JSON ---
                        st.session_state.processing_status = "Mengevaluasi kriteria IELTS..."
                        progress_bar.progress(40, text=st.session_state.processing_status)
                        status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
                        input_eval = {"soal": soal_ielts, "jawaban": esai_kandidat} # Pakai soal_ielts
                        raw_eval_string = eval_chain.invoke(input_eval)
                        st.session_state.raw_evaluasi_json_str = raw_eval_string 

                        # --- Proses 3: Koreksi Detail (Proofread) ---
                        st.session_state.processing_status = "Melakukan koreksi detail..."
                        progress_bar.progress(70, text=st.session_state.processing_status)
                        status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
                        saran_proofread_hasil = all_chains["proofread"].invoke({"jawaban": esai_kandidat})
                        st.session_state.saran_proofread = saran_proofread_hasil 

                        # --- Proses 4: Parse & Validasi JSON + Hitung Skor ---
                        st.session_state.processing_status = "Menghitung skor band..."
                        progress_bar.progress(80, text=st.session_state.processing_status)
                        status_text.markdown(f"✨ {st.session_state.processing_status}")

                        try:
                            match = re.search(r'\{.*\}', raw_eval_string, re.DOTALL)
                            json_str = match.group(0) if match else raw_eval_string
                            data_evaluasi = json.loads(json_str)
                            st.session_state.parsed_evaluasi_dict = data_evaluasi 
                            
                            if "error" not in data_evaluasi:
                                skor_temp = hitung_skor_keseluruhan(data_evaluasi)
                                if skor_temp != "N/A":
                                    st.session_state.skor_keseluruhan_float = float(skor_temp)
                                    st.session_state.skor_keseluruhan_display = f"{st.session_state.skor_keseluruhan_float:.1f}"
                                    st.session_state.evaluasi_valid = True
                        except Exception as parse_e:
                            print(f"[Debug App] Gagal parse JSON: {parse_e}")
                            st.session_state.evaluasi_valid = False
                            st.session_state.parsed_evaluasi_dict = {"error": f"Gagal parse JSON: {parse_e}"}

                        # --- Proses 5: Minta Saran Umum ---
                        st.session_state.processing_status = "Membuat saran perbaikan..."
                        progress_bar.progress(95, text=st.session_state.processing_status)
                        status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
                        saran_perbaikan_hasil = "(Evaluasi awal gagal/tidak valid)"
                        if st.session_state.evaluasi_valid:
                            input_saran = {"soal": soal_ielts, "jawaban": esai_kandidat, "evaluasi_json": raw_eval_string} # Pakai soal_ielts
                            saran_perbaikan_hasil = saran_chain.invoke(input_saran)
                        st.session_state.saran_perbaikan = saran_perbaikan_hasil 
                        
                        progress_bar.progress(100, text="Analisis Selesai!")
                        status_text.empty() 
                        st.session_state.processing_stage = None 
                        st.session_state.processing_status = "Complete"

                    except Exception as e:
                        st.error(f"Terjadi masalah saat pemrosesan: {e}")
                        st.exception(e) 
                        progress_bar.empty()
                        status_text.error("Analisis Gagal!")
                        st.session_state.processing_stage = None
                        st.session_state.processing_status = "Failed"

        # --- [B] BLOK TAMPILAN HASIL (Selalu jalan jika ada hasil di state) ---
        if st.session_state.parsed_evaluasi_dict and st.session_state.evaluasi_valid:
            data = st.session_state.parsed_evaluasi_dict 
            
            # --- Card: Overall Band Score ---
            with st.container(border=True):
                st.markdown(f"### Overall Band: {st.session_state.skor_keseluruhan_display}")
                st.progress(st.session_state.skor_keseluruhan_float / 9.0)
                
                min_words = 150 if st.session_state.task_type == 'task_1' else 250
                word_req_met = st.session_state.word_count >= min_words
                word_color = "green" if word_req_met else "red"
                
                st.markdown(f"**Word count:** <span style='color:{word_color};'>{st.session_state.word_count}</span> (Target: {min_words}+)", unsafe_allow_html=True)
                
                st.markdown("---")
                # Menggunakan 'overall_comment' jika ada, atau 'strengths'/'weaknesses' sebagai cadangan
                overall_comment = data.get("overall_comment", data.get("strengths", "N/A"))
                st.markdown(f"**Komentar Umum:** {overall_comment}")

            st.markdown("---")

            # --- Card: Detailed Criteria Scores & Feedback (VERSI SIMPLE) ---
            st.markdown("### 💎 Rincian Skor per Kriteria")
            
            kriteria_ordered = [
                next((k for k in data.keys() if "Task" in k), None), 
                "Coherence & Cohesion",
                "Lexical Resource",
                "Grammatical Range & Accuracy"
            ]
            kriteria_ordered = [k for k in kriteria_ordered if k and k in data and "error" not in k]

            # --- [FIX 2] ---
            # Loop ini sekarang memanggil fungsi display_band_detail_SIMPLE
            for kriteria_key in kriteria_ordered:
                kriteria_data = data.get(kriteria_key, {})
                band = kriteria_data.get("band", "N/A")
                comments = kriteria_data.get("comments", "N/A")
                # Panggil helper simple yang baru
                display_band_detail_simple(kriteria_key, band, comments) 
            # --- [AKHIR FIX 2] ---
            
            st.markdown("---")

            # --- Card: General Suggestions ---
            with st.container(border=True):
                st.markdown("### 💡 Saran Perbaikan Umum")
                st.markdown(st.session_state.saran_perbaikan)
            
            st.markdown("---")

            # --- Card: Proofread / Detailed Corrections ---
            with st.container(border=True):
                st.markdown("### ✍️ Koreksi Detail (Proofread)")
                st.markdown(st.session_state.saran_proofread)
            
            st.markdown("---")
            
            # --- Fitur Revisi ---
            st.subheader("✨ Opsi Revisi Otomatis")
            rewrite_chain = all_chains["rewrite_t1"] if st.session_state.task_type == 'task_1' else all_chains["rewrite_t2"]

            possible_targets = [b/2.0 for b in range(int(st.session_state.skor_keseluruhan_float * 2) + 1, 19)]
            
            if possible_targets:
                col_rev1, col_rev2 = st.columns([2,1])
                with col_rev1:
                    target_band = st.selectbox(
                        "Pilih Target Band Revisi:",
                        possible_targets,
                        format_func=lambda x: f"{x:.1f}",
                        key="target_band_selector"
                    )
                with col_rev2:
                    rewrite_button = st.button(f"Revisi ke Band {target_band}", key="rewrite_button", use_container_width=True)

                if rewrite_button:
                    # Ambil data dari state, karena form mungkin sudah tidak ada
                    current_soal = st.session_state.last_soal_ielts
                    current_esai = st.session_state.last_esai_kandidat
                    
                    if not current_soal or not current_esai:
                         st.warning("Data soal atau esai tidak ditemukan di session state.")
                    else:
                        with st.spinner(f"AI sedang merevisi esai ke Band {target_band}... ⏳"):
                            try:
                                input_rewrite = {
                                    "soal": current_soal,
                                    "jawaban": current_esai,
                                    "evaluasi_json": st.session_state.raw_evaluasi_json_str,
                                    "target_band": target_band
                                }
                                hasil_rewrite_text = rewrite_chain.invoke(input_rewrite)
                                st.session_state.hasil_rewrite = hasil_rewrite_text
                            except Exception as e:
                                st.error(f"Gagal melakukan revisi: {e}")
            else:
                st.info("Skor awal sudah 9.0 atau evaluasi gagal.")

            if st.session_state.hasil_rewrite:
                st.markdown("---")
                st.header(f"✨ ESEI REVISI (Target: Band {st.session_state.get('target_band_selector', 'N/A')})")
                with st.container(border=True):
                    st.markdown(st.session_state.hasil_rewrite)

        elif st.session_state.parsed_evaluasi_dict and "error" in st.session_state.parsed_evaluasi_dict:
            st.error("Gagal mengevaluasi esai Anda. Respon dari AI tidak dalam format JSON yang diharapkan.")
            st.caption("Respon mentah dari AI (untuk debug):")
            st.code(st.session_state.raw_evaluasi_json_str)

        elif st.session_state.processing_status not in ["Idle", "Complete", "Failed"]:
             # Ini adalah placeholder saat loading
             st.info("Hasil analisis esai Anda akan muncul di sini.")

        else:
            st.info("Hasil analisis esai Anda akan muncul di sini.")

else:
    st.error("Aplikasi gagal dimuat. Cek log di terminal untuk error setup.")
