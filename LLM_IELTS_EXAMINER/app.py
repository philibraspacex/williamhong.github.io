# # app.py
# import streamlit as st
# import config # Load konfigurasi (termasuk API Key via config)
# from rag_setup import load_rag_components # Load RAG
# from chains import create_all_chains # Buat chains
# from utils import tampilkan_laporan_streamlit # Helper untuk UI
# import traceback # Untuk debug error
# import re
# import json
# from utils import hitung_skor_keseluruhan

# # --- Konfigurasi Halaman Streamlit ---
# st.set_page_config(layout="wide", page_title="AI IELTS Coach")

# # --- Judul dan Deskripsi ---
# st.title("🤖 AI IELTS Writing Coach (GT Task 1 & 2)")
# st.caption(f"Powered by RAG & Groq ({config.LLM_MODEL_NAME})")
# st.markdown("---")

# # --- Setup Awal & Cache ---
# # Menggunakan cache_resource agar LLM, retriever, chain hanya di-load sekali
# @st.cache_resource
# def setup_application():
#     """Load RAG components and create chains."""
#     print("--- Memulai Setup Aplikasi ---")
#     try:
#         retriever_t1, retriever_t2 = load_rag_components()
#         all_chains = create_all_chains(retriever_t1, retriever_t2)
#         print("--- Setup Aplikasi Selesai ---")
#         return all_chains
#     except Exception as e:
#         print(f"!!! FATAL ERROR saat setup: {e}")
#         st.error(f"Gagal melakukan setup awal: {e}. Cek terminal/log untuk detail.")
#         # Cetak traceback ke terminal untuk debug
#         print(traceback.format_exc())
#         return None

# # Panggil fungsi setup
# all_chains = setup_application()

# # --- User Interface ---
# if all_chains:
#     col1, col2 = st.columns([1, 1]) # Bagi layar jadi 2 kolom sama besar

#     with col1:
#         st.subheader("📝 Masukkan Detail Tulisan Anda")
#         soal_ielts = st.text_area("Soal IELTS (Task 1 atau 2):", height=150, placeholder="Tempel soal lengkap di sini...")
#         esai_kandidat = st.text_area("Jawaban/Esai Anda:", height=400, placeholder="Tempel jawaban lengkap Anda di sini...")
#         submit_button = st.button("🚀 Evaluasi Sekarang!", use_container_width=True)

#     with col2:
#         st.subheader("🔍 Hasil Evaluasi")

#         # Gunakan session state untuk menyimpan hasil agar tidak hilang saat interaksi
#         if 'hasil_evaluasi' not in st.session_state:
#             st.session_state.hasil_evaluasi = None
#         if 'task_type' not in st.session_state:
#             st.session_state.task_type = None
#         if 'evaluasi_valid' not in st.session_state:
#             st.session_state.evaluasi_valid = False
#         if 'skor_awal_float' not in st.session_state:
#             st.session_state.skor_awal_float = None
#         if 'skor_awal_display' not in st.session_state:
#             st.session_state.skor_awal_display = "N/A"
#         if 'hasil_rewrite' not in st.session_state:
#             st.session_state.hasil_rewrite = None


#         if submit_button and soal_ielts and esai_kandidat:
#             if not esai_kandidat.strip() or not soal_ielts.strip():
#                 st.error("Soal dan Jawaban tidak boleh kosong.")
#             else:
#                 # Reset hasil sebelumnya
#                 st.session_state.hasil_evaluasi = None
#                 st.session_state.hasil_rewrite = None

#                 with st.spinner("Menganalisis dan mengevaluasi tulisan Anda... ⏳"):
#                     try:
#                         word_count = len(esai_kandidat.split())

#                         # 1. Klasifikasi Task
#                         st.write("Mengklasifikasi jenis task...")
#                         task_type_result = all_chains["classifier"].invoke({"soal": soal_ielts}).strip().lower().replace("'", "")
#                         st.session_state.task_type = task_type_result
#                         st.write(f"Terdeteksi sebagai: {st.session_state.task_type.upper()}")

#                         if st.session_state.task_type not in ['task_1', 'task_2']:
#                             st.error(f"Tidak bisa menentukan jenis task ('{st.session_state.task_type}'). Coba perjelas soal.")
#                             st.stop() # Hentikan proses jika task tidak jelas

#                         # Pilih chain
#                         if st.session_state.task_type == 'task_1':
#                              eval_chain, saran_chain, rewrite_chain = all_chains["rag_t1"], all_chains["saran_t1"], all_chains["rewrite_t1"]
#                         else: # task_2
#                              eval_chain, saran_chain, rewrite_chain = all_chains["rag_t2"], all_chains["saran_t2"], all_chains["rewrite_t2"]

#                         # 2. Evaluasi JSON
#                         st.write(f"Model ({config.LLM_MODEL_NAME}) berpikir (Tahap 1: Evaluasi JSON)...")
#                         input_eval = {"soal": soal_ielts, "jawaban": esai_kandidat}
#                         hasil_evaluasi_string = eval_chain.invoke(input_eval)
#                         st.session_state.hasil_evaluasi = hasil_evaluasi_string # Simpan hasil evaluasi

#                         # 3. Koreksi Detail
#                         st.write(f"Model ({config.LLM_MODEL_NAME}) berpikir (Tahap 2: Koreksi Detail)...")
#                         saran_proofread = all_chains["proofread"].invoke({"jawaban": esai_kandidat})

