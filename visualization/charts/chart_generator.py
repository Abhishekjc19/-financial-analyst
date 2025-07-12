"""
Chart Generator Module
Creates interactive charts for technical analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
import json

logger = logging.getLogger(__name__)

class ChartGenerator:
    """Generates interactive charts for financial analysis"""
    
    def __init__(self):
        self.chart_theme = 'plotly_white'
        self.chart_width = 1200
        self.chart_height = 600
        
    def create_technical_charts(self, data: pd.DataFrame, analysis: Dict) -> Dict:
        """
        Create comprehensive technical analysis charts
        
        Args:
            data: Market data
            analysis: Technical analysis results
            
        Returns:
            Dictionary with chart data
        """
        try:
            charts = {
                'price_chart': self._create_price_chart(data, analysis),
                'volume_chart': self._create_volume_chart(data),
                'rsi_chart': self._create_rsi_chart(data),
                'macd_chart': self._create_macd_chart(data),
                'bollinger_chart': self._create_bollinger_chart(data),
                'summary_chart': self._create_summary_chart(data, analysis)
            }
            
            return charts
            
        except Exception as e:
            logger.error(f"Error creating technical charts: {str(e)}")
            return {}
    
    def _create_price_chart(self, data: pd.DataFrame, analysis: Dict) -> Dict:
        """Create price chart with technical indicators"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=('Price Chart', 'Volume'),
                row_width=[0.7, 0.3]
            )
            
            # Candlestick chart
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name='OHLC',
                    increasing_line_color='#26A69A',
                    decreasing_line_color='#EF5350'
                ),
                row=1, col=1
            )
            
            # Moving averages
            if 'SMA_20' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['SMA_20'],
                        mode='lines',
                        name='SMA 20',
                        line=dict(color='blue', width=1)
                    ),
                    row=1, col=1
                )
            
            if 'SMA_50' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['SMA_50'],
                        mode='lines',
                        name='SMA 50',
                        line=dict(color='orange', width=1)
                    ),
                    row=1, col=1
                )
            
            # Support and resistance levels
            if 'support_resistance' in analysis:
                sr = analysis['support_resistance']
                if sr.get('nearest_support'):
                    fig.add_hline(
                        y=sr['nearest_support'],
                        line_dash="dash",
                        line_color="green",
                        annotation_text="Support",
                        row=1, col=1
                    )
                
                if sr.get('nearest_resistance'):
                    fig.add_hline(
                        y=sr['nearest_resistance'],
                        line_dash="dash",
                        line_color="red",
                        annotation_text="Resistance",
                        row=1, col=1
                    )
            
            # Volume bars
            colors = ['red' if close < open else 'green' for close, open in zip(data['Close'], data['Open'])]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
            
            # Update layout
            fig.update_layout(
                title='Price Chart with Technical Indicators',
                xaxis_rangeslider_visible=False,
                height=600,
                showlegend=True,
                template=self.chart_theme
            )
            
            return {
                'type': 'price_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating price chart: {str(e)}")
            return {}
    
    def _create_volume_chart(self, data: pd.DataFrame) -> Dict:
        """Create volume analysis chart"""
        try:
            fig = go.Figure()
            
            # Volume bars
            colors = ['red' if close < open else 'green' for close, open in zip(data['Close'], data['Open'])]
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name='Volume',
                    marker_color=colors,
                    opacity=0.7
                )
            )
            
            # Volume moving average
            if 'volume_sma_20' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['volume_sma_20'],
                        mode='lines',
                        name='Volume SMA 20',
                        line=dict(color='blue', width=2)
                    )
                )
            
            fig.update_layout(
                title='Volume Analysis',
                xaxis_title='Date',
                yaxis_title='Volume',
                height=400,
                template=self.chart_theme
            )
            
            return {
                'type': 'volume_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating volume chart: {str(e)}")
            return {}
    
    def _create_rsi_chart(self, data: pd.DataFrame) -> Dict:
        """Create RSI chart"""
        try:
            fig = go.Figure()
            
            if 'rsi' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['rsi'],
                        mode='lines',
                        name='RSI',
                        line=dict(color='purple', width=2)
                    )
                )
                
                # Overbought/oversold lines
                fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
                fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
                fig.add_hline(y=50, line_dash="dot", line_color="gray", annotation_text="Neutral")
            
            fig.update_layout(
                title='Relative Strength Index (RSI)',
                xaxis_title='Date',
                yaxis_title='RSI',
                yaxis=dict(range=[0, 100]),
                height=400,
                template=self.chart_theme
            )
            
            return {
                'type': 'rsi_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating RSI chart: {str(e)}")
            return {}
    
    def _create_macd_chart(self, data: pd.DataFrame) -> Dict:
        """Create MACD chart"""
        try:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=('MACD', 'MACD Histogram'),
                row_width=[0.7, 0.3]
            )
            
            if 'macd' in data.columns and 'macd_signal' in data.columns:
                # MACD line
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd'],
                        mode='lines',
                        name='MACD',
                        line=dict(color='blue', width=2)
                    ),
                    row=1, col=1
                )
                
                # Signal line
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['macd_signal'],
                        mode='lines',
                        name='Signal',
                        line=dict(color='red', width=2)
                    ),
                    row=1, col=1
                )
                
                # Zero line
                fig.add_hline(y=0, line_dash="dot", line_color="gray", row=1, col=1)
            
            if 'macd_histogram' in data.columns:
                # MACD histogram
                colors = ['green' if x >= 0 else 'red' for x in data['macd_histogram']]
                fig.add_trace(
                    go.Bar(
                        x=data.index,
                        y=data['macd_histogram'],
                        name='Histogram',
                        marker_color=colors,
                        opacity=0.7
                    ),
                    row=2, col=1
                )
            
            fig.update_layout(
                title='MACD (Moving Average Convergence Divergence)',
                height=500,
                template=self.chart_theme
            )
            
            return {
                'type': 'macd_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating MACD chart: {str(e)}")
            return {}
    
    def _create_bollinger_chart(self, data: pd.DataFrame) -> Dict:
        """Create Bollinger Bands chart"""
        try:
            fig = go.Figure()
            
            # Price line
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Price',
                    line=dict(color='black', width=2)
                )
            )
            
            # Bollinger Bands
            if 'BB_Upper' in data.columns and 'BB_Lower' in data.columns:
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['BB_Upper'],
                        mode='lines',
                        name='Upper Band',
                        line=dict(color='gray', width=1, dash='dash'),
                        fill=None
                    )
                )
                
                fig.add_trace(
                    go.Scatter(
                        x=data.index,
                        y=data['BB_Lower'],
                        mode='lines',
                        name='Lower Band',
                        line=dict(color='gray', width=1, dash='dash'),
                        fill='tonexty',
                        fillcolor='rgba(128,128,128,0.1)'
                    )
                )
                
                if 'BB_Middle' in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['BB_Middle'],
                            mode='lines',
                            name='Middle Band',
                            line=dict(color='blue', width=1)
                        )
                    )
            
            fig.update_layout(
                title='Bollinger Bands',
                xaxis_title='Date',
                yaxis_title='Price',
                height=400,
                template=self.chart_theme
            )
            
            return {
                'type': 'bollinger_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating Bollinger chart: {str(e)}")
            return {}
    
    def _create_summary_chart(self, data: pd.DataFrame, analysis: Dict) -> Dict:
        """Create summary dashboard chart"""
        try:
            # Create summary metrics
            summary = analysis.get('summary', {})
            
            # Create gauge charts for key metrics
            fig = make_subplots(
                rows=2, cols=2,
                specs=[[{"type": "indicator"}, {"type": "indicator"}],
                       [{"type": "indicator"}, {"type": "indicator"}]],
                subplot_titles=('Price Change %', 'RSI', 'Volatility', 'Trend Strength')
            )
            
            # Price change gauge
            price_change = summary.get('change_percent', 0)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number+delta",
                    value=price_change,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Price Change %"},
                    delta={'reference': 0},
                    gauge={
                        'axis': {'range': [-20, 20]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [-20, -10], 'color': "lightgray"},
                            {'range': [-10, 0], 'color': "gray"},
                            {'range': [0, 10], 'color': "lightgreen"},
                            {'range': [10, 20], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 15
                        }
                    }
                ),
                row=1, col=1
            )
            
            # RSI gauge
            momentum = analysis.get('momentum', {})
            rsi = momentum.get('rsi', 50)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=rsi,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "RSI"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "green"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "red"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 70
                        }
                    }
                ),
                row=1, col=2
            )
            
            # Volatility gauge
            volatility = analysis.get('volatility', {})
            hist_vol = volatility.get('historical_volatility', 20)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=hist_vol,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Volatility %"},
                    gauge={
                        'axis': {'range': [0, 50]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 15], 'color': "green"},
                            {'range': [15, 25], 'color': "yellow"},
                            {'range': [25, 50], 'color': "red"}
                        ]
                    }
                ),
                row=2, col=1
            )
            
            # Trend strength gauge
            trend = analysis.get('trend', {})
            trend_strength = trend.get('trend_strength', 50)
            fig.add_trace(
                go.Indicator(
                    mode="gauge+number",
                    value=trend_strength,
                    domain={'x': [0, 1], 'y': [0, 1]},
                    title={'text': "Trend Strength"},
                    gauge={
                        'axis': {'range': [0, 100]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 30], 'color': "red"},
                            {'range': [30, 70], 'color': "yellow"},
                            {'range': [70, 100], 'color': "green"}
                        ]
                    }
                ),
                row=2, col=2
            )
            
            fig.update_layout(
                title='Technical Analysis Summary',
                height=600,
                template=self.chart_theme
            )
            
            return {
                'type': 'summary_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating summary chart: {str(e)}")
            return {}
    
    def create_prediction_chart(self, data: pd.DataFrame, predictions: Dict) -> Dict:
        """Create prediction visualization chart"""
        try:
            fig = go.Figure()
            
            # Historical price
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data['Close'],
                    mode='lines',
                    name='Historical Price',
                    line=dict(color='blue', width=2)
                )
            )
            
            # Prediction scenarios
            scenarios = predictions.get('scenario_analysis', {})
            
            if 'bull_case' in scenarios:
                bull_prob = scenarios['bull_case']['probability']
                bull_change = scenarios['bull_case']['price_change']
                current_price = data['Close'].iloc[-1]
                bull_price = current_price * (1 + bull_change)
                
                fig.add_trace(
                    go.Scatter(
                        x=[data.index[-1], data.index[-1] + pd.Timedelta(days=30)],
                        y=[current_price, bull_price],
                        mode='lines+markers',
                        name=f'Bull Case ({bull_prob*100:.0f}%)',
                        line=dict(color='green', width=2, dash='dash')
                    )
                )
            
            if 'bear_case' in scenarios:
                bear_prob = scenarios['bear_case']['probability']
                bear_change = scenarios['bear_case']['price_change']
                current_price = data['Close'].iloc[-1]
                bear_price = current_price * (1 + bear_change)
                
                fig.add_trace(
                    go.Scatter(
                        x=[data.index[-1], data.index[-1] + pd.Timedelta(days=30)],
                        y=[current_price, bear_price],
                        mode='lines+markers',
                        name=f'Bear Case ({bear_prob*100:.0f}%)',
                        line=dict(color='red', width=2, dash='dash')
                    )
                )
            
            fig.update_layout(
                title='Price Predictions',
                xaxis_title='Date',
                yaxis_title='Price',
                height=500,
                template=self.chart_theme
            )
            
            return {
                'type': 'prediction_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            }
            
        except Exception as e:
            logger.error(f"Error creating prediction chart: {str(e)}")
            return {}
    
    def create_portfolio_chart(self, allocation: Dict, metrics: Dict) -> Dict:
        """Create portfolio allocation chart"""
        try:
            # Pie chart for allocation
            fig = make_subplots(
                rows=1, cols=2,
                specs=[[{"type": "pie"}, {"type": "bar"}]],
                subplot_titles=('Portfolio Allocation', 'Risk Metrics')
            )
            
            # Allocation pie chart
            if 'percentage_allocation' in allocation:
                symbols = list(allocation['percentage_allocation'].keys())
                percentages = list(allocation['percentage_allocation'].values())
                
                fig.add_trace(
                    go.Pie(
                        labels=symbols,
                        values=percentages,
                        name="Allocation"
                    ),
                    row=1, col=1
                )
            
            # Risk metrics bar chart
            if metrics:
                metric_names = list(metrics.keys())
                metric_values = list(metrics.values())
                
                fig.add_trace(
                    go.Bar(
                        x=metric_names,
                        y=metric_values,
                        name="Metrics"
                    ),
                    row=1, col=2
                )
            
            fig.update_layout(
                title='Portfolio Analysis',
                height=500,
                template=self.chart_theme
            )
            
            return {
                'type': 'portfolio_chart',
                'data': fig.to_dict(),
                'layout': fig.layout
            } 