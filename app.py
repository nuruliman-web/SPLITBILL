import streamlit as st
import pandas as pd

# Set layout ke centered agar pas untuk rasio layar vertikal HP
st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

# Judul menggunakan format Markdown standar agar adaptif mengikuti sistem (Dark/Light)
st.title("💰 Split Bill Gasss...")
st.caption("Input Aja Gak Usah Pusing Itung")

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
st.markdown("<h4 style='margin:0;'>👥 Siapa Aja Yang Ikut?</h4>", unsafe_allow_html=True)

teman_input = st.text_input(
    "Masukkan nama teman lu (pisahkan dengan koma):", 
    placeholder="Contoh: Monyet, Babi, Anjing",
    key="input_nama_teman",
    label_visibility="collapsed"
)

if st.button("💾 Simpan Daftar Teman", type="primary", use_container_width=True):
    list_nama = [nama.strip() for nama in teman_input.split(",") if nama.strip()]
    
    if list_nama:
        st.session_state.daftar_teman = list_nama
        st.success(f"✅ Berhasil menyimpan {len(list_nama)} teman!")
    else:
        st.error("❌ Input yang bener jing!.")

# Tampilan "Teman aktif" yang adaptif
if st.session_state.daftar_teman:
    st.info(f"🎯 **Ini yang Lu Ajak?** {', '.join(st.session_state.daftar_teman)}")
else:
    st.warning("⚠️ Input yang bener jing!")


# ==============================================================================
# 2. INPUT ITEM PESANAN & FIX CHECKBOX HORIZONTAL
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>🍔 Masukin Apa Aja yg Lu Makan</h4>", unsafe_allow_html=True)

with st.form("form_tambah_item", clear_on_submit=True):
    nama_item = st.text_input("Nama Makanan/Minuman:", placeholder="Contoh: Nasi Goreng")
    
    harga_item = st.number_input(
        "Harga (Rp):", 
        min_value=0, 
        step=1, 
        value=None, 
        placeholder="Masukkan harga angka saja"
    )
    
    # CSS kustom untuk memaksa checkbox bawaan Streamlit berjejer ke samping
    st.markdown(
        """
        <style>
        [data-testid="stForm"] .stCheckbox {
            display: inline-block !important;
            width: auto !important;
            margin-right: 15px !important;
            margin-bottom: 5px !important;
        }
        .checkbox-group {
            display: block;
            width: 100%;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )
    
    st.markdown("<p style='font-size: 14px; margin-bottom: 5px;'><b>Siapa Aja yang Pesen?:</b></p>", unsafe_allow_html=True)
    
    siapa_makan = []
    if st.session_state.daftar_teman:
        st.markdown('<div class="checkbox-group">', unsafe_allow_html=True)
        
        for nama in st.session_state.daftar_teman:
            if st.checkbox(nama, key=f"cb_{nama}"):
                siapa_makan.append(nama)
                
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("⚠️ Belum ada nama teman. Isi dulu di langkah 1 ya!")
    
    st.write("") 
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
            "dipesan_oleh": siapa_makan
        })
        st.rerun()

# Tampilan Daftar Pesanan (Auto-Theme & Muncul Detail Nama Orang)
if st.session_state.pesanan:
    st.markdown("##### 📝 Ini Rekap Makan Lu, Udah Bener?")
    
    for index, p in enumerate(st.session_state.pesanan):
        with st.container(border=True):
            st.markdown(f"**{p['item']}**")
            st.markdown(f"Rp {p['harga']:,} ||  Dipesan Oleh: {', '.join(p['dipesan_oleh'])}")
            
            if st.button("Hapus", key=f"hapus_{index}", type="secondary", use_container_width=True):
                st.session_state.pesanan.pop(index)
                st.rerun()
                
    st.write("") 
    if st.button("🚨 Reset Semua Pesanan", type="secondary", use_container_width=True):
        st.session_state.pesanan = []
        st.rerun()


# ==============================================================================
# 3. BIAYA TAMBAHAN & DISKON (DI-FIX AUTO CLEAR DI SINI)
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>📊 Ada Pajak Apa Diskon Gak?</h4>", unsafe_allow_html=True)

col_tax, col_service, col_discount = st.columns(3)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with col_discount:
    # DI-FIX: Diberi value=None dan placeholder agar langsung bersih/kosong saat diklik di HP
    diskon_input = st.number_input(
        "Diskon (Rp)", 
        min_value=0, 
        value=None, 
        step=1000, 
        placeholder="0"
    )
    # Jika isinya kosong/None, otomatis dianggap Rp 0 oleh sistem hitung
    diskon_rp = int(diskon_input) if diskon_input is not None else 0


# ==============================================================================
# 4. PERHITUNGAN AKHIR (DI-FIX STRUK GABUNGAN TOTAL)
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>🧾 Bayarnya Segini Ya Cek Nama Lu!</h4>", unsafe_allow_html=True)
st.write("")

if st.session_state.daftar_teman and st.session_state.pesanan:
    tagihan_per_orang = {nama: 0.0 for nama in st.session_state.daftar_teman}
    total_subtotal = 0

    # Hitung harga dasar makanan
    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["dipesan_oleh"])
        total_subtotal += p["harga"]
        for orang in p["dipesan_oleh"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    # Hitung nilai nominal Rp dari pajak dan service charge
    nilai_pajak_rp = total_subtotal * (pajak_persen / 100)
    nilai_service_rp = total_subtotal * (service_persen / 100)
    
    # Total gabungan matematika utuh
    total_akhir = total_subtotal + nilai_pajak_rp + nilai_service_rp - diskon_rp
    if total_akhir < 0: 
        total_akhir = 0

    # DI-FIX: Menampilkan Gabungan Rincian Pajak, Service, Makanan, dan Diskon di Struk
    st.info(
        f"🍔 **Harga Makanan (Subtotal):** Rp {total_subtotal:,.0f}\n\n"
        f"📌 **Pajak ({pajak_persen}%):** Rp {nilai_pajak_rp:,.0f}\n\n"
        f"⚡ **Service Charge ({service_persen}%):** Rp {nilai_service_rp:,.0f}\n\n"
        f"🎈 **Diskon Nota:** -Rp {diskon_rp:,.0f}\n"
        f"────────────────────────\n"
        f"💵 **TOTAL AKHIR GABUNGAN:** Rp {total_akhir:,.0f}"
    )

    # Distribusi hitungan adil per orang
    data_final = []
    for orang, subtotal_orang in tagihan_per_orang.items():
        if total_subtotal > 0:
            proporsi = subtotal_orang / total_subtotal
            # Tiap orang nanggung pajak/service dan dapet potongan diskon sesuai proporsi makannya sendiri
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
    st.info("Isi daftar teman dan pesanan untuk melihat hasil.")