#                         # 4. Parse & Validasi Awal (hanya untuk cek error & skor)
#                         data_evaluasi, skor_awal_f, eval_valid = None, None, False
#                         skor_awal_disp = "N/A"
#                         try:
#                             match = re.search(r'\{.*\}', hasil_evaluasi_string, re.DOTALL)
#                             json_str = match.group(0) if match else hasil_evaluasi_string
#                             data_evaluasi = json.loads(json_str)
#                             if "error" not in data_evaluasi:
#                                 skor_awal_disp_temp = hitung_skor_keseluruhan(data_evaluasi)
#                                 if skor_awal_disp_temp != "N/A":
#                                     skor_awal_f = float(skor_awal_disp_temp)
#                                     skor_awal_disp = f"{skor_awal_f:.1f}" # Format ke 1 desimal
#                                     eval_valid = True
#                         except Exception as parse_e:
#                              print(f"[Debug App] Gagal parse JSON awal: {parse_e}") # Debug di terminal
#                              eval_valid = False

#                         st.session_state.evaluasi_valid = eval_valid
#                         st.session_state.skor_awal_float = skor_awal_f
#                         st.session_state.skor_awal_display = skor_awal_disp

#                         saran_perbaikan = "(Evaluasi awal gagal/tidak valid)"
#                         if st.session_state.evaluasi_valid:
#                             # 5. Minta Saran Umum
#                             st.write(f"Model ({config.LLM_MODEL_NAME}) berpikir (Tahap 3: Minta Saran)...")
#                             input_saran = {"soal": soal_ielts, "jawaban": esai_kandidat, "evaluasi_json": hasil_evaluasi_string}
#                             saran_perbaikan = saran_chain.invoke(input_saran)

#                         # 6. Tampilkan Laporan Awal (panggil fungsi dari utils)
#                         # Kita pass saran_proofread dan saran_perbaikan ke fungsi tampilkan
#                         tampilkan_laporan_streamlit(
#                             st.session_state.task_type, st.session_state.hasil_evaluasi, word_count,
#                             saran_perbaikan, saran_proofread
#                         )


#                     except Exception as e:
#                         st.error(f"Terjadi masalah saat pemrosesan utama: {e}")
#                         st.exception(e) # Tampilkan traceback di UI untuk debug

#         # --- Tampilkan Hasil Evaluasi (jika sudah ada di session state) ---
#         elif st.session_state.hasil_evaluasi:
#              # Tampilkan lagi hasil evaluasi awal (tanpa memanggil LLM lagi)
#              # Perlu memanggil ulang saran dan proofread jika ingin ditampilkan lagi
#              # Atau simpan juga saran_perbaikan & saran_proofread di session_state
#              # Untuk simpelnya, kita panggil ulang tampilkan_laporan, tapi perlu saran & proofread
#              # Solusi lebih baik: Refactor tampilkan_laporan agar bisa dipanggil hanya dg hasil evaluasi
#              st.info("Menampilkan hasil evaluasi sebelumnya.")
#              # Ini hanya contoh, perlu penyesuaian agar saran/proofread bisa tampil lagi
#              tampilkan_laporan_streamlit(
#                  st.session_state.task_type, st.session_state.hasil_evaluasi,
#                  len(esai_kandidat.split()), # Perlu esai_kandidat dari input saat ini
#                  "(Saran perlu dijalankan ulang)", # Perlu input saran
#                  "(Koreksi perlu dijalankan ulang)" # Perlu input koreksi
#              )


#         # --- Fitur Revisi (di luar tombol submit utama) ---
#         if st.session_state.evaluasi_valid and st.session_state.skor_awal_float is not None:
#              st.markdown("---")
#              st.subheader("✨ Opsi Revisi Otomatis")
#              # Pastikan chain untuk rewrite dipilih dengan benar
#              rewrite_chain = all_chains["rewrite_t1"] if st.session_state.task_type == 'task_1' else all_chains["rewrite_t2"]

#              possible_targets = [b/2.0 for b in range(int(st.session_state.skor_awal_float * 2) + 1, 19)] # e.g., [6.5, 7.0, ..., 9.0]
#              if possible_targets:
#                  target_band = st.selectbox(
#                      "Pilih Target Band Revisi:",
#                      possible_targets,
#                      format_func=lambda x: f"{x:.1f}",
#                      key="target_band_selector" # Key unik untuk widget
#                  )
#                  rewrite_button = st.button(f"Revisi ke Band {target_band}", key="rewrite_button")

#                  if rewrite_button and target_band:
#                      # Ambil data dari state atau input saat ini
#                      current_soal = soal_ielts # Ambil dari text_area soal
#                      current_esai = esai_kandidat # Ambil dari text_area esai
#                      current_eval_str = st.session_state.hasil_evaluasi

#                      if not current_soal or not current_esai or not current_eval_str:
#                          st.warning("Pastikan Soal, Jawaban, dan hasil evaluasi awal tersedia.")
#                      else:
#                          with st.spinner(f"Merevisi esai ke Band {target_band}... ⏳"):
#                              try:
#                                  input_rewrite = {
#                                      "soal": current_soal,
#                                      "jawaban": current_esai,
#                                      "evaluasi_json": current_eval_str,
#                                      "target_band": target_band
#                                  }
#                                  hasil_rewrite_text = rewrite_chain.invoke(input_rewrite)
#                                  st.session_state.hasil_rewrite = hasil_rewrite_text # Simpan hasil revisi

#                              except Exception as e:
#                                  st.error(f"Gagal melakukan revisi: {e}")
#                                  # st.exception(e) # Traceback jika perlu

#              else:
#                  st.info("Skor awal sudah cukup tinggi (atau evaluasi gagal) sehingga tidak ada target revisi yang lebih tinggi.")

