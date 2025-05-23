import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns 
import numpy as np 
import streamlit as st 

def sales_revenue_product_customer(df):
    """
    Ürün bazlı satış sayısı ve satış başına ortalama gelir analizini yapar,
    ürünleri dört segmente ayırır ve scatter plot ile Streamlit'te görselleştirir.
    """
    # 1. Filtreleme: Yalnızca 2024 ve 2025 verisi
    df_filtered = df[df["Year"] >= 2024].copy()

    # 2. Row Revenue hesapla
    df_filtered['Row_Revenue_TL'] = df_filtered['Sale_Amount'] * df_filtered['Unit_Price(TL)']
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
    last_dates = df_filtered.groupby(['CustomerName', 'ProductName'])['Date'].max().reset_index()
    last_dates.rename(columns={'Date': 'Last_Sale_Date'}, inplace=True)
    last_dates['Last_Sale_Date'] = last_dates['Last_Sale_Date'].dt.strftime('%d-%m-%Y')
    df_filtered = df_filtered.merge(last_dates, on=['CustomerName', 'ProductName'], how='left')

    # 3. Müşteri-Ürün bazında toplulaştırma
    summary = df_filtered.groupby(['CustomerName', 'ProductName']).agg(
        Sales_Count=('Sale_Amount', 'count'),
        Total_Revenue=('Row_Revenue_TL', 'sum'),
        Last_Sale_Date=('Last_Sale_Date', 'max')
    ).reset_index()

    # 4. Ortalama gelir
    summary['Avg_Revenue_Per_Sale'] = summary['Total_Revenue'] / summary['Sales_Count']
    sales_median = summary['Sales_Count'].median()
    revenue_median = summary['Avg_Revenue_Per_Sale'].median()

    # 5. Segment atama
    def assign_segment(row):
        if row['Sales_Count'] >= sales_median and row['Avg_Revenue_Per_Sale'] >= revenue_median:
            return 'High Sales - High Revenue'
        elif row['Sales_Count'] >= sales_median and row['Avg_Revenue_Per_Sale'] < revenue_median:
            return 'High Sales - Low Revenue'
        elif row['Sales_Count'] < sales_median and row['Avg_Revenue_Per_Sale'] >= revenue_median:
            return 'Low Sales - High Revenue'
        else:
            return 'Low Sales - Low Revenue'
        
    summary['Segment'] = summary.apply(assign_segment, axis=1)

    # 6. Görselleştirme (matplotlib + seaborn)
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.scatterplot(
        data=summary,
        x='Sales_Count', 
        y='Avg_Revenue_Per_Sale',
        hue='Segment',
        palette={
            'High Sales - High Revenue': 'green',
            'High Sales - Low Revenue': 'blue',
            'Low Sales - High Revenue': 'orange',
            'Low Sales - Low Revenue': 'red'
        },
        s=100,
        ax=ax
    )

    ax.axvline(x=70, color='gray', linestyle='--')
    ax.axhline(y=2.0e6, color='gray', linestyle='--')
    ax.set_title('Müşteri- Ürün Bazlı Satış Sayısı ve Ortalama Gelir Segmentasyonu', fontsize=18)
    ax.set_xlabel('Satış Sayısı', fontsize=14)
    ax.set_ylabel('Satış Başına Ortalama Gelir (₺)', fontsize=14)
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(True)
    ax.legend(title='Segment', fontsize=10, title_fontsize=12, loc='upper right')

    # 7. Streamlit üzerinden göster
    st.pyplot(fig)

    # Opsiyonel: tablo olarak da göster
    st.dataframe(summary.sort_values(by='Segment'))


def sales_revenue_product(df):
    """
    Ürün bazlı satış sayısı ve satış başına ortalama gelir analizini yapar,
    ürünleri dört segmente ayırır ve scatter plot ile Streamlit'te görselleştirir.
    """

    # 1. Filtreleme: Yalnızca 2024 ve 2025 verisi
    df_filtered = df[df["Year"] >= 2024].copy()

    # 2. Row Revenue hesapla
    df_filtered['Row_Revenue_TL'] = df_filtered['Sale_Amount'] * df_filtered['Unit_Price(TL)']
    df_filtered['Date'] = pd.to_datetime(df_filtered['Date'])
    last_dates = df_filtered.groupby(['ProductName'])['Date'].max().reset_index()
    last_dates.rename(columns={'Date': 'Last_Sale_Date'}, inplace=True)
    last_dates['Last_Sale_Date'] = last_dates['Last_Sale_Date'].dt.strftime('%d-%m-%Y')
    df_filtered = df_filtered.merge(last_dates, on=['ProductName'], how='left')

    # 3. Müşteri-Ürün bazında toplulaştırma
    summary = df_filtered.groupby(['ProductName']).agg(
        Sales_Count=('Sale_Amount', 'count'),
        Total_Revenue=('Row_Revenue_TL', 'sum'),
        Last_Sale_Date=('Last_Sale_Date', 'max')
    ).reset_index()

    # 4. Ortalama gelir
    summary['Avg_Revenue_Per_Sale'] = summary['Total_Revenue'] / summary['Sales_Count']
    sales_median = summary['Sales_Count'].median()
    revenue_median = summary['Avg_Revenue_Per_Sale'].median()

    # 5. Segment atama
    def assign_segment(row):
        if row['Sales_Count'] >= sales_median and row['Avg_Revenue_Per_Sale'] >= revenue_median:
            return 'High Sales - High Revenue'
        elif row['Sales_Count'] >= sales_median and row['Avg_Revenue_Per_Sale'] < revenue_median:
            return 'High Sales - Low Revenue'
        elif row['Sales_Count'] < sales_median and row['Avg_Revenue_Per_Sale'] >= revenue_median:
            return 'Low Sales - High Revenue'
        else:
            return 'Low Sales - Low Revenue'

    summary['Segment'] = summary.apply(assign_segment, axis=1)

    # 6. Görselleştirme (matplotlib + seaborn)
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.scatterplot(
        data=summary,
        x='Sales_Count', 
        y='Avg_Revenue_Per_Sale',
        hue='Segment',
        palette={
            'High Sales - High Revenue': 'green',
            'High Sales - Low Revenue': 'blue',
            'Low Sales - High Revenue': 'orange',
            'Low Sales - Low Revenue': 'red'
        },
        s=100,
        ax=ax
    )

    ax.axvline(x=70, color='gray', linestyle='--')
    ax.axhline(y=2.0e6, color='gray', linestyle='--')
    ax.set_title('Ürün Bazlı Satış Sayısı ve Ortalama Gelir Segmentasyonu', fontsize=18)
    ax.set_xlabel('Satış Sayısı', fontsize=14)
    ax.set_ylabel('Satış Başına Ortalama Gelir (₺)', fontsize=14)
    ax.ticklabel_format(style='plain', axis='y')
    ax.grid(True)
    ax.legend(title='Segment', fontsize=10, title_fontsize=12, loc='upper right')

    # 7. Streamlit üzerinden göster
    st.pyplot(fig)

    # Opsiyonel: tablo olarak da göster
    st.dataframe(summary.sort_values(by='Segment'))


