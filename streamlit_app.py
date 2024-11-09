import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt

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

def siparis_ekle(siparis_adi, urun_kodu, miktar):
    urun_adi = st.session_state.stok_df.loc[st.session_state.stok_df['Ürün Kodu'] == urun_kodu, 'Ürün Adı'].values[0] if urun_kodu in st.session_state.stok_df['Ürün Kodu'].values else "Bilinmiyor"
    yeni_siparis = pd.DataFrame([[siparis_adi, urun_kodu, urun_adi, miktar]], columns=["Sipariş Adı", "Ürün Kodu", "Ürün Adı", "Miktar"])
    st.session_state.siparisler_df = pd.concat([st.session_state.siparisler_df, yeni_siparis], ignore_index=True)

# Uygulama Başlığı
st.title("Gelişmiş ERP Stok ve Sipariş Yönetimi")

# Sekmeler
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stok Yönetimi", "Güncel Stok Durumu", "Sipariş Ekle", "Siparişler Ekranı", "Analiz ve Raporlama"])

# Stok Yönetimi Sekmesi
with tab1:
    st.header("Stok Yönetimi")
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
    eksik_stok_df = st.session_state.stok_df[st.session_state.stok_df['Stok Miktarı'] < st.session_state.stok_df['Yeniden Sipariş Sınırı']]
    if not eksik_stok_df.empty:
        st.warning("Düşük stok seviyesine sahip ürünler:")
        st.write(eksik_stok_df)
    else:
        st.success("Tüm stoklar yeterli seviyede.")

# Sipariş Ekle Sekmesi
with tab3:
    st.header("Sipariş Ekle")
    siparis_adi = st.text_input("Sipariş Adı")
    urun_kodu = st.text_input("Ürün Kodu (Virgülle ayırarak birden fazla ürün ekleyebilirsiniz)")
    miktar = st.text_input("Miktar (Virgülle ayırarak sırasıyla miktarları girin)")

    if st.button("Siparişi Kaydet"):
        urun_kodlari = urun_kodu.split(',')
        miktarlar = [int(m) for m in miktar.split(',')]

        for k, m in zip(urun_kodlari, miktarlar):
            siparis_ekle(siparis_adi, k.strip(), m)
        st.success("Sipariş eklendi ve stoklar güncellendi.")

# Siparişler Ekranı Sekmesi
with tab4:
    st.header("Siparişler Ekranı")
    for siparis_adi in st.session_state.siparisler_df['Sipariş Adı'].unique():
        with st.expander(f"Sipariş: {siparis_adi}"):
            siparis_detay = st.session_state.siparisler_df[st.session_state.siparisler_df['Sipariş Adı'] == siparis_adi]
            st.write(siparis_detay)

# Analiz ve Raporlama Sekmesi
with tab5:
    st.header("Analiz ve Raporlama")
    
    # Günlük stok hareketleri
    if not st.session_state.siparisler_df.empty:
        st.subheader("En Çok Satılan Ürünler")
        en_cok_satilan = st.session_state.siparisler_df.groupby("Ürün Adı")["Miktar"].sum().sort_values(ascending=False).head(10)
        fig = px.bar(en_cok_satilan, x=en_cok_satilan.index, y="Miktar", labels={'x': 'Ürün Adı', 'y': 'Toplam Satış Miktarı'})
        st.plotly_chart(fig)

    # Haftalık satış trendleri
    st.subheader("Haftalık Satış Trendleri")
    haftalik_satis = st.session_state.siparisler_df.groupby("Sipariş Adı").sum()
    fig2, ax = plt.subplots()
    haftalik_satis['Miktar'].plot(kind='line', marker='o', ax=ax)
    ax.set_title("Haftalık Sipariş Miktarı")
    ax.set_xlabel("Sipariş")
    ax.set_ylabel("Toplam Miktar")
    st.pyplot(fig2)
