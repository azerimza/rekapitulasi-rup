import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Konfigurasi Halaman
st.set_page_config(page_title="Rekap RUP per OPD", page_icon="📑", layout="wide")

st.title("📑 Tabel Rekapitulasi Paket RUP per OPD")
st.write("Aplikasi ini menghitung jumlah paket dan menyusunnya dalam format laporan standar audit.")

# 2. Upload Data RUP
uploaded_file = st.file_uploader("Unggah File Excel/CSV RUP Anda", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Membaca file data
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        
        # Validasi jumlah kolom
        if df.shape[1] < 5:
            st.error("Format tidak sesuai. File harus memiliki minimal sampai Kolom E.")
            st.stop()
            
        # Pemetaan Kolom
        nama_kolom_B = df.columns[1]  # Kolom B: Nama OPD
        nama_kolom_E = df.columns[4]  # Kolom E: Metode Pengadaan
        
        # ==========================================
        # 3. PROSES PEMETAAN KATEGORI (KOLOM E)
        # ==========================================
        # Dictionary pemetaan agar penamaan seragam
        peta_metode = {
            "e-purchasing": "E-Purchasing",
            "pengadaan langsung": "Pengadaan Langsung",
            "penunjukan langsung": "Penunjukan Langsung",
            "seleksi": "Seleksi",
            "tender": "Tender",
            "dikecualikan": "Dikecualikan"
        }
        
        # Bersihkan teks di Kolom E (ubah ke huruf kecil & hilangkan spasi lebih)
        metode_bersih = df[nama_kolom_E].astype(str).str.strip().str.lower()
        
        # Buat kolom baru: Jika ada di map, gunakan nama resminya. Jika tidak, "Swakelola".
        df['Kategori Final'] = metode_bersih.map(peta_metode).fillna("Swakelola")
        
        # ==========================================
        # 4. MEMBUAT TABEL REKAPITULASI SESUAI FORMAT
        # ==========================================
        # Hitung jumlah tiap kategori per OPD
        rekap = pd.crosstab(df[nama_kolom_B], df['Kategori Final']).reset_index()
        rekap = rekap.rename(columns={nama_kolom_B: 'Nama OPD'})
        
        # Daftar kolom metode penyedia yang WAJIB ada di tabel
        kolom_penyedia = [
            "E-Purchasing", "Pengadaan Langsung", "Penunjukan Langsung", 
            "Seleksi", "Tender", "Dikecualikan"
        ]
        
        # Antisipasi: Jika di data Excel tidak ada sama sekali paket "Tender" atau lainnya, 
        # Pandas tidak akan membuat kolomnya. Kita harus paksa buat kolom tersebut dengan isi angka 0.
        for col in kolom_penyedia + ["Swakelola"]:
            if col not in rekap.columns:
                rekap[col] = 0
                
        # Menghitung Total "Penyedia" (Gabungan dari semua kolom metode penyedia)
        rekap['Penyedia'] = rekap[kolom_penyedia].sum(axis=1)
        
        # Menambahkan nomor urut di paling depan
        rekap.insert(0, 'No', range(1, len(rekap) + 1))
        
        # Menyusun urutan kolom PERSIS seperti permintaan Anda
        urutan_kolom_final = [
            'No', 'Nama OPD', 'Penyedia', 'Swakelola', 
            'E-Purchasing', 'Pengadaan Langsung', 'Penunjukan Langsung', 
            'Seleksi', 'Tender', 'Dikecualikan'
        ]
        tabel_final = rekap[urutan_kolom_final]

        # Menambahkan Baris "TOTAL KESELURUHAN" di paling bawah
        total_row = pd.DataFrame(tabel_final.sum(numeric_only=True)).T
        total_row['No'] = ""
        total_row['Nama OPD'] = "TOTAL KESELURUHAN"
        tabel_final = pd.concat([tabel_final, total_row], ignore_index=True)

        # ==========================================
        # 5. MENAMPILKAN HASIL
        # ==========================================
        st.subheader("📋 Tabel Rekapitulasi Paket RUP")
        
        # Menampilkan tabel (sembunyikan index bawaan pandas agar nomor urut 'No' terlihat rapi)
        st.dataframe(tabel_final, use_container_width=True, hide_index=True)
        
        # Tombol Unduh
        csv_rekap = tabel_final.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Unduh Tabel Laporan (CSV)",
            data=csv_rekap,
            file_name="Laporan_RUP_OPD.csv",
            mime="text/csv"
        )
        
        # ==========================================
        # 6. GRAFIK (OPSIONAL)
        # ==========================================
        st.write("---")
        st.subheader("📈 Proporsi Penyedia vs Swakelola")
        # Kita ambil data sebelum baris total ditambahkan untuk grafik
        df_grafik = tabel_final[tabel_final['Nama OPD'] != 'TOTAL KESELURUHAN']
        
        fig = px.bar(
            df_grafik, 
            x='Nama OPD', 
            y=['Penyedia', 'Swakelola'],
            title="Perbandingan Jumlah Paket Penyedia vs Swakelola per OPD",
            labels={'value': 'Jumlah Paket', 'variable': 'Kategori Pengadaan'},
            barmode='group'
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Terjadi kegagalan saat memproses file Excel: {e}")
        st.info("💡 Pastikan baris pertama pada file Excel Anda adalah Judul Kolom dan datanya sesuai format.")
else:
    st.info("💡 Silakan unggah file Excel/CSV RUP Anda untuk menghasilkan tabel laporan.")
