import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 
import streamlit as st 

def classify_segment(row):
    """
    Classifies a customer-product pair into a segment based on sales volatility (coefficient of variation),
    trend (slope), and recency of last sale.
    Parameters:
        row (pd.Series): A row containing 'Last_Sale_Date', 'coef_var', and 'Slope' fields.
    Returns:
        str: Segment label for the customer-product pair.
    """
    today = pd.to_datetime('today')  # Get today's date
    try:
        last_sale = pd.to_datetime(row['Last_Sale_Date'])  # Parse last sale date
    except:
        # If date parsing fails, return missing data segment
        return "Veri Eksikliği Olan Müşteri - Ürünler"
    cv = row['coef_var']  # Coefficient of variation (volatility)
    slope = row['Slope']  # Trend slope
    # If last sale was more than 180 days ago, mark as inactive
    if (today - last_sale).days > 180:
        return "Pasif Durumdaki Müşteri - Ürünler"
    # Low volatility
    if cv <= 0.01:
        if slope > 0:
            return "Stabil Büyüyen Müşteri - Ürünler"
        elif slope < 0:
            return "Stabil Düşüş Gösteren Müşteri - Ürünler"
        else:
            return "Sabit Satış Trendine Sahip Müşteri - Ürünler"
    # Moderate volatility
    elif cv <= 0.5:
        if slope > 0:
            return "İstikrarlı Büyüyen Müşteri - Ürünler"
        elif slope < 0:
            return "İstikrarlı Düşüş Gösteren Müşteri - Ürünler"
        else:
            return "İstikrarlı Stabil Müşteri - Ürünler"
    # High volatility
    else:
        if slope > 0:
            return "Dalgalı Ancak Büyüyen Müşteri - Ürünler"
        elif slope < 0:
            return "Dalgalı ve Düşüş Gösteren Müşteri - Ürünler"
        else:
            return "Dalgalı Stabil Müşteri - Ürünler"
    # Fallback for undefined cases
    return "Tanımlanamayan Ürünler"


def combine_trend_volatility_results(trend_df_customer_product, volatility_df_customer_product, df_clean):
    """
    Combines trend and volatility analysis results for customer-product pairs, enriches with customer and product names,
    applies segmentation, and displays the results in a Streamlit dataframe.

    Args:
        trend_df_customer_product (pd.DataFrame): DataFrame containing trend analysis results for each customer-product pair.
        volatility_df_customer_product (pd.DataFrame): DataFrame containing volatility analysis results for each customer-product pair.
        df_clean (pd.DataFrame): Cleaned DataFrame containing customer and product information.

    Returns:
        pd.DataFrame: Combined DataFrame with trend, volatility, customer/product info, and segmentation results.

    Notes:
        - The function merges trend and volatility data on 'CustomerCode' and 'Product_Code'.
        - Customer and product names are added from df_clean.
        - Segmentation is performed using the classify_segment function.
        - The results are displayed using Streamlit's dataframe component.
    """
    # Merge trend and volatility results on customer and product codes
    combined_df_customer_product = pd.merge(
        trend_df_customer_product, 
        volatility_df_customer_product, 
        on=['CustomerCode', 'Product_Code'], 
        how='left'
    )
    # Prepare customer and product name info from cleaned data
    customer_product_info = df_clean[['CustomerCode', 'CustomerName', 'Product_Code', 'ProductName']].drop_duplicates()

    # Merge customer and product names into the combined dataframe
    combined_df_customer_product = pd.merge(
        combined_df_customer_product, 
        customer_product_info, 
        on=['CustomerCode', 'Product_Code'], 
        how='left'
    )
    # Apply segmentation using classify_segment function
    combined_df_customer_product['Segment'] = combined_df_customer_product.apply(classify_segment, axis=1)
    combined_df_customer_product['Segment_Refined'] = combined_df_customer_product.apply(classify_segment, axis=1)
    # Copy refined segment to main segment column
    combined_df_customer_product['Segment'] = combined_df_customer_product['Segment_Refined'].copy()

    # Sort by segment for better display
    combined_df_customer_product.sort_values(by="Segment", ascending=False, inplace=True)

    # Display results in Streamlit
    st.markdown("### MÜŞTERİ-ÜRÜN SEGMENTASYONU")
    columns_to_show = ['CustomerCode', 'CustomerName', 'Product_Code', 'ProductName', 'Last_Sale_Date', 'Segment']
    st.dataframe(combined_df_customer_product[columns_to_show].reset_index(drop=True))

    return combined_df_customer_product
    
