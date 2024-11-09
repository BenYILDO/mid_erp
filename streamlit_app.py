import streamlit as st
import pandas as pd

# Başlangıç verileri
if 'stok_df' not in st.session_state:
    st.session_state.stok_df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])

# Stok güncelleme ve kontrol fonksiyonu
def stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri):
    # Eğer ürün mevcutsa güncelle
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] += miktar
    else:
        # Yeni ürün ekle
        yeni_veri = pd.DataFrame([[urun_kodu, urun_adi, miktar, yeniden_siparis_siniri]],
                                 columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])
        st.session_state.stok_df = pd.concat([st.session_state.stok_df, yeni_veri], ignore_index=True)

# Stok güncelle fonksiyonu
def stok_guncelle(urun_kodu, siparis_miktari):
    # Ürün mevcutsa stoktan düş
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        mevcut_stok = st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'].values[0]
        if mevcut_stok >= siparis_miktari:
            st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] -= siparis_miktari
            st.success(f"{urun_kodu} ürününden {siparis_miktari} adet düşüldü.")
        else:
            st.warning(f"{urun_kodu} ürününden yeterli stok bulunmuyor.")
    else:
        st.error("Bu ürün stokta bulunmuyor.")

# Dosyadan stokları yükle
def dosya_yukle(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
        # Beklenen sütunların mevcut olup olmadığını kontrol edelim
        if all(col in df.columns for col in ["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"]):
            st.session_state.stok_df = pd.concat([st.session_state.stok_df, df], ignore_index=True).drop_duplicates(subset=['Ürün Kodu'], keep='last')
            st.success("Dosya başarıyla yüklendi ve stok bilgileri güncellendi.")
        else:
            st.error("Excel dosyası gerekli sütunlara sahip değil: 'Ürün Kodu', 'Ürün Adı', 'Stok Miktarı', 'Yeniden Sipariş Sınırı'")
    except Exception as e:
        st.error(f"Hata: {e}")

# Uygulama başlığı
st.title("Gelişmiş ERP Stok ve Sipariş Yönetimi")

# Sekmeler
tab1, tab2 = st.tabs(["Stok Yönetimi", "Güncel Stok Durumu"])

# Stok Yönetimi Sekmesi
with tab1:
    st.header("Stok Yönetimi")

    # Ürün bilgilerini eklemek/güncellemek için form
    with st.expander("Stok Ekle"):
        urun_adi = st.text_input("Ürün Adı")
        urun_kodu = st.text_input("Ürün Kodu")
        miktar = st.number_input("Stok Miktarı", min_value=0)
        yeniden_siparis_siniri = st.number_input("Yeniden Sipariş Sınırı", min_value=0)
        
        if st.button("Stok Ekle"):
            stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri)
            st.success(f"{urun_adi} ({urun_kodu}) başarıyla eklendi veya güncellendi.")

    with st.expander("Stok Güncelle"):
        guncelle_urun_kodu = st.text_input("Güncelleme için Ürün Kodu")
        siparis_miktari = st.number_input("Sipariş Miktarı", min_value=1)
        
        if st.button("Stok Güncelle"):
            stok_guncelle(guncelle_urun_kodu, siparis_miktari)

    with st.expander("Dosya Ekle"):
        uploaded_file = st.file_uploader("Stok bilgilerini içeren bir Excel dosyası yükleyin", type=['xlsx'])
        
        if st.button("Dosya Yükle") and uploaded_file is not None:
            dosya_yukle(uploaded_file)

# Güncel Stok Durumu Sekmesi
with tab2:
    st.header("Güncel Stok Durumu")
    st.write(st.session_state.stok_df)

    # Düşük stok uyarısı
    eksik_stok_df = st.session_state.stok_df[st.session_state.stok_df['Stok Miktarı'] < st.session_state.stok_df['Yeniden Sipariş Sınırı']]
    if not eksik_stok_df.empty:
        st.warning("Düşük stok seviyesine sahip ürünler:")
        st.write(eksik_stok_df)
    else:
        st.success("Tüm stoklar yeterli seviyede.")