#         # Tampilkan hasil revisi jika ada di session state
#         if st.session_state.hasil_rewrite:
#             st.markdown("---")
#             st.header(f"✨ VERSI REVISI (Target: Band {st.session_state.get('target_band_selector', 'N/A')})")
#             st.markdown(st.session_state.hasil_rewrite)


# elif not all_chains:
#     st.warning("Sedang menunggu setup awal aplikasi...")

# # --- Footer (Opsional) ---
# st.markdown("---")
# st.caption("AI IELTS Coach | Dibuat dengan LangChain & Streamlit")




# app.py
# --- [IMPROVISASI UI TOTAL OLEH GEMINI] ---

# import streamlit as st
# import config 
# from rag_setup import load_rag_components
# from chains import create_all_chains
# from utils import tampilkan_laporan_streamlit # KITA TETAP PAKAI INI!
# import traceback 
# import re
# import json
# from utils import hitung_skor_keseluruhan

# # --- 1. Konfigurasi Halaman & Sidebar ---
# st.set_page_config(
#     layout="wide", 
#     page_title="AI IELTS Coach",
#     page_icon="🤖"
# )

# # --- Sidebar (Info Aplikasi) ---
# with st.sidebar:
#     st.title("Tentang Aplikasi")
#     st.info(
#         f"""
#         **AI IELTS Writing Coach** ini dirancang untuk menganalisis esai Task 1 & 2 Anda menggunakan RAG dan model AI canggih.

#         **Fitur Utama:**
#         - Evaluasi 4 kriteria IELTS.
#         - Feedback & Saran perbaikan.
#         - Koreksi tata bahasa (Proofread).
#         - Revisi otomatis ke target band.

#         **Model LLM:** `{config.LLM_MODEL_NAME}`
#         """
#     )
#     st.warning("Skor dari AI adalah estimasi dan BUKAN pengganti examiner resmi.")
#     st.caption("Dibuat dengan LangChain, Groq, & Streamlit.")

# # --- 2. Judul & Setup Aplikasi ---
# st.title("🤖 AI IELTS Writing General Training")
# st.caption(f"Analisis Mendalam Esai Anda dalam Hitungan Detik")

# # Menggunakan cache_resource agar LLM, retriever, chain hanya di-load sekali
# @st.cache_resource
# def setup_application():
#     """Load RAG components and create chains."""
#     print("--- Memulai Setup Aplikasi (hanya sekali) ---")
#     try:
#         retriever_t1, retriever_t2 = load_rag_components()
#         all_chains = create_all_chains(retriever_t1, retriever_t2)
#         print("--- Setup Aplikasi Selesai ---")
#         return all_chains
#     except Exception as e:
#         print(f"!!! FATAL ERROR saat setup: {e}")
#         st.error(f"Gagal melakukan setup awal: {e}. Cek terminal/log untuk detail.")
#         print(traceback.format_exc())
#         return None

# # Panggil fungsi setup
# all_chains = setup_application()

# # --- 3. Inisialisasi Session State (LEBIH LENGKAP) ---
# # Ini penting agar data tidak hilang dan UI rapi
# default_states = {
#     'hasil_evaluasi': None,      # Raw string JSON dari chain evaluasi
#     'saran_perbaikan': None,     # String saran dari chain saran
#     'saran_proofread': None,     # String markdown dari chain proofread
#     'hasil_rewrite': None,       # String esai hasil revisi
#     'task_type': None,           # 'task_1' atau 'task_2'
#     'word_count': 0,             # Jumlah kata esai
#     'evaluasi_valid': False,     # Status apakah JSON valid
#     'skor_awal_float': 0.0,      # Skor float (misal: 6.5)
#     'skor_awal_display': "N/A",  # Skor string (misal: "6.5")
#     'target_band_selector': None # Untuk menyimpan pilihan user
# }
# for key, value in default_states.items():
#     if key not in st.session_state:
#         st.session_state[key] = value

# # --- 4. User Interface Utama (Kolom Input & Output) ---
# if all_chains:
#     # Kolom input dibuat lebih besar (60%)
#     col1, col2 = st.columns([0.6, 0.4]) 

#     # === KOLOM 1: INPUT PENGGUNA (PAKE FORM) ===
#     with col1:
#         st.subheader("📝 Masukkan Tulisan Anda")
        
#         # Gunakan form untuk mengelompokkan input
#         with st.form(key="evaluasi_form"):
#             soal_ielts = st.text_area("Tempel Soal IELTS (Task 1 atau 2):", height=150, placeholder="Contoh: Some people think that... Discuss both views and give your opinion.")
#             esai_kandidat = st.text_area("Tempel Jawaban/Esai Anda:", height=400, placeholder="Tulis esai lengkap Anda di sini...")
            
#             # Tombol submit untuk form
#             submit_button = st.form_submit_button(
#                 label="🚀 Evaluasi Sekarang!", 
#                 use_container_width=True, 
#                 type="primary"
#             )

#     # === KOLOM 2: LOGIKA PROSES & TAMPILAN HASIL ===
#     with col2:
#         st.subheader("🔍 Hasil Evaluasi AI")

#         # --- [A] LOGIKA PROSES (Hanya jalan saat tombol form ditekan) ---
#         if submit_button:
#             if not esai_kandidat.strip() or not soal_ielts.strip():
#                 st.error("Soal dan Jawaban tidak boleh kosong.")
#             else:
#                 # 1. Reset semua state sebelum proses baru
#                 for key in default_states:
#                     st.session_state[key] = default_states[key]
                
#                 # 2. Tampilkan spinner UTAMA. Log "Model berpikir..." HILANG.
#                 with st.spinner("AI sedang menganalisis... Ini mungkin butuh 10-30 detik. 🧠"):
#                     try:
#                         st.session_state.word_count = len(esai_kandidat.split())

