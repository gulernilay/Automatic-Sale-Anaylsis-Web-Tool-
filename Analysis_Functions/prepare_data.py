import pandas as pd 

"""
İhtiyacımız olan veriler : 
Date  :2024-12-11 00:00:00
Year
Month
Label()  : Private Label or Own Brand 
Channel : Horeca Müşteriler , Endüstriyel Müşteriler, Perakende Müşteriler 
Season : kendimiz yaratıyoruz  
CustomerCode
CustomerName
Product_Code
ProductName
Sale_Amount
Unit_Price(TL)
Inflation, Interest Rate, PMI , Growth Rate 

Gelen veri dipsos/ sachet veya diğer ürün grupları ( sos / baharat olarak ayrılabilir) olarak ayrılmalı
- HAM/YAR codes were eliminated.
- Negative values of unit price and total price were eliminated.
- The economical features are added : PMI, Inflation,Growth Rate, Interest Rate
"""
def preprocessing(df):
    df=show_data(df)
    df = prepare_data(df)
    df["Season"] = df["Month"].apply(create_season_data)
    df["Season"] = df["Season"].astype('category')
    df = create_special_day_data(df)
    df = label_data(df)
    df = update_customercodes(df)
    return df


def show_data(df):
    """
    Displays the first 5 rows of the DataFrame.
    Parameters:
        df (pd.DataFrame): The DataFrame to display.
    """
    print("İlk 5 satır:",df.head(5))
    print("Sütunlar:",df.columns)
    
def prepare_data(df):
    #Create New Columns 
    df["InvoiceDate"].rename("Date", inplace=True)
    
    df['Date'] = pd.to_datetime(df['Date'])
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['YearMonth'] = df['Date'].dt.to_period('M')

    #Data Types
    df['Year'] = df['Year'].astype(int)
    df['Month'] = df['Month'].astype(int)
    df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
    df['Sale_Amount'] = df['Sale_Amount'].astype(float)
    df['Label'] =df['Label'].astype('category')
    df['Channel'] =df['Channel'].astype('category')
    

    #Data Formatting 
    df["Label"] = df["Label"].str.strip()
    df["Channel"]=df["Channel"].str.strip()
    df['Product_Code'] = df['Product_Code'].str.strip()
    df["Product_Code"]=df["Product_Code"].str.upper()
    df['Product_Code'] = df['Product_Code'].str.strip()
    df['Product_Code'] = df['Product_Code'].str.upper()
    df["ProductName"]=df["ProductName"].str.upper()
    df["CustomerName"]=df["CustomerName"].str.upper()
    df['Unit_Price(TL)'] = (
        df['Unit_Price(TL)']
        .astype(str)
        .str.replace('%', '', regex=False)
        .str.replace(',', '.', regex=False)
        .astype(float)
    )

    # Data Filtering
    df =df[(df['Sale_Amount'] >= 0) & (df['Unit_Price(TL)'] >= 0)] #Negative sales
    df = df[~df["Product_Code"].str.startswith(("HAM", "YAR"))] # HAM /YAR codes are eliminated. 

    #Sort the data
    df.sort_values(by="Date",ascending=True,inplace=True)
    return df

def create_season_data(month):
    """
    Assigns a season label to the input DataFrame row based on the value of the 'Month' column.
    Parameters:
        df (pd.Series): A DataFrame row or Series containing a 'Month' column.
    Returns:
        pd.Series: The input row with an added 'Season' column indicating the season in Turkish.
    """
    if month in [12, 1, 2]:
        return "Kış"
    elif month in [3, 4, 5]:
        return "İlkbahar"
    elif month in [6, 7, 8]:
        return "Yaz"
    elif month in [9, 10, 11]:
        return "Sonbahar"
        
def create_special_day_data(df):
    """
    Adds a 'Special_Day' column to the given DataFrame indicating whether each row corresponds to a month 
    containing either Ramazan Bayramı or Kurban Bayramı for the given year.
    The function uses predefined dictionaries mapping years to the Turkish month names in which 
    Ramazan Bayramı and Kurban Bayramı occur. It compares the 'Year' and 'Month' columns of the DataFrame 
    to these dictionaries and sets 'Special_Day' to True if the month matches either holiday for that year, 
    otherwise False.
    Parameters:
        df (pandas.DataFrame): Input DataFrame with at least 'Year' and 'Month' columns. 
            'Month' should be an integer (1-12) corresponding to the month number.
    Returns:
        pandas.DataFrame: The input DataFrame with an added 'Special_Day' boolean column.
    """
    ramazan_bayrami = {
        2013: "Ağustos", 2014: "Temmuz", 2015: "Temmuz", 2016: "Temmuz", 2017: "Haziran",
        2018: "Haziran", 2019: "Haziran", 2020: "Mayıs", 2021: "Mayıs", 2022: "Mayıs",
        2023: "Nisan", 2024: "Nisan", 2025: "Mart", 2026: "Şubat", 2027: "Şubat",
        2028: "Ocak", 2029: "Aralık", 2030: "Kasım"
    }
    kurban_bayrami = {
        2013: "Ekim", 2014: "Ekim", 2015: "Eylül", 2016: "Eylül", 2017: "Eylül",
        2018: "Ağustos", 2019: "Ağustos", 2020: "Temmuz", 2021: "Temmuz", 2022: "Temmuz",
        2023: "Haziran", 2024: "Haziran", 2025: "Haziran", 2026: "Mayıs", 2027: "Mayıs",
        2028: "Nisan", 2029: "Mart", 2030: "Şubat"
    }
    month_to_number = {
        "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6,
        "Temmuz": 7, "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12
    }
    # Ters çevir (sayıdan isme erişmek için)
    number_to_month = {v: k for k, v in month_to_number.items()}

    # Ay ismine göre karşılaştır
    def is_special_day(row):
        year = row["Year"]
        month = number_to_month.get(row["Month"])
        if month is None:
            return False
        return (
            ramazan_bayrami.get(year) == month or
            kurban_bayrami.get(year) == month
        )

    df["Special_Day"] = df.apply(is_special_day, axis=1)
    return df


