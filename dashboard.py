# import libraries 
import streamlit as st
import pandas as pd
from Analysis_Functions.Adet_Ciro_Bazında_EnCokSatanlar import yil_ay_bazinda_en_cok_satan_urunler
from Analysis_Functions.Aylık_Yıllık_Ciro_Büyüme_Oranı import ciro_buyume_orani_analizi
from Analysis_Functions.Ciro_Büyüme_Oranı import (
    aylik_en_yuksek_ciroya_sahip_3_musteri,
    aylik_en_yuksek_ciroya_sahip_3_ürün,
    düzenlisiparişverenler_aralıklı_müşteriler_ürünler,
    düzenlisiparişverenler_aralıklımüşteriler,
    düzenlisiparişverenler_aralıklıürünler,
)
from Analysis_Functions.Yıllık_Satış_Rakamları import yıllık_satış_rakamları
from Analysis_Functions.seasonality_channel_price_specialday_analysis import (
    check_seasonality_specialday_channel_price,
    check_price_and_sales,
)
from Analysis_Functions.macroeconomic_analysis import macroeconomic_parameters
from Analysis_Functions.top_3_customer_product_sales_by_month_year import top_3_customer_product_sales_by_month_year
from Analysis_Functions.plot_top10 import (
    plot_top10_products_per_year,
    plot_top10_productsandcustomers_per_year,
)
from Analysis_Functions.plot_top_products_by_season import plot_top_products_by_season
from Analysis_Functions.prepare_data import preprocessing
from Analysis_Functions.seasonal_sales_by_year import seasonal_sales_by_year
from Analysis_Functions.top5_products_per_season import top5_products_per_season
from Analysis_Functions.plot_top_selling_product_customer_by_season import plot_top_selling_product_customer_by_season
from Analysis_Functions.total_sales_and_trend_line import total_sales_and_trend_line
from Analysis_Functions.sales_volatility import sales_volatility
# from Analysis_Modules.ay_bazlı_analiz import ay_bazlı_analiz
from Analysis_Functions.sales_revenue import sales_revenue_product,sales_revenue_product_customer
from Analysis_Functions.trend_analysis import (
    customer_product_trend_analysis,
    product_trend_analysis,
    customer_trend_analysis,
    customer_product_segmentation,
    product_segmentation,
    customer_segmentation,
)
from Analysis_Functions.volatility_analysis import volatility_analysis
from Analysis_Functions.trend_volatility_analysis_segmentation import combine_trend_volatility_results
from Analysis_Functions.database import get_sales_data
from Analysis_Functions.AgingFactor import aging_factor_analysis
from Analysis_Functions.Aylık_Değişim_Oranı import rate_of_change_per_month