#                         # --- Proses 1: Klasifikasi Task ---
#                         # st.write("...") <-- DIHAPUS
#                         task_type_result = all_chains["classifier"].invoke({"soal": soal_ielts}).strip().lower().replace("'", "")
#                         st.session_state.task_type = task_type_result
#                         # st.write("...") <-- DIHAPUS

#                         if st.session_state.task_type not in ['task_1', 'task_2']:
#                             st.error(f"Tidak bisa menentukan jenis task ('{st.session_state.task_type}'). Coba perjelas soal.")
#                             st.stop()

#                         # --- Proses 2: Pilih chain ---
#                         if st.session_state.task_type == 'task_1':
#                             eval_chain, saran_chain, rewrite_chain = all_chains["rag_t1"], all_chains["saran_t1"], all_chains["rewrite_t1"]
#                         else: # task_2
#                             eval_chain, saran_chain, rewrite_chain = all_chains["rag_t2"], all_chains["saran_t2"], all_chains["rewrite_t2"]

#                         # --- Proses 3: Evaluasi JSON ---
#                         # st.write("...") <-- DIHAPUS
#                         input_eval = {"soal": soal_ielts, "jawaban": esai_kandidat}
#                         hasil_evaluasi_string = eval_chain.invoke(input_eval)
#                         st.session_state.hasil_evaluasi = hasil_evaluasi_string # Simpan string mentah

#                         # --- Proses 4: Koreksi Detail (Proofread) ---
#                         # st.write("...") <-- DIHAPUS
#                         saran_proofread_hasil = all_chains["proofread"].invoke({"jawaban": esai_kandidat})
#                         st.session_state.saran_proofread = saran_proofread_hasil # SIMPAN KE STATE

#                         # --- Proses 5: Parse & Validasi JSON ---
#                         try:
#                             match = re.search(r'\{.*\}', hasil_evaluasi_string, re.DOTALL)
#                             json_str = match.group(0) if match else hasil_evaluasi_string
#                             data_evaluasi = json.loads(json_str)
#                             if "error" not in data_evaluasi:
#                                 skor_awal_disp_temp = hitung_skor_keseluruhan(data_evaluasi)
#                                 if skor_awal_disp_temp != "N/A":
#                                     st.session_state.skor_awal_float = float(skor_awal_disp_temp)
#                                     st.session_state.skor_awal_display = f"{st.session_state.skor_awal_float:.1f}"
#                                     st.session_state.evaluasi_valid = True
#                         except Exception as parse_e:
#                             print(f"[Debug App] Gagal parse JSON: {parse_e}")
#                             st.session_state.evaluasi_valid = False

#                         # --- Proses 6: Minta Saran Umum (jika evaluasi valid) ---
#                         saran_perbaikan_hasil = "(Evaluasi awal gagal/tidak valid)"
#                         if st.session_state.evaluasi_valid:
#                             # st.write("...") <-- DIHAPUS
#                             input_saran = {"soal": soal_ielts, "jawaban": esai_kandidat, "evaluasi_json": hasil_evaluasi_string}
#                             saran_perbaikan_hasil = saran_chain.invoke(input_saran)
                        
#                         st.session_state.saran_perbaikan = saran_perbaikan_hasil # SIMPAN KE STATE

#                         # --- Proses 7: JANGAN TAMPILKAN DI SINI ---
#                         # HAPUS PANGGILAN 'tampilkan_laporan_streamlit' DARI SINI
#                         # Kita akan panggil di BLOK TAMPILAN
                        
#                         # st.rerun() # Tidak perlu rerun, biarkan script lanjut ke blok [B]

#                     except Exception as e:
#                         st.error(f"Terjadi masalah saat pemrosesan utama: {e}")
#                         st.exception(e) # Tampilkan traceback di UI untuk debug

#         # --- [B] BLOK TAMPILAN HASIL (Selalu jalan jika ada hasil di state) ---
#         # Ini adalah logika tampilan yang TERPISAH.
#         # Ini akan otomatis nampil setelah 'submit_button' selesai,
#         # dan akan nampil ulang DENGAN BENAR jika user mainin 'selectbox'
        
#         if st.session_state.hasil_evaluasi:
            
#             st.success(f"Analisis Selesai! Terdeteksi sebagai: **{st.session_state.task_type.upper()}**")
            
#             # Kita bungkus outputnya di 'container' biar rapi
#             with st.container(border=True):
#                 # KITA PANGGIL FUNGSI ASLI LU DI SINI!
#                 # Kita pakai data LENGKAP dari SESSION STATE
#                 tampilkan_laporan_streamlit(
#                     st.session_state.task_type,
#                     st.session_state.hasil_evaluasi,
#                     st.session_state.word_count,
#                     st.session_state.saran_perbaikan,
#                     st.session_state.saran_proofread
#                 )

#             # --- [C] Fitur Revisi (Tampil jika evaluasi valid) ---
#             if st.session_state.evaluasi_valid:
#                 st.markdown("---")
#                 st.subheader("✨ Opsi Revisi Otomatis")
#                 rewrite_chain = all_chains["rewrite_t1"] if st.session_state.task_type == 'task_1' else all_chains["rewrite_t2"]

#                 possible_targets = [b/2.0 for b in range(int(st.session_state.skor_awal_float * 2) + 1, 19)]
                
#                 if possible_targets:
#                     col_rev1, col_rev2 = st.columns([2,1])
#                     with col_rev1:
#                         target_band = st.selectbox(
#                             "Pilih Target Band Revisi:",
#                             possible_targets,
#                             format_func=lambda x: f"{x:.1f}",
#                             key="target_band_selector"
#                         )
#                     with col_rev2:
#                         # Tombol revisi dibuat full width
#                         rewrite_button = st.button(f"Revisi ke Band {target_band}", key="rewrite_button", use_container_width=True)

