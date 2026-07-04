import streamlit as st
import pandas as pd

st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

st.title("💰 Split Bill Calculator")
st.write("Aplikasi simpel untuk bagi rata tagihan makan atau belanja bareng temen!")

st.markdown("---")

# Inisialisasi session state jika belum ada
if "daftar_teman" not in st.session_state:
    st.session_state.daftar_teman = []
if "pesanan" not in st.session_state:
    st.session_state.pesanan = []

# ==============================================================================
# 1. Input Teman (Dengan Tombol Simpan)
# ==============================================================================
st.subheader("👥 1. Siapa saja yang ikut?")

# Nilai default di text_input diambil dari session_state jika sudah pernah disimpan
nama_default = ", ".join(st.session_state.daftar_teman) if st.session_state.daftar_teman else "Budi, Andi, Cici"
teman_input = st.text_input("Masukkan nama teman (pisahkan dengan koma):", value=nama_default)

if st.button("💾 Simpan Daftar Teman"):
    # Memproses input teks menjadi list nama
    list_nama = [nama.strip() for nama in teman_input.split(",") if nama.strip()]
    
    if list_nama:
        st.session_state.daftar_teman = list_nama
        st.success(f"✅ Berhasil menyimpan {len(list_nama)} teman!")
    else:
        st.error("❌ Gagal menyimpan! Harap masukkan minimal satu nama teman.")

# Tampilkan status teman saat ini
if st.session_state.daftar_teman:
    st.caption(f"Teman aktif saat ini: {', '.join(st.session_state.daftar_teman)}")
else:
    st.warning("⚠️ Belum ada teman yang disimpan. Silakan klik tombol 'Simpan Daftar Teman' terlebih dahulu.")


# ==============================================================================
# 2. Input Item Pesanan & Hapus Item Spesifik
# ==============================================================================
st.markdown("---")
st.subheader("🍔 2. Detail Pesanan & Siapa yang Makan")

with st.form("form_tambah_item"):
    col1, col2 = st.columns([2, 1])
    with col1:
        nama_item = st.text_input("Nama Makanan/Minuman:")
    with col2:
        harga_item = st.number_input("Harga (Rp):", min_value=0, step=1000)
    
    # Menggunakan daftar_teman dari session_state
    siapa_makan = st.multiselect(
        "Siapa yang patungan untuk item ini?", 
        options=st.session_state.daftar_teman
    )
    
    submit_button = st.form_submit_button(label="Tambah Item")

if submit_button:
    if not st.session_state.daftar_teman:
        st.error("❌ Gagal! Anda harus menyimpan daftar teman terlebih dahulu di langkah 1.")
    elif not nama_item:
        st.error("❌ Gagal! Nama makanan/minuman tidak boleh kosong.")
    elif harga_item <= 0:
        st.error("❌ Gagal! Harga harus lebih dari Rp 0.")
    elif not siapa_makan:
        st.error("❌ Gagal! Pilih minimal satu orang yang patungan.")
    else:
        st.session_state.pesanan.append({
            "item": nama_item,
            "harga": harga_item,
            "patungan": siapa_makan
        })
        st.success(f"✅ Berhasil menambahkan {nama_item}!")
        st.rerun()

# Tampilkan tabel pesanan & Fitur Hapus Per Item
if st.session_state.pesanan:
    st.write("### Daftar Pesanan Saat Ini:")
    
    # Loop untuk menampilkan setiap item beserta tombol hapus di sampingnya
    for index, p in enumerate(st.session_state.pesanan):
        col_item, col_aksi = st.columns([5, 1])
        with col_item:
            st.write(f"**{p['item']}** - Rp {p['harga']:,} (Patungan: {', '.join(p['patungan'])})")
        with col_aksi:
            # Membuat tombol hapus unik menggunakan index
            if st.button("🗑️ Hapus", key=f"hapus_{index}"):
                st.session_state.pesanan.pop(index)
                st.success(f"Item berhasil dihapus!")
                st.rerun()
                
    st.write("") # Spasi tambahan
    if st.button("🚨 Reset Semua Pesanan", type="secondary"):
        st.session_state.pesanan = []
        st.rerun()


# ==============================================================================
# 3. Pajak dan Service Charge
# ==============================================================================
st.markdown("---")
st.subheader("📊 3. Biaya Tambahan (Opsional)")
col_tax, col_service = st.columns(2)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service Charge (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)


# ==============================================================================
# 4. Perhitungan Akhir
# ==============================================================================
st.markdown("---")
st.subheader("🧾 4. Total Tagihan Per Orang")

if st.session_state.daftar_teman and st.session_state.pesanan:
    # Inisialisasi tagihan per orang berdasarkan daftar teman yang disimpan
    tagihan_per_orang = {nama: 0.0 for nama in st.session_state.daftar_teman}
    total_subtotal = 0

    # Hitung biaya dasar per item
    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["patungan"])
        total_subtotal += p["harga"]
        for orang in p["patungan"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    # Hitung pengali untuk Pajak dan Service
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
    st.info("Silakan simpan daftar teman dan masukkan item pesanan untuk melihat hasil perhitungan.")
