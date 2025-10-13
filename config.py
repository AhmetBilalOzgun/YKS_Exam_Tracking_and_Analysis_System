"""
YKS Analyzer System Configuration Module
"""

from pathlib import Path
from typing import Dict, List
import os
from dotenv import load_dotenv

load_dotenv()  # load .env file if present


class Config:
    
    # ==================== GOOGLE SHEETS ====================
    GOOGLE_SHEET_URL= os.getenv("GOOGLE_SHEET_URL")
    CREDENTIALS_PATH= os.getenv("CREDENTIALS_PATH")


    
    
    # ==================== PROJECT DIRECTORIES ====================
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"
    OUTPUT_DIR = BASE_DIR / "output"
    LOGS_DIR = BASE_DIR / "logs"
    REPORTS_DIR = OUTPUT_DIR / "reports"
    CHARTS_DIR = OUTPUT_DIR / "charts"
    
    # generate directories if they don't exist
    for directory in [DATA_DIR, OUTPUT_DIR, LOGS_DIR, REPORTS_DIR, CHARTS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
    

    # worksheet names
    TYT_SHEET_NAME = "TYT"
    AYT_SHEET_NAME = "AYT"


    @staticmethod
    def validate_config() -> bool:
        """
        Checks if the configuration is valid.
    
        Returns:
            bool: True if valid, False otherwise
        """
        errors = []
        
        # Load environment variables
        sheet_url = os.getenv("GOOGLE_SHEET_URL")
        credentials_path = os.getenv("CREDENTIALS_PATH")
        
        # Google Sheets URL control
        if not sheet_url:
            errors.append("GOOGLE_SHEET_URL boş bırakılamaz!")
    
        # Credentials dosyası control
        if not credentials_path or not Path(credentials_path).exists():
            errors.append(f"Credentials dosyası bulunamadı: {credentials_path}")
    
        if errors:
            print("❌ Config errors:")
            for error in errors:
                print(f"  - {error}")
            return False
    
        print("✅ Config is valid.")
        return True
    
    # ==================== DATA STRUCTURE ====================
    
    class TYT:
        """Constants for TYT exam"""
        
        # Subjects
        SUBJECTS = ["Türkçe", "Matematik", "Fen", "Sosyal"]
        
        # Maximum question counts
        MAX_QUESTIONS = {
            "Türkçe": 40,
            "Matematik": 40,
            "Fen": 20,
            "Sosyal": 20
        }
        
        # Maximum net values
        MAX_NETS = {
            "Türkçe Net": 40,
            "Matematik Net": 40,
            "Fen Net": 20,
            "Sosyal Net": 20,
            "Toplam Net": 120
        }
        
        #   Column names
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
        
        # Duration limits (minutes)
        MIN_DURATION = 30
        MAX_DURATION = 180
        RECOMMENDED_DURATION = 135
        
        # Science subcategories
        FEN_SUBCATEGORIES = ["Fizik", "Kimya", "Biyoloji"]
        
        # Score types
        SCORE_TYPES = ["SAY", "EA", "SÖZ", "DİL"]
    
    class AYT:
        """Constants for AYT exam"""
        
        # Subjects
        SUBJECTS = ["Matematik", "Fizik", "Kimya", "Biyoloji"]
        
        # Maximum question counts
        MAX_QUESTIONS = {
            "Matematik": 40,
            "Fizik": 14,
            "Kimya": 13,
            "Biyoloji": 13
        }
        
        # Maximum net values
        MAX_NETS = {
            "Matematik Net": 40,
            "Fizik Net": 14,
            "Kimya Net": 13,
            "Biyoloji Net": 13,
            "Toplam Net": 80
        }
        
        # Column names
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
        
        # Duration limits (minutes)
        MIN_DURATION = 30
        MAX_DURATION = 220
        RECOMMENDED_DURATION = 180
        
        #  Score types
        SCORE_TYPES = ["SAY", "EA"]
        
        
        OPTIONAL_SUBJECTS = ["Edebiyat", "Coğrafya", "Tarih", "Felsefe"]
    
    # ==================== VERİ TEMİZLEME ====================
    
    class Cleaning:
        """Data cleaning parameters"""
        
        # Mode settings
        STRICT_MODE = False  # İf strict mode is on, errors will raise exceptions
        AUTO_FIX = True      # If auto fix is on, some common issues will be fixed automatically
        
        # Date Control
        MIN_YEAR = 2020

        #Name lengths
        MAX_EXAM_NAME_LENGTH = 50

        # Critical columns that must not be empty
        CRITICAL_COLUMNS = ["Deneme Adı", "Tarih"]
        
        # Net values
        ALLOW_NEGATIVE_NETS = False
        NET_TOLERANCE = 0.5  # Toplam net ile alt netler arası fark toleransı
        
        # Topic constraints
        MIN_TOPIC_LENGTH = 2  # Minimum konu ismi uzunluğu
        MAX_TOPICS_PER_SUBJECT = 50  # Bir derste maksimum konu sayısı
        
        # Duplicate control
        CHECK_DUPLICATES = False
        DUPLICATE_SUBSET = ["Deneme Adı", "Tarih"]  # Bu sütunlara göre kontrol et
        
        # NaN handling
        FILL_NA_WITH_ZERO = ["Toplam Net"]  # Bu sütunlarda NaN'ı 0 yap
    
    # ==================== ANALYSIS SETTINGS ====================
    
    class Analysis:
        """Analysis parameters"""

        
        TOPIC_MIN_FREQUENCY = 2
        TOPIC_WEAK_AREA_THRESHOLD = 3
        TOPIC_PRIORITY_LEVELS = {
            "🔴 Very Urgent": 5,
            "🟠 Urgent": 3,
            "🟡 Not Urgent": 2
        }
        TOPIC_RECURRING_PAIR_MIN_COOCCURRENCE = 2
        
        # Statistics to calculate
        CALCULATE_MEAN = True
        CALCULATE_MEDIAN = True
        CALCULATE_STD = True
        CALCULATE_TREND = True  
        
        # Goal tracking
        ENABLE_TARGETS = True
        DEFAULT_TARGET_NET = {
            "TYT": 100,  # TYT Goal net
            "AYT": 60    # AYT Goal net
        }
        
        # Topic analysis
        TOP_N_TOPICS = 10  
        TOPIC_FREQUENCY_THRESHOLD = 2  # Minimum frequency to consider a topic
        
        # Time based analysis
        WEEKLY_ANALYSIS = True
        MONTHLY_ANALYSIS = True
        
        # Comparison settings
        COMPARE_LAST_N_EXAMS = 5  # Compare with last N exams
        
        # Trend analysis
        IMPROVEMENT_WINDOW = 3  
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

    
    # ==================== VISUALIZATION ====================
    
    class Visualization:
        """Graph and chart settings"""
        
        # General settings
        FIGURE_SIZE = (12, 6)
        DPI = 100
        STYLE = "seaborn-v0_8-darkgrid"  # matplotlib style
        
        
        COLOR_PALETTE = {
            "primary": "#3498db",      
            "secondary": "#2ecc71",    
            "danger": "#e74c3c",       
            "warning": "#f39c12",      
            "info": "#9b59b6",         
            "success": "#27ae60",      
            "muted": "#95a5a6"         
        }
        
        
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
        
        
        ENABLE_INTERACTIVE = True  # Plotly ile interaktif grafikler
        SAVE_STATIC = True         # PNG olarak kaydet
        SAVE_HTML = True           # HTML olarak kaydet (interaktif)
        
        
        BAR_WIDTH = 0.8
        BAR_EDGE_COLOR = "black"
        BAR_EDGE_WIDTH = 0.5
        
        
        LINE_WIDTH = 2
        MARKER_SIZE = 8
        
        
        HEATMAP_CMAP = "YlOrRd"  # Sarı-Turuncu-Kırmızı
        HEATMAP_ANNOT = True     # Değerleri göster
        
        
        FONT_FAMILY = "sans-serif"
        TITLE_FONT_SIZE = 16
        LABEL_FONT_SIZE = 12
        TICK_FONT_SIZE = 10
        
        
        LEGEND_LOCATION = "best"
        LEGEND_FRAME = True
    
    # ==================== REPORT SETTINGS ====================
    
    class Report:
        """Report generation settings"""
        
        # Output formats
        GENERATE_PDF = False  # Şimdilik False (gerekirse ekleriz)
        GENERATE_HTML = True
        GENERATE_MARKDOWN = True
        
        # Report sections
        INCLUDE_SUMMARY = True
        INCLUDE_DETAILED_STATS = True
        INCLUDE_CHARTS = True
        INCLUDE_RECOMMENDATIONS = True
        
        # Auto report settings
        AUTO_REPORT_FREQUENCY = "weekly"  # "daily", "weekly", "monthly"
        
        # Report template
        TEMPLATE_FILE = "report_template.html"
        
        # Report metadata
        REPORT_TITLE = "YKS Deneme Analiz Raporu"
        STUDENT_NAME = "Öğrenci"  # Kullanıcı tarafından doldurulacak
    
    # ==================== LOGGİNG ====================
    
    class Logging:
        """Logging settings"""
        
        LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
        FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
        
        # File logging
        LOG_FILE = "yks_analyzer.log"
        MAX_BYTES = 10 * 1024 * 1024  # 10 MB
        BACKUP_COUNT = 5
    
    # ==================== PERFORMANCE ====================
    
    class Performance:
        """Performance optimization settings"""
        
        # Caching
        ENABLE_CACHE = True
        CACHE_TTL = 3600  # 1 saat (saniye)
        
        # Multiprocessing
        USE_MULTIPROCESSING = False  # Büyük veri setleri için
        N_JOBS = -1  # -1 = tüm CPU çekirdekleri
        
        # Memory management
        MAX_ROWS_IN_MEMORY = 10000
        CHUNK_SIZE = 1000
    
    # ==================== YKS SYSTEM CONSTANTS ====================
    
    class YKS:
        """YKS exam system constants"""
        
        
        TYT_BASE_POINT = 100
        AYT_BASE_POINT = 100
        
        
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
        
        # Minimum net values to consider for score calculation
        MIN_NETS_FOR_SCORE = {
            "TYT": 0.5,
            "AYT": 0.5
        }
        
        # Target scores for different university tiers
        TARGET_SCORES = {
            "İyi Bir Devlet Üniversitesi": 400,
            "Orta Seviye Üniversite": 350,
            "YÖK Taban Puanı": 180
        }


# ==================== HELPERS ====================

def get_subject_color(subject: str) -> str:
    """
    Returns the hex color code for a given subject
    
    Args:
        subject: Subject name (e.g., "Matematik")
        
    Returns:
        str: Hex color code
    """
    return Config.Visualization.SUBJECT_COLORS.get(
        subject, 
        Config.Visualization.COLOR_PALETTE["muted"]
    )


def get_max_net(subject: str, exam_type: str = "TYT") -> int:
    """
    Returns the maximum net value for a given subject and exam type.
    
    Args:
        subject: Ders adı (e.g., "Matematik")
        exam_type: "TYT" or "AYT"
        
    Returns:
        int: Maximum net value
    """
    exam_config = Config.TYT if exam_type == "TYT" else Config.AYT
    return exam_config.MAX_NETS.get(subject, 0)



def print_config_summary():
    """Writes a summary of the configuration to the console"""
    print("=" * 60)
    print("📋 YKS Analyzer Configuration Summary")
    print("=" * 60)
    print(f"\n📁 :")
    print(f"  Base: {Config.BASE_DIR}")
    print(f"  Data: {Config.DATA_DIR}")
    print(f"  Output: {Config.OUTPUT_DIR}")
    print(f"\n📊 TYT Settings:")
    print(f"  Subjects: {', '.join(Config.TYT.SUBJECTS)}")
    print(f"  Maximum Net: {Config.TYT.MAX_NETS['Toplam Net']}")
    print(f"\n📊 AYT Settings:")
    print(f"  Subjects: {', '.join(Config.AYT.SUBJECTS)}")
    print(f"  Maximum Net: {Config.AYT.MAX_NETS['Toplam Net']}")
    print(f"\n🎨 Visualization:")
    print(f"  Stil: {Config.Visualization.STYLE}")
    print(f"  İnteraktif: {Config.Visualization.ENABLE_INTERACTIVE}")
    print("=" * 60)


# =================== RUN VALIDATION IF MAIN ====================
if __name__ == "__main__":
    print_config_summary()