#                     if rewrite_button:
#                         if not soal_ielts or not esai_kandidat:
#                              st.warning("Pastikan Soal dan Jawaban asli masih ada di kolom input.")
#                         else:
#                             with st.spinner(f"AI sedang merevisi esai ke Band {target_band}... ⏳"):
#                                 try:
#                                     input_rewrite = {
#                                         "soal": soal_ielts,
#                                         "jawaban": esai_kandidat,
#                                         "evaluasi_json": st.session_state.hasil_evaluasi,
#                                         "target_band": target_band
#                                     }
#                                     hasil_rewrite_text = rewrite_chain.invoke(input_rewrite)
#                                     st.session_state.hasil_rewrite = hasil_rewrite_text
#                                 except Exception as e:
#                                     st.error(f"Gagal melakukan revisi: {e}")
#                 else:
#                     st.info("Skor awal sudah 9.0 atau evaluasi gagal.")

#             # Tampilkan hasil revisi jika ada
#             if st.session_state.hasil_rewrite:
#                 st.markdown("---")
#                 st.header(f"✨ VERSI REVISI (Target: Band {st.session_state.get('target_band_selector', 'N/A')})")
#                 # Bungkus hasil revisi di container juga
#                 with st.container(border=True):
#                     st.markdown(st.session_state.hasil_rewrite)

#         # --- [D] Halaman Default (sebelum ada input) ---
#         elif not all_chains:
#             st.warning("Sedang menunggu setup awal aplikasi...")
#         else:
#             st.info("Hasil evaluasi AI akan muncul di sini setelah Anda menekan tombol 'Evaluasi Sekarang!'.")

# else:
#     st.error("Aplikasi gagal dimuat. Cek log di terminal untuk error setup.")

# # --- Footer (Opsional) --- 
# st.markdown("---")
# st.caption("AI IELTS Coach | Dibuat dengan LangChain, Groq, & Streamlit")


# app.py
# --- [IMPROVISASI UI TOTAL MIRIP SOCRATLY OLEH GEMINI] ---

# import streamlit as st
# import config 
# from rag_setup import load_rag_components
# from chains import create_all_chains
# # from utils import tampilkan_laporan_streamlit # DIHAPUS, LOGIKANYA PINDAH KE SINI
# import traceback 
# import re
# import json
# from utils import hitung_skor_keseluruhan # Ini tetap dipakai

# # --- 1. Konfigurasi Halaman & Sidebar ---
# st.set_page_config(
#     layout="wide", 
#     page_title="AI IELTS Coach",
#     page_icon="🤖"
# )

# # --- Sidebar (Info Aplikasi) ---
# with st.sidebar:
#     st.title("Tentang Aplikasi")
#     st.info(
#         f"""
#         **AI IELTS Writing Coach** ini dirancang untuk menganalisis esai Task 1 & 2 Anda menggunakan RAG dan model AI canggih.

#         **Fitur Utama:**
#         - Evaluasi 4 kriteria IELTS.
#         - Feedback & Saran perbaikan.
#         - Koreksi tata bahasa (Proofread).
#         - Revisi otomatis ke target band.

#         **Model LLM:** `{config.LLM_MODEL_NAME}`
#         """
#     )
#     st.warning("Skor dari AI adalah estimasi dan BUKAN pengganti examiner resmi.")
#     st.caption("Dibuat dengan LangChain, Groq, & Streamlit.")

# # --- 2. Judul & Setup Aplikasi ---
# st.title("✍️ Writing Challenge")
# st.subheader("IELTS Writing Tasks")
# st.caption(f"Task 1 of 15 (Powered by RAG & Groq ({config.LLM_MODEL_NAME}))") # Contoh aja

# # Menggunakan cache_resource agar LLM, retriever, chain hanya di-load sekali
# @st.cache_resource
# def setup_application():
#     """Load RAG components and create chains."""
#     print("--- Memulai Setup Aplikasi (hanya sekali) ---")
#     try:
#         retriever_t1, retriever_t2 = load_rag_components()
#         all_chains = create_all_chains(retriever_t1, retriever_t2)
#         print("--- Setup Aplikasi Selesai ---")
#         return all_chains
#     except Exception as e:
#         print(f"!!! FATAL ERROR saat setup: {e}")
#         st.error(f"Gagal melakukan setup awal: {e}. Cek terminal/log untuk detail.")
#         print(traceback.format_exc())
#         return None

# # Panggil fungsi setup
# all_chains = setup_application()

# # --- 3. Inisialisasi Session State (LEBIH LENGKAP & DETAIL) ---
# # Data akan disimpan lebih terstruktur untuk UI Socratly-like
# default_states = {
#     'raw_evaluasi_json_str': None,  # String JSON mentah dari chain evaluasi
#     'parsed_evaluasi_dict': None,   # Hasil parse JSON (dictionary)
#     'saran_perbaikan': None,        # String saran dari chain saran
#     'saran_proofread': None,        # String markdown dari chain proofread
#     'hasil_rewrite': None,          # String esai hasil revisi
#     'task_type': None,              # 'task_1' atau 'task_2'
#     'word_count': 0,                # Jumlah kata esai
#     'evaluasi_valid': False,        # Status apakah JSON valid
#     'skor_keseluruhan_float': 0.0,  # Skor float (misal: 6.5)
#     'skor_keseluruhan_display': "N/A", # Skor string (misal: "6.5")
#     'target_band_selector': None,   # Untuk menyimpan pilihan user di fitur revisi
#     'processing_stage': None,       # Untuk progress bar: 'classify', 'evaluate', 'proofread', 'suggest'
#     'processing_status': "Idle"
# }
# for key, value in default_states.items():
#     if key not in st.session_state:
#         st.session_state[key] = value

