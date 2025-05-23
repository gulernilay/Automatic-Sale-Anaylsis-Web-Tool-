import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import matplotlib.ticker as mticker

def top_3_customer_product_sales_by_month_year(df, plot=True):
    """
    Analyzes and visualizes the top 3 best-selling customer-product combinations for each month and year.
    For each year in the range 2023 to 2025 (inclusive), this function:
        - Filters the input DataFrame for the given year.
        - Combines customer and product names into a single identifier.
        - Aggregates total sales by month and customer-product combination.
        - Selects the top 3 customer-product combinations for each month based on sales.
        - Optionally plots the results using a barplot.
    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame containing at least the following columns:
            - "Year": int, the year of the sale.
            - "Month": int or str, the month of the sale.
            - "CustomerName": str, the name of the customer.
            - "ProductName": str, the name of the product.
            - "Sale_Amount": numeric, the amount of the sale.
    plot : bool, optional (default=True)
        If True, generates a barplot for each year showing the top 3 customer-product sales per month.
    Returns
    -------
    result_dict : dict
        A dictionary where each key is a year (int), and each value is a tuple:
            (top3_df, fig)
        - top3_df: pandas.DataFrame with columns ["Month", "Customer_Product", "Sale_Amount"] for the top 3 per month.
        - fig: matplotlib.figure.Figure object of the plot for that year, or None if plot=False.
    """
    # Initialize result dictionary to store results for each year
    result_dict = {}
    # Loop through each year in the specified range
    for year in range(2023, 2026):
        # Filter DataFrame for the current year
        df_filtered = df[df["Year"] == year].copy()
        # Combine customer and product names into a single identifier
        df_filtered["Customer_Product"] = df_filtered["CustomerName"] + " - " + df_filtered["ProductName"]

        # Aggregate total sales by month and customer-product combination
        sales_by_month = df_filtered.groupby(["Month", "Customer_Product"])["Sale_Amount"].sum().reset_index()
        # Sort sales by month and descending sale amount
        sales_by_month = sales_by_month.sort_values(by=["Month", "Sale_Amount"], ascending=[True, False])

        # Select the top 3 customer-product combinations for each month
        top3 = (
            sales_by_month.groupby("Month")
            .head(3)
            .reset_index(drop=True)
        )

        fig = None
        if plot:
            # Plot the results using a barplot
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(data=top3, x='Month', y='Sale_Amount', hue='Customer_Product', ax=ax)
            ax.set_title(f'{year} Yılında Aylık En Çok Satan Müşteri-Ürünler')
            ax.set_ylabel('Toplam Satış')
            ax.set_xlabel('Ay')
            ax.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
            ax.grid(axis='y')
            plt.tight_layout()

        # Store the DataFrame and figure in the result dictionary
        result_dict[year] = (top3, fig)
    
    return result_dict

