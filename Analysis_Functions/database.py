import pandas as pd
import pyodbc

def get_sales_data(option):
    server = '192.168.2.214'
    database = 'TEST'
    username = 'NilayTest'
    password = '1Y11m5egIoy13A'

    conn_str = (
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password}'
    )

    try:
        conn = pyodbc.connect(conn_str)
        # option'a göre sorgu belirle
        if option == "Yurtiçi -Dipsos/Sachet":
            query = "select * from allInvoices_bi where year(InvoiceDate) =2025"
        elif option == "Yurtiçi-Diğer Ürünler":
            query = "SELECT * FROM sales_data WHERE Channel='Yurtiçi' AND ProductType='Diğer Ürünler'"
        elif option == "İhracat-Dipsos/Sachet":
            query = "SELECT * FROM sales_data WHERE Channel='İhracat' AND ProductType='Dipsos/Sachet'"
        elif option == "İhracat-Diğer Ürünler":
            query = "SELECT * FROM sales_data WHERE Channel='İhracat' AND ProductType='Diğer Ürünler'"
        else:
            query = "SELECT * FROM sales_data"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
    except Exception as e:
        return None, str(e)
    
"""
    # Load dataset 
uploaded_file = st.file_uploader("Excel dosyasını yükleyin", type=["xlsx"])
if uploaded_file is not None:
    df_raw = pd.read_excel(uploaded_file)


"""