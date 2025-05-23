
import pandas as pd 
import numpy as np


import pandas as pd 
import numpy as np

def yıllık_satış_rakamları(df):
    df_test = df.copy()
    mask = df[df['Year'].isin([2024, 2025])]
    pairs = mask[['CustomerCode', 'Product_Code']].drop_duplicates()
    filtered = df.merge(pairs, on=['CustomerCode', 'Product_Code'], how='inner')
    filtered['Year'] = filtered['Date'].dt.year
    filtered['Month'] = filtered['Date'].dt.month

    # Pivot tablo: her yıl ve ay için ayrı sütun
    monthly_sales = filtered.pivot_table(
        index=['CustomerCode', 'Product_Code'],
        columns=['Year', 'Month'],
        values='Sale_Amount',
        aggfunc='sum',
        fill_value=0
    )

    # Sütun isimlerini "YYYY-AyAdı" şeklinde yap
    aylar = {1: 'Ocak', 2: 'Şubat', 3: 'Mart', 4: 'Nisan', 5: 'Mayıs', 6: 'Haziran',
             7: 'Temmuz', 8: 'Ağustos', 9: 'Eylül', 10: 'Ekim', 11: 'Kasım', 12: 'Aralık'}
    monthly_sales.columns = [f"{year}-{aylar[month]}" for year, month in monthly_sales.columns]
    monthly_sales = monthly_sales.reset_index()

    # Son satış tarihi, müşteri ve ürün adı ekle
    last_sales = (
        filtered.groupby(['CustomerCode', 'Product_Code'])
        .agg(
            Last_Sale_Date=('Date', 'max'),
            CustomerName=('CustomerName', 'first'),
            ProductName=('ProductName', 'first')
        )
        .reset_index()
    )
    monthly_sales = monthly_sales.merge(last_sales, on=['CustomerCode', 'Product_Code'], how='left')

    return monthly_sales

