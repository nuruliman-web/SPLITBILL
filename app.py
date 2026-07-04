import streamlit as st
import pandas as pd
from datetime import datetime
import time

# ============================================
# KONFIGURASI
# ============================================
st.set_page_config(
    page_title="💰 SplitBill",
    page_icon="💰",
    layout="wide"
)

# ============================================
# INISIALISASI SESSION STATE (Database Memory)
# ============================================
if 'orang' not in st.session_state:
    st.session_state.orang = [
        {'id': 1, 'nama': 'Adek'},
        {'id': 2, 'nama': 'Kamu'},
        {'id': 3, 'nama': 'Teman'}
    ]
    st.session_state.next_id_orang = 4

if 'transaksi' not in st.session_state:
    st.session_state.transaksi = []
    st.session_state.next_id_transaksi = 1

if 'last_split' not in st.session_state:
    st.session_state.last_split = None


# ============================================
# FUNGSI DATA
# ============================================
def get_orang():
    return st.session_state.orang

def get_orang_options():
    return {str(o['id']): o['nama'] for o in st.session_state.orang}

def tambah_orang(nama):
    if not nama or nama.strip() == '':
        return False
    st.session_state.orang.append({
        'id': st.session_state.next_id_orang,
        'nama': nama.strip()
    })
    st.session_state.next_id_orang += 1
    return True

def hapus_orang(id):
    st.session_state.orang = [o for o in st.session_state.orang if o['id'] != id]
    return True

def simpan_transaksi(data):
    trans_id = st.session_state.next_id_transaksi
    st.session_state.next_id_transaksi += 1
    
    transaksi = {
        'id': trans_id,
        'tanggal': data.get('tanggal', datetime.now().strftime('%Y-%m-%d')),
        'tempat': data.get('tempat', ''),
        'tax': data.get('tax', 0),
        'service': data.get('service', 0),
        'total': data.get('total', 0),
        'items': data.get('items', []),
        'created_at': datetime.now().isoformat()
    }
    st.session_state.transaksi.append(transaksi)
    return True

def get_transaksi():
    return st.session_state.transaksi


# ============================================
# UI HEADER
# ============================================
st.markdown("""
    <div style='background: linear-gradient(135deg, #1a237e, #0d47a1); padding: 20px; border-radius: 16px; text-align: center; margin-bottom: 20px;'>
        <h1 style='color: white; margin: 0; font-size: 28px;'>💰 SplitBill</h1>
        <p style='color: rgba(255,255,255,0.85); margin: 4px 0 0;'>Bagi tagihan bareng teman & keluarga</p>
    </div>
""", unsafe_allow_html=True)


# ============================================
# TABS
# ============================================
tab1, tab2, tab3 = st.tabs(["🧾 Split Bill", "👥 Kelola Orang", "📋 Riwayat"])


