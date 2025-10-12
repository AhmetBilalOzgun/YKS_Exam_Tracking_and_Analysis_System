"""
YKS Analiz Sistemi - Konu Görselleştirme Modülü
Yanlış konuları basit ve anlaşılır grafiklerle gösterir
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
    Konu analizleri için basit ve anlaşılır grafikler
    
    Tasarım prensibi: Her bakışta anlaşılır, sade, temiz
    """
    
    def __init__(self, config: Config, style: str = 'seaborn-v0_8-whitegrid', figsize: tuple = (14, 7)):
        """
        TopicVisualizer başlatıcı
    
        Args:
            config: Configuration object
            style: Matplotlib stili
            figsize: Grafik boyutu
        """
        self.config = config
        self.style = style
        self.figsize = figsize
    
        # Renkler - basit palet
        self.colors = {
            'critical': '#FC5C65',    # Kırmızı - çok acil
            'high': '#FD9644',        # Turuncu - acil
            'medium': '#FED330',      # Sarı - orta
            'low': '#26DE81',         # Yeşil - düşük
            'info': '#2E86DE'         # Mavi - bilgi
        }
    
        plt.style.use(self.style)
    
    def _get_priority_color(self, frequency: int) -> str:
        """Frekansa göre renk döndürür"""
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
        En çok yanlış yapılan konuların grafiği (YATAY SÜTUN)
        
        Args:
            df: Deneme verileri
            top_n: Kaç konu gösterilsin
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """

        top_topics = problematic_topics[:top_n]
        if not top_topics:
            logger.warning("Çizilecek konu verisi bulunamadı")
            return None
        
        # Veriyi hazırla
        topics = [t[0] for t in top_topics]
        counts = [t[1] for t in top_topics]
        colors = [self._get_priority_color(c) for c in counts]
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(self.figsize[0], self.figsize[1]))
        
        # Yatay bar grafik (ters sıra - en yüksek üstte)
        y_pos = np.arange(len(topics))
        bars = ax.barh(y_pos, counts, color=colors, alpha=0.85, edgecolor='black', linewidth=1)
        
        # Etiketler
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topics)
        ax.invert_yaxis()  # En yüksek üstte
        ax.set_xlabel('Yanlış Yapma Sayısı', fontsize=12, fontweight='bold')
        ax.set_title(f'En Çok Yanlış Yapılan {top_n} Konu', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.xaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değer etiketleri
        for i, (bar, count) in enumerate(zip(bars, counts)):
            width = bar.get_width()
            ax.text(width + 0.2, bar.get_y() + bar.get_height()/2,
                   f'{int(count)}',
                   ha='left', va='center', fontsize=10, fontweight='bold')
        
        # Öncelik göstergesi
        legend_elements = [
            plt.Rectangle((0,0),1,1, fc=self.colors['critical'], alpha=0.85, label='Çok Acil (5+)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['high'], alpha=0.85, label='Acil (3-4)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['medium'], alpha=0.85, label='Orta (2)'),
            plt.Rectangle((0,0),1,1, fc=self.colors['low'], alpha=0.85, label='Düşük (1)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=9)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_wrong_topics_by_exam(self, df: pd.DataFrame, exam_name: str,
                                 save_path: Optional[str] = None) -> plt.Figure:
        """
        Belirli bir denemedeki yanlış konuların grafiği (DERS BAZLI)
        
        Args:
            df: Deneme verileri
            exam_name: Deneme adı
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """
        # Denemeyi bul
        exam_row = df[df['Deneme Adı'] == exam_name]
        
        if exam_row.empty:
            logger.error(f"'{exam_name}' bulunamadı")
            return None
        
        exam_row = exam_row.iloc[0]
        
        # Konu verilerini topla
        exam_topics = {}
        topic_list_columns = [col for col in df.columns if 'Yanlış Konular_List' in col]
        
        for col in topic_list_columns:
            subject = col.replace(' Yanlış Konular_List', '')
            topics = exam_row[col]
            if isinstance(topics, list) and topics:
                exam_topics[subject] = topics
        
        if not exam_topics:
            logger.warning(f"'{exam_name}' için yanlış konu verisi yok")
            return None
        
        # Grafik oluştur - her ders için ayrı bölüm
        n_subjects = len(exam_topics)
        fig, axes = plt.subplots(1, n_subjects, figsize=(5*n_subjects, 6))
        
        if n_subjects == 1:
            axes = [axes]
        
        for ax, (subject, topics) in zip(axes, exam_topics.items()):
            # Her konu için 1 yükseklik
            counts = [1] * len(topics)
            colors = [self.colors['high']] * len(topics)
            
            # Yatay bar
            y_pos = np.arange(len(topics))
            ax.barh(y_pos, counts, color=colors, alpha=0.85, edgecolor='black')
            
            # Etiketler
            ax.set_yticks(y_pos)
            ax.set_yticklabels(topics, fontsize=9)
            ax.set_xlabel('Yanlış', fontsize=10)
            ax.set_title(subject, fontsize=11, fontweight='bold')
            ax.set_xlim(0, 1.5)
            ax.set_xticks([])
            ax.invert_yaxis()
        
        plt.suptitle(f'{exam_name} - Yanlış Yapılan Konular',
                    fontsize=14, fontweight='bold')
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_subject_topic_summary(self, df: pd.DataFrame, top_n: int = 7, save_path: Optional[str] = None) -> plt.Figure:
        """
        Her ders için en çok yanlış yapılan konuları gösteren bir dashboard oluşturur (sütun grafikleri).
        """
        topic_list_columns = [col for col in df.columns if 'Yanlış Konular_List' in col and df[col].apply(len).sum() > 0]
        num_subjects = len(topic_list_columns)

        if num_subjects == 0:
            logger.warning("Konu dashboard'u için veri bulunamadı.")
            return None

        # Subplot grid boyutunu belirle
        cols = 2
        rows = (num_subjects + 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5.5), squeeze=False)
        axes = axes.flatten()

        for i, col_name in enumerate(topic_list_columns):
            subject = col_name.replace(' Yanlış Konular_List', '')
            ax = axes[i]
            
            # Konuları topla ve say
            all_topics = [item for sublist in df[col_name].dropna() for item in sublist]
            
            if not all_topics:
                ax.text(0.5, 0.5, 'Yanlış konu verisi yok', ha='center', va='center')
                ax.set_title(f"En Çok Yanlış Yapılan {subject} Konuları", fontsize=12, fontweight='bold')
                ax.set_xticks([])
                ax.set_yticks([])
                continue

            topic_counts = Counter(all_topics).most_common(top_n)
            
            topics = [t[0] for t in topic_counts]
            counts = [t[1] for t in topic_counts]
            colors = [self._get_priority_color(c) for c in counts]
            
            # Yatay bar grafik
            y_pos = np.arange(len(topics))
            ax.barh(y_pos, counts, color=colors, alpha=0.85, edgecolor='black', linewidth=1)
            
            ax.set_yticks(y_pos)
            ax.set_yticklabels(topics, fontsize=9)
            ax.invert_yaxis()
            ax.set_xlabel('Yanlış Yapma Sayısı')
            ax.set_title(f"En Çok Yanlış Yapılan {subject} Konuları (Top {top_n})", fontsize=12, fontweight='bold')

            # Değer etiketleri
            for j, count in enumerate(counts):
                ax.text(count + 0.1, j, str(count), va='center', ha='left', fontsize=9)
                
            ax.xaxis.grid(True, alpha=0.3, linestyle='--')
            ax.set_axisbelow(True)

        # Kullanılmayan subplot'ları gizle
        for i in range(num_subjects, len(axes)):
            fig.delaxes(axes[i])
            
        fig.suptitle('Ders Bazlı Konu Analiz Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Konu dashboard kaydedildi: {save_path}")
            
        return fig
    
    def plot_subject_topic_comparison(self, df: pd.DataFrame,
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Derslerin toplam yanlış konu sayısı karşılaştırması (SÜTUN)
        
        Args:
            df: Deneme verileri
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """
        # Her ders için toplam yanlış konu sayısını hesapla
        topic_list_columns = [col for col in df.columns if 'Yanlış Konular_List' in col]
        
        subject_totals = {}
        
        for col in topic_list_columns:
            subject = col.replace(' Yanlış Konular_List', '')
            
            # Tüm konuları topla
            all_topics = []
            for topics_list in df[col].dropna():
                if isinstance(topics_list, list):
                    all_topics.extend(topics_list)
            
            subject_totals[subject] = len(all_topics)
        
        if not subject_totals:
            logger.warning("Ders bazlı konu verisi bulunamadı")
            return None
        
        # Sırala (en çoktan aza)
        sorted_subjects = sorted(subject_totals.items(), key=lambda x: x[1], reverse=True)
        subjects = [s[0] for s in sorted_subjects]
        totals = [s[1] for s in sorted_subjects]
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Sütun grafik
        colors = [self._get_priority_color(t//5) for t in totals]  # Normalize et
        bars = ax.bar(subjects, totals, color=colors, alpha=0.85, 
                     edgecolor='black', linewidth=1)
        
        # Etiketler
        ax.set_xlabel('Dersler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Toplam Yanlış Sayısı', fontsize=12, fontweight='bold')
        ax.set_title('Derslere Göre Toplam Yanlış Konu Sayısı',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değer etiketleri
        for bar, total in zip(bars, totals):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(total)}',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_topic_heatmap(self, df: pd.DataFrame, subject: str,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Konuların deneme bazlı ısı haritası
        
        Args:
            df: Deneme verileri
            subject: Ders adı
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """
        topic_column = f"{subject} Yanlış Konular_List"
        
        if topic_column not in df.columns:
            logger.error(f"{topic_column} sütunu bulunamadı")
            return None
        
        df_sorted = df.sort_values('Tarih').copy()
        
        # Tüm benzersiz konuları bul
        all_topics = []
        for topics_list in df_sorted[topic_column].dropna():
            if isinstance(topics_list, list):
                all_topics.extend(topics_list)
        
        unique_topics = sorted(set(all_topics))
        
        if not unique_topics or len(unique_topics) > 30:  # Çok fazla konu varsa
            logger.warning("Heatmap için çok fazla veya çok az konu var")
            return None
        
        # Matris oluştur (Deneme x Konu)
        matrix = []
        exam_names = []
        
        for idx, row in df_sorted.iterrows():
            exam_names.append(row['Deneme Adı'])
            topics_in_exam = row[topic_column] if isinstance(row[topic_column], list) else []
            
            row_data = [1 if topic in topics_in_exam else 0 for topic in unique_topics]
            matrix.append(row_data)
        
        matrix = np.array(matrix)
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(max(12, len(unique_topics)*0.5), 
                                       max(8, len(exam_names)*0.4)))
        
        # Heatmap
        im = ax.imshow(matrix, cmap='Reds', aspect='auto', vmin=0, vmax=1)
        
        # Eksen etiketleri
        ax.set_xticks(np.arange(len(unique_topics)))
        ax.set_yticks(np.arange(len(exam_names)))
        ax.set_xticklabels(unique_topics, rotation=45, ha='right', fontsize=9)
        ax.set_yticklabels(exam_names, fontsize=9)
        
        # Başlık
        ax.set_title(f'{subject} - Konu Hatalarının Zamana Göre Dağılımı',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Colorbar
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('Yanlış Yapıldı mı?', rotation=270, labelpad=20)
        
        # Grid
        ax.set_xticks(np.arange(len(unique_topics))-.5, minor=True)
        ax.set_yticks(np.arange(len(exam_names))-.5, minor=True)
        ax.grid(which="minor", color="gray", linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_topic_frequency_distribution(self, df: pd.DataFrame, subject: str,
                                         save_path: Optional[str] = None) -> plt.Figure:
        """
        Konuların frekans dağılımı histogramı
        
        Args:
            df: Deneme verileri
            subject: Ders adı
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """
        topic_column = f"{subject} Yanlış Konular_List"
        
        if topic_column not in df.columns:
            logger.error(f"{topic_column} sütunu bulunamadı")
            return None
        
        # Tüm konuları topla
        all_topics = []
        for topics_list in df[topic_column].dropna():
            if isinstance(topics_list, list):
                all_topics.extend(topics_list)
        
        if not all_topics:
            logger.warning(f"{subject} için konu verisi yok")
            return None
        
        # Frekansları say
        topic_counts = Counter(all_topics)
        frequencies = list(topic_counts.values())
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Histogram
        bins = range(1, max(frequencies) + 2)
        ax.hist(frequencies, bins=bins, color=self.colors['info'], 
               alpha=0.7, edgecolor='black', linewidth=1)
        
        # Etiketler
        ax.set_xlabel('Yanlış Yapma Sayısı', fontsize=12, fontweight='bold')
        ax.set_ylabel('Konu Sayısı', fontsize=12, fontweight='bold')
        ax.set_title(f'{subject} - Konu Frekans Dağılımı',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # İstatistikler ekle
        stats_text = f"Toplam Benzersiz Konu: {len(topic_counts)}\n"
        stats_text += f"Toplam Hata: {sum(frequencies)}\n"
        stats_text += f"Ortalama Frekans: {np.mean(frequencies):.1f}"
        
        ax.text(0.98, 0.97, stats_text, transform=ax.transAxes,
               fontsize=10, verticalalignment='top', horizontalalignment='right',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_improvement_areas(self, df: pd.DataFrame, subject: str,
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        İyileşen vs kötüleşen konuları gösterir
        
        Args:
            df: Deneme verileri
            subject: Ders adı
            save_path: Kaydedilecek dosya yolu
            
        Returns:
            plt.Figure: Grafik figürü
        """
        topic_column = f"{subject} Yanlış Konular_List"
        
        if topic_column not in df.columns or len(df) < 6:
            logger.warning("İyileşme analizi için yeterli veri yok")
            return None
        
        df_sorted = df.sort_values('Tarih')
        
        # İlk yarı ve son yarı
        mid = len(df_sorted) // 2
        first_half = df_sorted.iloc[:mid]
        second_half = df_sorted.iloc[mid:]
        
        # Her yarı için konu sayımı
        def count_topics(df_part):
            all_topics = []
            for topics_list in df_part[topic_column].dropna():
                if isinstance(topics_list, list):
                    all_topics.extend(topics_list)
            return Counter(all_topics)
        
        first_counts = count_topics(first_half)
        second_counts = count_topics(second_half)
        
        # Tüm konuları bul
        all_topics = set(list(first_counts.keys()) + list(second_counts.keys()))
        
        # İyileşme/kötüleşme hesapla
        improvements = {}
        for topic in all_topics:
            first = first_counts.get(topic, 0)
            second = second_counts.get(topic, 0)
            change = first - second  # Pozitif = iyileşme
            if change != 0:
                improvements[topic] = change
        
        if not improvements:
            logger.warning("İyileşme/kötüleşme verisi yok")
            return None
        
        # Sırala
        sorted_improvements = sorted(improvements.items(), key=lambda x: x[1])
        topics = [t[0] for t in sorted_improvements]
        changes = [t[1] for t in sorted_improvements]
        
        # Renkleri belirle
        colors = [self.colors['low'] if c > 0 else self.colors['critical'] for c in changes]
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=(12, max(8, len(topics)*0.3)))
        
        # Yatay bar
        y_pos = np.arange(len(topics))
        bars = ax.barh(y_pos, changes, color=colors, alpha=0.85, edgecolor='black')
        
        # Etiketler
        ax.set_yticks(y_pos)
        ax.set_yticklabels(topics, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel('Değişim (İlk Yarı - Son Yarı)', fontsize=12, fontweight='bold')
        ax.set_title(f'{subject} - Konu İyileşme/Kötüleşme Analizi',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Sıfır çizgisi
        ax.axvline(x=0, color='black', linestyle='-', linewidth=2)
        
        # Grid
        ax.xaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değer etiketleri
        for bar, change in zip(bars, changes):
            width = bar.get_width()
            label_x = width + (0.3 if width > 0 else -0.3)
            ax.text(label_x, bar.get_y() + bar.get_height()/2,
                   f'{int(abs(change))}',
                   ha='left' if width > 0 else 'right',
                   va='center', fontsize=9, fontweight='bold')
        
        # Legend
        legend_elements = [
            plt.Rectangle((0,0),1,1, fc=self.colors['low'], alpha=0.85, label='İyileşti ✓'),
            plt.Rectangle((0,0),1,1, fc=self.colors['critical'], alpha=0.85, label='Kötüleşti ✗')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    
    def plot_topic_trend_by_exam(self, df: pd.DataFrame, subject: str, topic: str, save_path: Optional[str] = None) -> Optional[plt.Figure]:
        """
        Belirli bir konunun denemelere göre yanlış yapılma trendini gösterir.
        Args:
            df: Deneme verileri
            subject: Ders adı (örn: 'Matematik')
            topic: Konu adı (örn: 'Türev')
            save_path: Kaydedilecek dosya yolu (opsiyonel)
        Returns:
            plt.Figure veya None
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
        ax.set_title(f"{subject} - '{topic}' Konusunun Yanlış Yapılma Trendi", fontsize=14, fontweight='bold')
        ax.set_xlabel('Deneme')
        ax.set_ylabel('Yanlış Sayısı')
        ax.grid(True, alpha=0.3, linestyle='--')
        plt.xticks(rotation=45, ha='right')

        # Değer etiketleri
        for i, val in enumerate(topic_counts):
            if val > 0:
                ax.text(i, val + 0.1, str(val), ha='center', va='bottom', fontsize=9)

        plt.tight_layout()
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")

        return fig


# Kullanım örneği
if __name__ == "__main__":
    # Örnek veri
    sample_data = {
        'Deneme Adı': [f'Deneme {i}' for i in range(1, 11)],
        'Tarih': pd.date_range('2024-01-01', periods=10, freq='W'),
        'Türkçe Yanlış Konular_List': [
            ['Anlatım', 'Paragraf'],
            ['Anlatım', 'Sözcükte Anlam'],
            ['Paragraf', 'Anlatım'],
            ['Anlatım', 'Paragraf', 'Sözcükte Anlam'],
            ['Anlatım'],
            ['Paragraf', 'Cümle'],
            ['Anlatım', 'Paragraf'],
            ['Sözcükte Anlam'],
            ['Paragraf', 'Cümle'],
            ['Sözcükte Anlam', 'Anlatım']
        ],
        'Matematik Yanlış Konular_List': [
            ['Türev', 'Limit'],
            ['Türev', 'İntegral'],
            ['Türev'],
            ['Türev', 'Limit'],
            ['İntegral', 'Türev'],
            ['Türev'],
            ['Limit', 'Fonksiyon'],
            ['Türev'],
            ['İntegral'],
            ['Limit']
        ]
    }
    
    df = pd.DataFrame(sample_data)
    
    visualizer = TopicVisualizer()
    
    print("Konu grafikleri oluşturuluyor...")
    
    # 1. En çok yanlış yapılan konular
    visualizer.plot_total_wrong_topics(df, top_n=10)
    
    # 2. Ders bazlı karşılaştırma
    visualizer.plot_subject_topic_comparison(df)
    
    # 3. Türkçe dashboard
    visualizer.create_topic_dashboard(df, 'Türkçe')
    
    # 4. İyileşme analizi
    visualizer.plot_improvement_areas(df, 'Matematik')
    
    # 5. Belirli bir konunun trendi
    visualizer.plot_topic_trend_by_exam(df, 'Matematik', 'Türev')
    
    plt.show()
    print("Grafikler gösteriliyor!")