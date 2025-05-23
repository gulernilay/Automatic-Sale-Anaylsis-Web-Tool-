import pandas as pd 
import numpy as np 
import matplotlib.pyplot as pt 
import streamlit as st 


def _calculate_active_months(df, group_cols):
  """
  Calculates the number of active months, total months between first and last sale, and the percentage of active months for each group in the DataFrame.

  This function filters groups whose last sale occurred in the years 2024 or 2025, then computes:
    - The number of unique months with sales ("Active_Months")
    - The first and last sale dates for each group
    - The total number of months between the first and last sale (inclusive)
    - The percentage of active months over the total possible months

  Args:
    df (pd.DataFrame): Input DataFrame containing at least a 'Date' column (datetime64) and columns specified in `group_cols`.
    group_cols (list of str): List of column names to group by (e.g., customer or product identifiers).

  Returns:
    pd.DataFrame: DataFrame with one row per group, containing:
      - group columns
      - 'Active_Months': Number of unique months with sales
      - 'First_Sale_Date': Date of first sale in the filtered period
      - 'Last_Sale_Date': Date of last sale in the filtered period
      - 'Total_Months': Number of months between first and last sale (inclusive)
      - 'Active_Months_Percentage': Percentage of active months over total months (rounded to 2 decimals)
  """
  # Copy the DataFrame to avoid modifying the original
  df = df.copy()
  # Create a YearMonth column for grouping by month
  df['YearMonth'] = df['Date'].dt.to_period('M')
  # Find the last sale date for each group
  last_sale = df.groupby(group_cols)['Date'].max().reset_index().rename(columns={'Date': 'Last_Sale_Date'})
  # Filter groups whose last sale is in 2024 or 2025
  valid_groups = last_sale[last_sale['Last_Sale_Date'].dt.year.isin([2024, 2025])][group_cols]
  # Keep only rows belonging to valid groups
  df_filtered = df.merge(valid_groups, on=group_cols, how='inner')
  df_filtered['YearMonth'] = df_filtered['Date'].dt.to_period('M')
  # Find first and last sale dates for each group
  first_sale = df_filtered.groupby(group_cols)['Date'].min().reset_index().rename(columns={'Date': 'First_Sale_Date'})
  last_sale = df_filtered.groupby(group_cols)['Date'].max().reset_index().rename(columns={'Date': 'Last_Sale_Date'})
  # Count unique months with sales for each group
  active_months = df_filtered.groupby(group_cols)['YearMonth'].nunique().reset_index().rename(columns={'YearMonth': 'Active_Months'})
  # Merge results
  result = active_months.merge(first_sale, on=group_cols, how='left').merge(last_sale, on=group_cols, how='left')
  # Calculate total months between first and last sale (inclusive)
  result['Total_Months'] = ((result['Last_Sale_Date'].dt.to_period('M') - result['First_Sale_Date'].dt.to_period('M')).apply(lambda x: x.n) + 1)
  # Calculate percentage of active months
  result['Active_Months_Percentage'] = (result['Active_Months'] / result['Total_Months'] * 100).round(2)
  return result

def _add_category_and_rename(result, regular_label, irregular_label):
  """
  Adds a 'Category' column to the result DataFrame based on customer activity and renames specific columns.

  Parameters:
    result (pd.DataFrame): The DataFrame containing customer sales data. Must include the columns:
      - 'Total_Months'
      - 'Active_Months_Percentage'
      - 'Last_Sale_Date'
      - 'First_Sale_Date'
      - 'Active_Months'
      - 'Active_Months_Percentage'
    regular_label (str): Label to assign for regular customers (active months percentage >= 80).
    irregular_label (str): Label to assign for irregular customers (active months percentage < 80).

  Returns:
    pd.DataFrame: The modified DataFrame with:
      - A new 'Category' column indicating customer type.
      - Renamed columns for improved readability.
  """
  result['Category'] = np.where(
    result['Total_Months'] == 1, "Hesaplanamaz",
    np.where(result['Active_Months_Percentage'] >= 80, regular_label, irregular_label)
  )
  return result.rename(columns={
    "Last_Sale_Date": "Son Satış Tarihi",
    "First_Sale_Date": "İlk Satış Tarihi",
    "Active_Months": "Satış Yapılan Ay Sayısı",
    "Total_Months": "Müşteri Yaşam Süresi(Ay Sayısı)",
    "Active_Months_Percentage": "Devamlılık Oranı "
  })

def düzenlisiparişverenler_aralıklı_müşteriler_ürünler(df):
  """
  Identifies and categorizes customers and products based on their order regularity.

  This function processes the input DataFrame to calculate active months for each combination
  of 'CustomerName' and 'ProductName'. It then categorizes the results into 'Düzenli Sipariş Verenler'
  (Regular Orderers) and 'Aralıklı Sipariş Verenler' (Intermittent Orderers), and renames the relevant columns.

  Args:
    df (pd.DataFrame): Input DataFrame containing at least 'CustomerName' and 'ProductName' columns.

  Returns:
    pd.DataFrame: A DataFrame with categorized and renamed columns indicating order regularity for each customer-product pair.
  """
  result = _calculate_active_months(df, ['CustomerName', 'ProductName'])
  return _add_category_and_rename(result, 'Düzenli Sipariş Verenler', 'Aralıklı Sipariş Verenler')

