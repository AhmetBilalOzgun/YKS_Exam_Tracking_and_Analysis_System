"""
YKS Analiz Sistemi - Net Görselleştirme Modülü
Basit, anlaşılır ve temiz grafikler
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from typing import Optional, List, Dict
import logging
from config import Config

logger = logging.getLogger(__name__)

# Türkçe karakter desteği için
plt.rcParams['font.family'] = 'DejaVu Sans'


class NetVisualizer:
    """
    Net değerleri için basit ve anlaşılır grafikler oluşturur
    
    Tasarım prensibi: Sade, temiz, anlaşılır
    """
    
    def __init__(self, config: Config, style: str = 'seaborn-v0_8-whitegrid', figsize: tuple = (12, 6)):
        """
        NetVisualizer başlatıcı
    
        Args:
            config: Configuration object
            style: Matplotlib stili
            figsize: Grafik boyutu (genişlik, yükseklik)
        """

        self.config = config
        self.style = self.config.Visualization.STYLE
        self.figsize = self.config.Visualization.FIGURE_SIZE
        self.colors = self.config.Visualization.COLOR_PALETTE
        self.subject_colors = self.config.Visualization.SUBJECT_COLORS

        plt.style.use(self.style)


    
    def _get_subject_color(self, subject: str) -> str:
        """Ders rengini döndürür"""
        for key in self.subject_colors.keys():
            if key in subject:
                return self.subject_colors[key]
        return self.colors['primary']
    
    def _add_value_labels(self, ax, spacing: int = 0):
        """Çubukların üzerine değer etiketleri ekler"""
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
        Belirli bir dersin deneme bazlı net grafiği (SÜTUN)
        
        Args:
            df: Deneme verileri
            subject: Ders adı (örn: "Türkçe Net")
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        if subject not in df.columns:
            logger.error(f"{subject} sütunu bulunamadı")
            return None
        
        # Veriyi hazırla
        df_sorted = df.sort_values('Tarih').copy()
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Sütun grafik
        bars = ax.bar(
            range(len(df_sorted)),
            df_sorted[subject],
            color=self._get_subject_color(subject),
            alpha=0.8,
            edgecolor='black',
            linewidth=1
        )
        
        # Etiketler
        ax.set_xlabel('Denemeler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title(f'{subject} - Deneme Bazlı Performans', 
                    fontsize=14, fontweight='bold', pad=20)
        
        # X ekseni etiketleri
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değer etiketleri ekle
        self._add_value_labels(ax, spacing=1)
        
        # Ortalama çizgisi ekle
        mean_value = df_sorted[subject].mean()
        ax.axhline(y=mean_value, color='red', linestyle='--', 
                  linewidth=2, alpha=0.7, label=f'Ortalama: {mean_value:.1f}')
        ax.legend(loc='upper left', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_total_nets_by_exam(self, df: pd.DataFrame, 
                               save_path: Optional[str] = None) -> plt.Figure:
        """
        Toplam netlerin deneme bazlı grafiği (SÜTUN)
        
        Args:
            df: sDeneme verileri
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        return self.plot_subject_nets_by_exam(df, 'Toplam Net', save_path)
    
    def plot_all_subjects_comparison(self, df: pd.DataFrame, 
                                    save_path: Optional[str] = None) -> plt.Figure:
        """
        Tüm derslerin son denemede karşılaştırması (YAN YANA SÜTUN)
        
        Args:
            df: Deneme verileri
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        # Son denemeyi al
        latest_exam = df.sort_values('Tarih').iloc[-1]
        
        # Net sütunlarını bul (Toplam Net hariç)
        net_columns = [col for col in df.columns if 'Net' in col and col != 'Toplam Net']
        
        if not net_columns:
            logger.error("Net sütunu bulunamadı")
            return None
        
        # Veriyi hazırla
        subjects = [col.replace(' Net', '') for col in net_columns]
        values = [latest_exam[col] for col in net_columns]
        colors = [self._get_subject_color(col) for col in net_columns]
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        bars = ax.bar(subjects, values, color=colors, alpha=0.8, 
                     edgecolor='black', linewidth=1)
        
        # Etiketler
        ax.set_xlabel('Dersler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title(f'Son Deneme: {latest_exam["Deneme Adı"]} - Ders Bazlı Performans',
                    fontsize=14, fontweight='bold', pad=20)
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Değer etiketleri
        self._add_value_labels(ax, spacing=0.5)
        
        # X ekseni etiketlerini döndürme
        plt.xticks(rotation=0)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_subject_trend(self, df: pd.DataFrame, subject: str,
                          save_path: Optional[str] = None) -> plt.Figure:
        """
        Dersin zaman içindeki trendi (ÇİZGİ GRAFİK)
        
        Args:
            df: Deneme verileri
            subject: Ders adı
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        if subject not in df.columns:
            logger.error(f"{subject} sütunu bulunamadı")
            return None
        
        df_sorted = df.sort_values('Tarih').copy()
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Çizgi grafik
        ax.plot(
            range(len(df_sorted)),
            df_sorted[subject],
            marker='o',
            markersize=8,
            linewidth=2.5,
            color=self._get_subject_color(subject),
            label=subject
        )
        
        # Trend çizgisi ekle (lineer regresyon)
        x = np.arange(len(df_sorted))
        y = df_sorted[subject].values
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        ax.plot(x, p(x), linestyle='--', color='red', linewidth=2, 
               alpha=0.7, label=f'Trend (eğim: {z[0]:.2f})')
        
        # Etiketler
        ax.set_xlabel('Denemeler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title(f'{subject} - Trend Analizi',
                    fontsize=14, fontweight='bold', pad=20)
        
        # X ekseni etiketleri
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
        
        # Grid
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Legend
        ax.legend(loc='best', fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def plot_net_dashboard(self, df: pd.DataFrame, subjects: List[str], save_path: Optional[str] = None) -> plt.Figure:
        """
        Her ders için deneme bazlı net artış/azalış çizgi grafiği dashboard'u oluşturur.
        """
        df_sorted = df.sort_values('Tarih').copy()
        num_subjects = len(subjects)
        
        if num_subjects == 0:
            logger.warning("Dashboard için ders listesi boş.")
            return None
            
        # Subplot grid boyutunu belirle (örn: 2x2, 2x3 vb.)
        cols = 2
        rows = (num_subjects + 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(cols * 7, rows * 5), squeeze=False)
        axes = axes.flatten() # Eksenleri tek boyutlu dizi yap

        for i, subject in enumerate(subjects):
            if subject not in df_sorted.columns:
                logger.warning(f"{subject} sütunu bulunamadı, atlanıyor.")
                continue
                
            ax = axes[i]
            
            # Çizgi grafik
            ax.plot(
                range(len(df_sorted)),
                df_sorted[subject],
                marker='o',
                markersize=7,
                linewidth=2.5,
                color=self._get_subject_color(subject),
                label=subject.replace(' Net', '')
            )
            
            # Trend çizgisi
            x = np.arange(len(df_sorted))
            y = df_sorted[subject].dropna().values
            if len(y) > 1:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), linestyle='--', color='red', linewidth=2, alpha=0.7)
                
            # Değer etiketleri
            for j, val in enumerate(df_sorted[subject]):
                if not np.isnan(val):
                    ax.text(j, val + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=8)

            # Etiketler ve Başlık
            ax.set_title(f"{subject.replace(' Net', '')} Net Trendi", fontsize=12, fontweight='bold')
            ax.set_ylabel('Net')
            ax.set_xticks(range(len(df_sorted)))
            ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
            ax.grid(True, alpha=0.4, linestyle='--')

        # Kullanılmayan subplot'ları gizle
        for i in range(num_subjects, len(axes)):
            fig.delaxes(axes[i])
            
        fig.suptitle('Ders Bazlı Net Performans Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96]) # Suptitle için yer bırak

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Net dashboard kaydedildi: {save_path}")
            
        return fig
    
    def plot_multi_subject_comparison(self, df: pd.DataFrame, subjects: List[str],
                                     save_path: Optional[str] = None) -> plt.Figure:
        """
        Birden fazla dersi karşılaştırma (ÇOK ÇİZGİLİ GRAFİK)
        
        Args:
            df: Deneme verileri
            subjects: Ders listesi (örn: ["Türkçe Net", "Matematik Net"])
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        df_sorted = df.sort_values('Tarih').copy()
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Her ders için çizgi
        for subject in subjects:
            if subject not in df.columns:
                logger.warning(f"{subject} sütunu bulunamadı, atlanıyor")
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
        
        # Etiketler
        ax.set_xlabel('Denemeler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title('Ders Karşılaştırması - Zaman İçinde Performans',
                    fontsize=14, fontweight='bold', pad=20)
        
        # X ekseni etiketleri
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
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    
    def plot_target_comparison(self, df: pd.DataFrame, target_net: float,
                              subject: str = 'Toplam Net',
                              save_path: Optional[str] = None) -> plt.Figure:
        """
        Hedef net ile gerçekleşen netlerin karşılaştırması
        
        Args:
            df: Deneme verileri
            target_net: Hedef net
            subject: Ders adı
            save_path: Kaydedilecek dosya yolu (opsiyonel)
            
        Returns:
            plt.Figure: Grafik figürü
        """
        if subject not in df.columns:
            logger.error(f"{subject} sütunu bulunamadı")
            return None
        
        df_sorted = df.sort_values('Tarih').copy()
        
        # Grafik oluştur
        fig, ax = plt.subplots(figsize=self.figsize)
        
        # Gerçekleşen netler
        bars = ax.bar(
            range(len(df_sorted)),
            df_sorted[subject],
            color=[self.colors['success'] if x >= target_net else self.colors['danger'] 
                  for x in df_sorted[subject]],
            alpha=0.8,
            edgecolor='black',
            linewidth=1,
            label='Gerçekleşen Net'
        )
        
        # Hedef çizgisi
        ax.axhline(y=target_net, color='orange', linestyle='--', 
                  linewidth=3, alpha=0.8, label=f'Hedef: {target_net}')
        
        # Etiketler
        ax.set_xlabel('Denemeler', fontsize=12, fontweight='bold')
        ax.set_ylabel('Net', fontsize=12, fontweight='bold')
        ax.set_title(f'{subject} - Hedef Takibi',
                    fontsize=14, fontweight='bold', pad=20)
        
        # X ekseni etiketleri
        ax.set_xticks(range(len(df_sorted)))
        ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
        
        # Grid
        ax.yaxis.grid(True, alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)
        
        # Legend
        ax.legend(loc='upper left', fontsize=10)
        
        # Değer etiketleri
        self._add_value_labels(ax, spacing=1)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Grafik kaydedildi: {save_path}")
        
        return fig
    
    def dashboard(self, df: pd.DataFrame, exam_type: str = "TYT", save_path: Optional[str] = None) -> plt.Figure:
        """
        Sınav türüne göre (TYT/AYT) tüm derslerin net trendlerini tek bir dashboardda gösterir.

        Args:
            df: Deneme verileri
            exam_type: "TYT" veya "AYT"
            save_path: Kaydedilecek dosya yolu (opsiyonel)

        Returns:
            plt.Figure: Grafik figürü
        """
        # Sınav türüne göre dersleri seç
        if exam_type == "TYT":
            subjects = ["Türkçe Net", "Matematik Net", "Fen Net", "Sosyal Net"]
        else:
            subjects = ["Matematik Net", "Fizik Net", "Kimya Net", "Biyoloji Net", "Türk Dili ve Edebiyatı Net", "Tarih Net", "Coğrafya Net"]

        # Sadece veri içinde olanları al
        subjects = [s for s in subjects if s in df.columns]
        num_subjects = len(subjects)
        if num_subjects == 0:
            logger.warning("Dashboard için uygun ders bulunamadı.")
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
            # Trend çizgisi
            x = np.arange(len(df_sorted))
            y = df_sorted[subject].dropna().values
            if len(y) > 1:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                ax.plot(x, p(x), linestyle='--', color='red', linewidth=2, alpha=0.7)
            # Değer etiketleri
            for j, val in enumerate(df_sorted[subject]):
                if not np.isnan(val):
                    ax.text(j, val + 0.5, f'{val:.1f}', ha='center', va='bottom', fontsize=8)
            ax.set_title(f"{subject.replace(' Net', '')} Net Trendi", fontsize=12, fontweight='bold')
            ax.set_ylabel('Net')
            ax.set_xticks(range(len(df_sorted)))
            ax.set_xticklabels(df_sorted['Deneme Adı'], rotation=45, ha='right')
            ax.grid(True, alpha=0.4, linestyle='--')

        # Kullanılmayan subplot'ları gizle
        for i in range(num_subjects, len(axes)):
            fig.delaxes(axes[i])

        fig.suptitle(f'{exam_type} Ders Bazlı Net Performans Dashboard', fontsize=16, fontweight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Dashboard kaydedildi: {save_path}")

        return fig

# Kullanım örneği
if __name__ == "__main__":
    # Örnek veri
    sample_data = {
        'Deneme Adı': [f'Deneme {i}' for i in range(1, 11)],
        'Tarih': pd.date_range('2024-01-01', periods=10, freq='W'),
        'Toplam Net': [75, 78, 82, 80, 85, 87, 90, 88, 92, 95],
        'Türkçe Net': [25, 26, 28, 27, 29, 30, 31, 30, 32, 33],
        'Matematik Net': [20, 22, 24, 23, 26, 27, 29, 28, 30, 32],
        'Fen Net': [15, 15, 16, 16, 16, 16, 16, 16, 16, 16],
        'Sosyal Net': [15, 15, 14, 14, 14, 14, 14, 14, 14, 14]
    }
    
    df = pd.DataFrame(sample_data)
    
    visualizer = NetVisualizer()
    
    # Grafikler oluştur
    print("Grafikler oluşturuluyor...")
    
    # 1. Toplam Net Grafiği
    visualizer.plot_total_nets_by_exam(df)
    
    # 2. Matematik Trendi
    visualizer.plot_subject_trend(df, 'Matematik Net')
    
    # 3. Tüm Dersler Karşılaştırma
    visualizer.plot_multi_subject_comparison(
        df, 
        ['Türkçe Net', 'Matematik Net', 'Fen Net', 'Sosyal Net']
    )
    
    
    
    plt.show()
    print("Grafikler gösteriliyor!")