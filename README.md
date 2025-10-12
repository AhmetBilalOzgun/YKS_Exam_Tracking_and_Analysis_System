📊 YKS Deneme Takip ve Analiz Sistemi
Bu proje, YKS'ye hazırlanan öğrencilerin deneme sınavı sonuçlarını Google Sheets üzerinden alarak detaylı net ve konu analizi yapan, sonuçları grafiklerle görselleştiren ve kişiselleştirilmiş çalışma önerileri sunan modüler bir Python uygulamasıdır.

🛠️ Kullanılan Teknolojiler
- **Veri Analizi:** Pandas, NumPy, SciPy
- **Görselleştirme:** Matplotlib, Seaborn
- **Veri Kaynağı:** Google Sheets API (gspread)
- **Ortam Yönetimi:** python-dotenv
- **Çalışma Ortamı:** Jupyter Notebook

🎯 Temel Özellikler
Veri Yönetimi: Google Sheets entegrasyonu sayesinde verilerinizi bulutta tutabilir ve her yerden erişebilirsiniz.

Otomatik Veri Temizleme: Yanlış girilen veya eksik verileri otomatik olarak düzelterek analizlerin tutarlı olmasını sağlar.

Detaylı Net Analizi: Ders bazında ortalama, standart sapma gibi istatistiklerin yanı sıra, doğrusal regresyon ile netlerinizin gidişatını (trend) analiz eder.

Akıllı Konu Analizi: En çok yanlış yapılan konuları tespit eder, ders bazında zayıf alanlarınızı belirler ve konu bazlı başarı trendinizi analiz eder.

Kişiselleştirilmiş Çalışma Planı: Konu analizlerine dayanarak "Çok Acil", "Acil", "Orta" gibi öncelik seviyelerine göre size özel bir çalışma planı oluşturur.

Zengin Görselleştirme: Matplotlib ve Seaborn kullanılarak oluşturulan 10'dan fazla grafik türü ile performansınızı net bir şekilde görmenizi sağlar.

🏗️ Proje Mimarisi
Proje, herbiri belirli bir görevi yerine getiren modüler bir yapıda tasarlanmıştır:

ders_takip/
│
├── 📂 analysis/             # Analiz scriptleri
│   ├── net_analyzer.py      # Net istatistikleri, trend analizi
│   └── topic_analyzer.py    # Konu frekansları, çalışma planı
│
├── 📂 data/                 # Veri yükleme ve temizleme
│   ├── data_cleaner.py      # Veri temizleme ve doğrulama
│   └── data_loader.py       # Google Sheets'ten veri okuma
│
├── 📂 output/                # Analiz çıktıları
│   ├── 📂 charts/             # Oluşturulan grafikler
│   └── 📂 data/               # Temizlenmiş veriler ve raporlar
│
├── 📂 visualization/         # Görselleştirme scriptleri
│   ├── net_charts.py        # Net grafikleri (çizgi, sütun vb.)
│   └── topic_charts.py      # Konu grafikleri (bar, ısı haritası vb.)
│
├── 📜 config.py              # Tüm ayarların ve sabitlerin merkezi
├── 📜 credentials.json      # Google API yetki anahtarı
├── 📜 main.ipynb             # Tüm modüllerin kullanıldığı ana Jupyter Notebook
├── 📜 requirements.txt       # Gerekli Python kütüphaneleri
└── 📜 README.md              # Bu dosya
🚀 Kurulum ve Kullanım
1. Projeyi Klonlama
Bash

git clone <repo_url>
cd ders_takip
2. Gerekli Kütüphaneleri Yükleme
Projenin çalışması için requirements.txt dosyasında belirtilen kütüphanelerin yüklü olması gerekir.

Bash

pip install -r requirements.txt
3. Google Sheets API Ayarları
Projenin Google Sheets'e erişebilmesi için bir servis hesabı oluşturmanız ve yetkilendirmeniz gerekmektedir.

a) Google Cloud Console:

Google Cloud Console'da yeni bir proje oluşturun.

"APIs & Services" > "Library" bölümünden "Google Sheets API" ve "Google Drive API"yi etkinleştirin.

"Credentials" bölümüne giderek yeni bir "Service Account" oluşturun.

Oluşturduğunuz servis hesabına "Editor" yetkisi verin.

Servis hesabı için bir JSON anahtarı oluşturun, indirin ve adını credentials.json olarak proje klasörüne kaydedin.

b) Google Sheets'i Paylaşma:

Analiz verilerinizin bulunduğu Google Sheets dosyasını açın.

"Share" butonuna tıklayarak credentials.json dosyası içindeki client_email adresini ekleyin ve "Editor" yetkisi verin.

4. Konfigürasyon
config.py dosyasını kendi bilgilerinize göre düzenleyin veya daha güvenli bir yöntem olarak bir .env dosyası oluşturup değişkenleri oraya yazın.

.env dosyası örneği:

GOOGLE_SHEET_URL="https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID"
CREDENTIALS_PATH="credentials.json"
5. Çalıştırma
Tüm analiz sürecini main.ipynb Jupyter Notebook'u üzerinden hücreleri sırayla çalıştırarak yürütebilirsiniz.

📊 Örnek Çıktılar
Proje, net ve konu analizlerinizi hem metin tabanlı raporlar hem de çeşitli grafiklerle sunar.

Net Analizi Raporu
=== TOPLAM NET İSTATİSTİKLERİ ===
  mean: 88.25
  std: 4.13
  min: 85.0
  max: 94.25
  latest: 87.5
Konu Analizi Raporu
=== ÖNERİLEN ÇALIŞMA PLANI ===
Matematik:
  1. problemler
     Öncelik: 🔴 Yüksek | Frekans: 4 | ➡️ Sabit
  2. olasılık
     Öncelik: 🔴 Yüksek | Frekans: 4 | ➡️ Sabit
