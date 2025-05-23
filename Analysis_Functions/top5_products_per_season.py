import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

def top5_products_per_season(df, years=[2024, 2025]):
    """
    Her yıl için ayrı sezon bazlı en çok satan 5 ürün grafiği üretir.

    Returns:
        Dict[int, matplotlib.figure.Figure]: Yıl → Grafik eşleşmesi
    """
    result_figures = {}  # Sonuçları saklamak için bir sözlük
    df_filtered = df[df['Year'].isin(years)].copy()  # Sadece belirtilen yılları filtrele

    for year in years:
        year_df = df_filtered[df_filtered['Year'] == year]  # O yılın verisini al
        # Sezon ve ürün bazında satış adedini say
        sales = year_df.groupby(['Season', 'ProductName'])['Sale_Amount'].count().reset_index()

        # Her sezon için en çok satan 5 ürünü seç
        top_products = (
            sales.groupby('Season')
            .apply(lambda x: x.sort_values('Sale_Amount', ascending=False).head(5))
            .reset_index(drop=True)
        )

        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=top_products, x='Season', y='Sale_Amount', hue='ProductName', ax=ax)
        # ax.set_title(f"{year} – Sezon Bazında En Çok Satılan 5 Ürün", fontsize=14)
        ax.set_xlabel("Sezon", fontsize=12)
        ax.set_ylabel("Toplam Satış (Adet)", fontsize=12)
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(axis='y')
        ax.legend(title='Ürün', fontsize=10, title_fontsize=11, bbox_to_anchor=(1.02, 1), loc='upper left')
        fig.tight_layout()

        result_figures[year] = fig  # Sonuç sözlüğüne ekle

    return result_figures  # Yıl → Grafik eşleşmesini döndür