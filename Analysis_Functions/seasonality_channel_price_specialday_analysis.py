import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st


# Helper function to create and display heatmaps in Streamlit
def plot_heatmap(data, x_label, y_label, title, cmap='YlGnBu'):
  """
  Creates and displays a heatmap using Seaborn and Matplotlib, and renders it in a Streamlit app.

  Parameters:
    data (DataFrame or 2D array-like): The data to be visualized in the heatmap.
    x_label (str): Label for the x-axis.
    y_label (str): Label for the y-axis.
    title (str): Title of the heatmap.
    cmap (str, optional): Colormap to use for the heatmap. Defaults to 'YlGnBu'.

  Displays:
    - The heatmap plot in the Streamlit app.
    - The title as a markdown header below the plot.
  """
  fig, ax = plt.subplots(figsize=(30, 20))
  sns.heatmap(data, cmap=cmap, annot=True, fmt=".1f", linewidths=0.1, ax=ax)
  ax.set_xlabel(x_label)
  ax.set_ylabel(y_label)
  ax.set_title(title, fontsize=16)
  plt.tight_layout()
  st.pyplot(fig)
  st.markdown(f"## {title}")


# Function to analyze seasonality, special day, channel, and price effects on product sales
def check_seasonality_specialday_channel_price(df):
  """
  Analyzes seasonality, special day, channel, and price effects on product sales.
  This function processes a sales DataFrame to:
    - Calculate the first and last sale dates for each product.
    - Filter products with recent sales (after or on "2024-06-01").
    - Aggregate and display sales by season, special day, and channel for each product.
    - Compute and display the standard deviation of unit prices per product.
    - Compute the standard deviation of unit prices per customer-product pair (returned).
  The results are displayed using Streamlit dataframes for interactive analysis.
  Parameters:
    df (pd.DataFrame): Input DataFrame containing at least the following columns:
      - 'Product_Code'
      - 'ProductName'
      - 'Date'
      - 'Sale_Amount'
      - 'Season'
      - 'Special_Day'
      - 'Channel'
      - 'Unit_Price(TL)'
      - 'CustomerCode'
  Returns:
    pd.DataFrame: DataFrame with standard deviation of unit prices per customer-product pair,
            with columns ['CustomerCode', 'Product_Code', 'Price_STD2'].
  """
  # Calculate last sale dates for each customer-product pair
  last_sale_dates_product = (
    df.groupby(['Product_Code', 'ProductName'])['Date']
    .max()
    .reset_index()
    .rename(columns={'Date': 'Product_Last_Sale_Date'})
  )
  first_sale_dates_product = (
    df.groupby(['Product_Code', 'ProductName'])['Date']
    .min()
    .reset_index()
    .rename(columns={'Date': 'Product_First_Sale_Date'})
  )

  # Merge last and first sale dates with the base dataframe
  df = df.merge(last_sale_dates_product, on=['Product_Code', 'ProductName'], how='left')
  df = df.merge(first_sale_dates_product, on=['Product_Code', 'ProductName'], how='left')

  # Filter products with last sale date after or on 2024-06-01
  df_filtered = df[df['Product_Last_Sale_Date'] >= "2024-06-01"]
  
  # Group and calculate seasonality results
  seasonality_results = df_filtered.groupby(['ProductName','Product_Code', 'Season'])['Sale_Amount'].sum().unstack()
  seasonality_results = seasonality_results.merge(
      last_sale_dates_product,
      on=['Product_Code', 'ProductName'],
      how='left'
  )
  seasonality_results = seasonality_results.merge(
      first_sale_dates_product,
      on=['Product_Code', 'ProductName'],
      how='left'
  )

  # Group and calculate special day results
  special_day_results = df_filtered.groupby(['ProductName','Product_Code', 'Special_Day'])['Sale_Amount'].sum().unstack()
  special_day_results= special_day_results.merge(
    last_sale_dates_product,
    on=['Product_Code', 'ProductName'],
    how='left'
  )
  special_day_results= special_day_results.merge(
    first_sale_dates_product,
    on=['Product_Code', 'ProductName'],
    how='left'
  )

  # Group and calculate channel results
  channel_results = df_filtered.groupby(['ProductName','Product_Code', 'Channel'])['Sale_Amount'].sum().unstack()
  channel_results= channel_results.merge(
    last_sale_dates_product,
    on=['Product_Code', 'ProductName'],
    how='left'
  )
  channel_results= channel_results.merge(
    first_sale_dates_product,
    on=['Product_Code', 'ProductName'],
    how='left'
  )

  # Calculate price standard deviation per product
  price_std = df_filtered.groupby(['ProductName', 'Product_Code'])['Unit_Price(TL)'].std().reset_index().rename(
    columns={'Unit_Price(TL)': 'Price_STD'}
  )
  # Merge sale dates with price_std
  price_std = price_std.merge(
      last_sale_dates_product,
      on=['Product_Code', 'ProductName'],
      how='left'
  )
  price_std = price_std.merge(
      first_sale_dates_product,
      on=['Product_Code', 'ProductName'],
      how='left'
  )

  # Calculate price standard deviation per customer-product pair
  price_std2= df_filtered.groupby(['CustomerCode', 'Product_Code'])['Unit_Price(TL)'].std().reset_index().rename(
    columns={'Unit_Price(TL)': 'Price_STD2'}
  )

  # Display seasonality analysis in Streamlit
  st.markdown("### Ürün Bazında Mevsimsellik Analizi")
  st.dataframe(seasonality_results)
  #plot_heatmap(seasonality_results, "Sezon", "Satış Miktarı", "Sezonsallık Analizi")

  # Display special day analysis in Streamlit
  st.markdown("### Ürün Bazında Özel Gün Analizi")
  st.dataframe(special_day_results)
  #plot_heatmap(special_day_results, "Özel Gün", "Satış Miktarı", "Özel Gün Analizi")

  # Display channel analysis in Streamlit
  st.markdown("### Ürün Bazında Kanal Analizi")
  st.dataframe(channel_results)
  #plot_heatmap(channel_results, "Kanal", "Satış Miktarı", "Kanal Analizi")

  # Display price effect analysis in Streamlit
  st.markdown("### Ürün Bazında Fiyat Etkisi Analizi")
  st.dataframe(price_std)
  #plot_heatmap(price_std, "Ürün", "Fiyat Standart Sapması", "Fiyat Etkisi Analizi")
  return price_std2

