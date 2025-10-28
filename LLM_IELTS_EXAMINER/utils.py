# # utils.py
# import json
# import re
# import streamlit as st # Import Streamlit untuk UI

# def hitung_skor_keseluruhan(skor_dict):
#     """Menghitung skor keseluruhan."""
#     try:
#         tr_key = next((key for key in skor_dict if "Task" in key), None)
#         if not tr_key or not isinstance(skor_dict.get(tr_key), dict) or "band" not in skor_dict[tr_key]:
#              print(f"[Debug] Key/Format 'Task...' salah: {skor_dict.get(tr_key)}")
#              return "N/A"
#         required_keys = ["Coherence & Cohesion", "Lexical Resource", "Grammatical Range & Accuracy"]
#         if not all(k in skor_dict and isinstance(skor_dict[k], dict) and "band" in skor_dict[k] for k in required_keys):
#              missing = [k for k in required_keys if k not in skor_dict or not isinstance(skor_dict[k], dict) or "band" not in skor_dict[k]]
#              print(f"[Debug] Key/Format kriteria lain salah/hilang: {missing}")
#              return "N/A"

#         tr = float(skor_dict[tr_key]["band"])
#         cc = float(skor_dict["Coherence & Cohesion"]["band"])
#         lr = float(skor_dict["Lexical Resource"]["band"])
#         gra = float(skor_dict["Grammatical Range & Accuracy"]["band"])
#         rata_rata = (tr + cc + lr + gra) / 4.0
#         sisa = rata_rata - int(rata_rata)
#         if sisa >= 0.75: return int(rata_rata) + 1.0
#         elif sisa >= 0.25: return int(rata_rata) + 0.5
#         else: return float(int(rata_rata))
#     except (TypeError, ValueError, KeyError, StopIteration) as e:
#         print(f"[Debug] Error hitung skor: {e} | Data: {skor_dict}")
#         return "N/A"
#     except Exception as e:
#         print(f"[Debug] Error tak terduga hitung skor: {e}")
#         return "N/A"


# def tampilkan_laporan_streamlit(task_type, evaluasi_string, word_count, saran_perbaikan, saran_proofread):
#     """Menampilkan laporan awal di UI Streamlit."""
#     st.markdown("---")
#     st.header(f"📝 HASIL PEMERIKSAAN AWAL ({task_type.upper()})")
#     data, skor_akhir_awal_str = None, "N/A"
#     min_words = 150 if task_type == 'task_1' else 250

#     try:
#         match = re.search(r'\{.*\}', evaluasi_string, re.DOTALL)
#         json_str = match.group(0) if match else evaluasi_string
#         data = json.loads(json_str)
#     except json.JSONDecodeError:
#         st.error("🚫 EVALUASI GAGAL (OUTPUT BUKAN JSON)")
#         st.warning("Model tidak menghasilkan JSON yang valid. Output mentah:")
#         st.code(evaluasi_string, language=None)
#         return None, "N/A"
#     except Exception as e:
#         st.error(f"🚫 Error parsing JSON: {e}")
#         st.code(evaluasi_string, language=None)
#         return None, "N/A"

#     st.markdown(f"**📝 JUMLAH KATA:** {word_count} kata")
#     if word_count < min_words:
#         st.warning(f"⚠️ **PERINGATAN:** Di bawah {min_words} kata (syarat minimum {task_type.upper()}). Skor mungkin terpengaruh.")

#     with st.expander("✍️ KOREKSI DETAIL (PROOFREAD)", expanded=False): # Tutup default
#         st.markdown(saran_proofread if saran_proofread else "_Tidak ada koreksi detail._")

#     if isinstance(data, dict) and "error" in data:
#         st.error(f"🚫 EVALUASI DIBATALKAN: {data['error']}")
#         return data, "N/A"

