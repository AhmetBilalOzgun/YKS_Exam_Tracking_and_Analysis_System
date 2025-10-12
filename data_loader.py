"""
YKS Analiz Sistemi - Veri Yükleme Modülü
Google Sheets'ten TYT ve AYT verilerini yükler
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict, List
from config import Config
import logging

# Logging ayarları

logger = logging.getLogger(__name__)


class GoogleSheetsLoader:
    """
    Google Sheets'ten YKS deneme verilerini yükleyen sınıf
    
    Attributes:
        sheet_url (str): Google Sheets doküman URL'si veya ID'si
        credentials_path (str): Service account JSON dosyasının yolu
        client: Google Sheets API client
        workbook: Açılan Google Sheets dokümanı
    """
    
    # Google Sheets API için gerekli scope'lar
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    
    def __init__(self, sheet_url: str, credentials_path: str):
        """
        GoogleSheetsLoader başlatıcı
        
        Args:
            sheet_url: Google Sheets URL'si veya doküman ID'si
            credentials_path: Service account credentials JSON dosya yolu
        """
        self.TYT_COLUMNS = {
            'required': Config.TYT.REQUIRED_COLUMNS,
            'topic_columns': Config.TYT.TOPIC_COLUMNS
        }
        self.AYT_COLUMNS = {
            'required': Config.AYT.REQUIRED_COLUMNS,
            'topic_columns': Config.AYT.TOPIC_COLUMNS
        }
        self.sheet_url = sheet_url
        self.credentials_path = credentials_path
        self.client = None
        self.workbook = None
        
        self._authenticate()
    
    def _authenticate(self) -> None:
        """Google Sheets API'ye kimlik doğrulama yapar"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets kimlik doğrulama başarılı")
        except Exception as e:
            logger.error(f"Kimlik doğrulama hatası: {e}")
            raise
    
    def _open_workbook(self) -> None:
        """Google Sheets dokümanını açar"""
        try:
            # URL veya ID ile açmayı dene
            if 'docs.google.com' in self.sheet_url:
                self.workbook = self.client.open_by_url(self.sheet_url)
            else:
                self.workbook = self.client.open_by_key(self.sheet_url)
            logger.info(f"Doküman açıldı: {self.workbook.title}")
        except Exception as e:
            logger.error(f"Doküman açma hatası: {e}")
            raise
    
    def _get_worksheet_data(self, worksheet_name: str) -> pd.DataFrame:
        """
        Belirtilen worksheet'ten veri çeker
        
        Args:
            worksheet_name: Worksheet (sayfa) adı
            
        Returns:
            pd.DataFrame: Çekilen veriler
        """
        try:
            if not self.workbook:
                self._open_workbook()
            
            worksheet = self.workbook.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            logger.info(f"{worksheet_name} sayfasından {len(df)} satır yüklendi")
            return df
            
        except gspread.WorksheetNotFound:
            logger.error(f"'{worksheet_name}' sayfası bulunamadı!")
            raise
        except Exception as e:
            logger.error(f"Veri çekme hatası ({worksheet_name}): {e}")
            raise
    
    def _validate_columns(self, df: pd.DataFrame, expected_cols: Dict[str, List[str]], 
                         exam_type: str) -> bool:
        """
        DataFrame'in beklenen sütunlara sahip olup olmadığını kontrol eder
        
        Args:
            df: Kontrol edilecek DataFrame
            expected_cols: Beklenen sütunlar dictionary'si
            exam_type: "TYT" veya "AYT"
            
        Returns:
            bool: Doğrulama başarılı mı?
        """
        required = expected_cols['required']
        topic_cols = expected_cols['topic_columns']
        all_expected = required + topic_cols
        
        missing_cols = set(all_expected) - set(df.columns)
        
        if missing_cols:
            logger.warning(f"{exam_type} için eksik sütunlar: {missing_cols}")
            # Sadece uyarı ver, hata verme (bazı sütunlar opsiyonel olabilir)
        
        # En azından zorunlu sütunlar olmalı
        critical_missing = set(required) - set(df.columns)
        if critical_missing:
            logger.error(f"{exam_type} için kritik eksik sütunlar: {critical_missing}")
            return False
        
        return True
    
    def load_tyt_data(self, worksheet_name: str = "TYT") -> pd.DataFrame:
        """
        TYT deneme verilerini yükler
        
        Args:
            worksheet_name: TYT verisinin bulunduğu sayfa adı (varsayılan: "TYT")
            
        Returns:
            pd.DataFrame: TYT deneme verileri
        """
        logger.info("TYT verileri yükleniyor...")
        df = self._get_worksheet_data(worksheet_name)
        
        if df.empty:
            logger.warning("TYT sayfası boş!")
            return df
        
        # Sütun kontrolü
        self._validate_columns(df, self.TYT_COLUMNS, "TYT")
        
        logger.info(f"TYT verileri başarıyla yüklendi: {df.shape}")
        return df

    def load_ayt_data(self, worksheet_name: str = "AYT") -> pd.DataFrame:
        """
        AYT deneme verilerini yükler
        
        Args:
            worksheet_name: AYT verisinin bulunduğu sayfa adı (varsayılan: "AYT")
            
        Returns:
            pd.DataFrame: AYT deneme verileri
        """
        logger.info("AYT verileri yükleniyor...")
        df = self._get_worksheet_data(worksheet_name)
        
        if df.empty:
            logger.warning("AYT sayfası boş!")
            return df
        
        # Sütun kontrolü
        self._validate_columns(df, self.AYT_COLUMNS, "AYT")
        
        logger.info(f"AYT verileri başarıyla yüklendi: {df.shape}")
        return df
    
    def refresh_data(self) -> Dict[str, pd.DataFrame]:
        """
        Hem TYT hem AYT verilerini yeniden yükler
        
        Returns:
            Dict: {'tyt': tyt_df, 'ayt': ayt_df}
        """
        logger.info("Tüm veriler yenileniyor...")
        
        # Workbook'u yeniden aç
        self._open_workbook()
        
        return {
            'tyt': self.load_tyt_data(),
            'ayt': self.load_ayt_data()
        }
    
    def get_worksheet_names(self) -> List[str]:
        """
        Dokümandaki tüm sayfa isimlerini döndürür
        
        Returns:
            List[str]: Sayfa isimleri
        """
        if not self.workbook:
            self._open_workbook()
        
        worksheets = self.workbook.worksheets()
        return [ws.title for ws in worksheets]
    
    def preview_data(self, worksheet_name: str, n_rows: int = 5) -> pd.DataFrame:
        """
        Belirtilen sayfanın ilk n satırını önizler
        
        Args:
            worksheet_name: Sayfa adı
            n_rows: Önizlenecek satır sayısı
            
        Returns:
            pd.DataFrame: İlk n satır
        """
        df = self._get_worksheet_data(worksheet_name)
        return df.head(n_rows)


