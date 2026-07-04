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
# Menggunakan HTML Font-size agar ukuran teks tidak kebesaran di HP (1 baris)
st.markdown("<h4 style='margin:0;'>👥 Siapa Aja Yang Ikut?</h4>", unsafe_allow_html=True)

teman_input = st.text_input(
    "Masukkan nama teman lu (pisahkan dengan koma):", 
    placeholder="Contoh: Monyet, Babi, Anjing",
    key="input_nama_teman",
    label_visibility="collapsed" # Menyembunyikan label bawaan agar hemat tempat
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
    
    # Keyboard HP angka saja (step=1)
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
        
        # Buat checkbox untuk masing-masing nama teman
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
# 3. BIAYA TAMBAHAN & DISKON (Dipecah Jadi 3 Kolom)
# ==============================================================================
st.markdown("---")
# Ukuran font dikecilkan sedikit agar muat 1 baris di HP
st.markdown("<h4 style='margin:0;'>📊 Ada Pajak Apa Diskon Gak?</h4>", unsafe_allow_html=True)

# Memisahkan input menjadi 3 kolom agar rapi menyamping di tablet/HP
col_tax, col_service, col_discount = st.columns(3)
with col_tax:
    pajak_persen = st.number_input("Pajak (%)", min_value=0.0, max_value=100.0, value=10.0, step=0.5)
with col_service:
    service_persen = st.number_input("Service (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.5)
with col_discount:
    # Menggunakan nominal Rupiah langsung karena lebih sering ditemui di nota diskon makan
    diskon_rp = st.number_input("Diskon (Rp)", min_value=0, value=0, step=1000)


# ==============================================================================
# 4. PERHITUNGAN AKHIR
# ==============================================================================
st.markdown("---")
# Judul ini dipastikan berukuran pas di HP agar tidak patah ke bawah
st.markdown("<h4 style='margin:0;'>🧾 Bayarnya Segini Ya Cek Nama Lu!</h4>", unsafe_allow_html=True)
st.write("")

if st.session_state.daftar_teman and st.session_state.pesanan:
    tagihan_per_orang = {nama: 0.0 for nama in st.session_state.daftar_teman}
    total_subtotal = 0

    # Menghitung subtotal dasar dari pesanan makanan
    for p in st.session_state.pesanan:
        harga_per_orang = p["harga"] / len(p["dipesan_oleh"])
        total_subtotal += p["harga"]
        for orang in p["dipesan_oleh"]:
            if orang in tagihan_per_orang:
                tagihan_per_orang[orang] += harga_per_orang

    # Hitung nilai pajak dan service dari subtotal bersih
    nilai_pajak = total_subtotal * (pajak_persen / 100)
    nilai_service = total_subtotal * (service_persen / 100)
    
    # Total akhir = Subtotal + Pajak + Service - Diskon
    total_akhir = total_subtotal + nilai_pajak + nilai_service - diskon_rp
    if total_akhir < 0: 
        total_akhir = 0 # Proteksi jika diskon lebih besar dari tagihan

    # Tampilkan kotak ringkasan struk belanja
    st.info(
        f"**Subtotal:** Rp {total_subtotal:,.0f}\n\n"
        f"**Diskon:** -Rp {diskon_rp:,.0f}\n\n"
        f"**Total Akhir (+ Pajak & Service):** Rp {total_akhir:,.0f}"
    )

    # Bagi beban pajak, service, dan diskon secara proporsional ke setiap orang
    data_final = []
    for orang, subtotal_orang in tagihan_per_orang.items():
        if total_subtotal > 0:
            # Rasio kontribusi belanjaan orang tersebut terhadap total meja
            proporsi = subtotal_orang / total_subtotal
            # Orang tersebut mendapat beban pajak & potongan diskon sesuai apa yang dia makan
            total_orang = subtotal_orang + (nilai_pajak * proporsi) + (nilai_service * proporsi) - (diskon_rp * proporsi)
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
