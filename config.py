"""
YKS Analiz Sistemi - Konfigürasyon Dosyası
Tüm sabitler, ayarlar ve yapılandırmalar
"""

from pathlib import Path
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükle


class Config:
    
    # ==================== GOOGLE SHEETS ====================
    GOOGLE_SHEET_URL= os.getenv("GOOGLE_SHEET_URL")
    CREDENTIALS_PATH= os.getenv("CREDENTIALS_PATH")


    
    
    # ==================== PROJE YOLLARI ====================
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = OUTPUT_DIR / "reports"
    CHARTS_DIR = OUTPUT_DIR / "charts"
    
    # Klasörleri oluştur
    for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, CHARTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    

    # Sayfa isimleri
    TYT_SHEET_NAME = "TYT"
    AYT_SHEET_NAME = "AYT"

    # config.py dosyasının ilgili bölümünü bu şekilde güncelle:

    @staticmethod
    def validate_config() -> bool:
        """
        Konfigürasyonun geçerliliğini kontrol eder
    
        Returns:
            bool: Konfigürasyon geçerli mi?
        """
        errors = []
        
        # Değişkenleri doğrudan ortamdan (environment) oku
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        credentials_path = os.getenv("CREDENTIALS_PATH")
        
        # Google Sheets URL kontrolü
        if not sheet_url:
            errors.append("GOOGLE_SHEET_URL boş bırakılamaz!")
    
        # Credentials dosyası kontrolü
        if not credentials_path or not Path(credentials_path).exists():
            errors.append(f"Credentials dosyası bulunamadı: {credentials_path}")
    
        if errors:
            print("❌ Konfigürasyon hataları:")
            for error in errors:
                print(f"  - {error}")
            return False
    
        print("✅ Konfigürasyon geçerli")
        return True
    
    # ==================== VERİ YAPISI ====================
    
    class TYT:
        """TYT sınavı için sabitler"""
        
        # Dersler
        SUBJECTS = ["Türkçe", "Matematik", "Fen", "Sosyal"]
        
        # Maksimum soru sayıları
        MAX_QUESTIONS = {
            "Türkçe": 40,
            "Matematik": 40,
            "Fen": 20,
            "Sosyal": 20
        }
        
        # Maksimum net değerleri
        MAX_NETS = {
            "Türkçe Net": 40,
            "Matematik Net": 40,
            "Fen Net": 20,
            "Sosyal Net": 20,
            "Toplam Net": 120
        }
        
        # Sütun isimleri
        REQUIRED_COLUMNS = [
            "Deneme Adı",
            "Tarih",
            "Süre (dk)",
            "Toplam Net",
            "Türkçe Net",
            "Matematik Net",
            "Fen Net",
            "Sosyal Net"
        ]
        
        TOPIC_COLUMNS = [
            "Türkçe Yanlış Konular",
            "Matematik Yanlış Konular",
            "Fen Yanlış Konular",
            "Sosyal Yanlış Konular"
        ]
        
        # Süre limitleri (dakika)
        MIN_DURATION = 30
        MAX_DURATION = 180
        RECOMMENDED_DURATION = 135
        
        # Fen alt dalları (opsiyonel detay için)
        FEN_SUBCATEGORIES = ["Fizik", "Kimya", "Biyoloji"]
        
        # Puan türü (YKS sistemi için)
        SCORE_TYPES = ["SAY", "EA", "SÖZ", "DİL"]
    
    class AYT:
        """AYT sınavı için sabitler"""
        
        # Dersler
        SUBJECTS = ["Matematik", "Fizik", "Kimya", "Biyoloji"]
        
        # Maksimum soru sayıları
        MAX_QUESTIONS = {
            "Matematik": 40,
            "Fizik": 14,
            "Kimya": 13,
            "Biyoloji": 13
        }
        
        # Maksimum net değerleri
        MAX_NETS = {
            "Matematik Net": 40,
            "Fizik Net": 14,
            "Kimya Net": 13,
            "Biyoloji Net": 13,
            "Toplam Net": 80
        }
        
        # Sütun isimleri
        REQUIRED_COLUMNS = [
            "Deneme Adı",
            "Tarih",
            "Süre (dk)",
            "Toplam Net",
            "Matematik Net",
            "Fizik Net",
            "Kimya Net",
            "Biyoloji Net"
        ]
        
        TOPIC_COLUMNS = [
            "Matematik Yanlış Konular",
            "Fizik Yanlış Konular",
            "Kimya Yanlış Konular",
            "Biyoloji Yanlış Konular"
        ]
        
        # Süre limitleri (dakika)
        MIN_DURATION = 30
        MAX_DURATION = 220
        RECOMMENDED_DURATION = 180
        
        # Puan türü
        SCORE_TYPES = ["SAY", "EA"]
        
        # Edebiyat-Coğrafya seçenekleri (bazı AYT'lerde var)
        OPTIONAL_SUBJECTS = ["Edebiyat", "Coğrafya", "Tarih", "Felsefe"]
    
    # ==================== VERİ TEMİZLEME ====================
    
    class Cleaning:
        """Veri temizleme ayarları"""
        
        # Mod ayarları
        STRICT_MODE = False  # True ise hatalı satırları atar
        AUTO_FIX = True      # Otomatik düzeltme yap
        
        # Tarih kontrolü
        MIN_YEAR = 2020

        #İsim uzunlukları
        MAX_EXAM_NAME_LENGTH = 50

        # Kritik sütunlar
        CRITICAL_COLUMNS = ["Deneme Adı", "Tarih"]
        
        # Net kontrolleri
        ALLOW_NEGATIVE_NETS = False
        NET_TOLERANCE = 0.5  # Toplam net ile alt netler arası fark toleransı
        
        # Konu parsing
        MIN_TOPIC_LENGTH = 2  # Minimum konu ismi uzunluğu
        MAX_TOPICS_PER_SUBJECT = 50  # Bir derste maksimum konu sayısı
        
        # Duplikasyon
        CHECK_DUPLICATES = False
        DUPLICATE_SUBSET = ["Deneme Adı", "Tarih"]  # Bu sütunlara göre kontrol et
        
        # Eksik veri doldurma
        FILL_NA_WITH_ZERO = ["Toplam Net"]  # Bu sütunlarda NaN'ı 0 yap
    
    # ==================== ANALİZ AYARLARI ====================
    
    class Analysis:
        """Analiz parametreleri"""

        # config.py -> Analysis sınıfı içi
        TOPIC_MIN_FREQUENCY = 2
        TOPIC_WEAK_AREA_THRESHOLD = 3
        TOPIC_PRIORITY_LEVELS = {
            "🔴 Çok Acil": 5,
            "🟠 Acil": 3,
            "🟡 Orta": 2
        }
        TOPIC_RECURRING_PAIR_MIN_COOCCURRENCE = 2
        
        # İstatistikler
        CALCULATE_MEAN = True
        CALCULATE_MEDIAN = True
        CALCULATE_STD = True
        CALCULATE_TREND = True  # Trend analizi (lineer regresyon)
        
        # Hedef belirleme
        ENABLE_TARGETS = True
        DEFAULT_TARGET_NET = {
            "TYT": 100,  # TYT hedef net
            "AYT": 60    # AYT hedef net
        }
        
        # Konu analizi
        TOP_N_TOPICS = 10  # En çok yanlış yapılan kaç konu gösterilsin
        TOPIC_FREQUENCY_THRESHOLD = 2  # En az kaç kez yanlış yapılmalı
        
        # Zaman analizi
        WEEKLY_ANALYSIS = True
        MONTHLY_ANALYSIS = True
        
        # Karşılaştırma
        COMPARE_LAST_N_EXAMS = 5  # Son kaç denemeyi karşılaştır
        
        # İlerleme hesaplama
        IMPROVEMENT_WINDOW = 3  # Son 3 denemeye göre ilerleme hesapla
        TREND_P_VALUE_THRESHOLD = 0.05
        TREND_STRONG_SLOPE = 0.5
        TREND_LIGHT_SLOPE = 0.1
        IMPROVEMENT_STRONG_THRESHOLD = 5.0
        IMPROVEMENT_LIGHT_THRESHOLD = 2.0
        WEAK_SUBJECT_PERCENTILE = 25
        STRONG_SUBJECT_PERCENTILE = 75
        CONSISTENCY_THRESHOLDS = { # CV %
            "Çok Tutarlı": 10,
            "Tutarlı": 20,
            "Orta": 30,
            "Dalgalı": 40
        }

    
    # ==================== GÖRSELLEŞTİRME ====================
    
    class Visualization:
        """Grafik ayarları"""
        
        # Genel ayarlar
        FIGURE_SIZE = (12, 6)
        DPI = 100
        STYLE = "seaborn-v0_8-darkgrid"  # matplotlib style
        
        # Renkler (hex kodları)
        COLOR_PALETTE = {
            "primary": "#3498db",      # Mavi
            "secondary": "#2ecc71",    # Yeşil
            "danger": "#e74c3c",       # Kırmızı
            "warning": "#f39c12",      # Turuncu
            "info": "#9b59b6",         # Mor
            "success": "#27ae60",      # Koyu yeşil
            "muted": "#95a5a6"         # Gri
        }
        
        # Ders renkleri
        SUBJECT_COLORS = {
            "Türkçe": "#e74c3c",
            "Matematik": "#3498db",
            "Fen": "#2ecc71",
            "Sosyal": "#f39c12",
            "Fizik": "#9b59b6",
            "Kimya": "#e67e22",
            "Biyoloji": "#1abc9c",
            "Edebiyat": "#34495e",
            "Coğrafya": "#16a085",
            "Tarih": "#c0392b"
        }
        
        # Grafik türleri
        ENABLE_INTERACTIVE = True  # Plotly ile interaktif grafikler
        SAVE_STATIC = True         # PNG olarak kaydet
        SAVE_HTML = True           # HTML olarak kaydet (interaktif)
        
        # Çubuk grafik ayarları
        BAR_WIDTH = 0.8
        BAR_EDGE_COLOR = "black"
        BAR_EDGE_WIDTH = 0.5
        
        # Çizgi grafik ayarları
        LINE_WIDTH = 2
        MARKER_SIZE = 8
        
        # Isı haritası ayarları
        HEATMAP_CMAP = "YlOrRd"  # Sarı-Turuncu-Kırmızı
        HEATMAP_ANNOT = True     # Değerleri göster
        
        # Font ayarları
        FONT_FAMILY = "sans-serif"
        TITLE_FONT_SIZE = 16
        LABEL_FONT_SIZE = 12
        TICK_FONT_SIZE = 10
        
        # Lejant
        LEGEND_LOCATION = "best"
        LEGEND_FRAME = True
    
    # ==================== RAPOR AYARLARI ====================
    
    class Report:
        """Rapor üretimi ayarları"""
        
        # Rapor formatları
        GENERATE_PDF = False  # Şimdilik False (gerekirse ekleriz)
        GENERATE_HTML = True
        GENERATE_MARKDOWN = True
        
        # İçerik
        INCLUDE_SUMMARY = True
        INCLUDE_DETAILED_STATS = True
        INCLUDE_CHARTS = True
        INCLUDE_RECOMMENDATIONS = True
        
        # Otomatik raporlama
        AUTO_REPORT_FREQUENCY = "weekly"  # "daily", "weekly", "monthly"
        
        # Rapor şablonu
        TEMPLATE_FILE = "report_template.html"
        
        # Logo/Başlık
        REPORT_TITLE = "YKS Deneme Analiz Raporu"
        STUDENT_NAME = "Öğrenci"  # Kullanıcı tarafından doldurulacak
    
    # ==================== LOGGİNG ====================
    
    class Logging:
        """Loglama ayarları"""
        
        LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        
        # Log dosyaları
        LOG_FILE = "yks_analyzer.log"
        MAX_BYTES = 10 * 1024 * 1024  # 10 MB
        BACKUP_COUNT = 5
    
    # ==================== PERFORMANS ====================
    
    class Performance:
        """Performans optimizasyonu"""
        
        # Cache
        ENABLE_CACHE = True
        CACHE_TTL = 3600  # 1 saat (saniye)
        
        # Paralel işleme
        USE_MULTIPROCESSING = False  # Büyük veri setleri için
        N_JOBS = -1  # -1 = tüm CPU çekirdekleri
        
        # Veri limitleri
        MAX_ROWS_IN_MEMORY = 10000
        CHUNK_SIZE = 1000
    
    # ==================== YKS SİSTEMİ SABİTLERİ ====================
    
    class YKS:
        """YKS puan sistemi sabitleri"""
        
        # Puan katsayıları (2024 sistemi)
        TYT_BASE_POINT = 100
        AYT_BASE_POINT = 100
        
        # TYT katsayıları (puan türüne göre)
        TYT_COEFFICIENTS = {
            "SAY": {
                "Türkçe": 3.3,
                "Matematik": 3.3,
                "Fen": 3.4,
                "Sosyal": 3.0
            },
            "EA": {
                "Türkçe": 3.3,
                "Matematik": 3.3,
                "Fen": 3.0,
                "Sosyal": 3.4
            },
            "SÖZ": {
                "Türkçe": 3.6,
                "Matematik": 3.0,
                "Fen": 3.0,
                "Sosyal": 3.4
            },
            "DİL": {
                "Türkçe": 3.6,
                "Matematik": 3.0,
                "Fen": 3.0,
                "Sosyal": 3.4
            }
        }
        
        # AYT katsayıları
        AYT_COEFFICIENTS = {
            "SAY": {
                "Matematik": 3.0,
                "Fizik": 3.1,
                "Kimya": 3.2,
                "Biyoloji": 3.1
            },
            "EA": {
                "Matematik": 3.4,
                "Fizik": 2.8,
                "Kimya": 2.8,
                "Biyoloji": 2.8
            }
        }
        
        # Minimum net gereksinimleri (puan almak için)
        MIN_NETS_FOR_SCORE = {
            "TYT": 0.5,  # En az 0.5 net olmalı
            "AYT": 0.5
        }
        
        # Hedef puanlar (örnek)
        TARGET_SCORES = {
            "İyi Bir Devlet Üniversitesi": 400,
            "Orta Seviye Üniversite": 350,
            "YÖK Taban Puanı": 180
        }


