import streamlit as st
import pandas as pd
import plotly.express as px

def tampilkan_menu_perbandingan(df, nama_kolom_B, nama_kolom_E):
    st.title("⚖️ Komparasi Strategi Pengadaan antar OPD")
    st.write("Bandingkan volume dan karakteristik 6 metode pemilihan serta Swakelola antar perangkat daerah secara langsung.")
    
    st.sidebar.header("⚙️ Pengaturan Komparasi")
    list_opd = sorted(df[nama_kolom_B].dropna().unique())
    
    # Pilihan OPD untuk dibandingan
    opd_komparasi = st.sidebar.multiselect(
        "Pilih OPD untuk Dibandingkan (Min. 2):", 
        options=list_opd,
        default=list_opd[:2] if len(list_opd) >= 2 else list_opd
    )
    
    if len(opd_komparasi) >= 2:
        # Filter data
        df_komparasi = df[df[nama_kolom_B].isin(opd_komparasi)]
        
        # --- MENYIAPKAN STANDAR KOLOM METODE ---
        daftar_metode = [
            "E-Purchasing", "Pengadaan Langsung", "Penunjukan Langsung", 
            "Seleksi", "Tender", "Dikecualikan", "Swakelola"
        ]
        
        # Tabel matriks dasar
        tabel_komparasi = pd.crosstab(df_komparasi[nama_kolom_B], df_komparasi['Kategori Final']).reset_index()
        tabel_komparasi = tabel_komparasi.rename(columns={nama_kolom_B: 'Nama OPD'})
        
        # Memaksa semua kolom metode ada di tabel (meskipun nilainya 0) agar seragam
        for metode in daftar_metode:
            if metode not in tabel_komparasi.columns:
                tabel_komparasi[metode] = 0
                
        # Menyusun urutan kolom agar rapi dan baku
        urutan_kolom = ['Nama OPD'] + daftar_metode
        tabel_komparasi = tabel_komparasi[urutan_kolom]
        
        # --- VISUALISASI GRAFIK ---
        st.subheader("📈 Grafik Perbandingan Metode Pengadaan")
        
        # Menghitung agregat untuk grafik
        df_melted = df_komparasi.groupby([nama_kolom_B, 'Kategori Final']).size().reset_index(name='Jumlah Paket')
        
        # Membuat Grafik Batang Interaktif
        fig = px.bar(
            df_melted, 
            x='Kategori Final', 
            y='Jumlah Paket', 
            color=nama_kolom_B, 
            barmode='group',
            category_orders={"Kategori Final": daftar_metode}, # Memaksa urutan di sumbu X konsisten
            labels={
                'Jumlah Paket': 'Volume Paket', 
                'Kategori Final': 'Metode Pemilihan', 
                nama_kolom_B: 'Perangkat Daerah'
            },
            title="Komparasi Head-to-Head (Rincian Metode)"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # --- TABEL DATA MATRIKS ---
        st.subheader("📊 Matriks Data Komparasi")
        st.dataframe(tabel_komparasi, use_container_width=True, hide_index=True)
        
    else:
        st.warning("⚠️ Silakan pilih minimal 2 Perangkat Daerah di panel sebelah kiri untuk melihat perbandingan.")
