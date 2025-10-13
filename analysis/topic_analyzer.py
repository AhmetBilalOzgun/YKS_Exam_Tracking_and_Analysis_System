# Functions required for topic-based analysis.

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
    Class for topic-based analyses.
    """
    
    def __init__(self, config: Config, exam_type: str = "TYT"):
        self.config = config
        self.exam_type = exam_type

    def _precompute_all_topic_trends(self, df: pd.DataFrame) -> Dict:
        """
        Scans the DataFrame once and collects trend data for all topics.
        """
        df_sorted = df.sort_values('Tarih').reset_index(drop=True)
        
        all_topic_data = defaultdict(lambda: {
            'appearances': [0] * len(df_sorted), 
            'dates': df_sorted['Tarih'].tolist(),
            'exam_names': df_sorted['Deneme Adı'].tolist() if 'Deneme Adı' in df_sorted else ['Unknown'] * len(df_sorted)
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
        Finds the most frequently wrong topics.
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
        Identifies weak areas (topics with many mistakes) by subject.
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
        Quickly analyzes the trend of a topic using precomputed data.
        """
        key = (subject, topic)
        if key not in precomputed_data:
            return {'trend': 'No Data'}

        topic_data = precomputed_data[key]
        appearances = np.array(topic_data['appearances'])
        dates = topic_data['dates']
        all_exam_names = topic_data['exam_names']

        indices = np.where(appearances == 1)[0]
        if len(indices) == 0:
            return {'trend': 'Never Repeated'}

        exam_names = [all_exam_names[i] for i in indices]
        exam_dates = [dates[i] for i in indices]

        total_exams = len(appearances)
        frequency = len(indices)
        
        recent_exams_window = max(1, total_exams // 4)
        recent_count = np.sum(appearances[-recent_exams_window:])
        
        trend = "➡️ Stable"
        if recent_count == 0:
            trend = "✅ Improving (Not repeated recently)"
        elif frequency > 1:
            if indices[-1] > total_exams * 0.75 and np.mean(np.diff(indices)) < total_exams / frequency:
                 trend = "⚠️ Repeating (Frequently wrong)"
            if recent_count / recent_exams_window > frequency / total_exams:
                trend = "🚨 Worsening (Repeated more often recently)"

        return {
            'topic': topic,
            'subject': subject,
            'frequency': frequency,
            'total_exams': total_exams,
            'last_seen_index': indices[-1] if len(indices) > 0 else -1,
            'trend': trend,
            'exam_names': exam_names,
            'dates': exam_dates
        }

    def compare_subjects_by_topics(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Compares subjects by the number of wrong topics.
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
                    'Subject': subject,
                    'Total Wrong Count': total_wrong_topics,
                    'Unique Wrong Topic Count': unique_wrong_topics
                })

        if not comparison_data:
            return pd.DataFrame()
            
        return pd.DataFrame(comparison_data).set_index('Subject')

    def generate_study_plan(self, df: pd.DataFrame, precomputed_trends: Dict, focus_subjects: Optional[List[str]] = None, max_topics_per_subject: int = 3) -> Dict:
        """
        Generates a prioritized study plan.
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
            return {"General": [{'order': 1, 'topic': 'Great! No urgent topic to study.', 'priority': '🟢 Low', 'frequency': 0, 'recent_status': '✅'}]}

        final_study_plan = {}
        subjects_to_process = focus_subjects or (self.config.TYT.SUBJECTS if self.exam_type == "TYT" else self.config.AYT.SUBJECTS)
        sorted_topics = sorted(all_topics.items(), key=lambda x: x[1], reverse=True)

        for subject in subjects_to_process:
            subject_plan_items = []
            subject_topics = [item for item in sorted_topics if subjects_of_topics.get(item[0]) == subject]
            
            for i, (topic, freq) in enumerate(subject_topics):
                if len(subject_plan_items) >= max_topics_per_subject:
                    break

                priority = "🔴 High"
                if freq < 3: priority = "🟡 Medium"
                if freq == 1: priority = "🟢 Low"
                
                trend_info = self.get_topic_trend_by_exam(precomputed_trends, subject, topic)
                recent_status = trend_info.get('trend', '➡️ Unknown')

                subject_plan_items.append({
                    'topic': topic, 'priority': priority, 'frequency': freq,
                    'recent_status': recent_status, 'order': i + 1
                })
            
            if subject_plan_items:
                sorted_plan = sorted(subject_plan_items, key=lambda x: (x['priority'], -x['frequency']))
                for idx, item in enumerate(sorted_plan):
                    item['order'] = idx + 1
                final_study_plan[subject] = sorted_plan
                
        return final_study_plan

    def generate_topic_summary_report(self, df: pd.DataFrame) -> Dict:
        """
        Creates a comprehensive summary report about topic analysis.
        """
        # Calculate the total number of wrong topics
        topic_count_cols = [col for col in df.columns if '_Count' in col]
        total_wrong_topics = df[topic_count_cols].sum().sum()

        report = {
            'total_wrong_topics': int(total_wrong_topics),
            'most_problematic_topics': self.get_most_problematic_topics(df, top_n=5),
            'weak_areas_by_subject': self.identify_weak_areas(df, threshold=2),
            'subject_comparison': self.compare_subjects_by_topics(df).to_dict('index')
        }
        return report