#     st.markdown("---")
#     st.header("📊 HASIL EVALUASI SKOR")
#     skor_akhir_awal_str = hitung_skor_keseluruhan(data)
#     if skor_akhir_awal_str != "N/A":
#         # Format skor jadi satu desimal (e.g., 6.0, 6.5)
#         skor_formatted = f"{float(skor_akhir_awal_str):.1f}"
#         st.metric(label="BAND KESELURUHAN", value=skor_formatted)
#     else:
#         st.error("Gagal menghitung skor keseluruhan. Periksa format JSON dari model.")
#     st.markdown("---")

#     # Tampilkan Detail per Kriteria dalam kolom agar lebih rapi
#     cols = st.columns(2) # Bagi jadi 2 kolom
#     col_idx = 0
#     kriteria_keys = list(data.keys())
#     emojis = {"Task": "🎯", "Coherence": "🔗", "Lexical": "📚", "Grammatical": "🖋️"}

#     for key in kriteria_keys:
#         if key == "error": continue
#         current_col = cols[col_idx % 2] # Pilih kolom (0 atau 1)
#         with current_col:
#             emoji = "📊"
#             for k_emoji, v_emoji in emojis.items():
#                 if k_emoji.lower() in key.lower(): emoji = v_emoji; break

#             st.subheader(f"{emoji} {key.upper()}")
#             if isinstance(data.get(key), dict):
#                 detail = data[key]
#                 band = detail.get("band", "N/A")
#                 comments = detail.get("comments", "_Tidak ada komentar._")
#                 st.write(f"**Skor:** {band}")
#                 st.markdown(f"**Komentar:** {comments}")
#             else:
#                  band_flat = data.get(key, "N/A")
#                  st.write(f"**Skor:** {band_flat}")
#                  st.markdown("**Komentar:** _(Format tidak standar)_")
#             st.markdown("---") # Pemisah antar kriteria
#         col_idx += 1

#     # Tampilkan Saran di bawah kolom skor
#     with st.expander("💡 SARAN PERBAIKAN UMUM", expanded=True): # Buka default
#         st.markdown(saran_perbaikan if saran_perbaikan else "_Tidak ada saran perbaikan._")

#     return data, skor_akhir_awal_str


# utils.py
import json
import re
import streamlit as st # Import Streamlit untuk UI

def hitung_skor_keseluruhan(skor_dict):
    """Menghitung skor keseluruhan."""
    try:
        tr_key = next((key for key in skor_dict if "Task" in key), None)
        if not tr_key or not isinstance(skor_dict.get(tr_key), dict) or "band" not in skor_dict[tr_key]:
              print(f"[Debug] Key/Format 'Task...' salah: {skor_dict.get(tr_key)}")
              return "N/A"
        required_keys = ["Coherence & Cohesion", "Lexical Resource", "Grammatical Range & Accuracy"]
        if not all(k in skor_dict and isinstance(skor_dict[k], dict) and "band" in skor_dict[k] for k in required_keys):
              missing = [k for k in required_keys if k not in skor_dict or not isinstance(skor_dict[k], dict) or "band" not in skor_dict[k]]
              print(f"[Debug] Key/Format kriteria lain salah/hilang: {missing}")
              return "N/A"

        tr = float(skor_dict[tr_key]["band"])
        cc = float(skor_dict["Coherence & Cohesion"]["band"])
        lr = float(skor_dict["Lexical Resource"]["band"])
        gra = float(skor_dict["Grammatical Range & Accuracy"]["band"])
        rata_rata = (tr + cc + lr + gra) / 4.0
        sisa = rata_rata - int(rata_rata)
        if sisa >= 0.75: return int(rata_rata) + 1.0
        elif sisa >= 0.25: return int(rata_rata) + 0.5
        else: return float(int(rata_rata))
    except (TypeError, ValueError, KeyError, StopIteration) as e:
        print(f"[Debug] Error hitung skor: {e} | Data: {skor_dict}")
        return "N/A"
    except Exception as e:
        print(f"[Debug] Error tak terduga hitung skor: {e}")
        return "N/A"


