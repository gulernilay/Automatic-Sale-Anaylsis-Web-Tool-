from sklearn.linear_model import LinearRegression
import numpy as np
import pandas as pd 
import streamlit as st

def aging_factor_analysis(df):
    """
    Analyze sales aging trends for customer-product pairs within a DataFrame.

    This function filters the input DataFrame for sales data in the years 2024 and 2025,
    identifies unique customer-product pairs, and computes monthly sales aggregates.
    For each customer-product pair with more than 6 months of sales data, it fits a linear
    regression model to the monthly sales amounts to determine the sales trend (increasing,
    decreasing, or stable). The function returns a DataFrame summarizing the trend, slope,
    first and last month sales, and last sale date for each qualifying pair.

    Parameters
    ----------
    df : pandas.DataFrame
      Input DataFrame containing at least the following columns:
      - 'Year': int, year of the sale
      - 'Date': datetime, date of the sale
      - 'CustomerCode': identifier for the customer
      - 'Product_Code': identifier for the product
      - 'Sale_Amount': numeric, amount of the sale
      - 'CustomerName': name of the customer
      - 'ProductName': name of the product

    Returns
    -------
    pandas.DataFrame
      DataFrame with columns:
      - 'CustomerCode'
      - 'Product_Code'
      - 'Toplam Kaç Aylık Satış Var': number of months with sales data
      - 'Satış_Eğilimi': sales trend ('Artıyor', 'Azalıyor', 'Sabit')
      - 'Eğim': slope of the sales trend
      - 'İlk_Ay_Satış': sales amount in the first month
      - 'Son_Ay_Satış': sales amount in the last month
      - 'Last_Sale_Date': date of the last sale
      - 'CustomerName'
      - 'ProductName'

    Notes
    -----
    - Only customer-product pairs with more than 6 months of sales data are analyzed.
    - Sales trend is determined by the sign of the regression slope.
    - The function requires pandas, numpy, and scikit-learn's LinearRegression.
    """
    mask = df[df['Year'].isin([2024, 2025])]
    pairs = mask[['CustomerCode', 'Product_Code']].drop_duplicates()
    filtered = df.merge(pairs, on=['CustomerCode', 'Product_Code'], how='inner')
    filtered['YearMonth'] = filtered['Date'].dt.to_period('M').astype(str)
    last_sales = (
        filtered.groupby(['CustomerCode', 'Product_Code'])
        .agg(Last_Sale_Date=('Date', 'max'))
        .reset_index()
    )
    monthly_sales = (
        filtered
        .groupby(['YearMonth', 'CustomerCode', 'Product_Code'])
        .agg(Sale_Amount=('Sale_Amount', 'sum'))
        .reset_index()
    )
    monthly_sales = monthly_sales.merge(
        last_sales, 
        on=['CustomerCode', 'Product_Code'],
        how='left'
    )
    monthly_sales['YearMonth'] = pd.to_datetime(monthly_sales['YearMonth'])
    monthly_sales['Sale_Amount_Log'] = np.log(monthly_sales['Sale_Amount'].replace(0, 1e-5))
    monthly_sales['Year'] = monthly_sales['YearMonth'].dt.year
    monthly_sales['Month'] = monthly_sales['YearMonth'].dt.month 
    monthly_sales.sort_values(by="YearMonth", ascending=True, inplace=True)
    name_map = filtered[['CustomerCode', 'Product_Code', 'CustomerName', 'ProductName']].drop_duplicates()
    aging_trends = []
    for (customer, product), group in monthly_sales.groupby(['CustomerCode', 'Product_Code']):
        group_sorted = group.sort_values('YearMonth')
        sales = group_sorted['Sale_Amount'].values
        periods = np.arange(len(sales)).reshape(-1, 1)
        if len(sales) > 6:
            model = LinearRegression().fit(periods, sales)
            slope = model.coef_[0]
            if slope > 0:
                trend = 'Artıyor'
            elif slope < 0:
                trend = 'Azalıyor'
            elif slope == 0:
                trend = 'Sabit'
            else:
                trend = "6 aydan az satış verisi olduğu için hesaplanamaz."
            # Son satış tarihi ekle
            last_sale_date = group_sorted['Last_Sale_Date'].iloc[0]
            aging_trends.append({
                'CustomerCode': customer,
                'Product_Code': product,
                'Toplam Kaç Aylık Satış Var': len(sales),
                'Satış_Eğilimi': trend,
                'Eğim': round(slope, 2),
                'İlk_Ay_Satış': sales[0],
                'Son_Ay_Satış': sales[-1],
                'Last_Sale_Date': last_sale_date
            })
    aging_trend_df = pd.DataFrame(aging_trends)
    aging_trend_df = aging_trend_df.merge(name_map, on=['CustomerCode', 'Product_Code'], how='left')
    aging_trend_df.sort_values(by="Satış_Eğilimi", ascending=True, inplace=True)
    return aging_trend_df