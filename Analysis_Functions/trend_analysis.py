import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from scipy.stats import linregress, zscore

def customer_product_trend_analysis(df):
    """
    Analyzes sales trends for customer-product pairs in a given DataFrame and classifies them as 'Stable', 'Increasing', 'Decreasing', or 'Volatile' based on sales data from 2023 onwards.
    The function performs the following steps:
    1. Filters customer-product pairs with sales in 2024 or 2025.
    2. Selects all sales records for these pairs from 2013-2025.
    3. Aggregates monthly sales and computes log-transformed sales amounts.
    4. Filters pairs with sufficient data and recent sales.
    5. Calculates trend slope and volatility for each pair using linear regression on log sales.
    6. Standardizes slope and volatility, then classifies trends.
    7. Displays results in a Streamlit dataframe and returns the trend classification DataFrame.
    Parameters:
        df (pd.DataFrame): Input DataFrame containing at least the following columns:
            - 'CustomerName', 'ProductName', 'CustomerCode_Encoded', 'Product_Code_Encoded',
            - 'CustomerCode', 'Product_Code', 'Date', 'Sale_Amount', 'Year'
    Returns:
        pd.DataFrame: DataFrame with trend classification for each customer-product pair, including:
            - 'CustomerCode', 'Product_Code', 'CustomerName', 'ProductName',
            - 'Trend_Type', and the date of last sale.
    # function body...
        Classifies the trend type for a customer-product pair based on standardized slope and volatility.
        Parameters:
            row (pd.Series): Row containing 'Slope_Z' and 'Volatility_Z' values.
        Returns:
            str: Trend type, one of 'Stable', 'Increasing', 'Decreasing', or 'Volatile'.
        # function body...
    """
    # 1. Copy the input DataFrame to avoid modifying the original
    df_test3 = df.copy()

    # 2. Filter for sales in 2024 or 2025
    mask_2024_2025 = df_test3[df_test3['Year'].isin([2024, 2025])]
    customer_product_pairs = mask_2024_2025[['CustomerName', 'ProductName','CustomerCode_Encoded', 'Product_Code_Encoded']].drop_duplicates()

    # 3. Select all records for these customer-product pairs from the full data (2013-2025)
    df_selected = df_test3.merge(customer_product_pairs, on=['CustomerName', 'ProductName','CustomerCode_Encoded', 'Product_Code_Encoded'], how='inner')
    df_selected.sort_values(by="Date", ascending=True, inplace=True)
    df_selected['YearMonth'] = df_selected['Date'].dt.to_period('M').astype(str)

    # 4. Aggregate monthly sales for each customer-product pair
    monthly_sales = (
        df_selected
        .groupby(['YearMonth', 'CustomerCode', 'Product_Code'])
        .agg(Sale_Amount=('Sale_Amount', 'sum'))
        .reset_index()
    )
   
    # 5. Prepare columns for trend analysis
    monthly_sales['YearMonth'] = pd.to_datetime(monthly_sales['YearMonth'])
    monthly_sales['Sale_Amount_Log'] = np.log(monthly_sales['Sale_Amount'].replace(0, 1e-5))
    monthly_sales['Year'] = monthly_sales['YearMonth'].dt.year
    monthly_sales['Month'] = monthly_sales['YearMonth'].dt.month 
    monthly_sales.sort_values(by="YearMonth", ascending=True, inplace=True)
    name_map = df_selected[['CustomerCode', 'Product_Code', 'CustomerName', 'ProductName']].drop_duplicates()

    # 6. Filter pairs with sufficient data and recent sales
    cleaned_data = []
    for (customer_code, product_code), group in monthly_sales.groupby(['CustomerCode', 'Product_Code']):
        df_filtered = group[group['YearMonth'] >= '2023-01-01'].copy()
        if df_filtered.empty or len(df_filtered) < 2:
            continue
        if df_filtered['YearMonth'].max().year not in [2024, 2025]:
            continue
        df_filtered['CustomerCode'] = customer_code
        df_filtered['Product_Code'] = product_code
        cleaned_data.append(df_filtered)

    if not cleaned_data:
        st.warning("Yeterli temiz müşteri-ürün çifti bulunamadı.")
        return

    df_cleaned = pd.concat(cleaned_data, ignore_index=True)

    # 7. Calculate trend slope and volatility for each pair using linear regression on log sales
    trend_results = []
    for (customer_code, product_code), df_p in df_cleaned.groupby(['CustomerCode', 'Product_Code']):
        df_p_sorted = df_p.sort_values('YearMonth').copy()
        df_p_sorted['Month'] = np.arange(len(df_p_sorted))
        df_p_sorted['Sale_Amount'] = df_p_sorted['Sale_Amount'].fillna(0)
        df_p_sorted.loc[df_p_sorted['Sale_Amount'] <= 0, 'Sale_Amount'] = 1e-5
        df_p_sorted['Sale_Amount_Log'] = np.log(df_p_sorted['Sale_Amount'])

        if len(df_p_sorted) > 1:
            slope, _, _, _, _ = linregress(df_p_sorted['Month'], df_p_sorted['Sale_Amount_Log'])
            std_dev = df_p_sorted['Sale_Amount_Log'].std()

            trend_results.append({
                'CustomerCode': customer_code,
                'Product_Code': product_code,
                'Slope': slope,
                'Volatility': std_dev
            })

    # 8. Create DataFrame for trend results and merge with names
    trend_df = pd.DataFrame(trend_results)
    trend_df = trend_df.merge(name_map, on=['CustomerCode', 'Product_Code'], how='left')

    # 9. Standardize slope and volatility (z-score)
    trend_df["Slope_Z"] = zscore(trend_df["Slope"])
    trend_df["Volatility_Z"] = zscore(trend_df["Volatility"])

    # 10. Classify trend type for each pair
    def classify_trend(row):
        if -0.5 <= row["Slope_Z"] <= 0.5 and row["Volatility_Z"] < 0.5:
            return "Stable"
        elif row["Slope_Z"] > 1 and row["Volatility_Z"] < 1:
            return "Increasing"
        elif row["Slope_Z"] < -1 and row["Volatility_Z"] < 1:
            return "Decreasing"
        else:
            return "Volatile"

    trend_df["Trend_Type"] = trend_df.apply(classify_trend, axis=1)
    trend_df = trend_df.sort_values(by='Slope', ascending=False)

    # 11. Add last sale date for each customer-product pair
    last_sale_dates = (
      monthly_sales
      .groupby(['CustomerCode', 'Product_Code'])['YearMonth']
      .max()
      .reset_index()
      .rename(columns={'YearMonth': 'Last_Sale_Date'})
    )

    trend_df = trend_df.merge(last_sale_dates, on=['CustomerCode', 'Product_Code'], how='left')

    # 12. Prepare DataFrame for display (remove intermediate columns)
    trend_df2 = trend_df.copy()
    trend_df2 = trend_df.drop(columns=["Slope", "Volatility", "Slope_Z", "Volatility_Z"])

    # 13. Show results in Streamlit
    st.subheader("📈 Müşteri-Ürün Bazında Trend Sınıflandırması")
    st.dataframe(trend_df2)
    """
    for trend in trend_df["Trend_Type"].unique():
        st.markdown(f"### 🔎 {trend} Trendine Sahip Müşteri-Ürünler")

        for idx, row in trend_df[trend_df["Trend_Type"] == trend].iterrows():
            cust = row["CustomerCode"]
            prod = row["Product_Code"]
            data = df_cleaned[(df_cleaned["CustomerCode"] == cust) & (df_cleaned["Product_Code"] == prod)].copy()
            if data.empty:
                continue

            data = data.sort_values("YearMonth")
            data["Month_Index"] = np.arange(len(data))
            slope, intercept, _, _, _ = linregress(data["Month_Index"], data["Sale_Amount"])
            data["Regression"] = intercept + slope * data["Month_Index"]

            fig, ax = plt.subplots(figsize=(12, 5))
            sns.lineplot(data=data, x="YearMonth", y="Sale_Amount", marker='o', label="Satış", ax=ax)
            sns.lineplot(data=data, x="YearMonth", y="Regression", linestyle='--', color='red', label="Trend", ax=ax)
            ax.set_title(f"{trend} • Customer: {cust} • Product: {prod}")
            ax.tick_params(axis='x', rotation=45)
            st.pyplot(fig)
    """
    return trend_df
