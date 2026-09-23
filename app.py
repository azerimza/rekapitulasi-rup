import pandas as pd
import streamlit as st

# ==========================================
# IMPORT MODUL LOKAL (DENGAN SAFE IMPORT)
# ==========================================
try:
  from laporan import tampilkan_menu_laporan
except ImportError:
  tampilkan_menu_laporan = None

try:
  from perbandingan import tampilkan_menu_perbandingan
except ImportError:
  tampilkan_menu_perbandingan = None

try:
  from rekonsiliasi import tampilkan_menu_rekonsiliasi
except ImportError:
  tampilkan_menu_rekonsiliasi = None

# Konfigurasi Halaman Dasar Utama Aplikasi
st.set_page_config(
    page_title="Dasbor Pusat Audit PBJ", page_icon="📊", layout="wide"
)

# ==========================================
# NAVIGASI UTAMA APLIKASI (SIDEBAR)
# ==========================================
st.sidebar.title("🧭 Menu Navigasi")
menu_terpilih = st.sidebar.radio(
    "Pilih Fitur Analisis:",
    [
        "📑 Ekstrak Laporan RUP",
        "⚖️ Perbandingan OPD",
        "🔄 Rekonsiliasi SIRUP & Realisasi",
    ],
)
st.sidebar.markdown("---")

# ==========================================
# LOGIKA ROUTING HALAMAN
# ==========================================

if menu_terpilih == "🔄 Rekonsiliasi SIRUP & Realisasi":
  if tampilkan_menu_rekonsiliasi:
    tampilkan_menu_rekonsiliasi()
  else:
    st.error(
        "❌ Modul `rekonsiliasi.py` belum ditemukan atau gagal dimuat. Pastikan"
        " file `rekonsiliasi.py` sudah di-push ke repositori GitHub."
    )

elif menu_terpilih == "⚖️ Perbandingan OPD":
  if tampilkan_menu_perbandingan:
    tampilkan_menu_perbandingan()
  else:
    st.error(
        "❌ Modul `perbandingan.py` belum ditemukan atau gagal dimuat. Pastikan"
        " file `perbandingan.py` sudah di-push ke repositori GitHub."
    )

elif menu_terpilih == "📑 Ekstrak Laporan RUP":
  st.sidebar.header("📂 Unggah Berkas")
  st.sidebar.info("Unggah 1 berkas RUP untuk diekstrak.")
  uploaded_file = st.sidebar.file_uploader(
      "Unggah Data RUP (Excel/CSV)", type=["xlsx", "csv"]
  )

  if uploaded_file is not None:
    try:
      if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
      else:
        df = pd.read_excel(uploaded_file)

      nama_kolom_B = df.columns[1]
      nama_kolom_E = df.columns[4]

      peta_metode = {
          "e-purchasing": "E-Purchasing",
          "pengadaan langsung": "Pengadaan Langsung",
          "penunjukan langsung": "Penunjukan Langsung",
          "seleksi": "Seleksi",
          "tender": "Tender",
          "dikecualikan": "Dikecualikan",
      }
      metode_bersih = df[nama_kolom_E].astype(str).str.strip().str.lower()
      df["Kategori Final"] = metode_bersih.map(peta_metode).fillna("Swakelola")

      if tampilkan_menu_laporan:
        tampilkan_menu_laporan(df, nama_kolom_B, nama_kolom_E)
      else:
        st.error(
            "❌ Modul `laporan.py` tidak ditemukan. Tampilan laporan tidak dapat"
            " dimuat."
        )

    except Exception as e:
      st.error(f"Gagal memproses file RUP: {e}")
  else:
    st.title("📥 Ekstrak Laporan RUP Terfilter")
    st.info(
        "💡 Silakan unggah dokumen Berkas RUP terlebih dahulu pada bilah samping"
        " kiri."
    )