# ============================================
# TAB 1: SPLIT BILL
# ============================================
with tab1:
    st.subheader("🧾 Split Bill Baru")
    
    orang_list = get_orang()
    if not orang_list:
        st.warning("⚠️ Belum ada orang! Tambahkan di tab 👥 Kelola Orang")
    else:
        orang_options = get_orang_options()
        
        with st.form(key="split_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                tempat = st.text_input("📍 Tempat", placeholder="Warung Bakso...")
            with col2:
                tanggal = st.date_input("📅 Tanggal", datetime.now())
            
            st.markdown("---")
            st.markdown("### 📋 Item-item")
            
            # Jumlah item
            num_items = st.number_input("Jumlah item", min_value=1, max_value=10, value=2, step=1)
            
            items = []
            for i in range(int(num_items)):
                col_i1, col_i2, col_i3 = st.columns([2, 1.2, 1.2])
                with col_i1:
                    nama_item = st.text_input(f"Nama {i+1}", key=f"item_{i}", placeholder="Bakso, Es Teh...")
                with col_i2:
                    harga = st.number_input(f"Harga {i+1}", min_value=0, key=f"harga_{i}", step=1000, value=0)
                with col_i3:
                    pemilik = st.selectbox(
                        f"Milik {i+1}", 
                        options=list(orang_options.keys()),
                        format_func=lambda x: orang_options[x],
                        key=f"owner_{i}"
                    )
                
                if nama_item and harga > 0:
                    items.append({
                        'item': nama_item,
                        'harga': harga,
                        'orang_id': int(pemilik)
                    })
            
            st.markdown("---")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                tax = st.number_input("💰 Pajak (%)", min_value=0, value=11, step=1)
            with col_t2:
                service = st.number_input("💰 Service", min_value=0, value=0, step=1000)
            
            submitted = st.form_submit_button("📊 Hitung Split", use_container_width=True, type="primary")
        
        # ============================================
        # PROSES HITUNG
        # ============================================
        if submitted:
            if not items:
                st.error("❌ Minimal 1 item dengan harga > 0!")
            else:
                # Hitung total
                total_harga = sum(i['harga'] for i in items)
                total_tax = (total_harga * tax) / 100
                grand_total = total_harga + total_tax + service
                
                # Hitung per orang
                per_orang = {}
                for item in items:
                    nama = orang_options[str(item['orang_id'])]
                    per_orang[nama] = per_orang.get(nama, 0) + item['harga']
                
                # Tampilkan hasil
                st.divider()
                st.subheader("📊 Hasil Split")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                col_r1.metric("Total Harga", f"Rp {total_harga:,.0f}".replace(',', '.'))
                col_r2.metric(f"Tax ({tax}%)", f"Rp {total_tax:,.0f}".replace(',', '.'))
                col_r3.metric("Service", f"Rp {service:,.0f}".replace(',', '.'))
                
                st.metric("Grand Total", f"Rp {grand_total:,.0f}".replace(',', '.'), delta=None)
                
                # Tabel per orang
                st.markdown("##### 👤 Rincian per Orang")
                result_data = []
                for nama, total in per_orang.items():
                    proporsi = total / total_harga if total_harga > 0 else 0
                    tax_orang = total_tax * proporsi
                    service_orang = service * proporsi
                    result_data.append({
                        'Nama': nama,
                        'Item Total': f"Rp {total:,.0f}".replace(',', '.'),
                        'Tax': f"Rp {tax_orang:,.0f}".replace(',', '.'),
                        'Service': f"Rp {service_orang:,.0f}".replace(',', '.'),
                        'Total': f"Rp {(total + tax_orang + service_orang):,.0f}".replace(',', '.')
                    })
                
                st.dataframe(pd.DataFrame(result_data), use_container_width=True, hide_index=True)
                
                # Simpan data ke session untuk tombol simpan
                st.session_state.last_split = {
                    'items': items,
                    'total_harga': total_harga,
                    'total_tax': total_tax,
                    'service': service,
                    'grand_total': grand_total,
                    'tax': tax,
                    'tempat': tempat,
                    'tanggal': tanggal.strftime('%Y-%m-%d')
                }
                
                # Tombol simpan
                if st.button("💾 Simpan Transaksi", use_container_width=True, type="primary"):
                    if st.session_state.last_split:
                        split = st.session_state.last_split
                        items_data = []
                        for item in split['items']:
                            proporsi = item['harga'] / split['total_harga'] if split['total_harga'] > 0 else 0
                            items_data.append({
                                'orang_id': item['orang_id'],
                                'item': item['item'],
                                'harga': item['harga'],
                                'total_per_orang': item['harga'] + (split['total_tax'] * proporsi) + (split['service'] * proporsi)
                            })
                        
                        if simpan_transaksi({
                            'tanggal': split['tanggal'],
                            'tempat': split['tempat'],
                            'tax': split['tax'],
                            'service': split['service'],
                            'total': split['grand_total'],
                            'items': items_data
                        }):
                            st.success("✅ Transaksi berhasil disimpan!")
                            st.session_state.last_split = None
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("❌ Gagal menyimpan!")
                    else:
                        st.warning("⚠️ Hitung split dulu!")


# ============================================
# TAB 2: KELOLA ORANG
# ============================================
with tab2:
    st.subheader("👥 Kelola Orang")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### ➕ Tambah Orang")
            nama_baru = st.text_input("Nama orang baru", placeholder="Masukkan nama...", key="input_nama_baru")
            if st.button("➕ Tambah", use_container_width=True, type="primary"):
                if tambah_orang(nama_baru):
                    st.success(f"✅ {nama_baru} berhasil ditambahkan!")
                    st.rerun()
                else:
                    st.error("❌ Nama tidak boleh kosong!")
    
    with col2:
        with st.container(border=True):
            st.markdown("#### 🗑️ Hapus Orang")
            orang_list = get_orang()
            if orang_list:
                orang_options = {str(o['id']): o['nama'] for o in orang_list}
                hapus_id = st.selectbox(
                    "Pilih orang",
                    options=list(orang_options.keys()),
                    format_func=lambda x: orang_options[x],
                    key="hapus_select"
                )
                if st.button("🗑️ Hapus", use_container_width=True):
                    if hapus_orang(int(hapus_id)):
                        st.success("✅ Berhasil dihapus!")
                        st.rerun()
            else:
                st.info("💡 Belum ada orang")
    
    st.divider()
    st.markdown("### 📋 Daftar Orang")
    orang_list = get_orang()
    if orang_list:
        for o in orang_list:
            st.markdown(f"👤 **{o['nama']}**")
    else:
        st.info("💡 Belum ada orang")


# ============================================
# TAB 3: RIWAYAT
# ============================================
with tab3:
    st.subheader("📊 Riwayat Transaksi")
    
    transaksi = get_transaksi()
    if not transaksi:
        st.info("💡 Belum ada transaksi")
    else:
        # Tampilkan dari yang terbaru
        for t in reversed(transaksi):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"**📅 {t['tanggal']} - {t['tempat']}**")
                    st.caption(f"Tax: {t['tax']}% | Service: Rp {t['service']:,.0f}".replace(',', '.'))
                with col2:
                    st.markdown(f"**Rp {t['total']:,.0f}**".replace(',', '.'), unsafe_allow_html=True)
                
                # Detail item
                if t.get('items'):
                    orang_map = {o['id']: o['nama'] for o in get_orang()}
                    for item in t['items']:
                        nama = orang_map.get(item['orang_id'], 'Unknown')
                        st.caption(f"  🛒 {item['item']} - Rp {item['harga']:,.0f} ({nama})".replace(',', '.'))


# ============================================
# FOOTER
# ============================================
st.divider()
st.caption("© 2026 SplitBill - Dibuat dengan ❤️")