# # --- HELPER FUNCTIONS for UI (mirip Socratly) ---

# def display_band_detail(kriteria_key, band_score, comments, data_evaluasi):
#     """Menampilkan detail Band per kriteria dalam expander."""
#     emoji_map = {"Task": "🎯", "Coherence": "🔗", "Lexical": "📚", "Grammatical": "🖋️"}
#     emoji = "📊"
#     for k_emoji, v_emoji in emoji_map.items():
#         if k_emoji.lower() in kriteria_key.lower(): emoji = v_emoji; break

#     # Extract detailed points from data_evaluasi if available
#     detail = data_evaluasi.get(kriteria_key, {})
#     strengths_points = detail.get("strengths_points", ["N/A"]) # Butuh perubahan prompt AI
#     weaknesses_points = detail.get("weaknesses_points", ["N/A"]) # Butuh perubahan prompt AI
#     band_descriptors = detail.get("band_descriptors", {"description": "N/A"}) # Butuh perubahan prompt AI
#     your_essay_quotes = detail.get("your_essay_quotes", ["N/A"]) # Butuh perubahan prompt AI
#     why_not_next_band = detail.get("why_not_next_band", ["N/A"]) # Butuh perubahan prompt AI

#     with st.expander(f"{emoji} {kriteria_key} - Band {band_score}", expanded=False):
#         # Overall Feedback
#         st.markdown(f"**Komentar Umum:** {comments}")
#         st.divider()

#         # Evidence for Band X
#         st.subheader("✅ Evidence for this Band")
#         col_check, col_quotes = st.columns(2)
#         with col_check:
#             for point in strengths_points:
#                 st.markdown(f"✔️ {point}")
#         with col_quotes:
#             st.markdown("**Your Essay Quotes:**")
#             for quote in your_essay_quotes:
#                 st.markdown(f"> _{quote}_")
        
#         st.divider()

#         # Why Not Band Y
#         next_band = int(float(band_score)) + 1 if float(band_score) < 9.0 else "N/A"
#         if next_band != "N/A":
#             st.subheader(f"❌ Why Not Band {next_band}?")
#             for point in why_not_next_band:
#                  st.markdown(f"• {point}")
        
#         st.divider()

#         # Band Descriptors (Original)
#         st.subheader("📚 Official Band Descriptors")
#         st.markdown(band_descriptors.get("description", "N/A"))


# # --- 4. User Interface Utama (Kolom Input & Output) ---
# if all_chains:
#     col_input, col_output = st.columns([0.4, 0.6]) # Input lebih kecil, output lebih besar

#     # === KOLOM 1: INPUT PENGGUNA (Soal & Esai) ===
#     with col_input:
#         st.subheader("Task 2")
#         with st.container(border=True): # Card untuk Task Description
#             st.markdown("Some people believe that the rise of online shopping is harmful to local shops and communities, while others argue it provides more convenience and wider choices. Discuss both views and give your opinion. Give reasons for your answer and include any relevant examples from your own knowledge or experience.")
#             st.caption("⌚ 40 minutes") # Contoh waktu

#             st.markdown("---")
#             st.markdown("💡 **Tips:**")
#             st.markdown("You should spend about 40 minutes on this task.")
#             st.markdown("Write at least 250 words.")
        
#         st.markdown("---") # Pemisah Card

#         st.subheader("Your Response:")
#         with st.form(key="evaluasi_form", clear_on_submit=False): # clear_on_submit=False agar teks tidak hilang
#             # Text area untuk soal tidak diperlukan lagi di sini karena soal sudah di hardcode
#             # Tetapi, untuk fleksibilitas (jika suatu saat soal bisa diganti), kita tetap sediakan variable soal_ielts
#             # Untuk demo ini, kita akan langsung pakai soal_hardcoded
#             soal_ielts_hardcoded = "Some people believe that the rise of online shopping is harmful to local shops and communities, while others argue it provides more convenience and wider choices. Discuss both views and give your opinion. Give reasons for your answer and include any relevant examples from your own knowledge or experience."
            
#             esai_kandidat = st.text_area(
#                 "Tulis esai lengkap Anda di sini...", 
#                 value=st.session_state.get('last_esai_kandidat', ''), # Pertahankan input terakhir
#                 height=450, 
#                 placeholder="Tulis esai lengkap Anda di sini..."
#             )
            
#             word_count_input = len(esai_kandidat.split())
#             st.caption(f"Word count: {word_count_input} | Target: 250+ words")

#             submit_button = st.form_submit_button(
#                 label="Submit Writing ✨", 
#                 use_container_width=True, 
#                 type="primary"
#             )
        
#     # === KOLOM 2: LOGIKA PROSES & TAMPILAN HASIL ===
#     with col_output:
#         st.subheader("Analysis & Feedback")
        
#         # --- [A] LOGIKA PROSES (Hanya jalan saat tombol form ditekan) ---
#         if submit_button:
#             if not esai_kandidat.strip():
#                 st.error("Jawaban esai tidak boleh kosong.")
#             else:
#                 # Simpan input terakhir ke session_state agar tidak hilang
#                 st.session_state.last_esai_kandidat = esai_kandidat
                
#                 # Reset semua state hasil sebelum proses baru
#                 for key in default_states:
#                     if key not in ['last_esai_kandidat']: # Jangan reset input
#                         st.session_state[key] = default_states[key]
                
