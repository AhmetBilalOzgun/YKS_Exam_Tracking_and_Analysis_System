"""
YKS Analiz Sistemi - Net Analiz Modülü
Net hesaplamaları, istatistikler ve trend analizleri
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from scipy import stats
from scipy.stats import linregress
import logging
from config import Config

logger = logging.getLogger(__name__)


class NetAnalyzer:
    def __init__(self, config: Config, exam_type: str):
        self.config = config
        self.exam_type = exam_type
    
    def calculate_statistics(self, df: pd.DataFrame, subject: str = "Toplam Net") -> Dict:
        """
        Belirli bir ders için temel istatistikleri hesaplar
        
        Args:
            df: Deneme verileri
            subject: Ders adı (örn: "Toplam Net", "Matematik Net")
            
        Returns:
            Dict: İstatistikler dictionary'si
        """
        if subject not in df.columns:
            logger.error(f"{subject} sütunu bulunamadı")
            return {}
        
        data = df[subject].dropna()
        
        if len(data) == 0:
            logger.warning(f"{subject} için veri yok")
            return {}
        
        stats_dict = {
            'count': len(data),
            'mean': float(data.mean()),
            'median': float(data.median()),
            'std': float(data.std()),
            'min': float(data.min()),
            'max': float(data.max()),
            'q25': float(data.quantile(0.25)),
            'q75': float(data.quantile(0.75)),
            'iqr': float(data.quantile(0.75) - data.quantile(0.25)),
            'cv': float(data.std() / data.mean() * 100) if data.mean() != 0 else 0,
            'range': float(data.max() - data.min()),
            'latest': float(data.iloc[-1]) if len(data) > 0 else None,
            'first': float(data.iloc[0]) if len(data) > 0 else None
        }
        
        if len(data) >= 3:
            stats_dict['skewness'] = float(data.skew())
            stats_dict['kurtosis'] = float(data.kurtosis())
        
        return stats_dict
    
    def get_all_subjects_statistics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tüm dersler için istatistikleri hesaplar
        """
        net_columns = [col for col in df.columns if 'Net' in col]
        
        stats_list = []
        for subject in net_columns:
            stats = self.calculate_statistics(df, subject)
            if stats:
                stats['subject'] = subject
                stats_list.append(stats)
        
        if not stats_list:
            return pd.DataFrame()
        
        stats_df = pd.DataFrame(stats_list)
        stats_df = stats_df.set_index('subject')
        
        return stats_df
    
    def get_progression_trend(self, df: pd.DataFrame, subject: str = "Toplam Net") -> Dict:
        """
        Net değerlerinin zaman içindeki trendini analiz eder
        """
        if subject not in df.columns:
            logger.error(f"{subject} sütunu bulunamadı")
            return {}
        
        df_sorted = df.sort_values('Tarih').copy()
        data = df_sorted[subject].dropna()
        
        if len(data) < 2:
            logger.warning(f"{subject} için yeterli veri yok (en az 2 gerekli)")
            return {}
        
        x = np.arange(len(data))
        y = data.values
        
        slope, intercept, r_value, p_value, std_err = linregress(x, y)
        
        # Trend kategorisi belirleme
        trend = "Belirsiz" 
        if p_value < self.config.Analysis.TREND_P_VALUE_THRESHOLD:
            if slope > self.config.Analysis.TREND_STRONG_SLOPE:
                trend = "Güçlü Artış"
            elif slope > self.config.Analysis.TREND_LIGHT_SLOPE:
                trend = "Hafif Artış"
            elif slope < -self.config.Analysis.TREND_STRONG_SLOPE:
                trend = "Güçlü Düşüş"
            elif slope < -self.config.Analysis.TREND_LIGHT_SLOPE:
                trend = "Hafif Düşüş"
            else:
                trend = "Sabit"
        else:
            trend = "İstatistiksel olarak anlamsız"
        # --------------------------------

        next_prediction = slope * len(data) + intercept
        
        trend_info = {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_error': float(std_err),
            'trend': trend,
            'next_prediction': float(next_prediction),
            'total_improvement': float(y[-1] - y[0]),
            'improvement_percentage': float((y[-1] - y[0]) / y[0] * 100) if y[0] != 0 else 0
        }
        
        return trend_info

    def get_all_subjects_trends(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Tüm dersler için trend analizi
        """
        net_columns = [col for col in df.columns if 'Net' in col]
        
        trends_list = []
        for subject in net_columns:
            trend = self.get_progression_trend(df, subject)
            if trend:
                trend['subject'] = subject
                trends_list.append(trend)
        
        if not trends_list:
            return pd.DataFrame()
        
        trends_df = pd.DataFrame(trends_list)
        trends_df = trends_df.set_index('subject')
        
        return trends_df
    
    def get_exam_comparison(self, df: pd.DataFrame, n_exams: int = 5) -> pd.DataFrame:
        """
        Son N denemeyi karşılaştırır
        """
        df_sorted = df.sort_values('Tarih').tail(n_exams).copy()
        
        net_columns = [col for col in df.columns if 'Net' in col]
        columns_to_show = ['Deneme Adı', 'Tarih'] + net_columns
        
        comparison_df = df_sorted[columns_to_show].copy()
        comparison_df = comparison_df.reset_index(drop=True)
        
        return comparison_df
    
    def calculate_improvement_rate(self, df: pd.DataFrame, subject: str = "Toplam Net", 
                                   window: int = 3) -> Dict:
        """
        Son N denemeye göre ilerleme oranını hesaplar
        """
        if subject not in df.columns: return {}
        
        df_sorted = df.sort_values('Tarih')
        data = df_sorted[subject].dropna()
        
        if len(data) < window:
            logger.warning(f"Yeterli veri yok (gerekli: {window}, mevcut: {len(data)})")
            return {}
        
        recent = data.tail(window)
        previous = data.iloc[-2*window:-window] if len(data) >= 2*window else data.head(window)
        
        improvement = {
            'recent_mean': float(recent.mean()),
            'previous_mean': float(previous.mean()),
            'absolute_change': float(recent.mean() - previous.mean()),
            'percentage_change': float((recent.mean() - previous.mean()) / previous.mean() * 100) if previous.mean() != 0 else 0,
            'recent_std': float(recent.std()),
            'previous_std': float(previous.std()),
            'consistency_improved': recent.std() < previous.std()
        }
        
        if improvement['absolute_change'] > 5:
            improvement['interpretation'] = "Harika! Önemli ilerleme var 🚀"
        elif improvement['absolute_change'] > 2:
            improvement['interpretation'] = "İyi! İlerleme devam ediyor 👍"
        elif improvement['absolute_change'] > -2:
            improvement['interpretation'] = "Sabit performans 📊"
        else:
            improvement['interpretation'] = "Dikkat! Gerileme var, konuları tekrar et ⚠️"
        
        return improvement
    
    def identify_weak_subjects(self, df: pd.DataFrame) -> List[Dict]:
        all_stats_df = self.get_all_subjects_statistics(df)
        all_trends_df = self.get_all_subjects_trends(df)
        all_stats_df = all_stats_df.drop(index='Toplam Net', errors='ignore')
        median_of_means = all_stats_df['mean'].median()
        weak_df = all_stats_df[all_stats_df['mean'] < median_of_means]
        weak_subjects = []
        for subject, row in weak_df.iterrows():
            weak_subjects.append({
                'subject': subject,
                'mean': row['mean'],
                'latest': row['latest'],
                'trend': all_trends_df.loc[subject, 'trend'] if subject in all_trends_df.index else 'Belirsiz'
            })
        weak_subjects.sort(key=lambda x: x['mean'])
        return weak_subjects
    
    def identify_strong_subjects(self, df: pd.DataFrame) -> List[Dict]:
        """
        Güçlü dersleri belirler.
        """
        all_stats_df = self.get_all_subjects_statistics(df)
        all_trends_df = self.get_all_subjects_trends(df)
        all_stats_df = all_stats_df.drop(index='Toplam Net', errors='ignore')
        if all_stats_df.empty: return []
        threshold = all_stats_df['mean'].quantile(0.75) 
        strong_df = all_stats_df[all_stats_df['mean'] >= threshold]
        strong_subjects = []
        for subject, row in strong_df.iterrows():
            strong_subjects.append({
                'subject': subject,
                'mean': row['mean'],
                'latest': row['latest'],
                'trend': all_trends_df.loc[subject, 'trend'] if subject in all_trends_df.index else 'Belirsiz'
            })
        strong_subjects.sort(key=lambda x: x['mean'], reverse=True)
        return strong_subjects
    
    def calculate_consistency_score(self, df: pd.DataFrame, subject: str = "Toplam Net") -> Dict:
        """
        Tutarlılık skoru hesaplar
        """
        stats = self.calculate_statistics(df, subject)
        if not stats: return {}
        cv = stats['cv']
        if cv < 10:
            consistency, score = "Çok Tutarlı", 5
        elif cv < 20:
            consistency, score = "Tutarlı", 4
        elif cv < 30:
            consistency, score = "Orta", 3
        elif cv < 40:
            consistency, score = "Dalgalı", 2
        else:
            consistency, score = "Çok Dalgalı", 1
        return {
            'subject': subject, 'cv': cv, 'consistency': consistency,
            'score': score, 'std': stats['std'], 'mean': stats['mean']
        }
    
    def predict_next_exam(self, df: pd.DataFrame, subject: str = "Toplam Net") -> Dict:
        """
        Bir sonraki deneme için tahmin yapar
        """
        trend_info = self.get_progression_trend(df, subject)
        stats = self.calculate_statistics(df, subject)
        if not trend_info or not stats: return {}
        prediction = trend_info['next_prediction']
        std_error = trend_info['std_error']
        confidence_interval = 1.96 * std_error
        prediction_info = {
            'subject': subject, 'prediction': prediction,
            'lower_bound': prediction - confidence_interval,
            'upper_bound': prediction + confidence_interval,
            'confidence': 95, 'based_on_exams': stats['count'],
            'latest_net': stats['latest']
        }
        return prediction_info
    
    def get_time_based_analysis(self, df: pd.DataFrame, subject: str = "Toplam Net") -> Dict:
        """
        Zamana dayalı analiz (hafta/ay bazlı)
        """
        if 'Tarih' not in df.columns:
            logger.warning("Tarih sütunu yok, zaman bazlı analiz yapılamaz")
            return {}
        df_copy = df.copy()
        df_copy['Hafta'] = df_copy['Tarih'].dt.isocalendar().week
        df_copy['Ay'] = df_copy['Tarih'].dt.month
        time_analysis = {}
        if 'Hafta' in df_copy.columns:
            weekly_mean = df_copy.groupby('Hafta')[subject].mean()
            time_analysis['weekly_mean'] = weekly_mean.to_dict()
        if 'Ay' in df_copy.columns:
            monthly_mean = df_copy.groupby('Ay')[subject].mean()
            time_analysis['monthly_mean'] = monthly_mean.to_dict()
        return time_analysis
    
    def compare_to_target(self, df: pd.DataFrame, target_net: float, 
                         subject: str = "Toplam Net") -> Dict:
        """
        Hedefe göre performans analizi
        """
        stats = self.calculate_statistics(df, subject)
        if not stats: return {}
        current_net = stats['latest']
        gap = target_net - current_net
        gap_percentage = (gap / target_net * 100) if target_net != 0 else 0
        trend = self.get_progression_trend(df, subject)
        exams_needed = int(np.ceil(gap / trend['slope'])) if trend and trend['slope'] > 0 else None
        comparison = {
            'target': target_net, 'current': current_net, 'gap': gap,
            'gap_percentage': gap_percentage, 'exams_needed': exams_needed,
            'achievable': gap <= trend['slope'] * 10 if trend and trend['slope'] > 0 else False
        }
        if gap <= 0:
            comparison['status'] = "🎉 Hedef aşıldı!"
        elif gap_percentage < 10:
            comparison['status'] = "🔥 Hedefe çok yakınsın!"
        elif gap_percentage < 25:
            comparison['status'] = "💪 İyi gidiyorsun, devam et!"
        else:
            comparison['status'] = "📚 Daha fazla çalışman gerekiyor"
        return comparison
    
    def generate_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Kapsamlı özet rapor oluşturur
        """
        report = {
            'exam_type': self.exam_type,
            'total_exams': len(df),
            'date_range': {
                'first': df['Tarih'].min() if 'Tarih' in df.columns else None,
                'last': df['Tarih'].max() if 'Tarih' in df.columns else None
            },
            'overall_stats': self.calculate_statistics(df, 'Toplam Net'),
            'subject_stats': self.get_all_subjects_statistics(df).to_dict(),
            'trends': self.get_all_subjects_trends(df).to_dict(),
            'weak_subjects': self.identify_weak_subjects(df),
            'strong_subjects': self.identify_strong_subjects(df),
            'recent_improvement': self.calculate_improvement_rate(df, 'Toplam Net')
        }
        return report