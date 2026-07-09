import streamlit as st
import pandas as pd

# Mengimpor menu dari modul file terpisah
from laporan import tampilkan_menu_laporan
from perbandingan import tampilkan_menu_perbandingan
from rekonsiliasi import tampilkan_menu_rekonsiliasi

# Konfigurasi Halaman Dasar Utama Aplikasi
st.set_page_config(page_title="Dasbor Pusat Audit PBJ", page_icon="📊", layout="wide")

# ==========================================
# NAVIGASI UTAMA APLIKASI (SIDEBAR)
# ==========================================
st.sidebar.title("🧭 Menu Navigasi")
menu_terpilih = st.sidebar.radio(
    "Pilih Fitur Analisis:",
    [
        "📑 Ekstrak Laporan RUP", 
        "⚖️ Perbandingan OPD",
        "🔄 Rekonsiliasi SIRUP & Realisasi"
    ]
)
st.sidebar.markdown("---")

# ==========================================
# LOGIKA ROUTING HALAMAN
# ==========================================

if menu_terpilih == "🔄 Rekonsiliasi SIRUP & Realisasi":
    tampilkan_menu_rekonsiliasi()

elif menu_terpilih == "⚖️ Perbandingan OPD":
    # Langsung panggil modulnya, urusan upload diserahkan ke perbandingan.py
    tampilkan_menu_perbandingan()

elif menu_terpilih == "📑 Ekstrak Laporan RUP":
    st.sidebar.header("📂 Unggah Berkas")
    st.sidebar.info("Unggah 1 berkas RUP untuk diekstrak.")
    uploaded_file = st.sidebar.file_uploader("Unggah Data RUP (Excel/CSV)", type=["xlsx", "csv"])
    
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            nama_kolom_B = df.columns[1]  
            nama_kolom_E = df.columns[4]  
            
            peta_metode = {
                "e-purchasing": "E-Purchasing", "pengadaan langsung": "Pengadaan Langsung",
                "penunjukan langsung": "Penunjukan Langsung", "seleksi": "Seleksi",
                "tender": "Tender", "dikecualikan": "Dikecualikan"
            }
            metode_bersih = df[nama_kolom_E].astype(str).str.strip().str.lower()
            df['Kategori Final'] = metode_bersih.map(peta_metode).fillna("Swakelola")
            
            tampilkan_menu_laporan(df, nama_kolom_B, nama_kolom_E)
                
        except Exception as e:
            st.error(f"Gagal memproses file RUP: {e}")
    else:
        st.title("📥 Ekstrak Laporan RUP Terfilter")
        st.info("💡 Silakan unggah dokumen Berkas RUP terlebih dahulu pada bilah samping kiri.")
