import streamlit as st
import pandas as pd
from datetime import datetime

# ============================================
# KONFIGURASI
# ============================================
st.set_page_config(
    page_title="SplitBill",
    page_icon="💰",
    layout="centered"
)

# ============================================
# SESSION STATE
# ============================================
if 'people' not in st.session_state:
    st.session_state.people = ['Adek', 'Kamu', 'Teman']

if 'transactions' not in st.session_state:
    st.session_state.transactions = []

if 'items' not in st.session_state:
    st.session_state.items = []


# ============================================
# FUNGSI
# ============================================
def add_person(name):
    if name and name not in st.session_state.people:
        st.session_state.people.append(name)
        return True
    return False

def remove_person(name):
    if name in st.session_state.people:
        st.session_state.people.remove(name)
        return True
    return False

def add_item(name, price, payer):
    st.session_state.items.append({
        'name': name,
        'price': price,
        'payer': payer
    })

def clear_items():
    st.session_state.items = []

def save_transaction(desc, tax, service):
    if not st.session_state.items:
        return False
    
    total = sum(item['price'] for item in st.session_state.items)
    tax_amount = total * (tax / 100)
    service_amount = service
    grand_total = total + tax_amount + service_amount
    
    # Hitung per orang
    per_person = {p: 0 for p in st.session_state.people}
    for item in st.session_state.items:
        per_person[item['payer']] += item['price']
    
    # Tambah tax & service proporsional
    for person in per_person:
        if total > 0:
            proporsi = per_person[person] / total
            per_person[person] += tax_amount * proporsi + service_amount * proporsi
    
    trans = {
        'date': datetime.now().strftime('%d/%m/%Y'),
        'desc': desc,
        'items': st.session_state.items.copy(),
        'total': grand_total,
        'tax': tax,
        'service': service,
        'per_person': per_person
    }
    
    st.session_state.transactions.append(trans)
    clear_items()
    return True


# ============================================
# UI
# ============================================
st.title("💰 SplitBill")
st.caption("Bagi tagihan bareng teman")

tab1, tab2, tab3 = st.tabs(["🧾 Split", "👥 Orang", "📋 Riwayat"])


# ============================================
# TAB 1: SPLIT
# ============================================
with tab1:
    if not st.session_state.people:
        st.warning("⚠️ Tambahkan orang dulu di tab 👥 Orang")
    else:
        # Form input item
        with st.form("add_item_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                item_name = st.text_input("Item", placeholder="Nasi Goreng")
            with col2:
                item_price = st.number_input("Harga", min_value=0, step=1000, value=0)
            with col3:
                item_payer = st.selectbox("Dibayar", st.session_state.people)
            
            submitted = st.form_submit_button("➕ Tambah Item", use_container_width=True)
            
            if submitted and item_name and item_price > 0:
                add_item(item_name, item_price, item_payer)
                st.success(f"✅ {item_name} - Rp {item_price:,.0f} ditambahkan".replace(',', '.'))
                st.rerun()
        
        # Daftar item
        if st.session_state.items:
            st.divider()
            st.subheader(f"📋 Items ({len(st.session_state.items)})")
            
            df = pd.DataFrame(st.session_state.items)
            df['price'] = df['price'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Hapus Semua", use_container_width=True):
                    clear_items()
                    st.rerun()
            
            with col2:
                tax = st.number_input("Tax (%)", min_value=0, value=11, step=1)
                service = st.number_input("Service", min_value=0, value=0, step=1000)
            
            if st.button("💾 Simpan Transaksi", use_container_width=True, type="primary"):
                desc = st.text_input("Deskripsi", placeholder="Makan malam...")
                if desc and save_transaction(desc, tax, service):
                    st.success("✅ Transaksi disimpan!")
                    st.rerun()
                elif not desc:
                    st.warning("⚠️ Masukkan deskripsi")
        else:
            st.info("💡 Belum ada item. Tambahkan item di atas.")


# ============================================
# TAB 2: ORANG
# ============================================
with tab2:
    st.subheader("👥 Daftar Orang")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("#### ➕ Tambah")
            new_name = st.text_input("Nama", placeholder="Masukkan nama", key="new_name")
            if st.button("Tambah", use_container_width=True):
                if add_person(new_name):
                    st.success(f"✅ {new_name} ditambahkan")
                    st.rerun()
                else:
                    st.error("❌ Nama sudah ada atau kosong")
    
    with col2:
        with st.container(border=True):
            st.markdown("#### 🗑️ Hapus")
            if st.session_state.people:
                remove_name = st.selectbox("Pilih", st.session_state.people, key="remove_name")
                if st.button("Hapus", use_container_width=True):
                    if remove_person(remove_name):
                        st.success(f"✅ {remove_name} dihapus")
                        st.rerun()
            else:
                st.info("Belum ada orang")
    
    st.divider()
    st.markdown("### 📋 Daftar")
    if st.session_state.people:
        for p in st.session_state.people:
            st.markdown(f"👤 {p}")
    else:
        st.info("Belum ada orang")


# ============================================
# TAB 3: RIWAYAT
# ============================================
with tab3:
    st.subheader("📋 Riwayat Transaksi")
    
    if not st.session_state.transactions:
        st.info("💡 Belum ada transaksi")
    else:
        for i, trans in enumerate(reversed(st.session_state.transactions)):
            with st.expander(f"📅 {trans['date']} - {trans['desc']} (Rp {trans['total']:,.0f})".replace(',', '.')):
                st.markdown(f"**Total:** Rp {trans['total']:,.0f}".replace(',', '.'))
                st.markdown(f"**Tax:** {trans['tax']}% | **Service:** Rp {trans['service']:,.0f}".replace(',', '.'))
                
                st.markdown("##### 📋 Detail Item")
                df_items = pd.DataFrame(trans['items'])
                df_items['price'] = df_items['price'].apply(lambda x: f"Rp {x:,.0f}".replace(',', '.'))
                st.dataframe(df_items, use_container_width=True, hide_index=True)
                
                st.markdown("##### 👤 Per Orang")
                per_person = []
                for person, total in trans['per_person'].items():
                    per_person.append({'Nama': person, 'Total': f"Rp {total:,.0f}".replace(',', '.')})
                st.dataframe(pd.DataFrame(per_person), use_container_width=True, hide_index=True)
