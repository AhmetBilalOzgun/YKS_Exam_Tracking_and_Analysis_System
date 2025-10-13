"""
Yks analyze system - Google Sheets data loader
"""

import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from typing import Optional, Dict, List
from config import Config
import logging

# Logging setup

logger = logging.getLogger(__name__)


class GoogleSheetsLoader:
    """
    Class to load data from Google Sheets using gspread and pandas.
    
    Attributes:
        sheet_url (str): Google Sheets URL or document ID
        credentials_path (str): Service account JSON credentials file path
        client: Google Sheets API client
        workbook: Açılan Google Sheets document
    """
    
    # Google Sheets API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/spreadsheets.readonly',
        'https://www.googleapis.com/auth/drive.readonly'
    ]
    
    
    def __init__(self, sheet_url: str, credentials_path: str):
        """
        GoogleSheetsLoader startup
        
        Args:
            sheet_url: Google Sheets URL or document ID
            credentials_path: Service account credentials JSON file path
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
        """Google Sheets API identity verification"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path,
                scopes=self.SCOPES
            )
            self.client = gspread.authorize(creds)
            logger.info("Google Sheets verified successfully")
        except Exception as e:
            logger.error(f"Verification error: {e}")
            raise
    
    def _open_workbook(self) -> None:
        """Opens the Google Sheets document"""
        try:
            # try to open by URL first, then by key
            if 'docs.google.com' in self.sheet_url:
                self.workbook = self.client.open_by_url(self.sheet_url)
            else:
                self.workbook = self.client.open_by_key(self.sheet_url)
            logger.info(f"Document has been opened: {self.workbook.title}")
        except Exception as e:
            logger.error(f"Document couldn't be opened: {e}")
            raise
    
    def _get_worksheet_data(self, worksheet_name: str) -> pd.DataFrame:
        """
        Reads data from the specified worksheet and returns it as a DataFrame
        
        Args:
            worksheet_name: Worksheet (tab) name
            
        Returns:
            pd.DataFrame: Worksheet data
        """
        try:
            if not self.workbook:
                self._open_workbook()
            
            worksheet = self.workbook.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            df = pd.DataFrame(data)
            
            logger.info(f"from page {worksheet_name} {len(df)} line data fetched")
            return df
            
        except gspread.WorksheetNotFound:
            logger.error(f"'{worksheet_name}' page not found in the document")
            raise
        except Exception as e:
            logger.error(f"Read error ({worksheet_name}): {e}")
            raise
    
    def _validate_columns(self, df: pd.DataFrame, expected_cols: Dict[str, List[str]], 
                         exam_type: str) -> bool:
        """
        Validates that the DataFrame contains the expected columns.
        
        Args:
            df: DataFrame to validate
            expected_cols: Dictionary with 'required' and 'topic_columns' lists
            exam_type: "TYT" or "AYT"
            
        Returns:
            bool: True if validation passes, False otherwise
        """
        required = expected_cols['required']
        topic_cols = expected_cols['topic_columns']
        all_expected = required + topic_cols
        
        missing_cols = set(all_expected) - set(df.columns)
        
        if missing_cols:
            logger.warning(f"{missing_cols} columns are missing in {exam_type} data")
            # Not all columns are mandatory
        
        # But these are critical
        critical_missing = set(required) - set(df.columns)
        if critical_missing:
            logger.error(f"{critical_missing} critical columns are missing in {exam_type} data")
            return False
        
        return True
    
    def load_tyt_data(self, worksheet_name: str = "TYT") -> pd.DataFrame:
        """
        Loads TYT exam data
        
        Args:
            worksheet_name: Name of the worksheet containing TYT data (default: "TYT")
            
        Returns:
            pd.DataFrame: TYT exam data
        """
        logger.info("TYT data is loading...")
        df = self._get_worksheet_data(worksheet_name)
        
        if df.empty:
            logger.warning("TYT page is empty!")
            return df
        
        # Sütun kontrolü
        self._validate_columns(df, self.TYT_COLUMNS, "TYT")
        
        logger.info(f"TYT data is loaded successfully: {df.shape}")
        return df

    def load_ayt_data(self, worksheet_name: str = "AYT") -> pd.DataFrame:
        """
        Loads AYT exam data
        
        Args:
            worksheet_name: Name of the worksheet containing AYT data (default: "AYT")
            
        Returns:
            pd.DataFrame: AYT exam data
        """
        logger.info("AYT data is loading...")
        df = self._get_worksheet_data(worksheet_name)
        
        if df.empty:
            logger.warning("AYT page is empty!")
            return df
        
        # Sütun kontrolü
        self._validate_columns(df, self.AYT_COLUMNS, "AYT")
        
        logger.info(f"AYT data is loaded successfully: {df.shape}")
        return df
    
    def refresh_data(self) -> Dict[str, pd.DataFrame]:
        """
        Reloads all data from the Google Sheets document
        
        Returns:
            Dict: {'tyt': tyt_df, 'ayt': ayt_df}
        """
        logger.info("Refreshing all data from Google Sheets...")
        
        # Ensure workbook is opened
        self._open_workbook()
        
        return {
            'tyt': self.load_tyt_data(),
            'ayt': self.load_ayt_data()
        }
    
    def get_worksheet_names(self) -> List[str]:
        """
        Lists all worksheet names in the Google Sheets document
        
        Returns:
            List[str]: Worksheet names
        """
        if not self.workbook:
            self._open_workbook()
        
        worksheets = self.workbook.worksheets()
        return [ws.title for ws in worksheets]
    
    def preview_data(self, worksheet_name: str, n_rows: int = 5) -> pd.DataFrame:
        """
        Previews the first n rows of the specified worksheet
        
        Args:
            worksheet_name: Worksheet name
            n_rows: Number of rows to preview (default: 5)
            
        Returns:
            pd.DataFrame: First n rows of the worksheet
        """
        df = self._get_worksheet_data(worksheet_name)
        return df.head(n_rows)