#                 st.session_state.word_count = word_count_input
                
#                 # Visualisasi Loading & Progress
#                 with st.container(border=True):
#                     st.markdown("### 🤖 Analyzing your essay...")
#                     st.info("This may take 10-30 seconds for comprehensive analysis.")
                    
#                     progress_bar = st.progress(0, text="Starting analysis...")
#                     status_text = st.empty()

#                     try:
#                         # --- Proses 1: Klasifikasi Task ---
#                         st.session_state.processing_stage = 'classify'
#                         st.session_state.processing_status = "Detecting Task Type..."
#                         progress_bar.progress(10, text=st.session_state.processing_status)
#                         status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
#                         task_type_result = all_chains["classifier"].invoke({"soal": soal_ielts_hardcoded}).strip().lower().replace("'", "")
#                         st.session_state.task_type = task_type_result
                        
#                         if st.session_state.task_type not in ['task_1', 'task_2']:
#                             st.error(f"Tidak bisa menentukan jenis task ('{st.session_state.task_type}'). Coba perjelas soal.")
#                             st.stop()

#                         # --- Pilih chain ---
#                         if st.session_state.task_type == 'task_1':
#                             eval_chain, saran_chain, rewrite_chain = all_chains["rag_t1"], all_chains["saran_t1"], all_chains["rewrite_t1"]
#                         else: # task_2
#                             eval_chain, saran_chain, rewrite_chain = all_chains["rag_t2"], all_chains["saran_t2"], all_chains["rewrite_t2"]

#                         # --- Proses 2: Evaluasi JSON ---
#                         st.session_state.processing_stage = 'evaluate'
#                         st.session_state.processing_status = "Evaluating IELTS criteria (TR, CC, LR, GRA)..."
#                         progress_bar.progress(40, text=st.session_state.processing_status)
#                         status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
#                         input_eval = {"soal": soal_ielts_hardcoded, "jawaban": esai_kandidat}
#                         raw_eval_string = eval_chain.invoke(input_eval)
#                         st.session_state.raw_evaluasi_json_str = raw_eval_string # Simpan string mentah

#                         # --- Proses 3: Koreksi Detail (Proofread) ---
#                         st.session_state.processing_stage = 'proofread'
#                         st.session_state.processing_status = "Performing detailed proofreading..."
#                         progress_bar.progress(70, text=st.session_state.processing_status)
#                         status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
#                         saran_proofread_hasil = all_chains["proofread"].invoke({"jawaban": esai_kandidat})
#                         st.session_state.saran_proofread = saran_proofread_hasil # SIMPAN KE STATE

#                         # --- Proses 4: Parse & Validasi JSON + Hitung Skor ---
#                         st.session_state.processing_stage = 'parse_score'
#                         st.session_state.processing_status = "Calculating overall band score..."
#                         progress_bar.progress(80, text=st.session_state.processing_status)
#                         status_text.markdown(f"✨ {st.session_state.processing_status}")

#                         try:
#                             match = re.search(r'\{.*\}', raw_eval_string, re.DOTALL)
#                             json_str = match.group(0) if match else raw_eval_string
#                             data_evaluasi = json.loads(json_str)
#                             st.session_state.parsed_evaluasi_dict = data_evaluasi # Simpan dictionary
                            
#                             if "error" not in data_evaluasi:
#                                 skor_temp = hitung_skor_keseluruhan(data_evaluasi)
#                                 if skor_temp != "N/A":
#                                     st.session_state.skor_keseluruhan_float = float(skor_temp)
#                                     st.session_state.skor_keseluruhan_display = f"{st.session_state.skor_keseluruhan_float:.1f}"
#                                     st.session_state.evaluasi_valid = True
#                         except Exception as parse_e:
#                             print(f"[Debug App] Gagal parse JSON: {parse_e}")
#                             st.session_state.evaluasi_valid = False
#                             st.session_state.parsed_evaluasi_dict = {"error": f"Gagal parse JSON: {parse_e}"}

#                         # --- Proses 5: Minta Saran Umum (jika evaluasi valid) ---
#                         st.session_state.processing_stage = 'suggest'
#                         st.session_state.processing_status = "Generating personalized suggestions..."
#                         progress_bar.progress(95, text=st.session_state.processing_status)
#                         status_text.markdown(f"✨ {st.session_state.processing_status}")
                        
#                         saran_perbaikan_hasil = "(Evaluasi awal gagal/tidak valid)"
#                         if st.session_state.evaluasi_valid:
#                             input_saran = {"soal": soal_ielts_hardcoded, "jawaban": esai_kandidat, "evaluasi_json": raw_eval_string}
#                             saran_perbaikan_hasil = saran_chain.invoke(input_saran)
#                         st.session_state.saran_perbaikan = saran_perbaikan_hasil # SIMPAN KE STATE
                        
#                         progress_bar.progress(100, text="Analysis Complete!")
#                         status_text.empty() # Hapus status teks akhir
#                         st.session_state.processing_stage = None # Reset
#                         st.session_state.processing_status = "Complete"

#                         # Setelah semua proses selesai, Streamlit akan otomatis rerun
#                         # dan menampilkan blok [B] dengan data yang sudah terisi di session_state

#                     except Exception as e:
#                         st.error(f"Terjadi masalah saat pemrosesan: {e}")
#                         st.exception(e) # Tampilkan traceback di UI untuk debug
#                         progress_bar.empty()
#                         status_text.error("Analysis Failed!")
#                         st.session_state.processing_stage = None # Reset
#                         st.session_state.processing_status = "Failed"

