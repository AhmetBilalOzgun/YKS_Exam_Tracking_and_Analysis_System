# Konu konu analizler için gerekli fonksiyonlar.

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
from scipy.stats import linregress
import logging
from config import Config

logger = logging.getLogger(__name__)


class TopicAnalyzer:
    """
    Konu bazlı analizler yapan sınıf.
    """
    
    def __init__(self, config: Config, exam_type: str = "TYT"):
        self.config = config
        self.exam_type = exam_type

    def _precompute_all_topic_trends(self, df: pd.DataFrame) -> Dict:
        """
        DataFrame'i tek seferde tarayarak tüm konuların trend verisini toplar.
        """
        df_sorted = df.sort_values('Tarih').reset_index(drop=True)
        
        all_topic_data = defaultdict(lambda: {
            'appearances': [0] * len(df_sorted), 
            'dates': df_sorted['Tarih'].tolist(),
            'exam_names': df_sorted['Deneme Adı'].tolist() if 'Deneme Adı' in df_sorted else ['Bilinmiyor'] * len(df_sorted)
        })

        for i, row in df_sorted.iterrows():
            for col_name in [c for c in df.columns if '_List' in c]:
                topics = row[col_name]
                if isinstance(topics, list):
                    for topic in topics:
                        subject = col_name.replace(' Yanlış Konular_List', '')
                        key = (subject, topic)
                        all_topic_data[key]['appearances'][i] = 1

        return all_topic_data

    def get_most_problematic_topics(self, df: pd.DataFrame, top_n: int = 10) -> List[Tuple[str, int]]:
        """
        En çok yanlış yapılan konuları bulur.
        """
        topic_columns = [col for col in df.columns if '_List' in col]
        all_topics = []
        for col in topic_columns:
            all_topics.extend([item for sublist in df[col].dropna() for item in sublist])
        
        if not all_topics:
            return []
            
        return Counter(all_topics).most_common(top_n)

    def identify_weak_areas(self, df: pd.DataFrame, threshold: int = 3) -> Dict[str, List[str]]:
        """
        Ders bazında zayıf alanları (çok yanlış yapılan konular) belirler.
        """
        weak_areas = {}
        subjects = self.config.TYT.SUBJECTS if self.exam_type == "TYT" else self.config.AYT.SUBJECTS
        
        for subject in subjects:
            col_name = f"{subject} Yanlış Konular_List"
            if col_name in df.columns:
                topics = [item for sublist in df[col_name].dropna() for item in sublist]
                topic_counts = Counter(topics)
                
                problematic_topics = [topic for topic, count in topic_counts.items() if count >= threshold]
                if problematic_topics:
                    weak_areas[subject] = problematic_topics
                    
        return weak_areas

    def get_topic_trend_by_exam(self, precomputed_data: Dict, subject: str, topic: str) -> Dict:
        """
        Ön-hesaplanmış veriyi kullanarak bir konunun trendini hızlıca analiz eder.
        """
        key = (subject, topic)
        if key not in precomputed_data:
            return {'trend': 'Veri Yok'}

        topic_data = precomputed_data[key]
        appearances = np.array(topic_data['appearances'])
        dates = topic_data['dates']
        all_exam_names = topic_data['exam_names']

        indices = np.where(appearances == 1)[0]
        if len(indices) == 0:
            return {'trend': 'Hiç Tekrarlanmamış'}

        exam_names = [all_exam_names[i] for i in indices]
        exam_dates = [dates[i] for i in indices]

        total_exams = len(appearances)
        frequency = len(indices)
        
        recent_exams_window = max(1, total_exams // 4)
        recent_count = np.sum(appearances[-recent_exams_window:])
        
        trend = "➡️ Sabit"
        if recent_count == 0:
            trend = "✅ Gelişiyor (Son zamanlarda tekrarlanmamış)"
        elif frequency > 1:
            if indices[-1] > total_exams * 0.75 and np.mean(np.diff(indices)) < total_exams / frequency:
                 trend = "⚠️ Tekrarlıyor (Sık sık yanlış yapılıyor)"
            if recent_count / recent_exams_window > frequency / total_exams:
                trend = "🚨 Kötüleşiyor (Son zamanlarda daha sık tekrarlanmış)"

        return {
            'konu': topic,
            'ders': subject,
            'frekans': frequency,
            'toplam_deneme': total_exams,
            'son_görülme_index': indices[-1] if len(indices) > 0 else -1,
            'trend': trend,
            'deneme_adları': exam_names,
            'tarihler': exam_dates
        }

    def compare_subjects_by_topics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Dersleri yanlış yapılan konu sayılarına göre karşılaştırır.
        """
        subjects = self.config.TYT.SUBJECTS if self.exam_type == "TYT" else self.config.AYT.SUBJECTS
        comparison_data = []

        for subject in subjects:
            list_col = f"{subject} Yanlış Konular_List"
            count_col = f"{subject} Yanlış Konular_Count"
            if list_col in df.columns:
                total_wrong_topics = df[count_col].sum()
                unique_wrong_topics = len(set(item for sublist in df[list_col].dropna() for item in sublist))
                comparison_data.append({
                    'Ders': subject,
                    'Toplam Yanlış Sayısı': total_wrong_topics,
                    'Farklı Yanlış Konu Sayısı': unique_wrong_topics
                })

        if not comparison_data:
            return pd.DataFrame()
            
        return pd.DataFrame(comparison_data).set_index('Ders')

    def generate_study_plan(self, df: pd.DataFrame, precomputed_trends: Dict, focus_subjects: Optional[List[str]] = None, max_topics_per_subject: int = 3) -> Dict:
        """
        Önceliklendirilmiş bir çalışma planı oluşturur.
        """
        all_topics = defaultdict(int)
        subjects_of_topics = {}
        for key, data in precomputed_trends.items():
            subject, topic = key
            count = sum(data['appearances'])
            if count > 0:
                all_topics[topic] += count
                subjects_of_topics[topic] = subject

        if not all_topics:
            return {"Genel": [{'sıra': 1, 'konu': 'Harika! Çalışılacak acil bir konu bulunamadı.', 'öncelik': '🟢 Düşük', 'frekans': 0, 'son_durum': '✅'}]}

        final_study_plan = {}
        subjects_to_process = focus_subjects or (self.config.TYT.SUBJECTS if self.exam_type == "TYT" else self.config.AYT.SUBJECTS)
        sorted_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)

        for subject in subjects_to_process:
            subject_plan_items = []
            subject_topics = [item for item in sorted_topics if subjects_of_topics.get(item[0]) == subject]
            
            for i, (topic, freq) in enumerate(subject_topics):
                if len(subject_plan_items) >= max_topics_per_subject:
                    break

                priority = "🔴 Yüksek"
                if freq < 3: priority = "🟡 Orta"
                if freq == 1: priority = "🟢 Düşük"
                
                trend_info = self.get_topic_trend_by_exam(precomputed_trends, subject, topic)
                recent_status = trend_info.get('trend', '➡️ Bilinmiyor')

                subject_plan_items.append({
                    'konu': topic, 'öncelik': priority, 'frekans': freq,
                    'son_durum': recent_status, 'sıra': i + 1
                })
            
            if subject_plan_items:
                sorted_plan = sorted(subject_plan_items, key=lambda x: (x['öncelik'], -x['frekans']))
                for idx, item in enumerate(sorted_plan):
                    item['sıra'] = idx + 1
                final_study_plan[subject] = sorted_plan
                
        return final_study_plan

    def generate_topic_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Konu analiziyle ilgili kapsamlı bir özet rapor oluşturur.
        """
        # Toplam yanlış yapılan konu sayısını hesapla
        topic_count_cols = [col for col in df.columns if '_Count' in col]
        total_wrong_topics = df[topic_count_cols].sum().sum()

        report = {
            'total_wrong_topics': int(total_wrong_topics),
            'most_problematic_topics': self.get_most_problematic_topics(df, top_n=5),
            'weak_areas_by_subject': self.identify_weak_areas(df, threshold=2),
            'subject_comparison': self.compare_subjects_by_topics(df).to_dict('index')
        }
        return report