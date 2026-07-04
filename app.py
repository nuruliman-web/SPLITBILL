import streamlit as st
import pandas as pd

# Set layout ke centered agar pas untuk rasio layar vertikal HP
st.set_page_config(page_title="Split Bill Apps", page_icon="💰", layout="centered")

# Judul menggunakan format Markdown standar agar adaptif mengikuti sistem (Dark/Light)
st.title("💰 Split Bill Gasss...")
st.caption("Input Aja Gak Usah Pusing Itung, Serahin ke AI")

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
st.markdown("<h4 style='margin:0;'>👥 Circle Member (Siapa Aja yang Ikut?)</h4>", unsafe_allow_html=True)

teman_input = st.text_input(
    "Masukin Nama Temen Lu (pisahkan make koma):", 
    placeholder="icha, kevin, aldi, nadia",
    key="input_nama_teman",
    label_visibility="collapsed"
)

if st.button("Lock Circle Member", type="primary", use_container_width=True):
    list_nama = [nama.strip() for nama in teman_input.split(",") if nama.strip()]
    
    if list_nama:
        st.session_state.daftar_teman = list_nama
        st.success(f"✅ Circle lu aman, ada {len(list_nama)} orang terdaftar!")
    else:
        st.error("❌ Duh beb, input nama temen lu yang bener dong!.")

# Tampilan "Teman aktif" yang adaptif
if st.session_state.daftar_teman:
    st.info(f"🎯 **Circle Member Ter-Update:** {', '.join(st.session_state.daftar_teman)}")
else:
    st.warning("⚠️ Circle lu masih kosong nih, buruan isi dulu!")


# ==============================================================================
# 2. INPUT ITEM PESANAN & FIX CHECKBOX HORIZONTAL
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>🍔 Spill Makanan / Minuman</h4>", unsafe_allow_html=True)

with st.form("form_tambah_item", clear_on_submit=True):
    nama_item = st.text_input("Nama Makanan Apa Minuman:", placeholder="Contoh: Ice Americano / Croissant")
    
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
    
    st.markdown("<p style='font-size: 14px; margin-bottom: 5px;'><b>Which is Siapa Aja yang Pesen?</b></p>", unsafe_allow_html=True)
    
    siapa_makan = []
    if st.session_state.daftar_teman:
        st.markdown('<div class="checkbox-group">', unsafe_allow_html=True)
        
        for nama in st.session_state.daftar_teman:
            if st.checkbox(nama, key=f"cb_{nama}"):
                siapa_makan.append(nama)
                
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.caption("⚠️ Buru-buru bener sis, masukin nama sirkel lu dulu di Langkah 1")
    
    st.write("") 
    submit_button = st.form_submit_button(label="➕ Add Item", use_container_width=True)

if submit_button:
    if not st.session_state.daftar_teman:
        st.error("❌ Save daftar sirkel lu dulu di langkah 1!")
    elif not nama_item:
        st.error("❌ Nama makanannya spill dulu kali!")
    elif harga_item is None or harga_item <= 0:
        st.error("❌ Gak ada yang gratis beb, harganya diisi ya!")
    elif not siapa_makan:
        st.error("❌ Siapa yang makan nih? Pilih minimal 1 orang!")
    else:
        st.session_state.pesanan.append({
            "item": nama_item,
            "harga": int(harga_item),
            "dipesan_oleh": siapa_makan
        })
        st.rerun()

# Tampilan Daftar Pesanan (Auto-Theme & Muncul Detail Nama Orang)
if st.session_state.pesanan:
    st.markdown("##### 📝 Order Summary (Double Check Ya!)")
    
    for index, p in enumerate(st.session_state.pesanan):
        with st.container(border=True):
            st.markdown(f"**{p['item']}**")
            st.markdown(f"Rp {p['harga']:,} || Split via: {', '.join(p['dipesan_oleh'])}")
            
            if st.button("Delete", key=f"hapus_{index}", type="secondary", use_container_width=True):
                st.session_state.pesanan.pop(index)
                st.rerun()
                
    st.write("") 
    if st.button("🚨 Reset All Orders", type="secondary", use_container_width=True):
        st.session_state.pesanan = []
        st.rerun()


# ==============================================================================
# 3. BIAYA TAMBAHAN & DISKON (DI-FIX AUTO CLEAR DI SINI)
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>📊 Tax, Service charge, & Discount</h4>", unsafe_allow_html=True)

col_tax, col_service, col_discount = st.columns(3)
with col_tax:
    pajak_persen = st.number_input("Tax (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with col_discount:
    diskon_input = st.number_input(
        "Discount (Rp)", 
        min_value=0, 
        value=None, 
        placeholder="0",
        step=1000
    )
    diskon_rp = int(diskon_input) if diskon_input is not None else 0


# ==============================================================================
# 4. PERHITUNGAN AKHIR (DI-FIX STRUK GABUNGAN TOTAL)
# ==============================================================================
st.markdown("---")
st.markdown("<h4 style='margin:0;'>🧾 Total Damage per Person (No Debat!)</h4>", unsafe_allow_html=True)
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

    # Menampilkan Gabungan Rincian Pajak, Service, Makanan, dan Diskon di Struk
    st.info(
        f"🍔 **Pure Subtotal (Food Only):** Rp {total_subtotal:,.0f}\n\n"
        f"📌 **Tax ({pajak_persen}%):** Rp {nilai_pajak_rp:,.0f}\n\n"
        f"⚡ **Service Charge ({service_persen}%):** Rp {nilai_service_rp:,.0f}\n\n"
        f"🎈 **Discount Voucher:** -Rp {diskon_rp:,.0f}\n"
        f"────────────────────────\n"
        f"💵 **TOTAL DAMAGE GABUNGAN:** Rp {total_akhir:,.0f}"
    )

    # Distribusi hitungan adil per orang
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
    st.info("Isi info circle sama list orderan lu dulu biar kelihatan bill-nya.")