def product_trend_analysis(df_test):
    """
    Analyzes sales trends for each product in the provided DataFrame, classifies products based on trend and volatility, 
    and displays the results in a Streamlit dataframe.
    Parameters:
        df_test (pd.DataFrame): Input DataFrame containing at least the following columns:
            - 'Product_Code': Unique identifier for each product.
            - 'ProductName': Name of the product.
            - 'Date': Date of the sale (string or datetime).
            - 'Sale_Amount': Numeric value representing the amount sold.
    Returns:
        pd.DataFrame: DataFrame containing trend analysis results for each product, including:
            - 'Product_Code': Product identifier.
            - 'ProductName': Name of the product.
            - 'Trend_Type': Classified trend type ('Increasing', 'Decreasing', or 'Volatile').
            - 'Last_Sale_Date': Most recent sale date for the product.
    Notes:
        - Outliers in sales amounts are removed using the IQR method before trend calculation.
        - Only products with sales data from 2023 onwards and with at least two data points are analyzed.
        - Trend is determined using the slope of a linear regression over time.
        - Volatility is measured as the standard deviation of sales amounts.
        - Z-score normalization is used for both slope and volatility to classify trends.
        - Results are displayed in a Streamlit dataframe and a warning is shown if insufficient data is available.
    """

    # Prepare for cleaning and analysis
    cleaned_data = []
    name_map = df_test[['Product_Code', 'ProductName']].drop_duplicates()
    df_test['Date'] = pd.to_datetime(df_test['Date'])

    # Iterate over each product to clean and filter data
    for product_code, group in df_test.groupby('Product_Code'):
        group = group.copy()

        # Aggregate sales by date for the product
        df_grouped_all = group.groupby('Date')['Sale_Amount'].sum().reset_index()
        if len(df_grouped_all) < 2:
            continue

        # Remove outliers using IQR method
        Q1 = df_grouped_all['Sale_Amount'].quantile(0.25)
        Q3 = df_grouped_all['Sale_Amount'].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        df_filtered_all = df_grouped_all[(df_grouped_all['Sale_Amount'] >= lower) &
                                         (df_grouped_all['Sale_Amount'] <= upper)].copy()

        # Filter for sales from 2023 onwards
        df_filtered_2023 = df_filtered_all[df_filtered_all['Date'] >= '2023-01-01'].copy()

        # Skip if no recent sales or not enough data points
        if df_filtered_2023.empty or df_filtered_2023['Date'].max().year not in [2024, 2025]:
            continue

        if len(df_filtered_2023) < 2:
            continue

        df_filtered_2023['Product_Code'] = product_code
        cleaned_data.append(df_filtered_2023)

    # If no products passed the filter, show warning and exit
    if not cleaned_data:
        st.warning("Yeterli veri yok.")
        return

    # Concatenate all cleaned product data
    df_cleaned = pd.concat(cleaned_data, ignore_index=True)

    # Calculate trend (slope) and volatility (std) for each product
    trend_results = []
    for product_code, df_p in df_cleaned.groupby('Product_Code'):
        df_p_sorted = df_p.sort_values('Date').copy()
        df_p_sorted['Month'] = np.arange(len(df_p_sorted))
        slope, _, _, _, _ = linregress(df_p_sorted['Month'], df_p_sorted['Sale_Amount'])
        std_dev = df_p_sorted['Sale_Amount'].std()

        trend_results.append({
            'Product_Code': product_code,
            'Slope': slope,
            'Volatility': std_dev
        })

    trend_df_product = pd.DataFrame(trend_results)

    # Standardize slope and volatility using z-score
    trend_df_product["Slope_Z"] = zscore(trend_df_product["Slope"])
    trend_df_product["Volatility_Z"] = zscore(trend_df_product["Volatility"])

    # Classify trend type based on z-scores
    def classify_trend(row):
        if row["Slope_Z"] > 1 and row["Volatility_Z"] < 1:
            return "Increasing"
        elif row["Slope_Z"] < -1 and row["Volatility_Z"] < 1:
            return "Decreasing"
        else:
            return "Volatile"

    trend_df_product["Trend_Type"] = trend_df_product.apply(classify_trend, axis=1)

    # Add product names
    trend_df_product = trend_df_product.merge(name_map, on='Product_Code', how='left')

    # Add last sale date for each product
    last_sale_dates = (
        df_test.groupby('Product_Code')['Date']
        .max()
        .reset_index()
        .rename(columns={'Date': 'Last_Sale_Date'})
    )
    trend_df_product = trend_df_product.merge(last_sale_dates, on='Product_Code', how='left')
    trend_df_product['Last_Sale_Date'] = trend_df_product['Last_Sale_Date'].dt.strftime('%Y-%m-%d')

    # Prepare and display the final table
    display_cols = ['Product_Code', 'ProductName', 'Trend_Type', 'Last_Sale_Date']
    st.subheader("📈 Ürün Bazlı Trend Sonuçları")
    st.dataframe(trend_df_product[display_cols].sort_values(by='Trend_Type'))
    return trend_df_product
    # Optional: add filtering or CSV download if needed