#         # --- [B] BLOK TAMPILAN HASIL (Selalu jalan jika ada hasil di state) ---
#         if st.session_state.parsed_evaluasi_dict and st.session_state.evaluasi_valid:
#             data = st.session_state.parsed_evaluasi_dict # Ambil data dict
            
#             # --- Card: Overall Band Score ---
#             with st.container(border=True):
#                 st.markdown(f"### Overall Band: {st.session_state.skor_keseluruhan_display}")
#                 st.progress(st.session_state.skor_keseluruhan_float / 9.0)
#                 st.caption(f"Word count: {st.session_state.word_count} ({'Requirement met' if st.session_state.word_count >= 250 else 'Below requirement'})") # Contoh target 250 kata
                
#                 st.markdown("---")
#                 st.markdown(f"**Overall Comment:** {data.get('overall_comment', 'N/A')}") # New field for overall comment

#             st.markdown("---")

#             # --- Card: Detailed Criteria Scores & Feedback ---
#             st.markdown("### Detailed Score Breakdown")
#             # Kita bisa pakai tab, atau langsung expander per kriteria
            
#             # Mendapatkan kunci kriteria dengan urutan yang benar
#             kriteria_ordered = [
#                 next((k for k in data.keys() if "Task" in k), None), # Task Response/Achievement
#                 "Coherence & Cohesion",
#                 "Lexical Resource",
#                 "Grammatical Range & Accuracy"
#             ]
#             kriteria_ordered = [k for k in kriteria_ordered if k and k in data and "error" not in k]

#             for kriteria_key in kriteria_ordered:
#                 kriteria_data = data.get(kriteria_key, {})
#                 band = kriteria_data.get("band", "N/A")
#                 comments = kriteria_data.get("comments", "N/A")
#                 display_band_detail(kriteria_key, band, comments, data) # Panggil fungsi helper
            
#             st.markdown("---")

#             # --- Card: General Suggestions ---
#             with st.container(border=True):
#                 st.markdown("### 💡 General Suggestions for Improvement")
#                 st.markdown(st.session_state.saran_perbaikan)
            
#             st.markdown("---")

#             # --- Card: Proofread / Detailed Corrections ---
#             with st.container(border=True):
#                 st.markdown("### ✍️ Detailed Corrections (Proofread)")
#                 st.markdown(st.session_state.saran_proofread)
            
#             st.markdown("---")
            
#             # --- Fitur Revisi (di luar tombol submit utama) ---
#             st.subheader("✨ Automatic Revision Options")
#             rewrite_chain = all_chains["rewrite_t1"] if st.session_state.task_type == 'task_1' else all_chains["rewrite_t2"]

#             # Buat daftar target band
#             possible_targets = [b/2.0 for b in range(int(st.session_state.skor_keseluruhan_float * 2) + 1, 19)]
            
#             if possible_targets:
#                 col_rev1, col_rev2 = st.columns([2,1])
#                 with col_rev1:
#                     target_band = st.selectbox(
#                         "Pilih Target Band Revisi:",
#                         possible_targets,
#                         format_func=lambda x: f"{x:.1f}",
#                         key="target_band_selector"
#                     )
#                 with col_rev2:
#                     rewrite_button = st.button(f"Revise to Band {target_band}", key="rewrite_button", use_container_width=True)

#                 if rewrite_button:
#                     if not soal_ielts_hardcoded or not esai_kandidat:
#                          st.warning("Pastikan Soal dan Jawaban asli masih ada di kolom input.")
#                     else:
#                         with st.spinner(f"AI sedang merevisi esai ke Band {target_band}... ⏳"):
#                             try:
#                                 input_rewrite = {
#                                     "soal": soal_ielts_hardcoded,
#                                     "jawaban": esai_kandidat,
#                                     "evaluasi_json": st.session_state.raw_evaluasi_json_str, # Pakai raw JSON string
#                                     "target_band": target_band
#                                 }
#                                 hasil_rewrite_text = rewrite_chain.invoke(input_rewrite)
#                                 st.session_state.hasil_rewrite = hasil_rewrite_text # Simpan hasil revisi
#                             except Exception as e:
#                                 st.error(f"Gagal melakukan revisi: {e}")
#             else:
#                 st.info("Skor awal sudah 9.0 atau evaluasi gagal.")

#             # Tampilkan hasil revisi jika ada
#             if st.session_state.hasil_rewrite:
#                 st.markdown("---")
#                 st.header(f"✨ REVISED ESSAY (Target: Band {st.session_state.get('target_band_selector', 'N/A')})")
#                 with st.container(border=True):
#                     st.markdown(st.session_state.hasil_rewrite)

#         elif st.session_state.parsed_evaluasi_dict and "error" in st.session_state.parsed_evaluasi_dict:
#             st.error("Gagal mengevaluasi esai Anda. Respon dari AI tidak dalam format JSON yang diharapkan atau ada error dari model.")
#             st.caption("Respon mentah dari AI (untuk debug):")
#             st.code(st.session_state.raw_evaluasi_json_str)

#         # --- Halaman Default (sebelum ada input atau saat loading) ---
#         else:
#             if st.session_state.processing_stage:
#                 # Ini akan ditampilkan saat proses sedang berjalan
#                 with st.container(border=True):
#                     st.markdown("### 🤖 Preparing Analysis...")
#                     st.info(f"Current stage: {st.session_state.processing_status}")
#                     st.progress(0) # Placeholder bar, nanti diisi dari atas
#             else:
#                 st.info("Hasil analisis esai Anda akan muncul di sini.")

# else:
#     st.error("Aplikasi gagal dimuat. Cek log di terminal untuk error setup.")

# app.py
# --- [REVISI UI FINAL - Menyesuaikan Input Soal & Data AI] ---

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