import streamlit as st
import pandas as pd

# Başlangıç verileri
if 'stok_df' not in st.session_state:
    st.session_state.stok_df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])

# Fonksiyonlar
def stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri):
    # Mevcut ürün varsa miktarı güncelle
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] += miktar
    else:
        # Yeni ürün ekle
        yeni_veri = pd.DataFrame([[urun_kodu, urun_adi, miktar, yeniden_siparis_siniri]],
                                 columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])
        st.session_state.stok_df = pd.concat([st.session_state.stok_df, yeni_veri], ignore_index=True)

def stok_guncelle(urun_kodu, siparis_miktari):
    # Stoktan düş ve uyarı ver
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        mevcut_stok = st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'].values[0]
        if mevcut_stok >= siparis_miktari:
            st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] -= siparis_miktari
            return f"{urun_kodu} ürününden {siparis_miktari} adet düşüldü."
        else:
            return f"{urun_kodu} ürünü için yeterli stok bulunmuyor."
    else:
        return "Bu ürün stokta bulunmuyor."

def dosya_yukle(uploaded_file):
    try:
        df = pd.read_excel(uploaded_file)
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
tab1, tab2, tab3 = st.tabs(["Stok Yönetimi", "Güncel Stok Durumu", "Sipariş Ekle"])

# Stok Yönetimi Sekmesi
with tab1:
    st.header("Stok Yönetimi")

    # Stok Ekleme
    with st.expander("Stok Ekle"):
        urun_adi = st.text_input("Ürün Adı")
        urun_kodu = st.text_input("Ürün Kodu")
        miktar = st.number_input("Stok Miktarı", min_value=0)
        yeniden_siparis_siniri = st.number_input("Yeniden Sipariş Sınırı", min_value=0)
        
        if st.button("Stok Ekle"):
            stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri)
            st.success(f"{urun_adi} ({urun_kodu}) başarıyla eklendi veya güncellendi.")

    # Stok Güncelleme
    with st.expander("Stok Güncelle"):
        guncelle_urun_kodu = st.text_input("Güncelleme için Ürün Kodu")
        siparis_miktari = st.number_input("Sipariş Miktarı", min_value=1)
        
        if st.button("Stok Güncelle"):
            mesaj = stok_guncelle(guncelle_urun_kodu, siparis_miktari)
            st.info(mesaj)

    # Dosya Yükleme
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

# Sipariş Ekle Sekmesi
with tab3:
    st.header("Sipariş Ekle")

    # Çoklu ürün sipariş girişi
    siparis_urun_kodu = st.text_input("Sipariş Ürün Kodu (virgülle ayırarak birden fazla ürün ekleyebilirsiniz)")
    siparis_miktar = st.text_input("Sipariş Miktarları (ürün kodlarına göre virgülle ayırarak sırasıyla miktarları girin)")
    
    if st.button("Siparişi İşle"):
        # Ürün kodları ve miktarları işleme
        urun_kodlari = siparis_urun_kodu.split(',')
        miktarlar = [int(m) for m in siparis_miktar.split(',')]
        
        # Sipariş işlemi ve stok güncelleme
        for urun, miktar in zip(urun_kodlari, miktarlar):
            mesaj = stok_guncelle(urun.strip(), miktar)
            st.info(mesaj)
        
        st.success("Sipariş işlendi ve stoklar güncellendi.")
