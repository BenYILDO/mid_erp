import streamlit as st
import altair as alt

# Başlangıç verileri
if 'stok_df' not in st.session_state:
    st.session_state.stok_df = {'Ürün Kodu': [], 'Ürün Adı': [], 'Stok Miktarı': [], 'Yeniden Sipariş Sınırı': []}

if 'siparisler_df' not in st.session_state:
    st.session_state.siparisler_df = {'Sipariş Adı': [], 'Ürün Kodu': [], 'Ürün Adı': [], 'Miktar': [], 'Tarih': []}

# Fonksiyonlar
def stok_ekle(urun_kodu, urun_adi, miktar, yeniden_siparis_siniri):
    for i, kod in enumerate(st.session_state.stok_df['Ürün Kodu']):
        if kod == urun_kodu:
            st.session_state.stok_df['Stok Miktarı'][i] += miktar
            return
    st.session_state.stok_df['Ürün Kodu'].append(urun_kodu)
    st.session_state.stok_df['Ürün Adı'].append(urun_adi)
    st.session_state.stok_df['Stok Miktarı'].append(miktar)
    st.session_state.stok_df['Yeniden Sipariş Sınırı'].append(yeniden_siparis_siniri)

def stok_guncelle(urun_kodu, eski_miktar, yeni_miktar):
    for i, kod in enumerate(st.session_state.stok_df['Ürün Kodu']):
        if kod == urun_kodu:
            stok_farki = eski_miktar - yeni_miktar
            st.session_state.stok_df['Stok Miktarı'][i] += stok_farki
            return f"{urun_kodu} ürününün stok durumu güncellendi."
    return "Bu ürün stokta bulunmuyor."

def siparis_ekle(siparis_adi, urun_kodu, miktar):
    urun_adi = "Bilinmiyor"
    for i, kod in enumerate(st.session_state.stok_df['Ürün Kodu']):
        if kod == urun_kodu:
            urun_adi = st.session_state.stok_df['Ürün Adı'][i]
            break
    st.session_state.siparisler_df['Sipariş Adı'].append(siparis_adi)
    st.session_state.siparisler_df['Ürün Kodu'].append(urun_kodu)
    st.session_state.siparisler_df['Ürün Adı'].append(urun_adi)
    st.session_state.siparisler_df['Miktar'].append(miktar)
    st.session_state.siparisler_df['Tarih'].append("today")

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
    
    # Veriyi yazdırma
    stok_data = {
        "Ürün Kodu": st.session_state.stok_df['Ürün Kodu'],
        "Ürün Adı": st.session_state.stok_df['Ürün Adı'],
        "Stok Miktarı": st.session_state.stok_df['Stok Miktarı'],
        "Yeniden Sipariş Sınırı": st.session_state.stok_df['Yeniden Sipariş Sınırı'],
    }
    st.write(stok_data)
    
    # Altair ile Stok Miktarı ve Yeniden Sipariş Sınırı Grafiği
    if len(st.session_state.stok_df['Ürün Kodu']) > 0:
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
    eksik_stok_df = [stok for stok in zip(st.session_state.stok_df['Ürün Kodu'], st.session_state.stok_df['Stok Miktarı'], st.session_state.stok_df['Yeniden Sipariş Sınırı']) if stok[1] < stok[2]]
    if eksik_stok_df:
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
    siparis_gruplari = list(set(st.session_state.siparisler_df['Sipariş Adı']))
    for siparis_adi in siparis_gruplari:
        with st.expander(f"Sipariş: {siparis_adi}"):
            siparis_detay = [(st.session_state.siparisler_df['Ürün Kodu'][i], st.session_state.siparisler_df['Ürün Adı'][i], st.session_state.siparisler_df['Miktar'][i]) for i, x in enumerate(st.session_state.siparisler_df['Sipariş Adı']) if x == siparis_adi]
            st.write(siparis_detay)

            # Sipariş Düzenleme
            urun_secimi = st.selectbox("Düzenlenecek Ürün", [item[0] for item in siparis_detay])
            mevcut_miktar = next(item[2] for item in siparis_detay if item[0] == urun_secimi)
            yeni_miktar = st.number_input("Yeni Miktar", min_value=0, value=mevcut_miktar)
            
            if st.button(f"{urun_secimi} Ürününü Güncelle"):
                for i, x in enumerate(st.session_state.siparisler_df['Sipariş Adı']):
                    if st.session_state.siparisler_df['Sipariş Adı'][i] == siparis_adi and st.session_state.siparisler_df['Ürün Kodu'][i] == urun_secimi:
                        st.session_state.siparisler_df['Miktar'][i] = yeni_miktar
                        stok_guncelle(urun_secimi, mevcut_miktar, yeni_miktar)
                        st.success(f"{urun_secimi} ürününün miktarı güncellendi ve stok durumu canlı tutuldu.")

# Raporlama ve Analiz Sekmesi
with tab5:
    st.header("Raporlama ve Analiz")
    
    # En çok satılan ürünler
    top_selling_products = {}
    for i, urun_kodu in enumerate(st.session_state.siparisler_df['Ürün Kodu']):
        if urun_kodu in top_selling_products:
            top_selling_products[urun_kodu] += st.session_state.siparisler_df['Miktar'][i]
        else:
            top_selling_products[urun_kodu] = st.session_state.siparisler_df['Miktar'][i]

    # En çok satılan ürünleri sıralama
    sorted_top_selling = sorted(top_selling_products.items(), key=lambda x: x[1], reverse=True)
    
    # Veriyi dataframe olarak gösterme
    top_selling_df = pd.DataFrame(sorted_top_selling, columns=["Ürün Kodu", "Satılan Miktar"])
    st.write(top_selling_df)
    
    # En çok satılan ürünler grafiği
    if not top_selling_df.empty:
        chart = alt.Chart(top_selling_df).mark_bar().encode(
            x='Ürün Kodu',
            y='Satılan Miktar',
            color='Ürün Kodu'
        ).properties(title="En Çok Satılan Ürünler")

        st.altair_chart(chart, use_container_width=True)
    
    # Düşük stok uyarılarını görselleştirme
    eksik_stok_df = [stok for stok in zip(st.session_state.stok_df['Ürün Kodu'], st.session_state.stok_df['Stok Miktarı'], st.session_state.stok_df['Yeniden Sipariş Sınırı']) if stok[1] < stok[2]]
    if eksik_stok_df:
        st.warning("Düşük stok seviyesindeki ürünler:")
        st.write(eksik_stok_df)
    else:
        st.success("Tüm stoklar yeterli seviyede.")