def label_data(df):
    # Tüm veriyi tabloya çevirelim
    data = [
        ["120-35-021", "PIZ001"], ["120-34-029", "D40000004"], ["120-35-021", "PIZ004"],
        ["120-35-021", "PIZ006"], ["120-35-041", "PIZ006"], ["120-35-042", "PIZ006"],
        ["120-33-001", "MRN013"], ["120-41-004", "YUM005"], ["120-41-004", "YUM006"],
        ["120-41-004", "YUM007"], ["120-41-004", "YUM008"], ["120-41-004", "YUM009"],
        ["120-34-063", "LCE008"], ["120-34-063", "LCE009"], ["120-41-004", "YUM012"],
        ["120-34-063", "LCE014"], ["120-34-063", "LCE015"], ["120-34-063", "LCE016"],
        ["120-34-063", "LCE017"], ["120-34-063", "LCE019"], ["120-34-063", "LCE020"],
        ["120-34-063", "LCE018"], ["120-34-085", "CSMK001"], ["120-34-085", "CSMK002"],
        ["120-22-001", "CSSC001"], ["120-23-001", "CSSC001"], ["120-07-006", "CSSC001"],
        ["120-34-097", "CSSC001"], ["120-34-095", "TVD011"], ["120-34-095", "TVD012"],
        ["120-34-095", "TVD013"], ["120-35-149", "ORG001"], ["120-34-063", "LCE021"],
        ["120-34-029", "D40001846"], ["120-34-063", "LCE022"], ["120-34-063", "LCE023"],
        ["120-34-103", "CSSC001"], ["120-34-104", "CSSC001"], ["120-07-007", "CSSC001"],
        ["120-07-008", "CSSC001"], ["120-34-106", "ORG001"], ["120-67-001", "CSSC001"],
        ["120-35-160", "CSDO001"], ["120-35-021", "PIZ019"], ["120-35-021", "PIZ020"],
        ["120-34-112", "CSSC001"], ["120-35-021", "PIZ021"], ["120-06-011", "CSSC001"],
        ["120-06-012", "CSSC001"], ["120-34-119", "CSSC001"], ["120-34-120", "CSSC001"],
        ["120-41-004", "YUM019"], ["120-25-001", "CSSC001"], ["120-10-002", "CSSC001"],
        ["120-34-110", "CSSC001"], ["120-01-006", "CSSC001"], ["120-34-013", "CSSC001"],
        ["120-34-013", "CSSC008"], ["120-34-013", "CSSC009"], ["120-34-013", "CSSC010"],
        ["120-34-122", "CSSC009"], ["120-34-122", "CSSC010"], ["120-34-122", "CSSC008"],
        ["120-34-122", "CSSC011"], ["120-34-122", "CSSC012"], ["120-34-122", "CSSC013"],
        ["120-34-122", "CSSC014"], ["120-34-122", "CSSC015"], ["120-34-122", "CSSC016"],
        ["120-34-122", "CSSC017"], ["120-34-122", "CSSC018"], ["120-34-122", "CSSC019"],
        ["120-34-122", "CSSC020"], ["120-34-122", "CSSC021"], ["120-34-122", "CSSC022"],
        ["120-34-122", "CSSC001"], ["120-34-063", "LCE027"], ["120-34-126", "CSSC018"],
        ["120-34-126", "CSSC019"], ["120-34-126", "CSSC021"], ["120-34-126", "CSSC022"],
        ["120-34-123", "CSSC001"], ["120-34-128", "YUM019"], ["120-34-128", "YUM007"],
        ["120-34-128", "YUM008"], ["120-34-128", "YUM005"], ["120-34-129", "CSSC001"],
        ["120-34-130", "CSSC001"], ["120-34-128", "YUM023"], ["120-34-137", "CSSC001"],
        ["120-41-004", "YUM023"], ["120-34-148", "YUM005"], ["120-34-148", "YUM023"],
        ["120-42-005", "CSSC001"], ["120-41-002", "BKN001"], ["120-34-029", "D40003146"],
        ["120-34-029", "D40003147"], ["120-34-029", "D40003148"], ["120-41-002", "PPY001"],
        ["120-41-002", "PPY002"], ["120-41-002", "PPY003"], ["120-34-029", "D40003659"],
        ["120-41-002", "SBR001"], ["120-41-002", "SBR002"], ["120-34-029", "D40003790"]
    ]

    dipsos_set = set((c, p) for c, p in data)
    # Her satır için kontrol et
    df["Ürün Grubu"] = df.apply(
        lambda row: "Dipsos/Sachet" if (row["CustomerCode"], row["Product_Code"]) in dipsos_set else "Other Products",
        axis=1
    )
    return df


def update_customercodes(df):
    mapping = {
        "METRO GR": "120-34-066",
        "ÖMEROĞLU": "120-35-178",
        "TR CRKS": "120-61-004",
        "KUVER EN": "120-41-006",
        "G2MEKSPE": "120-34-114",
        "BİOKENT": "120-34-094",
        "ALAMAR F": "120-90-020"
    }
    # Sadece mapping'de olanları güncelle
    df.loc[df["CustomerName"].isin(mapping.keys()), "CustomerCode"] = \
        df["CustomerName"].map(mapping)
    return df