def tampilkan_laporan_streamlit(task_type, evaluasi_string, word_count, saran_perbaikan, saran_proofread):
    """Menampilkan laporan awal di UI Streamlit."""
    
    # --- [REQUEST 1: DIHAPUS] ---
    # st.markdown("---") 
    # st.header(f"📝 HASIL PEMERIKSAAN AWAL ({task_type.upper()})")
    # --- [AKHIR REQUEST 1] ---
    
    data, skor_akhir_awal_str = None, "N/A"
    min_words = 150 if task_type == 'task_1' else 250

    try:
        match = re.search(r'\{.*\}', evaluasi_string, re.DOTALL)
        json_str = match.group(0) if match else evaluasi_string
        data = json.loads(json_str)
    except json.JSONDecodeError:
        st.error("🚫 EVALUASI GAGAL (OUTPUT BUKAN JSON)")
        st.warning("Model tidak menghasilkan JSON yang valid. Output mentah:")
        st.code(evaluasi_string, language=None)
        return None, "N/A"
    except Exception as e:
        st.error(f"🚫 Error parsing JSON: {e}")
        st.code(evaluasi_string, language=None)
        return None, "N/A"

    st.markdown(f"**📝 JUMLAH KATA:** {word_count} kata")
    if word_count < min_words:
        st.warning(f"⚠️ **PERINGATAN:** Di bawah {min_words} kata (syarat minimum {task_type.upper()}). Skor mungkin terpengaruh.")

    # --- Expander Koreksi Detail (Tetap) ---
    with st.expander("✍️ KOREKSI DETAIL (PROOFREAD)", expanded=False): # Tutup default
        st.markdown(saran_proofread if saran_proofread else "_Tidak ada koreksi detail._")

    if isinstance(data, dict) and "error" in data:
        st.error(f"🚫 EVALUASI DIBATALKAN: {data['error']}")
        return data, "N/A"

    
    # --- [REQUEST 2: DIHAPUS] ---
    # st.markdown("---") # Pemisah antar expander
    # --- [AKHIR REQUEST 2] ---
        
    with st.expander("📊 HASIL EVALUASI SKOR", expanded=True): # Dibuat 'expanded=True' (terbuka) by default
            
        skor_akhir_awal_str = hitung_skor_keseluruhan(data)
        if skor_akhir_awal_str != "N/A":
            skor_formatted = f"{float(skor_akhir_awal_str):.1f}"
            st.metric(label="BAND KESELURUHAN", value=skor_formatted)
        else:
            st.error("Gagal menghitung skor keseluruhan. Periksa format JSON dari model.")
        
        st.markdown("---") # Pemisah antara skor total dan rincian

        cols = st.columns(2) 
        col_idx = 0
        kriteria_keys = list(data.keys())
        emojis = {"Task": "🎯", "Coherence": "🔗", "Lexical": "📚", "Grammatical": "🖋️"}

        for key in kriteria_keys:
            if key == "error": continue
            current_col = cols[col_idx % 2]
            with current_col:
                emoji = "📊"
                for k_emoji, v_emoji in emojis.items():
                    if k_emoji.lower() in key.lower(): emoji = v_emoji; break

                st.subheader(f"{emoji} {key.upper()}")
                if isinstance(data.get(key), dict):
                    detail = data[key]
                    band = detail.get("band", "N/A")
                    comments = detail.get("comments", "_Tidak ada komentar._")
                    st.write(f"**Skor:** {band}")
                    st.markdown(f"**Komentar:** {comments}")
                else:
                    band_flat = data.get(key, "N/A")
                    st.write(f"**Skor:** {band_flat}")
                    st.markdown("**Komentar:** _(Format tidak standar)_")
                st.markdown("---") # Pemisah antar kriteria
            col_idx += 1
    
    with st.expander("💡 SARAN PERBAIKAN UMUM", expanded=True): # Buka default
        st.markdown(saran_perbaikan if saran_perbaikan else "_Tidak ada saran perbaikan._")

    return data, skor_akhir_awal_str  


