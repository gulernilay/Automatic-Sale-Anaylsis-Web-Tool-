import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.ticker as mticker
import pandas as pd

def ay_bazli_satis_analizi(df: pd.DataFrame, selected_year: int = None) -> None:
    """
    Belirli bir yıl için ayın farklı dönemlerindeki (baş, orta, son) toplam satışları analiz eder ve görselleştirir.

    Args:
        df (pd.DataFrame): Satış verilerini içeren DataFrame. 'Year', 'Date' ve 'Sale_Amount' sütunlarını içermelidir.
        selected_year (int, optional): Analiz yapılacak yıl. Belirtilmezse kullanıcıdan seçim istenir.

    Returns:
        None. Sonuçlar Streamlit arayüzünde görselleştirilir ve tablo olarak sunulur.
    """
    st.header("Ay Bazlı Dönemsel Satış Analizi")

    # Yılları otomatik olarak listele
    available_years = sorted(df["Year"].dropna().unique(), reverse=True)

    # Yıl seçimi
    year = selected_year if selected_year is not None else st.selectbox("Analiz yapılacak yılı seçiniz:", available_years)

    # Seçilen yıl için veriyi filtrele
    df_filtered = df[df["Year"] == year].copy()
    if df_filtered.empty:
        st.warning(f"{year} yılına ait veri bulunamadı.")
        return

    # Tarihe göre satışları grupla ve ayın dönemini etiketle
    sales_by_date = (
        df_filtered.groupby('Date', as_index=False)['Sale_Amount'].sum()
        .assign(
            Day=lambda x: x['Date'].dt.day,
            Period=lambda x: x['Day'].apply(
                lambda d: 'Ay Başı (1-10)' if d <= 10 else ('Ay Ortası (11-20)' if d <= 20 else 'Ay Sonu (21-31)')
            )
        )
    )

    # Döneme göre toplam satışları hesapla
    period_sales = sales_by_date.groupby('Period', as_index=False)['Sale_Amount'].sum()

    # Sonuçları görselleştir
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(data=period_sales, x='Period', y='Sale_Amount', ax=ax)
    ax.set_title(f'{year} Yılında Ay Bazlı Dönemsel Satışlar')
    ax.set_ylabel('Toplam Satış Adedi')
    ax.set_xlabel('Ayın Dönemi')
    ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
    ax.grid(axis='y')
    plt.tight_layout()

    # Grafik ve tabloyu göster
    st.pyplot(fig)
    st.markdown("### 📄 Dönem Bazlı Satış Verisi")
    st.dataframe(period_sales)
