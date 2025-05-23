import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def volatility_analysis(df):
    """
    Perform sales volatility (coefficient of variation, CV) analysis on the given DataFrame.

    The function generates two analyses:
    1. Customer-Product based CV analysis: Calculates the CV for each customer-product pair
       where the last sale date is after 2024-06-01, and displays the top 25 riskiest pairs.
    2. Product based CV analysis: Calculates the CV for each product where the last sale date
       is after 2024-06-01, and displays the top 25 riskiest products.

    Visualizations and data tables are rendered using Streamlit.

    Parameters:
        df (pd.DataFrame): Input DataFrame containing at least the following columns:
            - 'CustomerCode', 'Product_Code', 'ProductName', 'CustomerName', 'Date', 'Sale_Amount'

    Returns:
        tuple: (volatility_cp, volatility_p)
            - volatility_cp (pd.DataFrame): Customer-Product based volatility results.
            - volatility_p (pd.DataFrame): Product based volatility results.
    """
    st.subheader("SATIŞ VOLATİLİTESİ ANALİZİ")

    # --- Customer-Product Based Volatility ---
    # Find last sale date for each customer-product group
    last_sale_dates_cp = (
        df.groupby(['CustomerCode', 'Product_Code'])['Date']
        .max()
        .reset_index()
        .rename(columns={'Date': 'Customer_Product_Last_Sale_Date'})
    )
    # Merge last sale dates into original DataFrame
    df_cp = df.merge(last_sale_dates_cp, on=['CustomerCode', 'Product_Code'], how='left')
    # Filter for recent sales (after 2024-06-01)
    df_cp_recent = df_cp[df_cp['Customer_Product_Last_Sale_Date'] >= "2024-06-01"]

    # Calculate mean, std, and coefficient of variation (CV) for each customer-product pair
    volatility_cp = (
        df_cp_recent.groupby(['CustomerCode', 'Product_Code', 'ProductName', 'CustomerName'])['Sale_Amount']
        .agg(['mean', 'std'])
        .assign(coef_var=lambda x: x['std'] / x['mean'])
        .reset_index()
    )
    # Create combined columns for display
    volatility_cp['Customer_Product'] = (
        volatility_cp['CustomerCode'] + " | " + volatility_cp['Product_Code']
    )
    volatility_cp['Customer_Product_Name'] = (
        volatility_cp['CustomerName'] + " | " + volatility_cp['ProductName']
    )
    # Merge last sale dates and sort by CV
    volatility_cp = volatility_cp.merge(last_sale_dates_cp, on=['CustomerCode', 'Product_Code'], how='left')
    volatility_cp = volatility_cp.sort_values(by='coef_var', ascending=False)

    # Plot top 25 customer-product pairs by CV
    st.markdown("### 1- Müşteri – Ürün Bazlı CV Analizi")
    fig1, ax1 = plt.subplots(figsize=(20, 9))
    sns.barplot(
        data=volatility_cp.head(25),
        x='Customer_Product_Name',
        y='coef_var',
        palette='coolwarm',
        ax=ax1
    )
    ax1.set_title("Müşteri – Ürün Bazlı Varyasyon Katsayısı (CV)", fontsize=14)
    ax1.set_xlabel("Müşteri | Ürün")
    ax1.set_ylabel("CV (Varyasyon Katsayısı)")
    ax1.axhline(0.5, color='gray', linestyle='--', label='Riskli Eşik (CV = 0.5)')
    ax1.tick_params(axis='x', rotation=90)
    ax1.legend()
    plt.tight_layout()
    st.pyplot(fig1)

    # Display top 25 riskiest customer-product pairs in a table
    columns_cp = [
        'Product_Code', 'ProductName', 'CustomerCode', 'CustomerName',
        'coef_var', 'Customer_Product_Last_Sale_Date'
    ]
    top25_cp = volatility_cp[columns_cp].head(25)
    with st.expander("En Riskli 25 Müşteri – Ürün (CV En Yüksek)"):
        st.dataframe(top25_cp.reset_index(drop=True))

    # --- Product Based Volatility ---
    # Find last sale date for each product
    last_sale_dates_p = (
        df.groupby('Product_Code')['Date']
        .max()
        .reset_index()
        .rename(columns={'Date': 'Product_Last_Sale_Date'})
    )
    # Merge last sale dates into original DataFrame
    df_p = df.merge(last_sale_dates_p, on='Product_Code', how='left')
    # Filter for recent sales (after 2024-06-01)
    df_p_recent = df_p[df_p['Product_Last_Sale_Date'] >= "2024-06-01"]

    # Calculate mean, std, and coefficient of variation (CV) for each product
    volatility_p = (
        df_p_recent.groupby(['Product_Code', 'ProductName'])['Sale_Amount']
        .agg(['mean', 'std'])
        .assign(coef_var=lambda x: x['std'] / x['mean'])
        .reset_index()
    )
    # Merge last sale dates and sort by CV
    volatility_p = volatility_p.merge(last_sale_dates_p, on='Product_Code', how='left')
    volatility_p = volatility_p.sort_values(by='coef_var', ascending=False)

    # Plot top 25 products by CV
    st.markdown("### 2-Ürün Bazlı CV Analizi")
    fig2, ax2 = plt.subplots(figsize=(20, 9))
    sns.barplot(
        data=volatility_p.head(25),
        x='ProductName',
        y='coef_var',
        palette='coolwarm',
        ax=ax2
    )
    ax2.set_title("Ürün Bazlı Varyasyon Katsayısı (CV)", fontsize=14)
    ax2.set_xlabel("Ürün")
    ax2.set_ylabel("CV (Varyasyon Katsayısı)")
    ax2.axhline(0.5, color='gray', linestyle='--', label='Riskli Eşik (CV = 0.5)')
    ax2.tick_params(axis='x', rotation=90)
    ax2.legend()
    plt.tight_layout()
    st.pyplot(fig2)

    # Display product-based CV data in a table
    columns_p = [
        'Product_Code', 'ProductName',
        'coef_var', 'Product_Last_Sale_Date'
    ]
    with st.expander("Ürün Bazlı CV Verisi"):
        st.dataframe(volatility_p[columns_p])

    return volatility_cp, volatility_p
