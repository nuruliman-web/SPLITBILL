import streamlit as st
import pandas as pd

# Set layout ke centered agar pas untuk rasio layar vertikal HP
st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

# Judul utama kustom HP
st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>💰 Split Bill Calculator</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-size: 14px; color: gray;'>Bagi rata tagihan bareng temen langsung dari HP!</p>", unsafe_allow_html=True)

st.markdown("---")

# ==============================================================================
# INISIALISASI MEMORI (SESSION STATE)
# ==============================================================================
if "daftar_teman" not in st.session_state:
    st.session_state.daftar_teman = []
if "pesanan" not in st.session_state:
    st.session_state.pesanan = []

# ==============================================================================
# 1. INPUT TEMAN
# ==============================================================================
st.markdown("### 👥 1. Siapa saja yang ikut?")

teman_input = st.text_input(
    "Masukkan nama teman (pisahkan dengan koma):", 
    placeholder="Contoh: Budi, Andi, Cici",
    key="input_nama_teman"
)

if st.button("💾 Simpan Daftar Teman", type="primary", use_container_width=True):
    list_nama = [nama.strip() for nama in teman_input.split(",") if nama.strip()]
    
    if list_nama:
        st.session_state.daftar_teman = list_nama
        st.success(f"✅ Berhasil menyimpan {len(list_nama)} teman!")
    else:
        st.error("❌ Gagal menyimpan! Harap masukkan minimal satu nama teman.")

# TINGKATKAN: Teks "Teman aktif" diubah menjadi warna Hitam Pekat (#000000)
if st.session_state.daftar_teman:
    st.markdown(
        f"<div style='font-size: 14px; background-color: #f1f3f4; padding: 10px; border-radius: 5px; margin-top: 5px; border-left: 5px solid #5f6368; color: #000000; font-weight: 500;'>"
        f"🎯 Teman aktif: {', '.join(st.session_state.daftar_teman)}"
        f"</div>", 
        unsafe_allow_html=True
    )
else:
    st.warning("⚠️ Belum ada teman yang disimpan. Ketik nama di atas lalu klik tombol Simpan.")


# ==============================================================================
# 2. INPUT ITEM PESANAN
# ==============================================================================
st.markdown("---")
st.markdown("### 🍔 2. Detail Pesanan")

with st.form("form_tambah_item", clear_on_submit=True):
    nama_item = st.text_input("Nama Makanan/Minuman:", placeholder="Contoh: Nasi Goreng")
    
    # TINGKATKAN: Menggunakan step=1 dan nilai int agar keyboard HP otomatis memunculkan Numpad/Angka saja
    harga_item = st.number_input(
        "Harga (Rp):", 
        min_value=0, 
        step=1, 
        value=None, 
        placeholder="Masukkan harga angka saja"
    )
    
    siapa_makan = st.multiselect(
        "Dipesan oleh:", 
        options=st.session_state.daftar_teman
    )
    
    submit_button = st.form_submit_button(label="➕ Tambah Item", use_container_width=True)

if submit_button:
    if not st.session_state.daftar_teman:
        st.error("❌ Simpan daftar teman dulu di langkah 1!")
    elif not nama_item:
        st.error("❌ Nama item tidak boleh kosong!")
    elif harga_item is None or harga_item <= 0:
        st.error("❌ Harga harus lebih dari Rp 0!")
    elif not siapa_makan:
        st.error("❌ Pilih minimal satu orang!")
    else:
        st.session_state.pesanan.append({
            "item": nama_item,
            "harga": int(harga_item), # Memastikan disimpan sebagai angka bulat
            "patungan": siapa_makan
        })
        st.rerun()

# Tampilkan list pesanan
if st.session_state.pesanan:
    st.markdown("#### 📝 Daftar Pesanan Saat Ini:")
    
    for index, p in enumerate(st.session_state.pesanan):
        with st.container(border=True):
            st.markdown(f"<p style='margin:0; font-size:14px; color:#000000;'><b>{p['item']}</b></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='margin:0; font-size:13px; color:#5f6368;'>Rp {p['harga']:,} • Oleh: {', '.join(p['patungan'])}</p>", unsafe_allow_html=True)
            if st.button("🗑️ Hapus", key=f"hapus_{index}", type="secondary", use_container_width=True):
                st.session_state.pesanan.pop(index)
                st.rerun()
                
    st.write("") 
    if st.button("🚨 Reset Semua Pesanan", type="secondary", use_container_width=True):
        st.session_state.pesanan = []
        st.rerun()


# ==============================================================================
# 3. BIAYA TAMBAHAN
# ==============================================================================
st.markdown("---")
st.markdown("### 📊 3. Biaya Tambahan")
col_tax, col_service = st.columns(2)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)


# ==============================================================================
# 4. PERHITUNGAN AKHIR
# ==============================================================================
st.markdown("---")
st.markdown("### 🧾 4. Total Tagihan Per Orang")

if st.session_state.daftar_teman and st.session_state.pesanan:
    tagihan_per_orang = {nama: 0.0 for nama in st.session_state.daftar_teman}
    total_subtotal = 0

    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["patungan"])
        total_subtotal += p["harga"]
        for orang in p["patungan"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    faktor_tambahan = 1 + (pajak_persen / 100) + (service_persen / 100)
    total_akhir = total_subtotal * faktor_tambahan

    st.info(f"**Subtotal:** Rp {total_subtotal:,.0f}\n\n**Total Akhir (+ Pajak & Service):** Rp {total_akhir:,.0f}")

    data_final = []
    for orang, subtotal_orang in tagihan_per_orang.items():
        total_orang = subtotal_orang * faktor_tambahan
        data_final.append({
            "Nama": orang,
            "Total Bayar": f"Rp {round(total_orang):,}"
        })

    df_final = pd.DataFrame(data_final)
    st.dataframe(df_final.set_index("Nama"), use_container_width=True)
else:
    st.info("Isi daftar teman dan pesanan untuk melihat hasil.")
