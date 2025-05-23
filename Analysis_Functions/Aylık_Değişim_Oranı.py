import pandas as pd 
import numpy as np

def rate_of_change_per_month(df):
    """
    Calculates the monthly rate of change and volatility for each customer-product pair in the given sales DataFrame.
    The function performs the following steps:
    1. Converts the 'Date' column to datetime and extracts the year-month period.
    2. Aggregates total sales per customer, product, and month.
    3. For each customer-product pair:
      - If there are fewer than 6 months of data, marks the result as insufficient for calculation.
      - Otherwise, computes the mean, standard deviation, and volatility ratio (std/mean) of monthly sales.
      - Classifies volatility as 'Düşük Değişkenlik' (Low), 'Orta Değişkenlik' (Medium), or 'Yüksek Değişkenlik' (High).
    4. Adds the date of the last sale for each customer-product pair.
    5. Filters results to include only those with the last sale date in 2024 or later.
    6. Returns the last 15 rows of the filtered results, sorted by volatility ratio in descending order.
    Parameters:
      df (pd.DataFrame): Input DataFrame containing at least the following columns:
        - 'Date': Date of sale (string or datetime)
        - 'CustomerCode': Identifier for the customer
        - 'Product_Code': Identifier for the product
        - 'Sale_Amount': Amount of sale (numeric)
    Returns:
      pd.DataFrame: A DataFrame with the following columns for each customer-product pair:
        - 'CustomerCode'
        - 'Product_Code'
        - 'Ay_Sayısı' (Number of months with sales data)
        - 'Aylık_Ortalama' (Monthly average sales)
        - 'StdSapma' (Standard deviation of monthly sales)
        - 'Volatilite_Oranı' (Volatility ratio)
        - 'Değişkenlik_Durumu' (Volatility classification)
        - 'Last_Sale_Date' (Date of last sale)
      Only includes pairs with last sale date in 2024 or later, and returns the last 15 rows.
    """
    df['Date'] = pd.to_datetime(df['Date'])
    df['YearMonth'] = df['Date'].dt.to_period('M')

    # Müşteri-Ürün-YılAy bazında toplam satış
    monthly_sales = df.groupby(['CustomerCode', 'Product_Code', 'YearMonth'])['Sale_Amount'].sum().reset_index()
    # Son satış tarihi
    last_sales = df.groupby(['CustomerCode', 'Product_Code'])['Date'].max().reset_index().rename(columns={'Date': 'Last_Sale_Date'})
    results = []

    for (customer, product), group in monthly_sales.groupby(['CustomerCode', 'Product_Code']):
        sales_series = group.sort_values('YearMonth')['Sale_Amount'].values
        if len(sales_series) < 6:  # 6 aydan az veri varsa
            results.append({
                'CustomerCode': customer,
                'Product_Code': product,
                'Ay_Sayısı': len(sales_series),
                'Aylık_Ortalama': None,
                'StdSapma': None,
                'Volatilite_Oranı': None,
                'Değişkenlik_Durumu': '6 Aydan az veriye sahiptir hesaplanamaz',
                'Last_Sale_Date': last_sales[(last_sales['CustomerCode'] == customer) & (last_sales['Product_Code'] == product)]['Last_Sale_Date'].values[0]
            })
        else:
            mean = sales_series.mean()
            std = sales_series.std()
            volatility_ratio = std / mean if mean != 0 else None

            if volatility_ratio is None:
                volatility_label = 'Sabit (0 ortalama)'
            elif volatility_ratio < 0.3:
                volatility_label = 'Düşük Değişkenlik'
            elif volatility_ratio < 1.0:
                volatility_label = 'Orta Değişkenlik'
            else:
                volatility_label = 'Yüksek Değişkenlik'

            results.append({
                'CustomerCode': customer,
                'Product_Code': product,
                'Ay_Sayısı': len(sales_series),
                'Aylık_Ortalama': round(mean, 2),
                'StdSapma': round(std, 2),
                'Volatilite_Oranı': round(volatility_ratio, 2) if volatility_ratio is not None else None,
                'Değişkenlik_Durumu': volatility_label,
                'Last_Sale_Date': last_sales[(last_sales['CustomerCode'] == customer) & (last_sales['Product_Code'] == product)]['Last_Sale_Date'].values[0]
            })

    volatility_df = pd.DataFrame(results)
    volatility_df.sort_values(by='Volatilite_Oranı', ascending=True, inplace=True, na_position='last')
    volatility_df["Year"]=volatility_df["Last_Sale_Date"].dt.year
    df_final = volatility_df[volatility_df["Year"] >= 2024]
    df_final = df_final.drop(columns=["Year"])
    return df_final