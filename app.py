import streamlit as st
import pandas as pd

st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

st.title("💰 Split Bill Calculator")
st.write("Aplikasi simpel untuk bagi rata tagihan makan atau belanja bareng temen!")

st.markdown("---")

# 1. Input Teman
st.subheader("👥 1. Siapa saja yang ikut?")
teman_input = st.text_input("Masukkan nama teman (pisahkan dengan koma):", "Budi, Andi, Cici")
daftar_teman = [nama.strip() for nama in teman_input.split(",") if nama.strip()]

# 2. Input Item Pesanan
st.subheader("🍔 2. Detail Pesanan & Siapa yang Makan")

if "pesanan" not in st.session_state:
    st.session_state.pesanan = []

with st.form("form_tambah_item"):
    col1, col2 = st.columns([2, 1])
    with col1:
        nama_item = st.text_input("Nama Makanan/Minuman:")
    with col2:
        harga_item = st.number_input("Harga (Rp):", min_value=0, step=1000)
    
    siapa_makan = st.multiselect("Siapa yang patungan untuk item ini?", options=daftar_teman)
    
    submit_button = st.form_submit_button(label="Tambah Item")

if submit_button and nama_item and harga_item > 0 and siapa_makan:
    st.session_state.pesanan.append({
        "item": nama_item,
        "harga": harga_item,
        "patungan": siapa_makan
    })
    st.success(f"Berhasil menambahkan {nama_item}!")

# Tampilkan tabel pesanan saat ini
if st.session_state.pesanan:
    st.write("### Daftar Pesanan Saat Ini:")
    df_tampil = pd.DataFrame(st.session_state.pesanan)
    st.dataframe(df_tampil, use_container_width=True)
    
    if st.button("🗑️ Reset Semua Pesanan"):
        st.session_state.pesanan = []
        st.rerun()

# 3. Pajak dan Service Charge
st.markdown("---")
st.subheader("📊 3. Biaya Tambahan (Opsional)")
col_tax, col_service = st.columns(2)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service Charge (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)

# 4. Perhitungan Akhir
st.markdown("---")
st.subheader("🧾 4. Total Tagihan Per Orang")

if st.session_state.pesanan:
    # Inisialisasi tagihan per orang
    tagihan_per_orang = {nama: 0.0 for nama in daftar_teman}
    total_subtotal = 0

    # Hitung biaya dasar per item
    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["patungan"])
        total_subtotal += p["harga"]
        for orang in p["patungan"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    # Hitung pengali untuk Pajak dan Service
    # Rumus umum: Total = Subtotal * (1 + %pajak + %service)
    faktor_tambahan = 1 + (pajak_persen / 100) + (service_persen / 100)
    
    total_akhir = total_subtotal * faktor_tambahan

    # Tampilkan Ringkasan Total
    st.info(f"**Subtotal:** Rp {total_subtotal:,.0f}  \n"
            f"**Total (+ Pajak & Service):** Rp {total_akhir:,.0f}")

    # Hitung final per orang setelah pajak & service
    data_final = []
    for orang, subtotal_orang in tagihan_per_orang.items():
        total_orang = subtotal_orang * faktor_tambahan
        data_final.append({
            "Nama Teman": orang,
            "Subtotal (Rp)": round(subtotal_orang),
            "Total Akhir (Rp)": round(total_orang)
        })

    df_final = pd.DataFrame(data_final)
    st.table(df_final.set_index("Nama Teman"))
else:
    st.info("Silahkan masukkan item pesanan terlebih dahulu untuk melihat hasil split bill.")
