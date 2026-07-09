import streamlit as st
import pandas as pd

# Mengimpor menu dari file yang sudah kita pisahkan tadi
from laporan import tampilkan_menu_laporan
from perbandingan import tampilkan_menu_perbandingan

# Konfigurasi Halaman Dasar
st.set_page_config(page_title="Dasbor Audit RUP", page_icon="📊", layout="wide")

# Menu Navigasi di Samping
st.sidebar.title("🧭 Navigasi Dasbor")
menu_terpilih = st.sidebar.radio(
    "Pilih Menu Aplikasi:",
    ["📑 Ekstrak Laporan", "⚖️ Perbandingan OPD"]
)
st.sidebar.markdown("---")

# Area Unggah Dokumen di Samping (Berlaku untuk semua menu)
uploaded_file = st.sidebar.file_uploader("📂 Unggah Data RUP (Excel/CSV)", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Proses Membaca Data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        # Definisi Posisi Kolom (B dan E)
        nama_kolom_B = df.columns[1]  # Kolom B: Nama OPD
        nama_kolom_E = df.columns[4]  # Kolom E: Metode Pengadaan
        
        # Logika Pengelompokkan Standar Audit
        peta_metode = {
            "e-purchasing": "E-Purchasing",
            "pengadaan langsung": "Pengadaan Langsung",
            "penunjukan langsung": "Penunjukan Langsung",
            "seleksi": "Seleksi",
            "tender": "Tender",
            "dikecualikan": "Dikecualikan"
        }
        metode_bersih = df[nama_kolom_E].astype(str).str.strip().str.lower()
        df['Kategori Final'] = metode_bersih.map(peta_metode).fillna("Swakelola")
        
        # PERGANTIAN HALAMAN BERDASARKAN NAVIGASI
        if menu_terpilih == "📑 Ekstrak Laporan":
            tampilkan_menu_laporan(df, nama_kolom_B, nama_kolom_E)
        elif menu_terpilih == "⚖️ Perbandingan OPD":
            tampilkan_menu_perbandingan(df, nama_kolom_B, nama_kolom_E)
            
    except Exception as e:
        st.error(f"Terjadi kegagalan pemrosesan file: {e}")
else:
    # Tampilan Judul Utama Saat File Belum Diupload
    if menu_terpilih == "📑 Ekstrak Laporan":
        st.title("📥 Ekstrak Laporan RUP Terfilter")
    else:
        st.title("⚖️ Komparasi Strategi Pengadaan antar OPD")
    st.info("💡 Silakan unggah dokumen Excel RUP terlebih dahulu pada menu navigasi samping kiri untuk memulai analisa.")