# trend+volatility dataframe ile price_std birleştir  

def check_price_and_sales(combined_df_customer_product, price_std):
  """
  Analyzes the balance between price volatility and sales fluctuation for customer-product pairs.
  This function merges customer-product sales data with price standard deviation data, categorizes each pair
  based on price volatility (Price_STD2) and coefficient of variation (coef_var), and visualizes the results
  in a scatter plot. The function also displays the categorized data in a Streamlit dataframe.
  Parameters:
    combined_df_customer_product (pd.DataFrame): DataFrame containing sales data for customer-product pairs.
    price_std (pd.DataFrame): DataFrame containing price standard deviation and coefficient of variation
          for customer-product pairs.
  Returns:
    pd.DataFrame: A DataFrame with columns ["CustomerCode", "Product_Code", "Price_STD2", "coef_var",
    "Last_Sale_Date", "Kategori"], sorted by price volatility and sales fluctuation.
  """
  # Merge combined_df_customer_product with price_std on CustomerCode and Product_Code
  merged_df = pd.merge(combined_df_customer_product, price_std, on=["CustomerCode", "Product_Code"], how="left")
  merged_df.sort_values(by="Last_Sale_Date", ascending=True, inplace=True)
  merged_df.sort_values(by="Price_STD2", ascending=True, inplace=True)
  merged_df.drop_duplicates(subset=["CustomerCode", "Product_Code"], inplace=True)

  # Create a new column combining CustomerCode and Product_Code
  merged_df["Customer_Product"] = merged_df["CustomerCode"] + "-" + merged_df["Product_Code"]

  # Categorize products based on Price_STD and coef_var
  def categorize(row):
    # High risk if both price volatility and sales fluctuation are high
    if row["Price_STD2"] > 1.5 and row["coef_var"] > 0.6:
      return "Yüksek Risk"
    # Price volatile if price volatility is high or both are moderately high
    elif (row["Price_STD2"] > 0.5 and row["coef_var"] > 0.4) or row["Price_STD2"] > 1.5:
      return "Fiyat Dalgalı"
    # Otherwise, considered balanced
    else:
      return "Dengeli"

  merged_df["Kategori"] = merged_df.apply(categorize, axis=1)

  # Create a scatter plot
  fig, ax = plt.subplots(figsize=(10, 7))
  colors = {
    "Yüksek Risk": "red",
    "Fiyat Dalgalı": "orange",
    "Dengeli": "green"
  }

  # Plot each category with a different color
  for kategori, group in merged_df.groupby("Kategori"):
    ax.scatter(group["Price_STD2"], group["coef_var"], label=kategori, color=colors[kategori], s=100)

  ax.set_xlabel("Price_STD (Fiyat Oynaklığı)", fontsize=12)
  ax.set_ylabel("CV (Satış Dalgalanması)", fontsize=12)
  ax.set_title("Fiyat vs Satış Dalgalanması Grafiği", fontsize=14)
  ax.legend(title="Kategori")
  ax.grid(True)

  # Display the scatter plot in Streamlit
  st.pyplot(fig)

  # Display the merged dataframe in Streamlit
  st.markdown("### Fiyat ve Satış Dengesi Analizi")
  st.dataframe(merged_df[["CustomerCode", "Product_Code", "Price_STD2", "coef_var", "Last_Sale_Date", "Kategori"]])

  # Sort and return the dataframe
  merged_df.sort_values(by=["Price_STD2", "coef_var"], ascending=True, inplace=True)
  return merged_df[["CustomerCode", "Product_Code", "Price_STD2", "coef_var", "Last_Sale_Date", "Kategori"]]