def customer_trend_analysis(df_test):
    """
    Performs trend analysis on customer sales data over time and classifies customers based on their sales trends.
    This function groups the input DataFrame by customer and time (year, month), aggregates sales data, 
    and calculates the total revenue ("Toplam Ciro") for each customer per month. It then cleans the data 
    to include only customers with sufficient and recent sales history, computes the trend (slope) and 
    volatility (standard deviation) of the log-transformed total revenue over time for each customer, 
    and classifies customers into trend categories ("Stable", "Increasing", "Decreasing", "Volatile") 
    using Z-scores. The results are displayed in a Streamlit dataframe and returned as a DataFrame.
    Parameters
    ----------
    df_test : pandas.DataFrame
        Input DataFrame containing customer sales data. Must include at least the following columns:
        - 'CustomerCode': Unique identifier for each customer.
        - 'Year': Year of the sale.
        - 'Month': Month of the sale.
        - 'Sale_Amount': Quantity sold.
        - 'Unit_Price(TL)': Unit price in Turkish Lira.
        - 'Date': Date of the sale (datetime).
        Optionally, may include 'Order_Date' and other columns.
    Returns
    -------
    trend_df_customer : pandas.DataFrame
        DataFrame containing customer trend classification with the following columns:
        - 'CustomerCode': Customer identifier.
        - 'Trend_Type': Trend classification ('Stable', 'Increasing', 'Decreasing', 'Volatile').
        - 'Last_Sale_Date': Date of the last sale for each customer (YYYY-MM-DD format).
        - Additional columns: 'Slope', 'Volatility', 'Slope_Z', 'Volatility_Z' (not displayed).
    Notes
    -----
    - Displays a warning in Streamlit if there is insufficient clean customer data.
    - The function uses log transformation and linear regression to determine sales trends.
    - Trend classification is based on Z-scores of slope and volatility.
    - The function displays the results in a Streamlit dataframe and returns the full result DataFrame.
    """
    # Bilgilendirici açıklama
    st.markdown("Bu analiz zaman içerisindeki toplam ciro değeri baz alınarak hesaplanmıştır.")

    # Gruplama için kullanılacak sütunlar ve toplama sözlüğü
    group_cols = ['CustomerCode', 'Year', 'Month']
    agg_dict = {'Sale_Amount': 'sum'}

    # Diğer sütunları ilk değer olarak ekle
    for col in df_test.columns:
        if col not in group_cols + ['Sale_Amount']:
            agg_dict[col] = 'first'

    # Müşteri-Yıl-Ay bazında veriyi grupla
    df_grouped = (
        df_test
        .groupby(group_cols, as_index=False)
        .agg(agg_dict)
    )

    # Tarihe göre sırala
    df_grouped.sort_values(by="Date", ascending=True, inplace=True)

    # Order_Date yoksa oluştur
    if 'Order_Date' not in df_grouped.columns:
        df_grouped['Order_Date'] = pd.to_datetime(
            df_grouped['Year'].astype(str) + '-' + df_grouped['Month'].astype(str).str.zfill(2) + '-01'
        )

    # Toplam ciro hesapla
    df_grouped['Toplam_Ciro'] = df_grouped['Unit_Price(TL)'] * df_grouped['Sale_Amount']

    # Son satış tarihini bul
    last_sale_dates = (
        df_grouped.groupby('CustomerCode')['Date']
        .max()
        .reset_index()
        .rename(columns={'Date': 'Last_Sale_Date'})
    )

    # Temiz müşteri verisi oluştur
    cleaned_data = []
    for customer_code, group in df_grouped.groupby('CustomerCode'):
        df_filtered = group[group['Date'] >= '2013-01-01'].copy()
        if df_filtered.empty or len(df_filtered) < 2:
            continue
        if df_filtered['Date'].max().year not in [2024, 2025]:
            continue
        df_filtered['CustomerCode'] = customer_code
        cleaned_data.append(df_filtered)

    # Yeterli veri yoksa uyarı ver
    if not cleaned_data:
        st.warning("Yeterli temiz müşteri verisi bulunamadı.")
        return

    # Temizlenmiş verileri birleştir
    df_cleaned = pd.concat(cleaned_data, ignore_index=True)

    # Her müşteri için trend ve volatilite hesapla
    trend_results = []
    for customer_code, df_p in df_cleaned.groupby('CustomerCode'):
        df_p_sorted = df_p.sort_values('Date').copy()
        df_p_sorted['Month_Index'] = np.arange(len(df_p_sorted))
        df_p_sorted['Toplam_Ciro'] = pd.to_numeric(df_p_sorted['Toplam_Ciro'], errors='coerce').fillna(0)
        df_p_sorted.loc[df_p_sorted['Toplam_Ciro'] <= 0, 'Toplam_Ciro'] = 1e-5
        df_p_sorted['Toplam_Ciro_Log'] = np.log(df_p_sorted['Toplam_Ciro'])
        df_p_sorted = df_p_sorted.dropna(subset=['Month_Index', 'Toplam_Ciro_Log'])

        if len(df_p_sorted) > 1:
            slope, _, _, _, _ = linregress(df_p_sorted['Month_Index'], df_p_sorted['Toplam_Ciro_Log'])
            std_dev = df_p_sorted['Toplam_Ciro_Log'].std()

            trend_results.append({
                'CustomerCode': customer_code,
                'Slope': slope,
                'Volatility': std_dev
            })

    # Trend sonuçlarını DataFrame'e aktar
    trend_df_customer = pd.DataFrame(trend_results)

    # Z-score ile eğim ve volatiliteyi normalize et
    trend_df_customer["Slope_Z"] = zscore(trend_df_customer["Slope"])
    trend_df_customer["Volatility_Z"] = zscore(trend_df_customer["Volatility"])

    # Trend tipini sınıflandır
    def classify_trend(row):
        if -0.5 <= row["Slope_Z"] <= 0.5 and row["Volatility_Z"] < 0.5:
            return "Stable"
        elif row["Slope_Z"] > 1 and row["Volatility_Z"] < 1:
            return "Increasing"
        elif row["Slope_Z"] < -1 and row["Volatility_Z"] < 1:
            return "Decreasing"
        else:
            return "Volatile"

    trend_df_customer["Trend_Type"] = trend_df_customer.apply(classify_trend, axis=1)

    # Son satış tarihini ekle
    trend_df_customer = trend_df_customer.merge(last_sale_dates, on='CustomerCode', how='left')
    trend_df_customer['Last_Sale_Date'] = trend_df_customer['Last_Sale_Date'].dt.strftime('%Y-%m-%d')

    # Sonuç tablosunu hazırla ve göster
    display_cols = ['CustomerCode', 'Trend_Type', 'Last_Sale_Date']
    st.subheader("📈 Müşteri Trend Sınıflandırması")
    st.dataframe(trend_df_customer[display_cols].sort_values(by='Trend_Type'))
    return trend_df_customer
    # İndirme opsiyonu istersen:
    # st.download_button(" CSV olarak indir", trend_df_customer.to_csv(index=False), "musteri_trendleri.csv")


