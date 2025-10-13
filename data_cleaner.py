# ders_takip/data_cleaner.py

import pandas as pd
import numpy as np
from typing import List, Dict, Tuple, Optional
import re
from datetime import datetime
import logging
from config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """
    The class responsible for cleaning and validating YKS trial exam data.
    
    Attributes:
        strict_mode (bool): Katı mod - hatalı verileri reddeder
        auto_fix (bool): Otomatik düzeltme modu
    """
    
    def __init__(self, config: Config, strict_mode: bool = False, auto_fix: bool = True):
        """
        DataCleaner startup
    
        Args:
            config: Configuration object
            strict_mode: True ise hatalı satırları atar
            auto_fix: True ise düzeltilebilir hataları otomatik düzeltir
        """
        self.config = config
        self.strict_mode = strict_mode if strict_mode is not False else self.config.Cleaning.STRICT_MODE
        self.auto_fix = auto_fix if auto_fix is not False else self.config.Cleaning.AUTO_FIX

        self.cleaning_report = {
            'rows_removed': 0,
            'values_fixed': 0,
            'warnings': []
        }
    
    def clean_full_dataset(self, df: pd.DataFrame, exam_type: str = "TYT") -> pd.DataFrame:
        """
        pipeline of all cleaning steps
        
        Args:
            df: DataFrame to clean
            exam_type: "TYT" or "AYT"
            
        Returns:
            pd.DataFrame: cleaned DataFrame
        """
        logger.info(f"{exam_type} Data is getting cleaned...")
        self.cleaning_report = {'rows_removed': 0, 'values_fixed': 0, 'warnings': []}
        
        original_rows = len(df)

        # 0. Basic preprocessing
        df = self.basic_preprocessing(df)
        
        # 1. Date cleaning
        df = self.clean_dates(df)
        
        # 2. Handling missing values
        df = self.handle_missing_values(df)
        
        # 4. Validate duration
        df = self.validate_duration(df, exam_type=exam_type)
        
        # 5. Parse topics
        df = self.parse_all_topics(df, exam_type)
        
        # 6. Clean exam names
        df = self.clean_exam_names(df)
        
        # 8. Final validation
        df = self.validate_data(df)
        
        self.cleaning_report['rows_removed'] = original_rows - len(df)
        
        logger.info(f"Cleanin complete: {original_rows} -> {len(df)} satır")
        logger.info(f"Report: {self.cleaning_report}")
        
        return df
    
    def clean_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans and standardizes the 'Tarih' column
        
        Args:
            df: DataFrame
            
        Returns:
            pd.DataFrame: DataFrame with cleaned 'Tarih' column
        """
        if 'Tarih' not in df.columns:
            logger.warning("Tarih sütunu bulunamadı")
            return df
        
        df = df.copy()
        
        date_formats = [
            '%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%d.%m.%y', '%d/%m/%y',
        ]
        
        def parse_date(date_str):
            if pd.isna(date_str): return pd.NaT
            if isinstance(date_str, (pd.Timestamp, datetime)): return pd.Timestamp(date_str)
            date_str = str(date_str).strip()
            for fmt in date_formats:
                try: return pd.to_datetime(date_str, format=fmt)
                except: continue
            try: return pd.to_datetime(date_str, dayfirst=True)
            except:
                logger.warning(f"Tarih couldn't be parsed: {date_str}")
                return pd.NaT
        
        df['Tarih'] = df['Tarih'].apply(parse_date)
        
        future_dates = df[df['Tarih'] > pd.Timestamp.now()]
        if len(future_dates) > 0:
            self.cleaning_report['warnings'].append(f"{len(future_dates)} Date(s) in the future found")
        
        old_dates = df[df['Tarih'] < pd.Timestamp(f'{self.config.Cleaning.MIN_YEAR}-01-01')]
        if len(old_dates) > 0:
            self.cleaning_report['warnings'].append(f"{len(old_dates)} Date(s) older than {self.config.Cleaning.MIN_YEAR} found")
        
        return df

    def parse_topics(self, topics_string: str) -> List[str]:
        """
        Parse a comma-separated topic string into a list of cleaned topics
        """
        if pd.isna(topics_string) or topics_string == '': return []
        topics_string = str(topics_string).strip()
        topics = [topic.strip() for topic in topics_string.split(',')]
        topics = [t for t in topics if len(t) > 1]
        topics = [re.sub(r'[^a-zA-ZğüşöçıİĞÜŞÖÇ0-9\s()\-]', '', t) for t in topics]
        unique_topics = []
        seen_lower = set()
        for topic in topics:
            topic_lower = topic.lower()
            if topic_lower not in seen_lower and topic:
                unique_topics.append(topic)
                seen_lower.add(topic_lower)
        return unique_topics

    def parse_all_topics(self, df: pd.DataFrame, exam_type: str = "TYT") -> pd.DataFrame:
        """
        Parse all topic columns in the DataFrame
        """
        df = df.copy()
        topic_columns = [col for col in df.columns if 'Yanlış Konular' in col]
        if not topic_columns:
            logger.warning("Couldn't find 'Yanlış Konular' column to parse")
            return df
        for col in topic_columns:
            df[col + '_List'] = df[col].apply(self.parse_topics)
            df[col + '_Count'] = df[col + '_List'].apply(len)
        logger.info(f"{len(topic_columns)} topic columns parsed")
        return df

    def validate_duration(self, df: pd.DataFrame, exam_type: str) -> pd.DataFrame:
        """
        Validates and cleans the 'Süre (dk)' column
        """
        exam_config = self.config.TYT if exam_type == "TYT" else self.config.AYT
        min_duration = exam_config.MIN_DURATION
        max_duration = exam_config.MAX_DURATION

        if 'Süre (dk)' not in df.columns:
            return df
        
        df = df.copy()
        
        negative_mask = df['Süre (dk)'] < 0
        if negative_mask.any():
            if self.auto_fix:
                df.loc[negative_mask, 'Süre (dk)'] = np.nan
                self.cleaning_report['values_fixed'] += negative_mask.sum()
        
        short_mask = (df['Süre (dk)'] < 30) & (df['Süre (dk)'] > 0)
        if short_mask.any():
            self.cleaning_report['warnings'].append(f"{short_mask.sum()} unusually short durations found")
        
        long_tyt = df['Süre (dk)'] > 180
        long_ayt = df['Süre (dk)'] > 220
        
        if long_tyt.any() or long_ayt.any():
            self.cleaning_report['warnings'].append(f"{(long_tyt | long_ayt).sum()} unusually long durations found")
        
        return df
        

    def clean_exam_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Cleans and standardizes the 'Deneme Adı' column
        """
        if 'Deneme Adı' not in df.columns: return df
        df = df.copy()
        df['Deneme Adı'] = df['Deneme Adı'].str.strip()
        long_names = df['Deneme Adı'].str.len() > self.config.Cleaning.MAX_EXAM_NAME_LENGTH
        if long_names.any():
            df.loc[long_names, 'Deneme Adı'] = df.loc[long_names, 'Deneme Adı'].str[:50] + '...'
            self.cleaning_report['values_fixed'] += long_names.sum()
        return df

    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handles missing values based on strict_mode and auto_fix settings
        """
        df = df.copy()
        critical_columns = self.config.Cleaning.CRITICAL_COLUMNS
        if self.strict_mode:
            critical_columns += ['Toplam Net']
        missing_critical = df[critical_columns].isna().any(axis=1)
        if missing_critical.any():
            if self.strict_mode:
                df = df[~missing_critical]
                logger.warning(f"{missing_critical.sum()} lines removed due to critical missing data")
            else:
                logger.warning(f"{missing_critical.sum()} lines have critical missing data but strict_mode is off")
        net_columns = [col for col in df.columns if 'Net' in col]
        for col in net_columns:
            na_count = df[col].isna().sum()
            if na_count > 0 and self.auto_fix:
                df[col] = df[col].fillna(0)
                self.cleaning_report['values_fixed'] += na_count
        return df

    def basic_preprocessing(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Basic preprocessing steps
        """
        df = df.dropna(how='all')
        if 'Tarih' in df.columns:
            try: df['Tarih'] = pd.to_datetime(df['Tarih'], dayfirst=True, errors='coerce')
            except Exception as e: logger.warning(f"couldn't transform date: {e}")
        net_columns = [col for col in df.columns if 'Net' in col]
        for col in net_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        if 'Süre (dk)' in df.columns:
            df['Süre (dk)'] = pd.to_numeric(df['Süre (dk)'], errors='coerce')
        return df

    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Final validation to remove completely empty rows
        """
        df = df.copy()
        empty_rows = df.isna().all(axis=1)
        if empty_rows.any():
            df = df[~empty_rows]
            logger.info(f"{empty_rows.sum()} completely empty rows removed")
        df = df.reset_index(drop=True)
        return df

    def get_cleaning_report(self) -> Dict:
        """
        Returns the cleaning report
        """
        return self.cleaning_report

    def add_derived_features(self, df: pd.DataFrame, exam_type: str = "TYT") -> pd.DataFrame:
        """
        Adds derived features like week number, month, year, day of week, total wrong topics, exam order
        """
        df = df.copy()
        if 'Tarih' in df.columns and not df['Tarih'].isna().all():
            df['Hafta'] = df['Tarih'].dt.isocalendar().week
            df['Ay'] = df['Tarih'].dt.month
            df['Yıl'] = df['Tarih'].dt.year
            df['Haftanın_Günü'] = df['Tarih'].dt.day_name()
        
        
            
        topic_count_columns = [col for col in df.columns if '_Count' in col]
        if topic_count_columns:
            df['Toplam_Yanlış_Konu_Sayısı'] = df[topic_count_columns].sum(axis=1)
        if 'Tarih' in df.columns:
            df = df.sort_values('Tarih')
            df['Deneme_Sırası'] = range(1, len(df) + 1)
        logger.info("Derived features added")
        return df