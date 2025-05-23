import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
import streamlit as st


def macroeconomic_parameters(df, macro_col, macro_label, plot=True):
    """
    Belirtilen makroekonomik gösterge ile aylık satış arasındaki ilişkiyi gösterir.

    Parametreler:
        df: DataFrame (OrderDate, Sale_Amount ve makro_col içermeli)
        macro_col: Gösterge kolonu (örnek: 'Interest_Rate')
        macro_label: Grafikte gösterilecek etiket (örnek: 'Faiz Oranı')
        plot: Grafik çizilsin mi?

    Döndürür:
        Tuple: (monthly_sales_df, monthly_macro_df, fig)
    """
  
    df["Year-Month"] = pd.to_datetime(df["Date"]).dt.to_period("M").astype(str)

    monthly_sales = df.groupby("Year-Month")["Sale_Amount"].sum().reset_index()
    monthly_macro = df.groupby("Year-Month")[macro_col].mean().reset_index()

    fig = None
    if plot:
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Aylık satış çizgisi
        sns.lineplot(data=monthly_sales, x="Year-Month", y="Sale_Amount", ax=ax1, label="Aylık Satış")
        ax1.set_xlabel("Yıl-Ay")
        ax1.set_ylabel("Aylık Satış")
        ax1.yaxis.set_major_formatter(mticker.StrMethodFormatter('{x:,.0f}'))
        ax1.tick_params(axis='x', rotation=45)
        ax1.grid(axis='y')
        ax1.legend(loc="upper left")

        # Makro gösterge çizgisi (ikincil eksen)
        ax2 = ax1.twinx()
        sns.lineplot(data=monthly_macro, x="Year-Month", y=macro_col, ax=ax2, color="red", label=macro_label)
        ax2.set_ylabel(macro_label)
        ax2.legend(loc="upper right")
        plt.title(f"Aylık Satış ve {macro_label} İlişkisi")
        plt.tight_layout()
    
    return monthly_sales, monthly_macro, fig






