import pandas as pd
import matplotlib.pyplot as plt

def total_sales_and_trend_line(df: pd.DataFrame, plot: bool = True):
    """
    Calculates daily total sales and a 30-day moving average trend line for sales data from 2020 onwards.
    
    Args:
        df (pd.DataFrame): Input DataFrame containing at least 'Year', 'Date', and 'Sale_Amount' columns.
        plot (bool, optional): If True, generates a plot of daily sales and the 30-day moving average. Defaults to True.
    
    Returns:
        tuple: (pd.Series of 30-day moving average sales, matplotlib.figure.Figure or None)
    """
    df_filtered = df[df["Year"] >= 2020]

    # Group by date and sum sales
    sales_by_date = df_filtered.groupby('Date')['Sale_Amount'].sum().sort_index()

    # Calculate 30-day moving average
    sales_rolling = sales_by_date.rolling(window=30).mean()

    fig = None
    if plot:
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.plot(sales_by_date.index, sales_by_date.values, label='Günlük Satış', linewidth=1.5)
        ax.plot(sales_rolling.index, sales_rolling.values, label='30 Günlük Ort.', color='red', linewidth=2)
        ax.set_xlabel('Tarih', fontsize=12)
        ax.set_ylabel('Toplam Satış Miktarı', fontsize=12)
        ax.legend()
        ax.grid(True)
        fig.tight_layout()
        return sales_rolling, fig

    return sales_rolling, None
