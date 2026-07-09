import streamlit as st
import pandas as pd

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Ekstrak Laporan RUP per OPD", page_icon="📥", layout="wide")

st.title("📥 Ekstrak Laporan RUP Terfilter & Tersortir")
st.write("Unggah data, filter berdasarkan OPD, pilih metode sortir, lalu unduh hasilnya secara instan.")

# 2. Upload Data RUP
uploaded_file = st.file_uploader("Unggah File Excel/CSV RUP Anda", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Membaca file data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Pemetaan Kolom Berdasarkan Posisi
        nama_kolom_B = df.columns[1]  # Kolom B: Nama OPD
        nama_kolom_E = df.columns[4]  # Kolom E: Metode Pengadaan
        
        # Standarisasi Kategori Metode Pemilihan
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
        
        # ==========================================
        # 3. SIDEBAR: FILTER & SORTIR OTOMATIS
        # ==========================================
        st.sidebar.header("⚙️ Pengaturan Laporan")
        
        # FITUR FILTER: Memilih satu, beberapa, atau semua OPD
        list_opd = sorted(df[nama_kolom_B].dropna().unique())
        pilihan_opd = st.sidebar.multiselect(
            "Pilih OPD yang Ingin Diekstrak:", 
            options=list_opd,
            placeholder="Menampilkan Semua OPD (Silakan pilih untuk memfilter)"
        )
        
        # FITUR SORTIR: Memilih basis pengurutan data
        opsi_sortir = st.sidebar.selectbox(
            "Sortir Urutan Tabel Berdasarkan:",
            options=[
                "Nama OPD (A ke Z)", 
                "Total Paket Terbanyak 🔥", 
                "Paket Penyedia Terbanyak", 
                "Paket Swakelola Terbanyak"
            ]
        )
        
        # Mengaplikasikan Filter OPD ke Data Mentah
        df_filtered = df.copy()
        if pilihan_opd:
            df_filtered = df_filtered[df_filtered[nama_kolom_B].isin(pilihan_opd)]

        # ==========================================
        # 4. PROSES PEMBUATAN TABEL REKAPITULASI
        # ==========================================
        rekap = pd.crosstab(df_filtered[nama_kolom_B], df_filtered['Kategori Final']).reset_index()
        rekap = rekap.rename(columns={nama_kolom_B: 'Nama OPD'})
        
        # Memastikan semua kolom standar audit tersedia
        kolom_penyedia = ["E-Purchasing", "Pengadaan Langsung", "Penunjukan Langsung", "Seleksi", "Tender", "Dikecualikan"]
        for col in kolom_penyedia + ["Swakelola"]:
            if col not in rekap.columns:
                rekap[col] = 0
                
        # Hitung akumulasi Total Penyedia dan Total Keseluruhan Paket
        rekap['Penyedia'] = rekap[kolom_penyedia].sum(axis=1)
        rekap['Total Paket'] = rekap['Penyedia'] + rekap['Swakelola']
        
        # ==========================================
        # 5. EKSEKUSI SORTIR (PENGURUTAN DATA)
        # ==========================================
        if opsi_sortir == "Nama OPD (A ke Z)":
            rekap = rekap.sort_values(by="Nama OPD", ascending=True)
        elif opsi_sortir == "Total Paket Terbanyak 🔥":
            rekap = rekap.sort_values(by="Total Paket", ascending=False)
        elif opsi_sortir == "Paket Penyedia Terbanyak":
            rekap = rekap.sort_values(by="Penyedia", ascending=False)
        elif opsi_sortir == "Paket Swakelola Terbanyak":
            rekap = rekap.sort_values(by="Swakelola", ascending=False)

        # Menyusun urutan kolom final laporan Anda
        urutan_kolom = [
            'Nama OPD', 'Penyedia', 'Swakelola', 
            'E-Purchasing', 'Pengadaan Langsung', 'Penunjukan Langsung', 
            'Seleksi', 'Tender', 'Dikecualikan', 'Total Paket'
        ]
        tabel_siap_cetak = rekap[urutan_kolom].copy()
        
        # Membuat penomoran urut otomatis (No) setelah data selesai disortir
        tabel_siap_cetak.insert(0, 'No', range(1, len(tabel_siap_cetak) + 1))

        # Menambahkan Baris "TOTAL KESELURUHAN" di bagian paling bawah laporan
        total_row = pd.DataFrame(tabel_siap_cetak.sum(numeric_only=True)).T
        total_row['No'] = ""
        total_row['Nama OPD'] = "TOTAL KESELURUHAN"
        laporan_final = pd.concat([tabel_siap_cetak, total_row], ignore_index=True)

        # ==========================================
        # 6. TAMPILAN & TOMBOL EKSTRAK LAPORAN
        # ==========================================
        st.subheader("📋 Preview Hasil Laporan")
        st.write(f"Menampilkan {len(tabel_siap_cetak)} Perangkat Daerah terpilih.")
        
        # Tampilkan tabel interaktif di browser
        st.dataframe(laporan_final, use_container_width=True, hide_index=True)
        
        # Tombol Sakti untuk Ekstrak / Download Hasil Laporan
        # Jika Anda memilih 3 OPD di sidebar, maka file CSV yang terdownload HANYA berisi 3 OPD tersebut beserta baris totalnya.
        csv_data = laporan_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Ekstrak & Unduh Laporan Terfilter (CSV)",
            data=csv_data,
            file_name="Laporan_Audit_RUP_Tersortir.csv",
            mime="text/csv",
            help="Klik di sini untuk mengunduh tabel di atas ke dalam format Excel/CSV"
        )

    except Exception as e:
        st.error(f"Terjadi kesalahan pemrosesan: {e}")
else:
    st.info("💡 Silakan unggah file data RUP Anda untuk mengaktifkan modul ekstrak laporan.")
