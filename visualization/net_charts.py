"""
YKS Analysis System - Net Visualization Module
Simple, understandable, and clean charts
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

# For Turkish character support
plt.rcParams['font.family'] = 'DejaVu Sans'


class NetVisualizer:
    """
    Creates simple and understandable charts for net values
    
    Design principle: Simple, clean, understandable
    """
    
    def __init__(self, config: Config, style: str = 'seaborn-v0_8-whitegrid', figsize: tuple = (12, 6)):
        """
        NetVisualizer initializer
    
        Args:
            config: Configuration object
            style: Matplotlib style
            figsize: Figure size (width, height)
        """

        self.config = config
        self.style = self.config.Visualization.STYLE
        self.figsize = self.config.Visualization.FIGURE_SIZE
        self.colors = self.config.Visualization.COLOR_PALETTE
        self.subject_colors = self.config.Visualization.SUBJECT_COLORS

        plt.style.use(self.style)


    
    def _get_subject_color(self, subject: str) -> str:
        """Returns the color for the subject"""
        for key in self.subject_colors.keys():
            if key in subject:
                return self.subject_colors[key]
        return self.colors['primary']
    
    def _add_value_labels(self, ax, spacing: int = 0):
        """Adds value labels on top of bars"""
        for bar in ax.patches:
            height = bar.get_height()
            if not np.isnan(height) and height > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    height + spacing,
                    f'{height:.1f}',
                    ha='center',
                    va='bottom',
                    fontsize=9,
                    fontweight='bold'
                )
    
    def plot_subject_nets_by_exam(self, df: pd.DataFrame, subject: str, 
                                  save_path: Optional[str] = None) -> plt.Figure:
        """
        Bar chart of a specific subject's net values by exam
        
        Args:
            df: Exam data
            subject: Subject name (e.g. "Türkçe Net")
            save_path: File path to save the chart (optional)
            
        Returns:
            plt.Figure: Chart figure
        """
        if subject not in df.columns:
            logger.error(f"{subject} column not found")
            return None
        
        # Prepare data
        df_sorted = df.sort_values('Tarih').copy()
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Bar chart
        bars = ax.bar(
            range(len(df_sorted)),
            df_sorted[subject],
            color=self._get_subject_color(subject),
            alpha=0.8,
            edgecolor='black',
            linewidth=1
        )
        
        # Labels
        ax.set_xlabel('Exams', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title('Performance by Exam', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # X axis labels
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Add value labels
        self._add_value_labels(ax, spacing=1)
        
        # Add mean line
        mean_value = df_sorted[subject].mean()
        ax.axhline(y=mean_value, color='red', linestyle='--', 
                  linewidth=2, alpha=0.7, label=f'Mean: {mean_value:.1f}')
        ax.legend(loc='upper left', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved: {save_path}")
        
        return fig
    
    def plot_total_nets_by_exam(self, df: pd.DataFrame, 
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Bar chart of total net values by exam
        
        Args:
            df: Exam data
            save_path: File path to save the chart (optional)
            
        Returns:
            plt.Figure: Chart figure
        """
        return self.plot_subject_nets_by_exam(df, 'Toplam Net', save_path)
    
    def plot_all_subjects_comparison(self, df: pd.DataFrame, 
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Comparison of all subjects in the latest exam (SIDE-BY-SIDE BAR)
        
        Args:
            df: Exam data
            save_path: File path to save the chart (optional)
            
        Returns:
            plt.Figure: Chart figure
        """
        # Get the latest exam
        latest_exam = df.sort_values('Tarih').iloc[-1]
        
        # Find net columns (excluding Toplam Net)
        net_columns = [col for col in df.columns if 'Net' in col and col != 'Toplam Net']
        
        if not net_columns:
            logger.error("Net column not found")
            return None
        
        # Prepare data
        subjects = [col.replace(' Net', '') for col in net_columns]
        values = [latest_exam[col] for col in net_columns]
        colors = [self._get_subject_color(col) for col in net_columns]
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bars = ax.bar(subjects, values, color=colors, alpha=0.8, 
                     edgecolor='black', linewidth=1)
        
        # Labels
        ax.set_xlabel('Subjects', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title(f'Latest Exam: {latest_exam["Deneme Adı"]} - Subject Performance',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Value labels
        self._add_value_labels(ax, spacing=0.5)
        
        # Rotate x axis labels
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved: {save_path}")
        
        return fig
    
   
    
    
    def plot_multi_subject_comparison(self, df: pd.DataFrame, subjects: List[str],
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Multi-line comparison of several subjects
        
        Args:
            df: Exam data
            subjects: List of subjects (e.g. ["Türkçe Net", "Matematik Net"])
            save_path: File path to save the chart (optional)
            
        Returns:
            plt.Figure: Chart figure
        """
        df_sorted = df.sort_values('Tarih').copy()
        
        # Create figure
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Line for each subject
        for subject in subjects:
            if subject not in df.columns:
                logger.warning(f"{subject} column not found, skipping")
                continue
            
            ax.plot(
                range(len(df_sorted)),
                df_sorted[subject],
                marker='o',
                markersize=6,
                linewidth=2,
                color=self._get_subject_color(subject),
                label=subject.replace(' Net', ''),
                alpha=0.8
            )
        
        # Labels
        ax.set_xlabel('Exams', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title('Subject Comparison - Performance Over Time',
                    fontsize=14, fontweight='bold', pad=20)
        
        # X axis labels
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Legend
        ax.legend(loc='best', fontsize=10, framealpha=0.9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Chart saved: {save_path}")
        
        return fig
    
    
    
    def dashboard(self, df: pd.DataFrame, exam_type: str = "TYT", save_path: Optional[str] = None) -> plt.Figure:
        """
        Shows net trends of all subjects in a single dashboard according to exam type (TYT/AYT).

        Args:
            df: Exam data
            exam_type: "TYT" or "AYT"
            save_path: File path to save the chart (optional)

        Returns:
            plt.Figure: Chart figure
        """
        # Select subjects according to exam type
        if exam_type == "TYT":
            subjects = ["Türkçe Net", "Matematik Net", "Fen Net", "Sosyal Net"]
        else:
            subjects = ["Matematik Net", "Fizik Net", "Kimya Net", "Biyoloji Net", "Türk Dili ve Edebiyatı Net", "Tarih Net", "Coğrafya Net"]

        # Only keep subjects present in the data
        subjects = [s for s in subjects if s in df.columns]
        num_subjects = len(subjects)
        if num_subjects == 0:
            logger.warning("No suitable subject found for dashboard.")
            return None

        cols = 2
        rows = (num_subjects + 1) // cols

        df_sorted = df.sort_values('Tarih').copy()
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5), squeeze=False)
        axes = axes.flatten()

        for i, subject in enumerate(subjects):
            ax = axes[i]
            ax.plot(
                range(len(df_sorted)),
                df_sorted[subject],
                marker='o',
                markersize=7,
                linewidth=2.5,
                color=self._get_subject_color(subject),
                label=subject.replace(' Net', '')
            )
            # Trend line
            x = np.arange(len(df_sorted))
            y = df_sorted[subject].dropna().values
            if len(y) > 1:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), linestyle='--', color='red', linewidth=2, alpha=0.7)
            # Value labels
            for j, val in enumerate(df_sorted[subject]):
                if not np.isnan(val):
                    ax.text(j, val + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=8)
            ax.set_title(f"{subject.replace(' Net', '')} Net Trend", fontsize=12, fontweight='bold')
            ax.set_ylabel('Net')
            ax.set_xticks(range(len(df_sorted)))
            ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
            ax.grid(True, alpha=0.4, linestyle='--')

        # Hide unused subplots
        for i in range(num_subjects, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(f'{exam_type} Subject-Based Net Performance Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Dashboard saved: {save_path}")

        return fig

