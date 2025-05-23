import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

def plot_top_selling_product_customer_by_season(df, years=[2024, 2025]):
    """
    Her yıl için sezon bazında en çok satan 5 ürün–müşteri kombinasyonunu gösteren grafik üretir.

    Returns:
        Dict[int, matplotlib.figure.Figure]: Yıl → Grafik eşleşmesi
    """
    result_figures = {}
    df_filtered = df[df['Year'].isin(years)].copy()

    for year in years:
        year_df = df_filtered[df_filtered['Year'] == year]
        # Sezon + Ürün + Müşteri bazında satış toplamı
        sales = year_df.groupby(['Season', 'ProductName', 'CustomerName'])['Sale_Amount'].sum().reset_index()
        # Ürün + Müşteri ismini birleştir
        sales['Product_Customer'] = sales['ProductName'] + ' - ' + sales['CustomerName']
        # Her sezon için en çok satış yapan ilk 5 ürün–müşteri kombinasyonu
        top_combinations = (
            sales.groupby('Season')
            .apply(lambda x: x.sort_values('Sale_Amount', ascending=False).head(5))
            .reset_index(drop=True)
        )
        # Grafik çizimi
        fig, ax = plt.subplots(figsize=(14, 7))
        sns.barplot(data=top_combinations, x='Season', y='Sale_Amount', hue='Product_Customer', ax=ax)
        ax.set_title(f"{year} – Sezon Bazında En Çok Satılan Ürün–Müşteri Kombinasyonları", fontsize=14)
        ax.set_xlabel("Sezon", fontsize=12)
        ax.set_ylabel("Toplam Satış (Adet)", fontsize=12)
        ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
        ax.ticklabel_format(style='plain', axis='y')
        ax.grid(axis='y')
        ax.legend(title='Ürün - Müşteri', fontsize=9, title_fontsize=10, bbox_to_anchor=(1.02, 1), loc='upper left')
        fig.tight_layout()

        result_figures[year] = fig

    return result_figures
