import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

def seasonal_sales_by_year(df, years=[2020, 2021, 2022, 2023, 2024, 2025], plot=True):
    """
    Sezon ve yıl bazında toplam satışları hesaplar. İsteğe bağlı olarak grafiğini çizer.
    
    Parametreler:
    - df: DataFrame (içinde 'Season', 'Year' ve 'Sale_Amount' sütunları olmalı)
    - years: Gösterilecek yıl listesi
    - plot: True ise grafik çizer

    Geri dönüş: Sezon & yıl bazında toplam satışlar (DataFrame)
    """
    # Yalnızca belirtilen yıllardaki verileri filtrele
    df_filtered = df[df["Year"].isin(years)].copy()
    
    # Sezon ve yıl bazında toplam satışları grupla ve hesapla
    sales_by_season_year = df_filtered.groupby(['Season', 'Year'])['Sale_Amount'].sum().reset_index()

    if plot:
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(14,8))
        sns.barplot(data=sales_by_season_year, x='Season', y='Sale_Amount', hue='Year', ax=ax)
        # Y eksenini binlik ayırıcı ile biçimlendir
        ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        ax.set_title('2020-2025 Yılları Arasında Sezon Bazlı Toplam Satışlar')
        ax.set_xlabel('Sezon')
        ax.set_ylabel('Toplam Satış Adedi')
        ax.grid(axis='y')
        ax.legend(title='Yıl')
        plt.tight_layout()
        # Sonuçları ve grafiği döndür
        return sales_by_season_year, fig

    # Sadece sonuçları döndür
    return sales_by_season_year, None