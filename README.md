# Automatic-Sale-Anaylsis-Web-Tool-
Bu proje, satış verilerinin detaylı analizini ve görselleştirilmesini sağlayan, Python ve Streamlit tabanlı bir web uygulamasıdır. Kullanıcılar, satış performansını farklı açılardan inceleyebilir, raporlar oluşturabilir ve iş kararlarını veriyle destekleyebilir.

## Özellikler

- **Kullanıcı Girişi:** Güvenli giriş ekranı ile sadece yetkili kullanıcılar erişebilir.
- **Veritabanından Otomatik Veri Çekme:** Satış verileri doğrudan veritabanından alınabilir.
- **Veri Ön İşleme:** Yüklenen veya çekilen veriler otomatik olarak temizlenir ve analiz için hazırlanır.
- **Çok Yönlü Analizler:**
  - Yıl-Ay bazında satış ve ciro analizleri
  - En çok satan ürünler ve müşteri-ürün kombinasyonları
  - Trend ve volatilite analizleri
  - Düzenli/aralıklı sipariş veren müşteri ve ürünlerin tespiti
  - Sezonluk satış analizleri ve görselleştirmeleri
  - Makroekonomik göstergeler ile satış karşılaştırmaları
  - Ürün ve müşteri performans analizleri
  - Satış değişim oranları ve yaşlanma etkisi analizi

## Kurulum

1. **Gereksinimler**
   - Python 3.8+
   - [Streamlit](https://streamlit.io/)
   - Pandas, Numpy, Matplotlib, Seaborn ve diğer gerekli kütüphaneler (`requirements.txt` ile yüklenebilir)

2. **Kurulum Adımları**
   ```sh
   git clone https://github.com/<kullanici-adi>/Automatic-Sale-Anaylsis-Web-Tool-.git
   cd Automatic-Sale-Anaylsis-Web-Tool-
   pip install -r requirements.txt

3.**Gizli Bilgiler** .streamlit/secrets.toml dosyasına kullanıcı adı ve parola ekleyin:
[auth]
username = "kullaniciadi"
password = "parolaniz"

4.**Kullanım**
streamlit run [dashboard.py](http://_vscodecontentref_/0)

Tarayıcıda açılan arayüzden giriş yaparak analizleri kullanabilirsiniz.

5. **Klasör Yapısı**
dashboard.py: Ana uygulama dosyası
Analysis_Functions/: Analiz fonksiyonları ve veri işleme modülleri
.streamlit/secrets.toml: Giriş bilgileri
assets/: Görsel ve statik dosyalar

