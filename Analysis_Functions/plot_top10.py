import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

def plot_top10_products_per_year(df: pd.DataFrame) -> None:
    """
    Her yıl (2020–2025) için en çok satan 10 ürünün toplam satışlarını çubuk grafik olarak gösterir.
    Her çubuğun içine o yılın top 10 ürün isimlerini yazar. Ayrıca detaylı tabloyu gösterir.

    Args:
        df (pd.DataFrame): Satış verisi. 'Year', 'Date', 'ProductName', 'Sale_Amount' sütunlarını içermelidir.
    """
    # Verinin kopyasını al ve yıl aralığını filtrele
    df_filtered = df.copy()
    df_filtered["Year"] = df_filtered["Year"].astype(int)
    df_filtered = df_filtered[df_filtered["Year"].between(2020, 2025)]
    df_filtered = df_filtered.sort_values(by="Date", ascending=True)

    # Yıl ve ürün bazında toplam satışları hesapla
    sales_by_year_product = (
        df_filtered
        .groupby(['Year', 'ProductName'])['Sale_Amount']
        .sum()
        .reset_index()
    )

    # Her yıl için en çok satan 10 ürünü bul
    top10_per_year = (
        sales_by_year_product
        .sort_values(['Year', 'Sale_Amount'], ascending=[True, False])
        .groupby('Year')
        .head(10)
    )

    # Her yılın top 10 ürünlerinin toplam satışını hesapla
    sum_top10_sales = top10_per_year.groupby('Year')['Sale_Amount'].sum().reset_index()

    # Her yılın top 10 ürün isimlerini birleştir (çubuk içine yazmak için)
    top10_product_names = (
        top10_per_year.groupby('Year')['ProductName']
        .apply(lambda names: '\n'.join(names))
        .reset_index()
    )

    # Grafik oluştur
    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(
        sum_top10_sales['Year'],
        sum_top10_sales['Sale_Amount'],
        color='skyblue',
        width=0.6
    )

    # Her çubuğun içine ürün isimlerini yaz
    for bar, label in zip(bars, top10_product_names['ProductName']):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            label,
            ha='center',
            va='center',
            fontsize=10,
            color='black'
        )

    # Grafik başlık ve eksen ayarları
    ax.set_title('2020–2025 Arası Yıllık En Çok Satan 10 Ürünler', fontsize=18)
    ax.set_xlabel('Yıl', fontsize=14)
    ax.set_ylabel('Toplam Satış Miktarı (Top 10 Ürün)', fontsize=14)
    ax.set_xticks(sum_top10_sales['Year'])
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(axis='y')

    # Streamlit ile grafiği ve tabloyu göster
    st.pyplot(fig)
    st.subheader("📄 Detaylı Ürün Satış Tablosu (Her Yılın En Çok Satan 10 Ürünü)")
    st.dataframe(top10_per_year.sort_values(['Year', 'Sale_Amount'], ascending=[True, False]))


def plot_top10_productsandcustomers_per_year(df: pd.DataFrame) -> None:
    """
    Her yıl (2020–2025) için en çok satan 10 müşteri-ürün kombinasyonunun toplam satışlarını çubuk grafik olarak gösterir.
    Her çubuğun içine o yılın top 10 müşteri-ürün kombinasyonunu yazar. Ayrıca detaylı tabloyu gösterir.

    Args:
        df (pd.DataFrame): Satış verisi. 'Year', 'Date', 'CustomerName', 'ProductName', 'Sale_Amount' sütunlarını içermelidir.
    """
    # Verinin kopyasını al ve yıl aralığını filtrele
    df_filtered = df.copy()
    df_filtered = df_filtered[df_filtered["Year"].between(2020, 2025)]
    df_filtered["Year"] = df_filtered["Year"].astype(int)
    df_filtered = df_filtered.sort_values(by="Date", ascending=True)

    # Yıl, müşteri ve ürün bazında toplam satışları hesapla
    sales_by_year_product_customer = (
        df_filtered
        .groupby(['Year', 'CustomerName', 'ProductName'])['Sale_Amount']
        .sum()
        .reset_index()
    )

    # Her yıl için en çok satan 10 müşteri-ürün kombinasyonunu bul
    top10_per_year_product = (
        sales_by_year_product_customer
        .sort_values(['Year', 'Sale_Amount'], ascending=[True, False])
        .groupby('Year')
        .head(10)
    )

    # Müşteri ve ürün adlarını birleştir (etiket olarak)
    top10_per_year_product['Label'] = (
        top10_per_year_product['CustomerName'] + " - " + top10_per_year_product['ProductName']
    )

    # Her yıl için etiketleri birleştir (çubuk içine yazmak için)
    top10_product_labels = (
        top10_per_year_product.groupby('Year')['Label']
        .apply(lambda names: '\n'.join(names))
        .reset_index()
    )

    # Her yılın top 10 müşteri-ürün kombinasyonunun toplam satışını hesapla
    sum_top10_sales = top10_per_year_product.groupby('Year')['Sale_Amount'].sum().reset_index()

    # Grafik oluştur
    fig, ax = plt.subplots(figsize=(16, 10))
    bars = ax.bar(
        sum_top10_sales['Year'],
        sum_top10_sales['Sale_Amount'],
        color='skyblue',
        width=0.6
    )

    # Her çubuğun içine müşteri-ürün etiketlerini yaz
    for bar, label in zip(bars, top10_product_labels['Label']):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() / 2,
            label,
            ha='center',
            va='center',
            fontsize=10,
            color='black'
        )

    # Grafik başlık ve eksen ayarları
    ax.set_title('2020–2025 Arası Yıllık En Çok Satan 10 Müşteri-Ürün', fontsize=18)
    ax.set_xlabel('Yıl', fontsize=14)
    ax.set_ylabel('Toplam Satış Miktarı (Top 10)', fontsize=14)
    ax.set_xticks(sum_top10_sales['Year'])
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(axis='y')

    # Streamlit ile grafiği ve tabloyu göster
    st.pyplot(fig)
    st.subheader("📄 Detaylı Satış Tablosu (Her Yılın En Çok Satan 10 Müşteri-Ürün)")
    st.dataframe(top10_per_year_product.sort_values(['Year', 'Sale_Amount'], ascending=[True, False]))