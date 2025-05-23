import pandas as pd
import streamlit as st

def filter_recent_customers(df, year_range=(2024, 2025)):
    """
    Filters the DataFrame to include only customers whose most recent sale occurred within the specified year range.

    Args:
        df (pd.DataFrame): Input sales data with 'CustomerCode' and 'Date' columns.
        year_range (tuple): Years to consider as recent (default: (2024, 2025)).

    Returns:
        pd.DataFrame: Filtered DataFrame containing only recent customers.
    """
    # Find the last sale date for each customer
    last_sales = df.groupby('CustomerCode')['Date'].max().reset_index()
    # Select customers whose last sale year is in the specified range
    recent_customers = last_sales[last_sales['Date'].dt.year.isin(year_range)]['CustomerCode'].unique()
    # Filter the original DataFrame for these customers
    return df[df['CustomerCode'].isin(recent_customers)]

def filter_recent_customers_products(df, year_range=(2024, 2025)):
    """
    Filters the DataFrame to include only customer-product pairs whose most recent sale occurred within the specified year range.

    Args:
        df (pd.DataFrame): Input sales data with 'CustomerCode', 'Product_Code', and 'Date' columns.
        year_range (tuple): Years to consider as recent (default: (2024, 2025)).

    Returns:
        pd.DataFrame: Filtered DataFrame containing only recent customer-product pairs.
    """
    # 1. Find last sale date for each customer-product pair
    last_sales = df.groupby(['CustomerCode', 'Product_Code'])['Date'].max().reset_index()
    # 2. Select pairs with last sale year in the specified range
    recent_pairs = last_sales[last_sales['Date'].dt.year.isin(year_range)][['CustomerCode', 'Product_Code']]
    # 3. Filter the original DataFrame for these pairs
    df_filtered = df.merge(recent_pairs, on=['CustomerCode', 'Product_Code'], how='inner')
    return df_filtered

def compute_customer_volatility(df):
    """
    Computes volatility score for each customer based on monthly sales.

    Args:
        df (pd.DataFrame): Input sales data with 'CustomerCode', 'CustomerName', 'Date', and 'Sale_Amount' columns.

    Returns:
        pd.DataFrame: DataFrame with customer code, name, last sale date, and volatility score.
    """
    # Add YearMonth column for monthly grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Calculate monthly sales per customer
    monthly = df.groupby(['CustomerCode', 'YearMonth'])['Sale_Amount'].sum().reset_index()
    # Compute standard deviation and mean of monthly sales
    vol = monthly.groupby('CustomerCode')['Sale_Amount'].agg(['std', 'mean']).reset_index()
    # Calculate volatility score as std/mean
    vol['Volatility_Score'] = vol['std'] / vol['mean']
    # Get customer names
    names = df.groupby('CustomerCode')['CustomerName'].first().reset_index()
    # Get last sale date for each customer
    last_sale = df.groupby('CustomerCode')['Date'].max().reset_index().rename(columns={'Date': 'Last_Sale_Date'})
    # Merge additional info
    vol = vol.merge(names, on='CustomerCode', how='left')
    vol = vol.merge(last_sale, on='CustomerCode', how='left')
    # Return relevant columns
    return vol[['CustomerCode', 'CustomerName', 'Last_Sale_Date', 'Volatility_Score']]

def compute_customer_product_volatility(df):
    """
    Computes volatility score for each customer-product pair based on monthly sales.

    Args:
        df (pd.DataFrame): Input sales data with 'CustomerCode', 'CustomerName', 'Product_Code', 'ProductName', 'Date', and 'Sale_Amount' columns.

    Returns:
        pd.DataFrame: DataFrame with customer code, name, product code, product name, last sale date, and volatility score.
    """
    # Add YearMonth column for monthly grouping
    df['YearMonth'] = df['Date'].dt.to_period('M')
    # Calculate monthly sales per customer-product pair
    monthly = df.groupby(['CustomerCode', 'Product_Code', 'YearMonth'])['Sale_Amount'].sum().reset_index()
    # Compute standard deviation and mean of monthly sales
    vol = monthly.groupby(['CustomerCode', 'Product_Code'])['Sale_Amount'].agg(['std', 'mean']).reset_index()
    # Calculate volatility score as std/mean
    vol['Volatility_Score'] = vol['std'] / vol['mean']
    # Get customer and product names
    customer_names = df.groupby('CustomerCode')['CustomerName'].first().reset_index()
    product_names = df.groupby('Product_Code')['ProductName'].first().reset_index()
    # Get last sale date for each customer-product pair
    last_sale = df.groupby(['CustomerCode', 'Product_Code'])['Date'].max().reset_index().rename(columns={'Date': 'Last_Sale_Date'})
    # Merge additional info
    vol = vol.merge(customer_names, on='CustomerCode', how='left')
    vol = vol.merge(product_names, on='Product_Code', how='left')
    vol = vol.merge(last_sale, on=['CustomerCode', 'Product_Code'], how='left')
    # Return relevant columns
    return vol[['CustomerCode', 'CustomerName', 'Product_Code', 'ProductName', 'Last_Sale_Date', 'Volatility_Score']]

def sales_volatility(df, top_n=10):
    """
    Displays and returns the top N customers and customer-product pairs with the highest sales volatility.

    Args:
        df (pd.DataFrame): Input sales data.
        top_n (int): Number of top results to display (default: 10).

    Returns:
        tuple: (customer volatility DataFrame, customer-product volatility DataFrame)
    """
    # Filter for recent customers
    df_filtered = filter_recent_customers(df)
    st.markdown("### 🔹 Müşteri Bazlı Volatilite Skoru")
    # Compute and display customer volatility
    cust_vol = compute_customer_volatility(df_filtered).sort_values('Volatility_Score', ascending=False)
    st.dataframe(cust_vol.head(top_n))

    # Filter for recent customer-product pairs
    df_filtered = filter_recent_customers_products(df)
    st.markdown("### 🔹 Müşteri-Ürün Bazlı Volatilite Skoru")
    # Compute and display customer-product volatility
    cust_prod_vol = compute_customer_product_volatility(df_filtered).sort_values('Volatility_Score', ascending=False)
    st.dataframe(cust_prod_vol.head(top_n))

    return cust_vol, cust_prod_vol