# Sayfa arka planı ve kenar boşlukları için renkli stil
st.markdown(
    """
    <style>
    body {
        background-color: #e6ffe3 !important;
    }
    .stApp {
        background: linear-gradient(120deg, #e6ffe3 0%, #e6fff9 100%);
    }
    .block-container {
        background-color: white;
        border-radius: 18px;
        box-shadow: 0 4px 24px rgba(44, 62, 80, 0.08);
        padding: 2rem 2rem 2rem 2rem;
        margin-top: 30px;
        max-width: 900px;
        margin-bottom: 30px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sabit logo üstte ve ortada
st.markdown(
    """
    <div style="display: flex; justify-content: center; margin-bottom: 30px; margin-top: 0px;">
        <img src="https://chefseasons.com/static/images/logo-tr.png" alt="Logo" width="300">
    </div>
    """,
    unsafe_allow_html=True
)

# Header başlığı
st.markdown(
    """
    <div style="display: flex; align-items: center; justify-content: center; margin-bottom: 50px;">
        <h1 style="display:inline; color:#2E4053;font-size: 38px;">Chef Seasons Satış Analiz Dashboardu</h1>
    </div>
    """,
    unsafe_allow_html=True
)
#Login Screen 
def login():
    username = st.text_input("Kullanıcı Adı")
    password = st.text_input("Parola", type="password")
    if st.button("Giriş"):
        auth = st.secrets.get("auth", {})
        if username == auth.get("username") and password == auth.get("password"):
            st.session_state["authenticated"] = True
            st.success("Giriş başarılı!")
            st.rerun()
        else:
            st.error("Hatalı kullanıcı adı veya parola")

# Check Login 
if not st.session_state.get("authenticated", False):
    login()
    st.stop()


# Choose the analysis type 
st.markdown(
    """
    <style>
    .selectbox-label {
        color: #000;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 0px !important;
        margin-top: 0px !important;
        padding-bottom: 0px !important;
    }
    div[data-baseweb="select"] {
        margin-top: -18px !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)
st.markdown(
    "<span class='selectbox-label'>Yapmak istediğiniz analizi seçiniz:</span>",
    unsafe_allow_html=True
)
option = st.selectbox(
    "",  # Boş bırakıyoruz, başlığı yukarıda verdik
    ("Yurtiçi -Dipsos/Sachet", "Yurtiçi-Diğer Ürünler", "İhracat-Dipsos/Sachet", "İhracat-Diğer Ürünler")
)
#st.write("Seçiminiz:", option)
# Kullanıcı dosya yüklemeden önce veritabanından çekmek için:
if st.button("Veritabanından Veriyi Çek"):
    df_raw2 = get_sales_data(option)
    st.dataframe(df_raw2)
    # Sonrasında df_raw ile analizlerine devam edebilirsin
    df_raw=pd.DataFrame(df_raw2)
    df_clean = preprocessing(df_raw)
    
    # Kullanım:
    st.title("Yıl-Ay Bazında Satış Rakamları")
    st.markdown("2024 ve 2025 yıllarında aktif satışı olan müşteri-ürün grupları bazında yapılmıştır.")
    monthly_sales = yıllık_satış_rakamları(df_clean)
    st.write(monthly_sales)
    
    # Kullanım:
    st.title("Yıl-Ay Bazında Adet&Ciro Bazında En Çok Satan Ürünler")
    st.markdown("2024 ve 2025 yıllarında aktif satışı olan müşteri-ürün grupları bazında yapılmıştır.")
    sonuc = yil_ay_bazinda_en_cok_satan_urunler(df_clean)
    st.write(sonuc)

    # Örnek kullanım
    result, result2 = ciro_buyume_orani_analizi(df_clean) 
    st.title("Aylık ve Yıllık Ciro Büyüme Oranı")
    st.subheader("Aylık Ciro Büyüme Oranı")
    st.write(result)
    st.subheader("Yıllık Ciro Büyüme Oranı")
    st.write(result2)

    st.title("Trend Analizi Sonuçları")
    st.markdown("Bu analiz 2024 ve 2025 yıllarında aktif satışı olan müşteri-ürün grupları bazında yapılmıştır. ")
    musteri_ürün=customer_product_trend_analysis(df_clean)
    ürün=product_trend_analysis(df_clean)
    musteri=customer_trend_analysis(df_clean)
    customer_product_segmentation(musteri_ürün)
    product_segmentation(ürün) 
    #customer_segmentation(musteri)
    volatility_df_customer_product, volatility_df_product = volatility_analysis(df_clean)
    trend_volatility=combine_trend_volatility_results(musteri_ürün,volatility_df_customer_product,df_clean)
    price_std=check_seasonality_specialday_channel_price(df_clean)
    check_price_and_sales(trend_volatility,price_std)

    # Müşteri-Ürün Sipariş Yoğunluğu ve Düzenlilik Analizi
    st.header("Müşteri-Ürün Sipariş Yoğunluğu ve Düzenlilik Analizi")
    st.markdown(
        "Son satışı 2024 ve 2025 yıllarında olan müşteri-ürün gruplarının yaşam süresi boyunca ilgili üründen ne kadar sipariş verildiği hesaplanmıştır. "
        "Bu analizde, her müşterinin ilgili üründe yaşam süresi boyunca verdiği sipariş sayısı değerlendirilmiştir. "
        "Müşteri, yaşam süresi boyunca ilgili ürünü **tüm olası ayların %80'inden fazlasında sipariş verdiyse**, **“Düzenli Müşteri”** olarak etiketlenmiştir."
    )
    siparis_kategorileri_mu = düzenlisiparişverenler_aralıklı_müşteriler_ürünler(df_clean)
    st.subheader("Düzenli Siparişi Olan Müşteri-Ürün Grupları")
    st.dataframe(siparis_kategorileri_mu[siparis_kategorileri_mu["Category"] == "Düzenli Sipariş Verenler"])
    st.subheader("Aralıklı Siparişi Olan Müşteri-Ürün Grupları")
    st.dataframe(siparis_kategorileri_mu[siparis_kategorileri_mu["Category"] == "Aralıklı Sipariş Verenler"])
    st.subheader("Tek Seferlik Siparişi Olan Müşteri-Ürün Grupları")
    st.dataframe(siparis_kategorileri_mu[siparis_kategorileri_mu["Category"] == "Hesaplanamaz"])

    # Müşteri Sipariş Yoğunluğu ve Düzenlilik Analizi
    st.header("Müşteri Sipariş Yoğunluğu ve Düzenlilik Analizi")
    st.markdown(
        "Son satışı 2024 ve 2025 yıllarında olan müşterilerin yaşam süresi boyunca ne kadar sipariş verdiği hesaplanmıştır. "
        "Bu analizde, her müşterinin yaşam süresi boyunca verdiği sipariş sayısı değerlendirilmiştir. "
        "Müşteri, yaşam süresi boyunca **tüm olası ayların %80'inden fazlasında sipariş verdiyse**, **“Düzenli Sipariş Veren Müşteri”** olarak etiketlenmiştir."
    )
    siparis_kategorileri_m = düzenlisiparişverenler_aralıklımüşteriler(df_clean)
    st.subheader("Düzenli Siparişi Olan Müşteriler")
    st.dataframe(siparis_kategorileri_m[siparis_kategorileri_m["Category"] == "Düzenli Sipariş Verenler"])
    st.subheader("Aralıklı Siparişi Olan Müşteriler")
    st.dataframe(siparis_kategorileri_m[siparis_kategorileri_m["Category"] == "Aralıklı Sipariş Verenler"])
    st.subheader("Tek Seferlik Siparişi Olan Müşteriler")
    st.dataframe(siparis_kategorileri_m[siparis_kategorileri_m["Category"] == "Hesaplanamaz"])

    # Ürün Sipariş Yoğunluğu ve Düzenlilik Analizi
    st.header("Ürün Sipariş Yoğunluğu ve Düzenlilik Analizi")
    st.markdown(
        "Son satışı 2024 ve 2025 yıllarında olan ürünlerin yaşam süresi boyunca ne kadar sipariş verildiği hesaplanmıştır. "
        "Bu analizde, yaşam süresi boyunca verilen sipariş sayısı değerlendirilmiştir. "
        "Ürün, yaşam süresi boyunca **tüm olası ayların %80'inden fazlasında sipariş aldıysa**, **“Düzenli Sipariş Verilen Ürün”** olarak etiketlenmiştir."
    )
    siparis_kategorileri_u = düzenlisiparişverenler_aralıklıürünler(df_clean)
    st.subheader("Düzenli Siparişi Olan Ürünler")
    st.dataframe(siparis_kategorileri_u[siparis_kategorileri_u["Category"] == "Düzenli Sipariş Verilenler"])
    st.subheader("Aralıklı Siparişi Olan Ürünler")
    st.dataframe(siparis_kategorileri_u[siparis_kategorileri_u["Category"] == "Aralıklı Sipariş Verilenler"])
    st.subheader("Tek Seferlik Siparişi Olan Ürünler")
    st.dataframe(siparis_kategorileri_u[siparis_kategorileri_u["Category"] == "Hesaplanamaz"])

    # En yüksek ciroya sahip müşteriler 
    st.header("En Yüksek Ciroya Sahip Müşteriler")
    st.markdown("2024 yılı itibari ile her ay en yüksek 3 ciroya sahip müşteriler listelenmiştir.")
    top3_customers = aylik_en_yuksek_ciroya_sahip_3_musteri(df_clean)
    st.dataframe(top3_customers)
    
    # En yüksek ciroya sahip ürünler
    st.header("En Yüksek Ciroya Sahip Ürünler")
    st.markdown("2024 yılı itibari ile her ay en yüksek 3 ciroya sahip ürünler listelenmiştir.")
    top3_ürünler = aylik_en_yuksek_ciroya_sahip_3_ürün(df_clean)
    st.dataframe(top3_ürünler)


    st.markdown("### 2020-2025 Aralığında Sezon Bazlı Satış Analizi")
    seasonal_sales_df, fig = seasonal_sales_by_year(df_clean, plot=True)
    if fig:
        st.pyplot(fig)

    # En çok satan 5 ürün 
    top5_figs = plot_top_products_by_season(df_clean, years=[2024, 2025])
    for year, fig in top5_figs.items():
      st.markdown(f"#### {year} – Sezon Bazında En Çok Satan 5 Ürün")
      st.pyplot(fig)
     
    #En çok kez satan 5 ürün 
    top5_frequencyfigs = top5_products_per_season(df_clean, years=[2024, 2025])
    for year, fig in top5_frequencyfigs.items():
      st.markdown(f"#### {year} – Sezon Bazında En Çok Kez Satan 5 Ürün")
      st.pyplot(fig)

    #En çok satan müşteri-ürün kombinasyonları
    top_combo_figs = plot_top_selling_product_customer_by_season(df_clean, years=[2024, 2025])
    for year, fig in top_combo_figs.items():
        st.markdown(f"#### {year} – Sezon Bazında En Çok Satılan Ürün–Müşteri Kombinasyonları")
        st.pyplot(fig)

    #En çok kez satan müşteri-ürün kombinasyonları
    top_combo_frequency_figs = plot_top_selling_product_customer_by_season(df_clean, years=[2024, 2025])
    for year, fig in top_combo_frequency_figs.items():
        st.markdown(f"#### {year} – Sezon Bazında En Çok Satılan Ürün–Müşteri Kombinasyonları")
        st.pyplot(fig)

    #Toplam satış ve trend çizgisi
    st.markdown("### 2020-2025 Aralığında Toplam Satış ve Trend Çizgisi")
    trend_df, fig = total_sales_and_trend_line(df_clean, plot=True)
    if fig:
        st.pyplot(fig)

    #Volatility Analizi
    st.markdown("## Volatilite Analizi")
    st.markdown("Bu analizdeki veriler, 2024 ve 2025 yıllarında satış yapan müşterilere aittir.Her müşterinin satın alım hacimlerindeki zaman içindeki değişkenliği ölçmek için standart sapma ve ortalama kullanılarak bir volatilite skoru hesaplanmıştır. Bu skor, her müşterinin satın alım hacimlerinin ne kadar değişken olduğunu gösterir. Skorun yüksek olması, müşterinin satın alım hacimlerinde büyük dalgalanmalar olduğunu gösterir.")
    customer_vol_df, cust_prod_vol_df = sales_volatility(df_clean, top_n=10)

    st.title("Yaşlandıkça Değişen Satış Eğilimleri")
    aging_df = aging_factor_analysis(df_clean)
    st.dataframe(aging_df)

    st.title("Aylık Satış Değişim Oranları")
    value=rate_of_change_per_month(df_clean)
    st.dataframe(value)


    # Ay bazlı satış dağılımı 
    #st.markdown("## 2025 yılındaki Gün bazlı satış dağılımı ")
    #period_sales, fig = ay_bazlı_analiz(df_clean, year=2024, plot=True)
    #if fig:
    #    st.pyplot(fig)


    # Ay bazlı satış dağılımı 
    #st.markdown("## 2024 yılındaki Gün bazlı satış dağılımı ")
    #period_sales, fig = ay_bazlı_analiz(df_clean, year=2024, plot=True)
    #if fig:
    #    st.pyplot(fig)

    # Ay bazlı satış dağılımı 
    #st.markdown("## 2023 yılındaki Gün bazlı satış dağılımı ")
    #period_sales, fig = ay_bazlı_analiz(df_clean, year=2023, plot=True)
    #if fig:
    #    st.pyplot(fig)  
    

    # Yıl-Ay bazında en çok satan müşteri ürünler
    st.markdown("## 📈 Yıl–Ay Bazında En Çok Satan Müşteri–Ürünler")
    results = top_3_customer_product_sales_by_month_year(df_clean, plot=True)
    for year, (data, fig) in results.items():
      st.markdown(f"### 📊 {year} Yılı – Aylık En Çok Satanlar")
      if fig:
          st.pyplot(fig)
      st.dataframe(data)


    # Makroekonomik veriler -  satış dağılımı  
    st.markdown("## Makroekonomik Göstergeler ile Satış Karşılaştırmaları")
    st.markdown("2013-2025 yılları arasındaki veriler kullanılarak hazırlanmıştır.")
    metrics = {
        "Interest_Rate": "Faiz Oranı",
        "Inflation": "Enflasyon",
        "PMI": "PMI",
        "Growth_Rate": "Büyüme Oranı"
    }
    for col, label in metrics.items():
        st.markdown(f"###  Aylık Satış ve {label}")
        sales_df, macro_df, fig = macroeconomic_parameters(df_clean, macro_col=col, macro_label=label, plot=True)
        if fig:
          st.pyplot(fig)
    

    # Customer-Product Performance Matrix
    st.markdown("## Müşteri-Ürün Performans Analizi")
    st.markdown("2024 ve 2025 yıllarında satışı bulunan müşteri ürünler için hazırlanmıştır.Ürün her satış işleminde ortalama ne kadar para kazandırıyor sorusunun cevabını verir.")
    sales_revenue_product_customer(df_clean)
    # Product Performance Matrix
    st.markdown("## Ürün Performans Analizi")
    st.markdown("2024 ve 2025 yıllarında satışı bulunan ürünler için hazırlanmıştır.Ürün her satış işleminde ortalama ne kadar para kazandırıyor sorusunun cevabını verir.")
    sales_revenue_product(df_clean)
    
    #Yıllık çok satan 10 ürün
    st.title(" Yıllık En Çok Satan 10 Ürün Analizi")
    plot_top10_products_per_year(df_clean)

    #Yıllık çok satan 10 ürün
    st.title(" Yıllık En Çok Satan 10 Müşteri-Ürün Analizi")
    plot_top10_productsandcustomers_per_year(df_clean)



    

    
    