# ==================== YARDIMCI FONKSİYONLAR ====================

def get_subject_color(subject: str) -> str:
    """
    Ders adına göre renk döndürür
    
    Args:
        subject: Ders adı
        
    Returns:
        str: Hex renk kodu
    """
    return Config.Visualization.SUBJECT_COLORS.get(
        subject, 
        Config.Visualization.COLOR_PALETTE["muted"]
    )


def get_max_net(subject: str, exam_type: str = "TYT") -> int:
    """
    Dersin maksimum net değerini döndürür
    
    Args:
        subject: Ders adı (örn: "Türkçe Net")
        exam_type: "TYT" veya "AYT"
        
    Returns:
        int: Maksimum net değeri
    """
    exam_config = Config.TYT if exam_type == "TYT" else Config.AYT
    return exam_config.MAX_NETS.get(subject, 0)



def print_config_summary():
    """Konfigürasyon özetini yazdırır"""
    print("=" * 60)
    print("YKS ANALİZ SİSTEMİ - KONFİGÜRASYON ÖZETİ")
    print("=" * 60)
    print(f"\n📁 Klasörler:")
    print(f"  Base: {Config.BASE_DIR}")
    print(f"  Data: {Config.DATA_DIR}")
    print(f"  Output: {Config.OUTPUT_DIR}")
    print(f"\n📊 TYT Ayarları:")
    print(f"  Dersler: {', '.join(Config.TYT.SUBJECTS)}")
    print(f"  Maksimum Net: {Config.TYT.MAX_NETS['Toplam Net']}")
    print(f"\n📊 AYT Ayarları:")
    print(f"  Dersler: {', '.join(Config.AYT.SUBJECTS)}")
    print(f"  Maksimum Net: {Config.AYT.MAX_NETS['Toplam Net']}")
    print(f"\n🎨 Görselleştirme:")
    print(f"  Stil: {Config.Visualization.STYLE}")
    print(f"  İnteraktif: {Config.Visualization.ENABLE_INTERACTIVE}")
    print("=" * 60)


# Modül import edildiğinde çalışsın
if __name__ == "__main__":
    print_config_summary()