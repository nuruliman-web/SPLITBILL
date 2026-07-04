import streamlit as st
import pandas as pd

# ==============================================================================
# KONFIGURASI HALAMAN
# ==============================================================================
st.set_page_config(
    page_title="Split Bill Gasss",
    page_icon="💰",
    layout="centered"
)

# ==============================================================================
# CSS KUSTOM (POKOKNYA UNGU JADIIN PUTIH/MINIMALIS)
# ==============================================================================
st.markdown("""
<style>
    /* Mengubah background form dan container jadi transparan/bersih */
    div[data-testid="stForm"] {
        background: rgba(128, 128, 128, 0.05);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(128, 128, 128, 0.15);
    }
    div[data-testid="stContainer"] {
        background: rgba(128, 128, 128, 0.03);
        border-radius: 12px;
        padding: 12px 16px;
        border: 1px solid rgba(128, 128, 128, 0.1);
    }
    
    /* Memaksa Checkbox ke samping */
    [data-testid="stForm"] .stCheckbox {
        display: inline-block !important;
        width: auto !important;
        margin-right: 16px !important;
        margin-bottom: 4px !important;
    }
    .checkbox-group {
        display: block;
        width: 100%;
    }
    
    /* SAKLAR: Ubah Tombol Utama (Primary) dari Ungu Jadi Putih Elegan */
    .stButton button[kind="primary"] {
        background-color: #ffffff !important;
        color: #1e293b !important;
        border: 1px solid #cbd5e1 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #f8fafc !important;
        border-color: #94a3b8 !important;
    }
    
    /* Tombol Secondary biasa */
    .stButton button {
        border-radius: 12px !important;
        font-weight: 600 !important;
    }
    
    /* SAKLAR: Ubah Garis Pinggir Ungu/Indigo di Alert Box (st.info, st.success) jadi Putih/Abu Bersih */
    .stAlert {
        border-radius: 12px !important;
        border-left: 4px solid #cbd5e1 !important; /* Diubah dari ungu ke abu-abu putih */
        background-color: rgba(128, 128, 128, 0.05) !important;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HEADER
# ==============================================================================
st.markdown("""
<div style='text-align: center; padding: 8px 0 0 0;'>
    <h1 style='font-size: 26px; margin: 0;'>💰 Split Bill</h1>
    <p style='color: #94a3b8; font-size: 14px; margin: 0;'>Santai aja, urusan ngitung serahin ke sini</p>
</div>
""", unsafe_allow_html=True)

st.divider()

# ==============================================================================
# SESSION STATE
# ==============================================================================
if "daftar_teman" not in st.session_state:
    st.session_state.daftar_teman = []
if "pesanan" not in st.session_state:
    st.session_state.pesanan = []

# ==============================================================================
# 1. DAFTAR TEMAN
# ==============================================================================
st.markdown("<h4 style='margin:0;'>👥 Yang Ikut Makan</h4>", unsafe_allow_html=True)
st.write("")

teman_input = st.text_input(
    "Nama-namanya, pisahin pake koma ya",
    placeholder="contoh: agus, budi, citra",
    key="input_nama_teman",
    label_visibility="collapsed"
)

if st.button("Simpan Daftar Teman", type="primary", use_container_width=True):
    list_nama = [nama.strip() for nama in teman_input.split(",") if nama.strip()]
    if list_nama:
        st.session_state.daftar_teman = list_nama
        st.success(f"Berhasil nyimpen {len(list_nama)} orang!")
    else:
        st.error("Isi dulu namanya, jangan kosong!")

if st.session_state.daftar_teman:
    st.info("Yang ikut: " + ", ".join(st.session_state.daftar_teman))
else:
    st.warning("Belum ada teman nih, isi dulu ya")

# ==============================================================================
# 2. PESANAN
# ==============================================================================
st.divider()
st.markdown("<h4 style='margin:0;'>🍽️ Pesanan Apa Aja</h4>", unsafe_allow_html=True)
st.write("")

with st.form("form_tambah_item", clear_on_submit=True):
    nama_item = st.text_input("Nama menu", placeholder="nasgor, es teh, pisang goreng")

    harga_item = st.number_input(
        "Harga",
        min_value=0,
        step=1,
        value=None,
        placeholder="masukkan angka"
    )

    st.markdown("<p style='font-size: 14px; margin-bottom: 4px;'><b>Siapa yang pesan ini?</b></p>", unsafe_allow_html=True)

    siapa_makan = []
    if st.session_state.daftar_teman:
        st.markdown('<div class="checkbox-group">', unsafe_allow_html=True)
        for nama in st.session_state.daftar_teman:
            if st.checkbox(nama, key=f"cb_{nama}"):
                siapa_makan.append(nama)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("Belum ada teman, masukin dulu di bagian atas ya")

    st.write("")
    submit_button = st.form_submit_button(label="Tambah ke daftar", use_container_width=True)

if submit_button:
    if not st.session_state.daftar_teman:
        st.error("Simpen dulu daftar temannya!")
    elif not nama_item:
        st.error("Nama menu jangan dikosongin")
    elif harga_item is None or harga_item <= 0:
        st.error("Harganya harus lebih dari 0")
    elif not siapa_makan:
        st.error("Ceklis minimal satu nama")
    else:
        st.session_state.pesanan.append({
            "item": nama_item,
            "harga": int(harga_item),
            "dipesan_oleh": siapa_makan
        })
        st.rerun()

# Daftar pesanan
if st.session_state.pesanan:
    st.markdown("##### Daftar pesanan")
    for index, p in enumerate(st.session_state.pesanan):
        with st.container(border=True):
            col_a, col_b = st.columns([3, 1])
            with col_a:
                st.markdown(f"**{p['item']}**")
                st.caption(f"Rp {p['harga']:,} | yang pesan: {', '.join(p['dipesan_oleh'])}")
            with col_b:
                if st.button("Hapus", key=f"hapus_{index}"):
                    st.session_state.pesanan.pop(index)
                    st.rerun()

    if st.button("Hapus semua pesanan", type="secondary", use_container_width=True):
        st.session_state.pesanan = []
        st.rerun()

# ==============================================================================
# 3. PAJAK, SERVICE, DISKON
# ==============================================================================
st.divider()
st.markdown("<h4 style='margin:0;'>📊 Tambahan</h4>", unsafe_allow_html=True)
st.write("")

col_tax, col_service, col_discount = st.columns(3)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with col_discount:
    diskon_input = st.number_input(
        "Diskon (Rp)",
        min_value=0,
        value=None,
        step=1000,
        placeholder="0"
    )
    diskon_rp = int(diskon_input) if diskon_input is not None else 0

# ==============================================================================
# 4. HASIL AKHIR
# ==============================================================================
st.divider()
st.markdown("<h4 style='margin:0;'>🧾 Hasilnya</h4>", unsafe_allow_html=True)
st.write("")

if st.session_state.daftar_teman and st.session_state.pesanan:
    tagihan_per_orang = {nama: 0.0 for nama in st.session_state.daftar_teman}
    total_subtotal = 0

    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["dipesan_oleh"])
        total_subtotal += p["harga"]
        for orang in p["dipesan_oleh"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    nilai_pajak_rp = total_subtotal * (pajak_persen / 100)
    nilai_service_rp = total_subtotal * (service_persen / 100)
    total_akhir = total_subtotal + nilai_pajak_rp + nilai_service_rp - diskon_rp
    if total_akhir < 0:
        total_akhir = 0

    st.info(
        f"**Makanan:** Rp {total_subtotal:,.0f}\n\n"
        f"**Pajak ({pajak_persen}%):** Rp {nilai_pajak_rp:,.0f}\n\n"
        f"**Service ({service_persen}%):** Rp {nilai_service_rp:,.0f}\n\n"
        f"**Diskon:** -Rp {diskon_rp:,.0f}\n\n"
        f"**Total semua:** Rp {total_akhir:,.0f}"
    )

    data_final = []
    for orang, subtotal_orang in tagihan_per_orang.items():
        if total_subtotal > 0:
            proporsi = subtotal_orang / total_subtotal
            total_orang = subtotal_orang + (nilai_pajak_rp * proporsi) + (nilai_service_rp * proporsi) - (diskon_rp * proporsi)
        else:
            total_orang = 0
        data_final.append({
            "Nama": orang,
            "Total Bayar": f"Rp {max(0, round(total_orang)):,}"
        })

    df_final = pd.DataFrame(data_final)
    st.dataframe(df_final.set_index("Nama"), use_container_width=True)
else:
    st.info("Isi dulu daftar teman dan pesanan")

# ==============================================================================
# FOOTER
# ==============================================================================
st.divider()
st.caption("dibuat sambil ngopi ☕")
