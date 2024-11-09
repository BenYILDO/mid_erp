import streamlit as st
import pandas as pd

# Başlangıç verileri
if 'stok_df' not in st.session_state:
    st.session_state.stok_df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])

if 'siparisler_df' not in st.session_state:
    st.session_state.siparisler_df = pd.DataFrame(columns=["Sipariş Adı", "Ürün Kodu", "Ürün Adı", "Miktar"])

# Fonksiyonlar
def stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri):
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] += miktar
    else:
        yeni_veri = pd.DataFrame([[urun_kodu, urun_adi, miktar, yeniden_siparis_siniri]],
                                 columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])
        st.session_state.stok_df = pd.concat([st.session_state.stok_df, yeni_veri], ignore_index=True)

def stok_guncelle(urun_kodu, eski_miktar, yeni_miktar):
    if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values:
        stok_farki = eski_miktar - yeni_miktar  # Eski ve yeni miktar farkı
        st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Stok Miktarı'] += stok_farki
        return f"{urun_kodu} ürününün stok durumu güncellendi."
    else:
        return "Bu ürün stokta bulunmuyor."

def siparis_ekle(siparis_adi, urun_kodu, miktar):
    urun_adi = st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Ürün Adı'].values[0] if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values else "Bilinmiyor"
    yeni_siparis = pd.DataFrame([[siparis_adi, urun_kodu, urun_adi, miktar]], columns=["Sipariş Adı", "Ürün Kodu", "Ürün Adı", "Miktar"])
    st.session_state.siparisler_df = pd.concat([st.session_state.siparisler_df, yeni_siparis], ignore_index=True)

# Uygulama Başlığı
st.title("Gelişmiş ERP Stok ve Sipariş Yönetimi")

# Sekmeler
tab1, tab2, tab3, tab4 = st.tabs(["Stok Yönetimi", "Güncel Stok Durumu", "Sipariş Ekle", "Siparişler Ekranı"])

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

    # Sipariş bilgileri girişi
    siparis_adi = st.text_input("Sipariş Adı")
    urun_kodu = st.text_input("Ürün Kodu (Virgülle ayırarak birden fazla ürün ekleyebilirsiniz)")
    miktar = st.text_input("Miktar (Virgülle ayırarak sırasıyla miktarları girin)")

    if st.button("Siparişi Kaydet"):
        urun_kodlari = urun_kodu.split(',')
        miktarlar = [int(m) for m in miktar.split(',')]

        for k, m in zip(urun_kodlari, miktarlar):
            siparis_ekle(siparis_adi, k.strip(), m)
            stok_guncelle(k.strip(), 0, m)  # İlk sipariş eklemede eski miktar 0 olarak alınır.
        
        st.success("Sipariş eklendi ve stoklar güncellendi.")

# Siparişler Ekranı Sekmesi
with tab4:
    st.header("Siparişler Ekranı")

    # Tüm siparişler için liste
    for siparis_adi in st.session_state.siparisler_df['Sipariş Adı'].unique():
        with st.expander(f"Sipariş: {siparis_adi}"):
            siparis_detay = st.session_state.siparisler_df[st.session_state.siparisler_df['Sipariş Adı'] == siparis_adi]
            st.write(siparis_detay)

            # Sipariş Düzenleme
            urun_secimi = st.selectbox("Düzenlenecek Ürün", siparis_detay['Ürün Kodu'])
            mevcut_miktar = siparis_detay[siparis_detay['Ürün Kodu'] == urun_secimi]['Miktar'].values[0]
            yeni_miktar = st.number_input("Yeni Miktar", min_value=0, value=mevcut_miktar)
            
            if st.button(f"{urun_secimi} Ürününü Güncelle"):
                st.session_state.siparisler_df.loc[(st.session_state.siparisler_df['Sipariş Adı'] == siparis_adi) &
                                                   (st.session_state.siparisler_df['Ürün Kodu'] == urun_secimi), 'Miktar'] = yeni_miktar
                
                # Stok miktarını eski ve yeni miktar farkına göre güncelle
                stok_guncelle(urun_secimi, mevcut_miktar, yeni_miktar)
                st.success(f"{urun_secimi} ürününün miktarı güncellendi ve stok durumu canlı tutuldu.")
