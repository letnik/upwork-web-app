"""
Базові візуалізації для аналізу логів (Phase 3)
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import base64
import io

from shared.config.logging import get_logger


@dataclass
class BasicChartConfig:
    """Базова конфігурація графіка"""
    title: str
    width: int = 800
    height: int = 600
    save_path: Optional[str] = None


class BasicVisualizations:
    """Система базових візуалізацій"""
    
    def __init__(self):
        self.logger = get_logger("basic-visualizations")
        
        # Налаштування
        self.default_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        # Статистика
        self.stats = {
            'charts_generated': 0,
            'total_views': 0
        }
        
        self.logger.info("Система базових візуалізацій ініціалізовано")
    
    def create_log_timeline(self, log_data: List[Dict[str, Any]], 
                          config: BasicChartConfig = None) -> str:
        """Створення часової шкали логів"""
        if config is None:
            config = BasicChartConfig(title="Timeline of Log Events")
        
        try:
            # Підготовка даних
            df = pd.DataFrame(log_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Групування по рівнях логування
            level_counts = df.groupby([df['timestamp'].dt.hour, 'level']).size().unstack(fill_value=0)
            
            # Створення графіка
            plt.figure(figsize=(12, 6))
            
            for level in level_counts.columns:
                plt.plot(level_counts.index, level_counts[level], 
                        marker='o', label=level, linewidth=2, markersize=6)
            
            plt.title(config.title, fontsize=14, fontweight='bold')
            plt.xlabel('Hour of Day', fontsize=12)
            plt.ylabel('Number of Logs', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення часової шкали", extra={"error": str(e)})
            return ""
    
    def create_error_distribution(self, log_data: List[Dict[str, Any]], 
                                config: BasicChartConfig = None) -> str:
        """Створення розподілу помилок"""
        if config is None:
            config = BasicChartConfig(title="Error Distribution")
        
        try:
            # Підготовка даних
            df = pd.DataFrame(log_data)
            
            # Фільтрація помилок
            error_logs = df[df['level'].isin(['ERROR', 'CRITICAL'])]
            
            if error_logs.empty:
                return ""
            
            # Підрахунок помилок по типах
            error_counts = error_logs['level'].value_counts()
            
            # Створення кругової діаграми
            plt.figure(figsize=(10, 8))
            
            colors = self.default_colors[:len(error_counts)]
            plt.pie(error_counts.values, labels=error_counts.index, 
                   autopct='%1.1f%%', colors=colors, startangle=90)
            
            plt.title(config.title, fontsize=14, fontweight='bold')
            plt.axis('equal')
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення розподілу помилок", extra={"error": str(e)})
            return ""
    
    def create_performance_chart(self, performance_data: List[Dict[str, Any]], 
                               config: BasicChartConfig = None) -> str:
        """Створення графіка продуктивності"""
        if config is None:
            config = BasicChartConfig(title="Performance Metrics")
        
        try:
            # Підготовка даних
            df = pd.DataFrame(performance_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Створення subplots
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
            
            # CPU Usage
            if 'cpu_usage' in df.columns:
                ax1.plot(df['timestamp'], df['cpu_usage'], color='#1f77b4', linewidth=2)
                ax1.set_title('CPU Usage')
                ax1.set_ylabel('CPU %')
                ax1.grid(True, alpha=0.3)
            
            # Memory Usage
            if 'memory_usage' in df.columns:
                ax2.plot(df['timestamp'], df['memory_usage'], color='#ff7f0e', linewidth=2)
                ax2.set_title('Memory Usage')
                ax2.set_ylabel('Memory %')
                ax2.grid(True, alpha=0.3)
            
            # Response Time
            if 'response_time' in df.columns:
                ax3.plot(df['timestamp'], df['response_time'], color='#2ca02c', linewidth=2)
                ax3.set_title('Response Time')
                ax3.set_ylabel('Time (ms)')
                ax3.grid(True, alpha=0.3)
            
            # Error Rate
            if 'error_rate' in df.columns:
                ax4.plot(df['timestamp'], df['error_rate'], color='#d62728', linewidth=2)
                ax4.set_title('Error Rate')
                ax4.set_ylabel('Error Rate %')
                ax4.grid(True, alpha=0.3)
            
            plt.suptitle(config.title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення графіка продуктивності", extra={"error": str(e)})
            return ""
    
    def create_service_comparison(self, services_data: Dict[str, List[Dict[str, Any]]], 
                                config: BasicChartConfig = None) -> str:
        """Створення порівняння сервісів"""
        if config is None:
            config = BasicChartConfig(title="Service Performance Comparison")
        
        try:
            # Підготовка даних
            service_stats = {}
            
            for service_name, data in services_data.items():
                df = pd.DataFrame(data)
                service_stats[service_name] = {
                    'avg_response_time': df.get('response_time', pd.Series([0])).mean(),
                    'error_rate': df.get('error_rate', pd.Series([0])).mean(),
                    'total_requests': len(df)
                }
            
            # Створення графіка
            fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(18, 6))
            
            services = list(service_stats.keys())
            
            # Середній час відповіді
            response_times = [service_stats[s]['avg_response_time'] for s in services]
            ax1.bar(services, response_times, color='#1f77b4', alpha=0.7)
            ax1.set_title('Average Response Time')
            ax1.set_ylabel('Time (ms)')
            ax1.tick_params(axis='x', rotation=45)
            
            # Частота помилок
            error_rates = [service_stats[s]['error_rate'] for s in services]
            ax2.bar(services, error_rates, color='#d62728', alpha=0.7)
            ax2.set_title('Error Rate')
            ax2.set_ylabel('Error Rate %')
            ax2.tick_params(axis='x', rotation=45)
            
            # Загальна кількість запитів
            total_requests = [service_stats[s]['total_requests'] for s in services]
            ax3.bar(services, total_requests, color='#2ca02c', alpha=0.7)
            ax3.set_title('Total Requests')
            ax3.set_ylabel('Count')
            ax3.tick_params(axis='x', rotation=45)
            
            plt.suptitle(config.title, fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення порівняння сервісів", extra={"error": str(e)})
            return ""
    
    def create_anomaly_chart(self, anomaly_data: List[Dict[str, Any]], 
                           config: BasicChartConfig = None) -> str:
        """Створення графіка аномалій"""
        if config is None:
            config = BasicChartConfig(title="Anomaly Detection Results")
        
        try:
            # Підготовка даних
            df = pd.DataFrame(anomaly_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Створення графіка
            plt.figure(figsize=(12, 6))
            
            # Нормальні точки
            normal_data = df[df['is_anomaly'] == False]
            if not normal_data.empty:
                plt.scatter(normal_data['timestamp'], normal_data['value'], 
                          c='blue', alpha=0.6, s=20, label='Normal')
            
            # Аномальні точки
            anomaly_data = df[df['is_anomaly'] == True]
            if not anomaly_data.empty:
                plt.scatter(anomaly_data['timestamp'], anomaly_data['value'], 
                          c='red', s=50, marker='x', label='Anomaly')
            
            plt.title(config.title, fontsize=14, fontweight='bold')
            plt.xlabel('Time', fontsize=12)
            plt.ylabel('Value', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення графіка аномалій", extra={"error": str(e)})
            return ""
    
    def create_summary_dashboard(self, summary_data: Dict[str, Any], 
                               config: BasicChartConfig = None) -> str:
        """Створення зведеного dashboard"""
        if config is None:
            config = BasicChartConfig(title="Log Analysis Summary Dashboard")
        
        try:
            # Створення графіка
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
            
            # 1. Загальна статистика
            if 'total_logs' in summary_data:
                ax1.text(0.5, 0.5, f"Total Logs: {summary_data['total_logs']}", 
                        ha='center', va='center', fontsize=20, fontweight='bold')
                ax1.set_title('Total Logs')
                ax1.axis('off')
            
            # 2. Розподіл по рівнях
            if 'level_distribution' in summary_data:
                levels = list(summary_data['level_distribution'].keys())
                counts = list(summary_data['level_distribution'].values())
                ax2.bar(levels, counts, color=self.default_colors[:len(levels)])
                ax2.set_title('Log Level Distribution')
                ax2.set_ylabel('Count')
            
            # 3. Часовий розподіл
            if 'hourly_distribution' in summary_data:
                hours = list(summary_data['hourly_distribution'].keys())
                counts = list(summary_data['hourly_distribution'].values())
                ax3.plot(hours, counts, marker='o', linewidth=2, markersize=6)
                ax3.set_title('Hourly Distribution')
                ax3.set_xlabel('Hour')
                ax3.set_ylabel('Count')
                ax3.grid(True, alpha=0.3)
            
            # 4. Статистика помилок
            if 'error_stats' in summary_data:
                error_stats = summary_data['error_stats']
                stats_text = f"Errors: {error_stats.get('total_errors', 0)}\n"
                stats_text += f"Critical: {error_stats.get('critical_errors', 0)}\n"
                stats_text += f"Rate: {error_stats.get('error_rate', 0):.2f}%"
                
                ax4.text(0.5, 0.5, stats_text, ha='center', va='center', 
                        fontsize=16, fontweight='bold')
                ax4.set_title('Error Statistics')
                ax4.axis('off')
            
            plt.suptitle(config.title, fontsize=18, fontweight='bold')
            plt.tight_layout()
            
            # Збереження графіка
            if config.save_path:
                plt.savefig(config.save_path, dpi=300, bbox_inches='tight')
            
            # Конвертація в base64
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
            img_buffer.seek(0)
            img_data = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
            plt.close()
            
            self.stats['charts_generated'] += 1
            
            return f"data:image/png;base64,{img_data}"
            
        except Exception as e:
            self.logger.error("Помилка створення dashboard", extra={"error": str(e)})
            return ""
    
    def get_visualization_stats(self) -> Dict[str, Any]:
        """Отримання статистики візуалізацій"""
        return {
            **self.stats,
            'total_charts': self.stats['charts_generated']
        }


# Глобальний екземпляр системи базових візуалізацій
basic_visualizations = BasicVisualizations()


def get_basic_visualizations() -> BasicVisualizations:
    """Отримання системи базових візуалізацій"""
    return basic_visualizations 