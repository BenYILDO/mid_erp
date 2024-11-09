import streamlit as st
import pandas as pd
import altair as alt

# Başlangıç verileri
if 'stok_df' not in st.session_state:
    st.session_state.stok_df = pd.DataFrame(columns=["Ürün Kodu", "Ürün Adı", "Stok Miktarı", "Yeniden Sipariş Sınırı"])

if 'siparisler_df' not in st.session_state:
    st.session_state.siparisler_df = pd.DataFrame(columns=["Sipariş Adı", "Ürün Kodu", "Ürün Adı", "Miktar", "Tarih"])

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
    yeni_siparis = pd.DataFrame([[siparis_adi, urun_kodu, urun_adi, miktar, pd.to_datetime('today')]], columns=["Sipariş Adı", "Ürün Kodu", "Ürün Adı", "Miktar", "Tarih"])
    st.session_state.siparisler_df = pd.concat([st.session_state.siparisler_df, yeni_siparis], ignore_index=True)

# Uygulama Başlığı
st.title("Gelişmiş ERP Stok ve Sipariş Yönetimi")

# Sekmeler
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Stok Yönetimi", "Güncel Stok Durumu", "Sipariş Ekle", "Siparişler Ekranı", "Raporlama ve Analiz"])

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

    # Altair ile Stok Miktarı ve Yeniden Sipariş Sınırı Grafiği
    if not st.session_state.stok_df.empty:
        stok_chart = alt.Chart(st.session_state.stok_df).mark_bar().encode(
            x='Ürün Kodu',
            y='Stok Miktarı',
            color=alt.condition(
                alt.datum['Stok Miktarı'] < alt.datum['Yeniden Sipariş Sınırı'],
                alt.value('red'),  # Düşük stok seviyesindeyse kırmızı
                alt.value('green')  # Yeterli stok seviyesindeyse yeşil
            )
        ).properties(title="Stok Miktarı ve Yeniden Sipariş Sınırı")

        st.altair_chart(stok_chart, use_container_width=True)

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

# Raporlama ve Analiz Sekmesi
with tab5:
    st.header("Raporlama ve Analiz")
    
    # En çok satılan ürünler
    top_selling_products = st.session_state.siparisler_df.groupby('Ürün Kodu')['Miktar'].sum().reset_index()
    top_selling_products = top_selling_products.sort_values(by='Miktar', ascending=False)
    
    st.subheader("En Çok Satılan Ürünler")
    top_selling_chart = alt.Chart(top_selling_products).mark_bar().encode(
        x='Ürün Kodu',
        y='Miktar',
        color='Ürün Kodu'
    ).properties(title="En Çok Satılan Ürünler")
    st.altair_chart(top_selling_chart, use_container_width=True)

        # Günlük/Haftalık Sipariş Hareketi
    st.subheader("Günlük ve Haftalık Sipariş Hareketi")

    # Sipariş tarihine göre sıralama
    if not st.session_state.siparisler_df.empty:
        # Günlük ve haftalık analiz için 'Tarih' sütununu kullanıyoruz
        siparisler_df = st.session_state.siparisler_df.copy()
        siparisler_df['Tarih'] = pd.to_datetime(siparisler_df['Tarih'])

        # Günlük sipariş verisi
        daily_sales = siparisler_df.groupby(siparisler_df['Tarih'].dt.date)['Miktar'].sum().reset_index()
        daily_sales.columns = ['Tarih', 'Toplam Miktar']

        # Haftalık sipariş verisi
        weekly_sales = siparisler_df.groupby(siparisler_df['Tarih'].dt.to_period('W'))['Miktar'].sum().reset_index()
        weekly_sales.columns = ['Tarih', 'Toplam Miktar']

        # Altair ile grafikler
        daily_sales_chart = alt.Chart(daily_sales).mark_line().encode(
            x='Tarih:T',
            y='Toplam Miktar:Q',
            color=alt.value('blue')
        ).properties(title="Günlük Sipariş Hareketi")

        weekly_sales_chart = alt.Chart(weekly_sales).mark_line().encode(
            x='Tarih:T',
            y='Toplam Miktar:Q',
            color=alt.value('orange')
        ).properties(title="Haftalık Sipariş Hareketi")

        st.altair_chart(daily_sales_chart, use_container_width=True)
        st.altair_chart(weekly_sales_chart, use_container_width=True)
    else:
        st.warning("Henüz sipariş verisi bulunmamaktadır.")

    # Düşük Stok Uyarı Raporu
    st.subheader("Düşük Stok Uyarıları")

    # Düşük stok seviyesindeki ürünlerin raporlanması
    eksik_stok_df = st.session_state.stok_df[st.session_state.stok_df['Stok Miktarı'] < st.session_state.stok_df['Yeniden Sipariş Sınırı']]
    
    if not eksik_stok_df.empty:
        st.write("Düşük stok seviyesindeki ürünler:")
        st.write(eksik_stok_df[['Ürün Kodu', 'Ürün Adı', 'Stok Miktarı', 'Yeniden Sipariş Sınırı']])
    else:
        st.success("Tüm ürünler yeterli stok seviyesinde.")

    # Sipariş ve stok analizi
    st.subheader("Ürün Bazlı Sipariş ve Stok Analizi")

    if not st.session_state.stok_df.empty and not st.session_state.siparisler_df.empty:
        # Ürün bazında stok ve sipariş bilgilerini birleştirme
        stok_siparis_df = pd.merge(st.session_state.stok_df, st.session_state.siparisler_df.groupby('Ürün Kodu')['Miktar'].sum().reset_index(), on='Ürün Kodu', how='left')
        stok_siparis_df['Miktar'] = stok_siparis_df['Miktar'].fillna(0)  # Eğer sipariş yoksa 0 olarak al

        stok_siparis_df['Kalan Stok'] = stok_siparis_df['Stok Miktarı'] - stok_siparis_df['Miktar']

        # Ürün bazında raporlama
        st.write(stok_siparis_df[['Ürün Kodu', 'Ürün Adı', 'Stok Miktarı', 'Miktar', 'Kalan Stok']])

        # Altair ile stok ve sipariş analizi grafiği
        product_analysis_chart = alt.Chart(stok_siparis_df).mark_bar().encode(
            x='Ürün Adı',
            y='Stok Miktarı',
            color='Ürün Kodu',
            tooltip=['Ürün Adı', 'Stok Miktarı', 'Miktar', 'Kalan Stok']
        ).properties(title="Ürün Bazlı Stok ve Sipariş Analizi")

        st.altair_chart(product_analysis_chart, use_container_width=True)

    else:
        st.warning("Stok veya sipariş verisi eksik.")