def düzenlisiparişverenler_aralıklımüşteriler(df):
  """
  Identifies and categorizes customers as 'Düzenli Sipariş Verenler' (Regular Orderers) or 'Aralıklı Sipariş Verenler' (Intermittent Orderers) based on their order activity.

  Args:
    df (pd.DataFrame): Input DataFrame containing customer order data. Must include a 'CustomerName' column.

  Returns:
    pd.DataFrame: DataFrame with customers categorized and columns renamed accordingly.
  """
  result = _calculate_active_months(df, ['CustomerName'])
  return _add_category_and_rename(result, 'Düzenli Sipariş Verenler', 'Aralıklı Sipariş Verenler')

def düzenlisiparişverenler_aralıklıürünler(df):
  """
  Identifies customers who place regular orders for products at intervals.
  This function processes the given DataFrame to determine active months for each product
  and categorizes them as 'Düzenli Sipariş Verilenler' (Regular Orderers) and 
  'Aralıklı Sipariş Verilenler' (Interval Orderers).
  Args:
    df (pd.DataFrame): Input DataFrame containing order data. Must include a 'ProductName' column.
  Returns:
    pd.DataFrame: DataFrame with categorized and renamed columns indicating regular and interval orderers.
  """
  
  result = _calculate_active_months(df, ['ProductName'])
  return _add_category_and_rename(result, 'Düzenli Sipariş Verilenler', 'Aralıklı Sipariş Verilenler')


def aylik_en_yuksek_ciroya_sahip_3_musteri(df):
    """
    Finds the top 3 customers with the highest monthly revenue (Ciro) for each month starting from January 2024.

    Parameters:
      df (pd.DataFrame): Input DataFrame containing at least the following columns:
        - 'Sale_Amount': Number of units sold.
        - 'Unit_Price(TL)': Price per unit in TL.
        - 'Date': Date of the sale (should be datetime type).
        - 'CustomerName': Name of the customer.

    Returns:
      pd.DataFrame: A DataFrame with columns:
        - 'YearMonth': Year and month of the sale (as pandas Period).
        - 'CustomerName': Name of the customer.
        - 'Ciro(TL)': Total revenue for the customer in that month.

    Notes:
      - Only includes data from January 2024 onwards.
      - For each month, returns the top 3 customers by total revenue.
    """
    # Calculate revenue
    df['Ciro(TL)'] = df['Sale_Amount'] * df['Unit_Price(TL)']
    # Create YearMonth column for monthly grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Filter for data from January 2024 onwards
    df = df[df['YearMonth'] >= pd.Period('2024-01', freq='M')]
    # Calculate total revenue per customer per month
    monthly_revenue = df.groupby(['CustomerName', 'YearMonth'])['Ciro(TL)'].sum().reset_index()
    # For each month, get the top 3 customers with the highest revenue
    top3 = (
      monthly_revenue
      .sort_values(['YearMonth', 'Ciro(TL)'], ascending=[True, False])
      .groupby('YearMonth')
      .head(3)
      .reset_index(drop=True)
    )
    # Return only customer names, year-month, and revenue
    return top3[['YearMonth', 'CustomerName', 'Ciro(TL)']]

def aylik_en_yuksek_ciroya_sahip_3_ürün(df):
    """
    Belirtilen DataFrame'den, 2024 Ocak ve sonrasındaki her ay için en yüksek ciroya sahip ilk 3 ürünü döndürür.

    Parametreler:
      df (pd.DataFrame): Satış verilerini içeren DataFrame. 
        Gerekli sütunlar: 'Sale_Amount', 'Unit_Price(TL)', 'Date', 'ProductName'.

    Dönüş:
      pd.DataFrame: Her yıl-ay ('YearMonth') için en yüksek ciroya sahip ilk 3 ürünün
        ürün adı ('ProductName') ve ciro ('Ciro(TL)') ile birlikte listelendiği DataFrame.
    """
    # Calculate revenue
    df['Ciro(TL)'] = df['Sale_Amount'] * df['Unit_Price(TL)']
    # Create YearMonth column for monthly grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Filter for data from January 2024 onwards
    df = df[df['YearMonth'] >= pd.Period('2024-01', freq='M')]
    # Calculate total revenue per product per month
    monthly_revenue = df.groupby(['ProductName', 'YearMonth'])['Ciro(TL)'].sum().reset_index()
    # For each month, get the top 3 products with the highest revenue
    top3 = (
      monthly_revenue
      .sort_values(['YearMonth', 'Ciro(TL)'], ascending=[True, False])
      .groupby('YearMonth')
      .head(3)
      .reset_index(drop=True)
    )
    # Return only product names, year-month, and revenue
    return top3[['YearMonth', 'ProductName', 'Ciro(TL)']]


def ençoksatan_enazsatanürünler_ciroveadetbazlı(df_test):
    return 


def cirobüyümeoranı_yoy_mom(df_test):
  return 


def CustomerLifetimevalue(df_test):
  return 


def RFM_Analysis(df_test):
  return 

def FiyatDeğişikliğiSonrasıSatışEtkisi(df_test):
  return 





