import pandas as pd 

def ciro_buyume_orani_analizi(df):
    """
    Aylık ve yıllık ciro büyüme oranlarını hesaplar ve analiz sonucu üretir.

    Parametreler
    ------------
    df : pandas.DataFrame
        Satış verilerini içeren DataFrame. Gerekli sütunlar:
        - 'Date' (datetime): Satış tarihi
        - 'Sale_Amount' (numeric): Satış adedi
        - 'Unit_Price(TL)' (numeric): Birim fiyat
        Opsiyonel: 'Revenue' (numeric). Yoksa otomatik hesaplanır.

    Dönüş
    ------
    monthly_revenue : pandas.DataFrame
        Aşağıdaki sütunları içerir:
        - 'YearMonth': Yıl ve ay (yyyy-mm)
        - 'Revenue': O ayın toplam cirosu
        - 'Aylık_Büyüme_Oranı': Bir önceki aya göre ciro değişim oranı (%)
        - 'Analiz': Büyüme oranına göre kısa yorum
    yearly_revenue : pandas.DataFrame
        - 'Year': Yıl
        - 'Revenue': O yılın toplam cirosu
        - 'Yıllık_Büyüme_Oranı': Bir önceki yıla göre ciro değişim oranı (%)
        - 'Analiz': Büyüme oranına göre kısa yorum

    Notlar
    ------
    - 'Aylık_Büyüme_Oranı' yüzde olarak hesaplanır (örn. 0.12 = %12 artış).
    - 'Analiz' sütunu, büyüme oranına göre otomatik olarak yorum üretir.
    """
    df = df.copy()
    if 'Revenue' not in df.columns:
        df['Revenue'] = df['Sale_Amount'] * df['Unit_Price(TL)']

    # Aylık ciro
    df['YearMonth'] = df['Date'].dt.to_period('M')
    monthly_revenue = df.groupby('YearMonth')['Revenue'].sum().reset_index()
    monthly_revenue['Aylık_Büyüme_Oranı'] = monthly_revenue['Revenue'].pct_change()

    # Yıllık ciro
    df['Year'] = df['Date'].dt.year
    yearly_revenue = df.groupby('Year')['Revenue'].sum().reset_index()
    yearly_revenue['Yıllık_Büyüme_Oranı'] = yearly_revenue['Revenue'].pct_change()

    # Analiz yorumu ekle (aylık için)
    def yorum_ay(row):
        oran = row['Aylık_Büyüme_Oranı']
        if pd.isna(oran):
            return ""
        elif oran > 0.1:
            return "Ciroda güçlü artış"
        elif oran > 0.02:
            return "Ciroda hafif artış"
        elif oran < -0.1:
            return "Ciroda ciddi düşüş"
        elif oran < -0.02:
            return "Ciroda hafif düşüş"
        else:
            return "Ciroda durağanlık"

    def yorum_yil(row):
        oran = row['Yıllık_Büyüme_Oranı']
        if pd.isna(oran):
            return ""
        elif oran > 0.1:
            return "Ciroda güçlü artış"
        elif oran > 0.02:
            return "Ciroda hafif artış"
        elif oran < -0.1:
            return "Ciroda ciddi düşüş"
        elif oran < -0.02:
            return "Ciroda hafif düşüş"
        else:
            return "Ciroda durağanlık"

    monthly_revenue['Analiz'] = monthly_revenue.apply(yorum_ay, axis=1)
    yearly_revenue['Analiz'] = yearly_revenue.apply(yorum_yil, axis=1)

    # Sonuç: aylık ve yıllık tablo
    return monthly_revenue, yearly_revenue

