import streamlit as st
import pandas as pd

# Set layout ke centered agar pas untuk rasio layar vertikal HP
st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

# Judul menggunakan format Markdown standar agar warnanya adaptif mengikuti sistem (Dark/Light)
st.title("💰 Split Bill Calculator")
st.caption("Bagi rata tagihan bareng temen langsung dari HP!")

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

# Tampilan "Teman aktif" yang adaptif mengikuti tema layar HP/Laptop
if st.session_state.daftar_teman:
    # Menggunakan st.info agar background dan warna teksnya otomatis menyesuaikan dark/light mode sistem
    st.info(f"🎯 **Teman aktif:** {', '.join(st.session_state.daftar_teman)}")
else:
    st.warning("⚠️ Belum ada teman yang disimpan. Ketik nama di atas lalu klik tombol Simpan.")


# ==============================================================================
# 2. INPUT ITEM PESANAN (Menggunakan Checkbox Pengganti Dropdown)
# ==============================================================================
st.markdown("---")
st.markdown("### 🍔 2. Detail Pesanan")

with st.form("form_tambah_item", clear_on_submit=True):
    nama_item = st.text_input("Nama Makanan/Minuman:", placeholder="Contoh: Nasi Goreng")
    
    harga_item = st.number_input(
        "Harga (Rp):", 
        min_value=0, 
        step=1, 
        value=None, 
        placeholder="Masukkan harga angka saja"
    )
    
    # --- PENGGANTI DROPDOWN: Checkbox Sesuai Nama Orang ---
    st.markdown("<p style='font-size: 14px; margin-bottom: 5px;'><b>Dipesan oleh:</b></p>", unsafe_allow_html=True)
    
    siapa_makan = []
    if st.session_state.daftar_teman:
        # Membuat baris horizontal untuk nama-nama teman di HP
        cols = st.columns(len(st.session_state.daftar_teman))
        for idx, nama in enumerate(st.session_state.daftar_teman):
            with cols[idx]:
                # Jika dicentang, nama teman akan dimasukkan ke dalam list siapa_makan
                if st.checkbox(nama, key=f"cb_{nama}"):
                    siapa_makan.append(nama)
    else:
        st.caption("⚠️ Belum ada nama teman. Isi dulu di langkah 1 ya!")
    # -----------------------------------------------------
    
    st.write("") # Spasi pemisah
    submit_button = st.form_submit_button(label="➕ Tambah Item", use_container_width=True)

if submit_button:
    if not st.session_state.daftar_teman:
        st.error("❌ Simpan daftar teman dulu di langkah 1!")
    elif not nama_item:
        st.error("❌ Nama item tidak boleh kosong!")
    elif harga_item is None or harga_item <= 0:
        st.error("❌ Harga harus lebih dari Rp 0!")
    elif not siapa_makan:
        st.error("❌ Pilih minimal satu orang yang memesan!")
    else:
        st.session_state.pesanan.append({
            "item": nama_item,
            "harga": int(harga_item),
            "patungan": siapa_makan
        })
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
