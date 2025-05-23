import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

def plot_top_products_by_season(df, years=[2024, 2025]):
    """
    Her yıl için ayrı sezon bazlı en çok satan 5 ürün grafiği üretir.

    Returns:
        Dict[int, matplotlib.figure.Figure]: Yıl → Grafik eşleşmesi
    """
    result_figures = {}
    # Sadece belirtilen yılları filtrele
    df_filtered = df[df['Year'].isin(years)].copy()

    for year in years:
        # İlgili yılın verilerini al
        year_df = df_filtered[df_filtered['Year'] == year]
        # Sezon ve ürün bazında toplam satış miktarını hesapla
        sales = year_df.groupby(['Season', 'ProductName'])['Sale_Amount'].sum().reset_index()

        # Her sezon için en çok satan 5 ürünü seç
        top_products = (
            sales.groupby('Season')
            .apply(lambda x: x.sort_values('Sale_Amount', ascending=False).head(5))
            .reset_index(drop=True)
        )

        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_products, x='Season', y='Sale_Amount', hue='ProductName', ax=ax)
        #ax.set_title(f"{year} – Sezon Bazında En Çok Satılan 5 Ürün", fontsize=14)
        ax.set_xlabel("Sezon", fontsize=12)
        ax.set_ylabel("Toplam Satış (Adet)", fontsize=12)
        # Y eksenini düz sayı formatında göster
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(axis='y')
        # Legend ayarları
        ax.legend(title='Ürün', fontsize=10, title_fontsize=11, bbox_to_anchor=(1.02, 1), loc='upper left')
        fig.tight_layout()

        # Sonuç sözlüğüne ekle
        result_figures[year] = fig

    return result_figures