"""
YKS Analysis System - Topic Visualizations
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, List, Dict, Tuple
from collections import Counter
import logging
from config import Config

logger = logging.getLogger(__name__)

plt.rcParams['font.family'] = 'DejaVu Sans'


class TopicVisualizer:
    """
    Understandable and clean topic-based visualizations.
    """
    
    def __init__(self, config: Config, style: str = 'seaborn-v0_8-whitegrid', figsize: tuple = (14, 7)):
        """
        TopicVisualizer startup
    
        Args:
            config: Configuration object
            style: Matplotlib style
            figsize: Default figure size
        """
        self.config = config
        self.style = style
        self.figsize = figsize
    
        self.colors = {
            'critical': '#FC5C65',    
            'high': '#FD9644',        
            'medium': '#FED330',      
            'low': '#26DE81',         
            'info': '#2E86DE'         
        }
    
        plt.style.use(self.style)
    
    def _get_priority_color(self, frequency: int) -> str:
        
        if frequency >= 5:
            return self.colors['critical']
        elif frequency >= 3:
            return self.colors['high']
        elif frequency >= 2:
            return self.colors['medium']
        else:
            return self.colors['low']
    
    def plot_total_wrong_topics(self, problematic_topics: List[Tuple[str, int]], top_n: int = 15, 
                            save_path: Optional[str] = None) -> plt.Figure:
        """
        Most frequently wrong topics chart (HORIZONTAL BAR)
        
        Args:
            df: Exam data
            top_n: Number of top topics to display
            save_path: File path to save the chart
            
        Returns:
            plt.Figure: Chart figure
        """

        top_topics = problematic_topics[:top_n]
        if not top_topics:
            logger.warning("No data available for the chart.")
            return None
        
        # Data for plotting
        topics = [t[0] for t in top_topics]
        counts = [t[1] for t in top_topics]
        colors = [self._get_priority_color(c) for c in counts]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(self.figsize[0], self.figsize[1]))
        
        # Horizontal bar
        y_pos = np.arange(len(topics))
        bars = ax.barh(y_pos, counts, color=colors, alpha=0.85, edgecolor='black', linewidth=1)
        
        # Labels
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topics)
        ax.invert_yaxis()  # Most frequent on top
        ax.set_xlabel('Wrong count', fontsize=12, fontweight='bold')
        ax.set_title(f'Weakest {top_n} Topics Overall', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.xaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Value labels
        for i, (bar, count) in enumerate(zip(bars, counts)):
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                   f'{int(count)}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, fc=self.colors['critical'], alpha=0.85, label='Very Urgent (5+)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['high'], alpha=0.85, label='Urgent (3-4)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['medium'], alpha=0.85, label='Normal (2)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['low'], alpha=0.85, label='Low (1)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved: {save_path}")
        
        return fig
    
    
    def plot_topic_trend_by_exam(self, df: pd.DataFrame, subject: str, topic: str, save_path: Optional[str] = None) -> Optional[plt.Figure]:
        """
        Trend of a specific topic over exams (LINE CHART)
        Args:
            df: Exam data
            subject: Subject name (e.g., 'Mathematics')
            topic: Topic name (e.g., 'Quadratic Equations')
            save_path: File path to save the chart
        Returns:
            plt.Figure or None: Chart figure or None if no data
        """
        if not topic or not subject:
            return None

        topic_column = f"{subject} Yanlış Konular_List"
        if topic_column not in df.columns:
            return None

        df_sorted = df.sort_values('Tarih').copy()
        exam_names = df_sorted['Deneme Adı'].tolist()
        topic_counts = []
        for topics_list in df_sorted[topic_column]:
            if isinstance(topics_list, list):
                topic_counts.append(topics_list.count(topic))
            else:
                topic_counts.append(0)

        if sum(topic_counts) == 0:
            return None

        fig, ax = plt.subplots(figsize=(max(10, len(exam_names)*0.7), 5))
        ax.plot(exam_names, topic_counts, marker='o', linewidth=2.5, color=self.colors['critical'])
        ax.set_title(f"{subject} - '{topic}' topic's trend", fontsize=14, fontweight='bold')
        ax.set_xlabel('Exam Name')
        ax.set_ylabel('Number of Wrong Answers')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')

        # Value labels
        for i, val in enumerate(topic_counts):
            if val > 0:
                ax.text(i, val + 0.1, str(val), ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved: {save_path}")

        return fig


