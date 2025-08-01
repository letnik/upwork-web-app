"""
Розширені візуалізації для аналізу логів
"""

import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import base64
import io
from collections import defaultdict, Counter

from shared.config.logging import get_logger


@dataclass
class VisualizationConfig:
    """Конфігурація візуалізації"""
    title: str
    width: int = 800
    height: int = 600
    theme: str = "plotly_white"
    colors: List[str] = None
    show_legend: bool = True
    interactive: bool = True


@dataclass
class ChartData:
    """Дані для графіка"""
    x: List[Any]
    y: List[Any]
    labels: List[str] = None
    colors: List[str] = None
    metadata: Dict[str, Any] = None


class AdvancedVisualizations:
    """Система розширених візуалізацій"""
    
    def __init__(self):
        self.logger = get_logger("advanced-visualizations")
        
        # Налаштування
        self.default_colors = [
            '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
            '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
        ]
        
        # Статистика
        self.stats = {
            'charts_generated': 0,
            'total_views': 0,
            'popular_charts': Counter()
        }
        
        self.logger.info("Система розширених візуалізацій ініціалізовано")
    
    def create_log_timeline(self, log_data: List[Dict[str, Any]], 
                          config: VisualizationConfig = None) -> str:
        """Створення часової шкали логів"""
        if config is None:
            config = VisualizationConfig(
                title="Timeline of Log Events",
                width=1200,
                height=400
            )
        
        try:
            # Підготовка даних
            df = pd.DataFrame(log_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Групування по рівнях логування
            level_counts = df.groupby([df['timestamp'].dt.hour, 'level']).size().unstack(fill_value=0)
            
            # Створення графіка
            fig = go.Figure()
            
            for level in level_counts.columns:
                fig.add_trace(go.Scatter(
                    x=level_counts.index,
                    y=level_counts[level],
                    mode='lines+markers',
                    name=level,
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Hour of Day",
                yaxis_title="Number of Logs",
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend,
                hovermode='x unified'
            )
            
            # Збереження як HTML
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['timeline'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення часової шкали", extra={"error": str(e)})
            return f"<p>Error creating timeline: {str(e)}</p>"
    
    def create_error_heatmap(self, log_data: List[Dict[str, Any]], 
                           config: VisualizationConfig = None) -> str:
        """Створення теплової карти помилок"""
        if config is None:
            config = VisualizationConfig(
                title="Error Heatmap by Hour and Day",
                width=1000,
                height=600
            )
        
        try:
            # Підготовка даних
            df = pd.DataFrame(log_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Фільтрація помилок
            error_logs = df[df['level'].isin(['ERROR', 'CRITICAL'])]
            
            if error_logs.empty:
                return "<p>No error logs found for the specified period</p>"
            
            # Створення теплової карти
            error_logs['hour'] = error_logs['timestamp'].dt.hour
            error_logs['day'] = error_logs['timestamp'].dt.day_name()
            
            heatmap_data = error_logs.groupby(['day', 'hour']).size().unstack(fill_value=0)
            
            # Порядок днів тижня
            day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            heatmap_data = heatmap_data.reindex(day_order)
            
            fig = go.Figure(data=go.Heatmap(
                z=heatmap_data.values,
                x=heatmap_data.columns,
                y=heatmap_data.index,
                colorscale='Reds',
                showscale=True,
                text=heatmap_data.values,
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Hour of Day",
                yaxis_title="Day of Week",
                width=config.width,
                height=config.height,
                template=config.theme
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['heatmap'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення теплової карти", extra={"error": str(e)})
            return f"<p>Error creating heatmap: {str(e)}</p>"
    
    def create_performance_dashboard(self, performance_data: List[Dict[str, Any]], 
                                   config: VisualizationConfig = None) -> str:
        """Створення dashboard продуктивності"""
        if config is None:
            config = VisualizationConfig(
                title="Performance Dashboard",
                width=1400,
                height=800
            )
        
        try:
            # Підготовка даних
            df = pd.DataFrame(performance_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Створення subplots
            fig = make_subplots(
                rows=2, cols=2,
                subplot_titles=('CPU Usage', 'Memory Usage', 'Response Time', 'Error Rate'),
                specs=[[{"secondary_y": False}, {"secondary_y": False}],
                       [{"secondary_y": False}, {"secondary_y": False}]]
            )
            
            # CPU Usage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['cpu_usage'],
                    mode='lines',
                    name='CPU Usage',
                    line=dict(color='#1f77b4', width=2)
                ),
                row=1, col=1
            )
            
            # Memory Usage
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['memory_usage'],
                    mode='lines',
                    name='Memory Usage',
                    line=dict(color='#ff7f0e', width=2)
                ),
                row=1, col=2
            )
            
            # Response Time
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['response_time'],
                    mode='lines',
                    name='Response Time',
                    line=dict(color='#2ca02c', width=2)
                ),
                row=2, col=1
            )
            
            # Error Rate
            fig.add_trace(
                go.Scatter(
                    x=df['timestamp'],
                    y=df['error_rate'],
                    mode='lines',
                    name='Error Rate',
                    line=dict(color='#d62728', width=2)
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title=config.title,
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['dashboard'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення dashboard", extra={"error": str(e)})
            return f"<p>Error creating dashboard: {str(e)}</p>"
    
    def create_service_comparison(self, services_data: Dict[str, List[Dict[str, Any]]], 
                                config: VisualizationConfig = None) -> str:
        """Створення порівняння сервісів"""
        if config is None:
            config = VisualizationConfig(
                title="Service Performance Comparison",
                width=1200,
                height=700
            )
        
        try:
            # Підготовка даних
            all_data = []
            for service_name, data in services_data.items():
                df = pd.DataFrame(data)
                df['service'] = service_name
                all_data.append(df)
            
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # Створення графіка
            fig = go.Figure()
            
            metrics = ['cpu_usage', 'memory_usage', 'response_time', 'error_rate']
            colors = self.default_colors[:len(metrics)]
            
            for i, metric in enumerate(metrics):
                if metric in combined_df.columns:
                    fig.add_trace(go.Box(
                        y=combined_df[metric],
                        x=combined_df['service'],
                        name=metric.replace('_', ' ').title(),
                        marker_color=colors[i],
                        boxpoints='outliers'
                    ))
            
            fig.update_layout(
                title=config.title,
                yaxis_title="Value",
                xaxis_title="Service",
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['comparison'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення порівняння сервісів", extra={"error": str(e)})
            return f"<p>Error creating service comparison: {str(e)}</p>"
    
    def create_anomaly_detection_chart(self, anomaly_data: List[Dict[str, Any]], 
                                     config: VisualizationConfig = None) -> str:
        """Створення графіка виявлення аномалій"""
        if config is None:
            config = VisualizationConfig(
                title="Anomaly Detection Results",
                width=1200,
                height=600
            )
        
        try:
            # Підготовка даних
            df = pd.DataFrame(anomaly_data)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Створення графіка
            fig = go.Figure()
            
            # Нормальні точки
            normal_data = df[df['is_anomaly'] == False]
            fig.add_trace(go.Scatter(
                x=normal_data['timestamp'],
                y=normal_data['value'],
                mode='markers',
                name='Normal',
                marker=dict(color='blue', size=4),
                opacity=0.6
            ))
            
            # Аномальні точки
            anomaly_data = df[df['is_anomaly'] == True]
            if not anomaly_data.empty:
                fig.add_trace(go.Scatter(
                    x=anomaly_data['timestamp'],
                    y=anomaly_data['value'],
                    mode='markers',
                    name='Anomaly',
                    marker=dict(color='red', size=8, symbol='x'),
                    text=anomaly_data['description'],
                    hovertemplate='<b>Anomaly</b><br>' +
                                'Time: %{x}<br>' +
                                'Value: %{y}<br>' +
                                'Description: %{text}<br>' +
                                '<extra></extra>'
                ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Time",
                yaxis_title="Value",
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['anomaly'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення графіка аномалій", extra={"error": str(e)})
            return f"<p>Error creating anomaly chart: {str(e)}</p>"
    
    def create_correlation_matrix(self, correlation_data: Dict[str, Dict[str, float]], 
                                config: VisualizationConfig = None) -> str:
        """Створення матриці кореляцій"""
        if config is None:
            config = VisualizationConfig(
                title="Correlation Matrix",
                width=800,
                height=800
            )
        
        try:
            # Підготовка даних
            metrics = list(correlation_data.keys())
            correlation_matrix = np.zeros((len(metrics), len(metrics)))
            
            for i, metric1 in enumerate(metrics):
                for j, metric2 in enumerate(metrics):
                    correlation_matrix[i, j] = correlation_data[metric1].get(metric2, 0)
            
            # Створення теплової карти
            fig = go.Figure(data=go.Heatmap(
                z=correlation_matrix,
                x=metrics,
                y=metrics,
                colorscale='RdBu',
                zmid=0,
                text=np.round(correlation_matrix, 2),
                texttemplate="%{text}",
                textfont={"size": 10},
                hoverongaps=False
            ))
            
            fig.update_layout(
                title=config.title,
                width=config.width,
                height=config.height,
                template=config.theme
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['correlation'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення матриці кореляцій", extra={"error": str(e)})
            return f"<p>Error creating correlation matrix: {str(e)}</p>"
    
    def create_distribution_chart(self, data: List[float], labels: List[str] = None, 
                                config: VisualizationConfig = None) -> str:
        """Створення графіка розподілу"""
        if config is None:
            config = VisualizationConfig(
                title="Data Distribution",
                width=800,
                height=600
            )
        
        try:
            # Створення гістограми
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=data,
                nbinsx=30,
                name='Distribution',
                marker_color='#1f77b4',
                opacity=0.7
            ))
            
            fig.update_layout(
                title=config.title,
                xaxis_title="Value",
                yaxis_title="Frequency",
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=config.show_legend
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['distribution'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення графіка розподілу", extra={"error": str(e)})
            return f"<p>Error creating distribution chart: {str(e)}</p>"
    
    def create_3d_scatter(self, data: List[Dict[str, float]], 
                         x_col: str, y_col: str, z_col: str,
                         config: VisualizationConfig = None) -> str:
        """Створення 3D scatter plot"""
        if config is None:
            config = VisualizationConfig(
                title="3D Scatter Plot",
                width=1000,
                height=800
            )
        
        try:
            # Підготовка даних
            df = pd.DataFrame(data)
            
            fig = go.Figure(data=[go.Scatter3d(
                x=df[x_col],
                y=df[y_col],
                z=df[z_col],
                mode='markers',
                marker=dict(
                    size=5,
                    color=df.get('color', 0),
                    colorscale='Viridis',
                    opacity=0.8
                ),
                text=df.get('label', ''),
                hovertemplate='<b>%{text}</b><br>' +
                            f'{x_col}: %{{x}}<br>' +
                            f'{y_col}: %{{y}}<br>' +
                            f'{z_col}: %{{z}}<br>' +
                            '<extra></extra>'
            )])
            
            fig.update_layout(
                title=config.title,
                scene=dict(
                    xaxis_title=x_col,
                    yaxis_title=y_col,
                    zaxis_title=z_col
                ),
                width=config.width,
                height=config.height,
                template=config.theme
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['3d_scatter'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення 3D scatter plot", extra={"error": str(e)})
            return f"<p>Error creating 3D scatter plot: {str(e)}</p>"
    
    def create_interactive_dashboard(self, dashboard_data: Dict[str, Any], 
                                   config: VisualizationConfig = None) -> str:
        """Створення інтерактивного dashboard"""
        if config is None:
            config = VisualizationConfig(
                title="Interactive Log Analysis Dashboard",
                width=1600,
                height=1000
            )
        
        try:
            # Створення dashboard з кількома графіками
            fig = make_subplots(
                rows=3, cols=2,
                subplot_titles=(
                    'Log Volume Over Time', 'Error Distribution',
                    'Performance Metrics', 'Service Health',
                    'Anomaly Detection', 'Correlation Analysis'
                ),
                specs=[[{"type": "scatter"}, {"type": "bar"}],
                       [{"type": "scatter"}, {"type": "indicator"}],
                       [{"type": "scatter"}, {"type": "heatmap"}]]
            )
            
            # 1. Log Volume Over Time
            if 'log_volume' in dashboard_data:
                log_data = dashboard_data['log_volume']
                fig.add_trace(
                    go.Scatter(
                        x=log_data['timestamps'],
                        y=log_data['volumes'],
                        mode='lines',
                        name='Log Volume',
                        line=dict(color='#1f77b4', width=2)
                    ),
                    row=1, col=1
                )
            
            # 2. Error Distribution
            if 'error_distribution' in dashboard_data:
                error_data = dashboard_data['error_distribution']
                fig.add_trace(
                    go.Bar(
                        x=list(error_data.keys()),
                        y=list(error_data.values()),
                        name='Error Types',
                        marker_color='#d62728'
                    ),
                    row=1, col=2
                )
            
            # 3. Performance Metrics
            if 'performance' in dashboard_data:
                perf_data = dashboard_data['performance']
                for metric, values in perf_data.items():
                    fig.add_trace(
                        go.Scatter(
                            x=values['timestamps'],
                            y=values['values'],
                            mode='lines',
                            name=metric,
                            line=dict(width=2)
                        ),
                        row=2, col=1
                    )
            
            # 4. Service Health Indicator
            if 'service_health' in dashboard_data:
                health_data = dashboard_data['service_health']
                fig.add_trace(
                    go.Indicator(
                        mode="gauge+number+delta",
                        value=health_data['value'],
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': "Service Health"},
                        delta={'reference': health_data.get('reference', 100)},
                        gauge={
                            'axis': {'range': [None, 100]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, 50], 'color': "lightgray"},
                                {'range': [50, 80], 'color': "yellow"},
                                {'range': [80, 100], 'color': "green"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': 90
                            }
                        }
                    ),
                    row=2, col=2
                )
            
            # 5. Anomaly Detection
            if 'anomalies' in dashboard_data:
                anomaly_data = dashboard_data['anomalies']
                fig.add_trace(
                    go.Scatter(
                        x=anomaly_data['timestamps'],
                        y=anomaly_data['values'],
                        mode='markers',
                        name='Anomalies',
                        marker=dict(
                            color='red',
                            size=8,
                            symbol='x'
                        )
                    ),
                    row=3, col=1
                )
            
            # 6. Correlation Heatmap
            if 'correlation_matrix' in dashboard_data:
                corr_matrix = dashboard_data['correlation_matrix']
                fig.add_trace(
                    go.Heatmap(
                        z=corr_matrix['values'],
                        x=corr_matrix['x_labels'],
                        y=corr_matrix['y_labels'],
                        colorscale='RdBu',
                        zmid=0
                    ),
                    row=3, col=2
                )
            
            fig.update_layout(
                title=config.title,
                width=config.width,
                height=config.height,
                template=config.theme,
                showlegend=True
            )
            
            html_content = fig.to_html(include_plotlyjs=True, full_html=False)
            
            self.stats['charts_generated'] += 1
            self.stats['popular_charts']['dashboard'] += 1
            
            return html_content
            
        except Exception as e:
            self.logger.error("Помилка створення інтерактивного dashboard", extra={"error": str(e)})
            return f"<p>Error creating interactive dashboard: {str(e)}</p>"
    
    def export_chart_as_image(self, html_content: str, format: str = 'png') -> str:
        """Експорт графіка як зображення"""
        try:
            # Конвертація HTML в зображення
            import plotly.io as pio
            
            # Створення тимчасового файлу
            import tempfile
            import os
            
            with tempfile.NamedTemporaryFile(suffix=f'.{format}', delete=False) as tmp_file:
                # Збереження як зображення
                pio.write_image(html_content, tmp_file.name, format=format)
                
                # Читання файлу
                with open(tmp_file.name, 'rb') as f:
                    image_data = f.read()
                
                # Видалення тимчасового файлу
                os.unlink(tmp_file.name)
                
                # Кодування в base64
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                
                return f"data:image/{format};base64,{encoded_image}"
                
        except Exception as e:
            self.logger.error("Помилка експорту графіка", extra={"error": str(e)})
            return ""
    
    def get_visualization_stats(self) -> Dict[str, Any]:
        """Отримання статистики візуалізацій"""
        return {
            **self.stats,
            'popular_charts': dict(self.stats['popular_charts']),
            'total_charts': self.stats['charts_generated']
        }


# Глобальний екземпляр системи візуалізацій
advanced_visualizations = AdvancedVisualizations()


def get_advanced_visualizations() -> AdvancedVisualizations:
    """Отримання системи розширених візуалізацій"""
    return advanced_visualizations 