def customer_product_segmentation(trend_df_customer_product):
    """
    Segments customer-product pairs based on sales trends and visualizes the results using Streamlit.
    This function analyzes the trend data for each customer-product pair, segments them into various categories
    (such as growing, declining, stable, volatile, etc.) based on dynamic thresholds for slope and volatility,
    and displays the results as bar plots and data tables in a Streamlit app.
    Parameters:
        trend_df_customer_product (pd.DataFrame): 
            DataFrame containing trend analysis results for customer-product pairs.
            Expected columns include:
                - "CustomerCode": Unique identifier for the customer.
                - "CustomerName": Name of the customer.
                - "Product_Code": Unique identifier for the product.
                - "ProductName": Name of the product.
                - "Last_Sale_Date": Date of the last sale (string or datetime).
                - "Slope": Trend slope value for the customer-product pair.
                - "Volatility": Volatility value for the customer-product pair.
    Returns:
        None. The function outputs visualizations and tables directly to the Streamlit interface.
    """
    st.header("Müşteri - Ürün Trend Segmentasyonu")

    # Filter for recent customer-product pairs (last sale date >= June 2024)
    trend_df_customer_product2 = trend_df_customer_product[trend_df_customer_product["Last_Sale_Date"] >= "2024-06"]

    # Create a combined label for plotting
    trend_df_customer_product2["Customer_Product"] = (
        trend_df_customer_product2["CustomerCode"].astype(str) + " | " + trend_df_customer_product2["Product_Code"].astype(str)
    )

    # --- Dynamic thresholds for segmentation ---
    slope_mean = trend_df_customer_product2["Slope"].mean()
    slope_std = trend_df_customer_product2["Slope"].std()
    volatility_mean = trend_df_customer_product2["Volatility"].mean()

    slope_threshold_up = slope_mean + slope_std
    slope_threshold_down = slope_mean - slope_std
    volatility_threshold = volatility_mean

    # --- Define segments based on slope and volatility ---
    top_growing = trend_df_customer_product2.sort_values("Slope", ascending=False).head(5)
    top_declining = trend_df_customer_product2.sort_values("Slope", ascending=True).head(5)

    stable_rising = trend_df_customer_product2[
        (trend_df_customer_product2["Slope"] > slope_threshold_up) &
        (trend_df_customer_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_rising = trend_df_customer_product2[
        (trend_df_customer_product2["Slope"] > slope_threshold_up) &
        (trend_df_customer_product2["Volatility"] > volatility_threshold)
    ]
    stable_falling = trend_df_customer_product2[
        (trend_df_customer_product2["Slope"] < slope_threshold_down) &
        (trend_df_customer_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_falling = trend_df_customer_product2[
        (trend_df_customer_product2["Slope"] < slope_threshold_down) &
        (trend_df_customer_product2["Volatility"] > volatility_threshold)
    ]
    stable_products = trend_df_customer_product2[
        (trend_df_customer_product2["Volatility"] <= volatility_threshold) &
        (trend_df_customer_product2["Slope"].abs() < 0.01)
    ]

    # --- Segment mapping for display ---
    segment_mapping = {
        " Büyüyen ve İstikrarlı": stable_rising,
        " Riskli ama Popüler": volatile_rising,
        " Churn Adayları": stable_falling,
        " Müdahale Gereken Ürünler": volatile_falling,
        " Sabit ve Güvenilir": stable_products,
        " En Çok Artış Gösterenler": top_growing,
        " En Çok Düşüş Gösterenler": top_declining
    }

    # --- Plot and display each segment ---
    for title, df in segment_mapping.items():
        st.subheader(title)
        if df.empty:
            st.info("Bu segmentte görüntülenecek veri bulunamadı.")
            continue

        # Sort for better visualization
        sorted_df = df.sort_values('Slope', ascending=False)
        fig, ax = plt.subplots(figsize=(12, max(4, len(sorted_df) * 0.4)))
        sns.barplot(data=sorted_df, y='Customer_Product', x='Slope', ax=ax, palette='coolwarm')
        ax.set_xlabel("Trend Eğim (Slope)")
        ax.set_ylabel("Müşteri | Ürün")
        ax.set_title(title)
        ax.grid(True)
        st.pyplot(fig)

        # Optionally show the data table for the segment
        with st.expander("📄 Veriyi Göster"):
            display_columns = [
                "CustomerCode", "CustomerName",
                "Product_Code", "ProductName",
                "Last_Sale_Date"
            ]
            display_df = sorted_df[display_columns].reset_index(drop=True)
            st.dataframe(display_df)

# Ürün trend segmentasyonu fonksiyonu: Ürünleri eğim ve volatiliteye göre segmentlere ayırır ve Streamlit ile görselleştirir.
def product_segmentation(trend_df_product):
    """
    Segments products based on their sales trend and volatility, and visualizes each segment using Streamlit.
    This function analyzes a DataFrame containing product trend data, segments products into various categories
    (such as stable rising, volatile rising, stable falling, volatile falling, stable products, top growing, and top declining)
    based on dynamic thresholds calculated from the data. It then displays bar plots and data tables for each segment
    using Streamlit.
    Parameters:
        trend_df_product (pd.DataFrame): 
            DataFrame containing product trend analysis results. 
            Expected columns include:
                - "Product_Code": Unique identifier for each product.
                - "ProductName": Name of the product.
                - "Last_Sale_Date": Date of the last sale (should be in a comparable date format).
                - "Slope": Trend slope value for the product.
                - "Volatility": Volatility measure for the product.
    Returns:
        None: The function displays visualizations and tables in the Streamlit app, but does not return a value.
    Notes:
        - Only products with "Last_Sale_Date" >= "2024-06-01" are considered.
        - Dynamic thresholds for segmentation are computed using the mean and standard deviation of "Slope" and the mean of "Volatility".
        - Each segment is visualized with a bar plot and an expandable data table.
    """
    st.header("Ürün Trend Segmentasyonu")
    trend_df_product2=trend_df_product[trend_df_product["Last_Sale_Date"]>="2024-06-01"]
    
    # 🔧 Dinamik eşikler
    slope_mean = trend_df_product2["Slope"].mean()
    slope_std = trend_df_product2["Slope"].std()
    volatility_mean = trend_df_product2["Volatility"].mean()

    slope_threshold_up = slope_mean + slope_std
    slope_threshold_down = slope_mean - slope_std
    volatility_threshold = volatility_mean

    # Segmentler
    top_growing = trend_df_product2.sort_values("Slope", ascending=False).head(5)
    top_declining = trend_df_product2.sort_values("Slope", ascending=True).head(5)

    stable_rising = trend_df_product2[
        (trend_df_product2["Slope"] > slope_threshold_up) &
        (trend_df_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_rising = trend_df_product2[
        (trend_df_product2["Slope"] > slope_threshold_up) &
        (trend_df_product2["Volatility"] > volatility_threshold)
    ]
    stable_falling = trend_df_product2[
        (trend_df_product2["Slope"] < slope_threshold_down) &
        (trend_df_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_falling = trend_df_product2[
        (trend_df_product2["Slope"] < slope_threshold_down) &
        (trend_df_product2["Volatility"] > volatility_threshold)
    ]
    stable_products = trend_df_product2[
        (trend_df_product2["Volatility"] <= volatility_threshold) &
        (trend_df_product2["Slope"].abs() < 0.01)
    ]

    # Segment eşleşmeleri
    segment_mapping = {
        " Büyüyen ve İstikrarlı": stable_rising,
        " Riskli ama Popüler": volatile_rising,
        " Churn Adayları": stable_falling,
        " Müdahale Gereken Ürünler": volatile_falling,
        " Sabit ve Güvenilir": stable_products,
        " En Çok Artış Gösterenler": top_growing,
        " En Çok Düşüş Gösterenler": top_declining
    }

    # Her segmenti çiz ve göster
    for title, df in segment_mapping.items():
        st.subheader(title)
        if df.empty:
            st.info("Bu segmentte görüntülenecek veri bulunamadı.")
            continue

        sorted_df = df.sort_values('Slope', ascending=False)
        fig, ax = plt.subplots(figsize=(12, max(4, len(sorted_df) * 0.4)))
        sns.barplot(data=sorted_df, y='Product_Code', x='Slope', ax=ax, palette='coolwarm')
        ax.set_xlabel("Trend Eğim (Slope)")
        ax.set_ylabel("Ürün")
        ax.set_title(title)
        ax.grid(True)
        st.pyplot(fig)

        # Opsiyonel: tabloyu da göster
        with st.expander("📄 Veriyi Göster"):
            display_columns = [
                "Product_Code", "ProductName",
                "Last_Sale_Date"
            ]
            display_df = sorted_df[display_columns].reset_index(drop=True)
            st.dataframe(display_df)

# Customer segmentation function for product trends (duplicate of product_segmentation, can be customized for customer-based segmentation)
def customer_segmentation(trend_df_product):
    """
    Segments products based on their sales trend and volatility, and visualizes each segment using Streamlit.
    This function analyzes a DataFrame containing product trend data, segments the products into various categories 
    such as stable rising, volatile rising, stable falling, volatile falling, stable products, top growing, and 
    top declining based on dynamic thresholds for slope and volatility. It then displays the results in Streamlit 
    with bar plots and expandable data tables for each segment.
    Parameters:
        trend_df_product (pd.DataFrame): 
            DataFrame containing product trend information. 
            Expected columns include:
                - "Product_Code": Unique identifier for the product.
                - "ProductName": Name of the product.
                - "Last_Sale_Date": Date of the last sale (should be in a comparable date format).
                - "Slope": Trend slope value for the product.
                - "Volatility": Volatility measure for the product.
    Returns:
        None: 
            The function outputs visualizations and tables directly to the Streamlit app.
    """
    st.header("Ürün Trend Segmentasyonu")
    trend_df_product2 = trend_df_product[trend_df_product["Last_Sale_Date"] >= "2024-06-01"]
    
    # 🔧 Dynamic thresholds for segmentation
    slope_mean = trend_df_product2["Slope"].mean()
    slope_std = trend_df_product2["Slope"].std()
    volatility_mean = trend_df_product2["Volatility"].mean()

    slope_threshold_up = slope_mean + slope_std
    slope_threshold_down = slope_mean - slope_std
    volatility_threshold = volatility_mean

    # Segments
    top_growing = trend_df_product2.sort_values("Slope", ascending=False).head(5)
    top_declining = trend_df_product2.sort_values("Slope", ascending=True).head(5)

    stable_rising = trend_df_product2[
        (trend_df_product2["Slope"] > slope_threshold_up) &
        (trend_df_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_rising = trend_df_product2[
        (trend_df_product2["Slope"] > slope_threshold_up) &
        (trend_df_product2["Volatility"] > volatility_threshold)
    ]
    stable_falling = trend_df_product2[
        (trend_df_product2["Slope"] < slope_threshold_down) &
        (trend_df_product2["Volatility"] <= volatility_threshold)
    ]
    volatile_falling = trend_df_product2[
        (trend_df_product2["Slope"] < slope_threshold_down) &
        (trend_df_product2["Volatility"] > volatility_threshold)
    ]
    stable_products = trend_df_product2[
        (trend_df_product2["Volatility"] <= volatility_threshold) &
        (trend_df_product2["Slope"].abs() < 0.01)
    ]

    # Segment mapping for display
    segment_mapping = {
        " Büyüyen ve İstikrarlı": stable_rising,
        " Riskli ama Popüler": volatile_rising,
        " Churn Adayları": stable_falling,
        " Müdahale Gereken Ürünler": volatile_falling,
        " Sabit ve Güvenilir": stable_products,
        " En Çok Artış Gösterenler": top_growing,
        " En Çok Düşüş Gösterenler": top_declining
    }

    # Plot and display each segment
    for title, df in segment_mapping.items():
        st.subheader(title)
        if df.empty:
            st.info("Bu segmentte görüntülenecek veri bulunamadı.")
            continue

        sorted_df = df.sort_values('Slope', ascending=False)
        fig, ax = plt.subplots(figsize=(12, max(4, len(sorted_df) * 0.4)))
        sns.barplot(data=sorted_df, y='Product_Code', x='Slope', ax=ax, palette='coolwarm')
        ax.set_xlabel("Trend Eğim (Slope)")
        ax.set_ylabel("Ürün")
        ax.set_title(title)
        ax.grid(True)
        st.pyplot(fig)

        # Optionally: show the data table for the segment
        with st.expander("📄 Veriyi Göster"):
            display_columns = [
                "Product_Code", "ProductName",
                "Last_Sale_Date"
            ]
            display_df = sorted_df[display_columns].reset_index(drop=True)
            st.dataframe(display_df)
