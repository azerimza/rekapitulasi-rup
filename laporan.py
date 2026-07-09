import streamlit as st
import pandas as pd

def tampilkan_menu_laporan(df, nama_kolom_B, nama_kolom_E):
    st.title("📥 Ekstrak Laporan RUP Terfilter")
    st.write("Silakan gunakan filter di bilah samping untuk menyaring dan menyortir laporan.")
    
    # --- FILTER & SORTIR ---
    st.sidebar.header("⚙️ Pengaturan Ekstrak")
    list_opd = sorted(df[nama_kolom_B].dropna().unique())
    pilihan_opd = st.sidebar.multiselect("Pilih OPD:", options=list_opd, placeholder="Semua OPD")
    opsi_sortir = st.sidebar.selectbox("Sortir Berdasarkan:", [
        "Nama OPD (A ke Z)", 
        "Total Paket Terbanyak 🔥", 
        "Paket Penyedia Terbanyak", 
        "Paket Swakelola Terbanyak"
    ])
    
    # Aplikasi Filter
    df_filtered = df.copy()
    if pilihan_opd:
        df_filtered = df_filtered[df_filtered[nama_kolom_B].isin(pilihan_opd)]

    # --- HITUNG REKAPITULASI ---
    rekap = pd.crosstab(df_filtered[nama_kolom_B], df_filtered['Kategori Final']).reset_index()
    rekap = rekap.rename(columns={nama_kolom_B: 'Nama OPD'})
    
    kolom_penyedia = ["E-Purchasing", "Pengadaan Langsung", "Penunjukan Langsung", "Seleksi", "Tender", "Dikecualikan"]
    for col in kolom_penyedia + ["Swakelola"]:
        if col not in rekap.columns:
            rekap[col] = 0
            
    rekap['Penyedia'] = rekap[kolom_penyedia].sum(axis=1)
    rekap['Total Paket'] = rekap['Penyedia'] + rekap['Swakelola']
    
    # Aplikasi Sortir
    if opsi_sortir == "Nama OPD (A ke Z)":
        rekap = rekap.sort_values(by="Nama OPD", ascending=True)
    elif opsi_sortir == "Total Paket Terbanyak 🔥":
        rekap = rekap.sort_values(by="Total Paket", ascending=False)
    elif opsi_sortir == "Paket Penyedia Terbanyak":
        rekap = rekap.sort_values(by="Penyedia", ascending=False)
    elif opsi_sortir == "Paket Swakelola Terbanyak":
        rekap = rekap.sort_values(by="Swakelola", ascending=False)

    # Susun Kolom Akhir
    urutan_kolom = ['Nama OPD', 'Penyedia', 'Swakelola', 'E-Purchasing', 'Pengadaan Langsung', 'Penunjukan Langsung', 'Seleksi', 'Tender', 'Dikecualikan', 'Total Paket']
    tabel_siap_cetak = rekap[urutan_kolom].copy()
    tabel_siap_cetak.insert(0, 'No', range(1, len(tabel_siap_cetak) + 1))

    # Tambah Baris Total Keseluruhan
    total_row = pd.DataFrame(tabel_siap_cetak.sum(numeric_only=True)).T
    total_row['No'] = ""
    total_row['Nama OPD'] = "TOTAL KESELURUHAN"
    laporan_final = pd.concat([tabel_siap_cetak, total_row], ignore_index=True)

    # Tampilkan Tabel
    st.dataframe(laporan_final, use_container_width=True, hide_index=True)
    
    # Tombol Download
    st.download_button(
        label="📥 Ekstrak & Unduh Laporan (CSV)", 
        data=laporan_final.to_csv(index=False).encode('utf-8'), 
        file_name="Laporan_Audit_RUP.csv", 
        mime="text/csv"
    )
