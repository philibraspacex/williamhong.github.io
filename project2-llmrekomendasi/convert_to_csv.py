import json
import csv
import os

# --- PENGATURAN ---
JSON_FILE_PATH = "matakuliah.json"
CSV_FILE_PATH = "matakuliah.csv"

def flatten_prasyarat(prasyarat_list):
    """Mengubah list prasyarat JSON jadi string yang gampang dibaca."""
    if not prasyarat_list:
        return ""
    
    parts = []
    for item in prasyarat_list:
        kode = item.get("kode_mk", "?")
        nilai = item.get("nilai_min", "-")
        sedang = item.get("sedang_ambil_diperbolehkan", False)
        
        prasyarat_str = f"{kode} (> {nilai}"
        if sedang:
            prasyarat_str += ", Sedang"
        prasyarat_str += ")"
        parts.append(prasyarat_str)
        
    return ", ".join(parts)

def convert_json_to_csv():
    print(f"Membaca data dari {JSON_FILE_PATH}...")
    
    # 1. Buka file JSON
    try:
        with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Gagal membaca file JSON: {e}")
        return

    print(f"Data JSON berhasil dimuat. Total {len(data)} mata kuliah.")

    # 2. Tentukan header CSV
    # Kita pakai header yang gampang dibaca
    headers = [
        "Kode", 
        "Nama Mata Kuliah", 
        "SKS", 
        "Kategori", 
        "Semester", 
        "Prasyarat SKS Total", 
        "Prasyarat MK", 
        "Profesi Relevan", 
        "Deskripsi"
    ]

    # 3. Buka file CSV untuk ditulis
    print(f"Menulis data ke {CSV_FILE_PATH}...")
    try:
        with open(CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as f:
            # Kita pakai titik koma (;) biar aman kalo deskripsinya ada koma
            writer = csv.writer(f, delimiter=';')
            
            # Tulis header
            writer.writerow(headers)
            
            # Tulis data per baris
            for item in data:
                writer.writerow([
                    item.get('kode', ''),
                    item.get('nama', ''),
                    item.get('sks', 0),
                    item.get('kategori', 'N/A'),
                    item.get('semester_umum', 0),
                    item.get('prasyarat_sks_total', 0),
                    flatten_prasyarat(item.get('prasyarat_mk', [])),
                    ", ".join(item.get('profesi_relevan', [])),
                    item.get('deskripsi', '')
                ])
                
        print("====================================================")
        print(f"🎉 SUKSES! File '{CSV_FILE_PATH}' berhasil dibuat.")
        print("====================================================")

    except Exception as e:
        print(f"❌ Gagal menulis file CSV: {e}")

# --- Jalankan Skrip ---
if __name__ == "__main__":
    convert_json_to_csv()