import pandas as pd 
import numpy as np

def yil_ay_bazinda_en_cok_satan_urunler(df):
    """
    Parametreler:
      df (pd.DataFrame): Satış verilerini içeren DataFrame. 
        Gerekli sütunlar: 'Date' (datetime), 'ProductName' (str), 'Sale_Amount' (numeric), 'Unit_Price(TL)' (numeric).
        Opsiyonel sütun: 'Revenue' (numeric). Eğer yoksa, 'Sale_Amount' * 'Unit_Price(TL)' ile hesaplanır.
    Dönüş:
      pd.DataFrame: Her yıl ve ay için;
        - 'Year': Yıl
        - 'Month': Ay
        - 'Adet_Bazinda_En_Cok_Satan': Adet bazında en çok satan ürün adı
        - 'Adet_Bazinda_En_Cok_Satan_Adet': Adet bazında en çok satan ürünün toplam satışı
        - 'Ciro_Bazinda_En_Cok_Satan': Ciro bazında en çok satan ürün adı
        - 'Ciro_Bazinda_En_Cok_Satan_Ciro': Ciro bazında en çok satan ürünün toplam cirosu
    Notlar:
      - Her yıl ve ay için, satış adedi ve ciroya göre en çok satan ürünler ayrı ayrı belirlenir.
      - Tarih sütununun datetime tipinde olması gerekir.
    """
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month

    # Adet bazında en çok satan ürün
    adet_bazinda = (
        df.groupby(['Year', 'Month', 'ProductName'])
        .agg({'Sale_Amount': 'sum'})
        .reset_index()
        .sort_values(['Year', 'Month', 'Sale_Amount'], ascending=[True, True, False])
    )
    adet_bazinda_top = adet_bazinda.groupby(['Year', 'Month']).first().reset_index()
    adet_bazinda_top = adet_bazinda_top[['Year', 'Month', 'ProductName', 'Sale_Amount']]
    adet_bazinda_top.rename(columns={
        'ProductName': 'En Çok Satan Ürün (Adet Bazında)',
        'Sale_Amount': 'Adet (Birim)'
    }, inplace=True)

    # Ciro bazında en çok satan ürün
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Sale_Amount'] * df['Unit_Price(TL)']
    ciro_bazinda = (
        df.groupby(['Year', 'Month', 'ProductName'])
        .agg({'Revenue': 'sum'})
        .reset_index()
        .sort_values(['Year', 'Month', 'Revenue'], ascending=[True, True, False])
    )
    ciro_bazinda_top = ciro_bazinda.groupby(['Year', 'Month']).first().reset_index()
    ciro_bazinda_top = ciro_bazinda_top[['Year', 'Month', 'ProductName', 'Revenue']]
    ciro_bazinda_top.rename(columns={
        'ProductName': 'En Çok Satan (Ciro Bazında)',
        'Revenue': 'Ciro(TL)'
    }, inplace=True)

    # Birleştir
    result = pd.merge(adet_bazinda_top, ciro_bazinda_top, on=['Year', 'Month'], how='outer')
    return result