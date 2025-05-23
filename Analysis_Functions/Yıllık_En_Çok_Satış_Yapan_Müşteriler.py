import matplotlib.pyplot as plt
import pandas as pd

# 1. Veriyi hazırla
df_test2 = df_test.copy()
df_test2 = df_test2[df_test2["Year"].between(2020, 2025)]
df_test2 = df_test2.sort_values(by="Date", ascending=True)

# 2. Yıl + Ürün bazında satışları toplayalım
sales_by_year_product = (
    df_test2
    .groupby(['Year', 'CustomerCode'])['Sale_Amount']
    .sum()
    .reset_index()
)

# 3. Her yılın en çok satan 10 ürününü bul
top10_per_year = (
    sales_by_year_product
    .sort_values(['Year', 'Sale_Amount'], ascending=[True, False])
    .groupby('Year')
    .head(5)
)

# 4. Her yılın Top 10 ürün satışlarını toplayalım
sum_top10_sales = top10_per_year.groupby('Year')['Sale_Amount'].sum().reset_index()

# 5. Her yılın Top 10 ürün isimlerini alt alta yazalım
top10_product_names = (
    top10_per_year.groupby('Year')['CustomerName']
    .apply(lambda names: '\n'.join(names))
    .reset_index()
)

# 6. Grafik çizimi
plt.figure(figsize=(16, 10))
bars = plt.bar(
    sum_top10_sales['Year'], 
    sum_top10_sales['Sale_Amount'], 
    color='skyblue', 
    width=0.6
)

# 7. Her sütunun içine 10 ürünün isimlerini yazalım
for bar, label in zip(bars, top10_product_names['CustomerName']):
    plt.text(
        bar.get_x() + bar.get_width()/2, 
        bar.get_height()/2,  # Sütunun ortasına yazı
        label,
        ha='center', 
        va='center', 
        fontsize=10, 
        color='black'
    )

# 8. Grafik ayarları
plt.title('2020-2025 Arası Yıllık En Çok Satış Yapılan 5 Müşteri ', fontsize=18)
plt.xlabel('Yıl', fontsize=14)
plt.ylabel('Toplam Satış Miktarı (Top 5 Müşteri)', fontsize=14)
plt.xticks(sum_top10_sales['Year'], fontsize=12)
plt.yticks(fontsize=12)

# 🔥 Bilimsel gösterimi kapat
plt.ticklabel_format(style='plain', axis='y')

plt.grid(axis='y')
plt.tight_layout()
plt.show()
