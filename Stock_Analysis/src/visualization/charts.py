"""
Charts Module - Creates interactive charts using Plotly for stock analysis
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class StockCharts:
   
    
    def __init__(self, theme='plotly_white'):
       
        self.theme = theme
        self.colors = {
            'bullish': '#00CC96',
            'bearish': '#FF6692',
            'volume': '#636EFA',
            'sma': '#FFA15A',
            'ema': '#19D3F3',
            'rsi': '#B6E880',
            'macd': '#FF97FF',
            'signal': '#FECB52'
        }
    
    def create_candlestick_chart(self, data, title="Stock Price", show_volume=True):
       
        if data.empty:
            logger.error("Cannot create chart with empty data")
            return go.Figure()
        
        required_columns = ['Open', 'High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Required columns {required_columns} not found in data")
            return go.Figure()
        
        # Create subplots
        if show_volume and 'Volume' in data.columns:
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.03,
                subplot_titles=(title, 'Volume'),
                row_width=[0.7, 0.3]
            )
        else:
            fig = make_subplots(rows=1, cols=1)
        
        # Add candlestick chart
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="OHLC",
                increasing_line_color=self.colors['bullish'],
                decreasing_line_color=self.colors['bearish']
            ),
            row=1, col=1
        )
        
        # Add volume if requested
        if show_volume and 'Volume' in data.columns:
            colors = [self.colors['bullish'] if close >= open else self.colors['bearish'] 
                     for close, open in zip(data['Close'], data['Open'])]
            
            fig.add_trace(
                go.Bar(
                    x=data.index,
                    y=data['Volume'],
                    name="Volume",
                    marker_color=colors,
                    opacity=0.7
                ),
                row=2, col=1
            )
        
        # Update layout
        fig.update_layout(
            title=title,
            yaxis_title="Price",
            template=self.theme,
            xaxis_rangeslider_visible=False,
            height=600 if show_volume else 400
        )
        
        if show_volume:
            fig.update_yaxes(title_text="Volume", row=2, col=1)
        
        return fig
    
    def create_line_chart(self, data, columns, title="Stock Price", colors=None):
       
        if data.empty:
            logger.error("Cannot create chart with empty data")
            return go.Figure()
        
        missing_columns = [col for col in columns if col not in data.columns]
        if missing_columns:
            logger.error(f"Columns {missing_columns} not found in data")
            return go.Figure()
        
        fig = go.Figure()
        
        if colors is None:
            colors = px.colors.qualitative.Set1
        
        for i, column in enumerate(columns):
            color = colors[i % len(colors)] if i < len(colors) else None
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=data[column],
                    mode='lines',
                    name=column,
                    line=dict(color=color) if color else None
                )
            )
        
        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Price",
            template=self.theme,
            height=400
        )
        
        return fig
    
    def create_indicator_chart(self, data, price_indicators=None, oscillators=None, title="Technical Indicators"):
      
        if data.empty:
            logger.error("Cannot create chart with empty data")
            return go.Figure()
        
        # Determine number of subplots
        num_subplots = 1
        if oscillators:
            num_subplots += len(oscillators)
        
        # Create subplots
        subplot_titles = [title]
        if oscillators:
            subplot_titles.extend(oscillators)
        
        fig = make_subplots(
            rows=num_subplots, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=subplot_titles,
            row_heights=[0.6] + [0.4/(num_subplots-1)]*(num_subplots-1) if num_subplots > 1 else [1.0]
        )
        
        # Add candlestick chart
        if all(col in data.columns for col in ['Open', 'High', 'Low', 'Close']):
            fig.add_trace(
                go.Candlestick(
                    x=data.index,
                    open=data['Open'],
                    high=data['High'],
                    low=data['Low'],
                    close=data['Close'],
                    name="OHLC",
                    increasing_line_color=self.colors['bullish'],
                    decreasing_line_color=self.colors['bearish']
                ),
                row=1, col=1
            )
        
        # Add price indicators
        if price_indicators:
            for indicator in price_indicators:
                if indicator in data.columns:
                    color = self.colors.get(indicator.lower(), None)
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data[indicator],
                            mode='lines',
                            name=indicator,
                            line=dict(color=color) if color else None
                        ),
                        row=1, col=1
                    )
        
        # Add oscillators
        if oscillators:
            for i, oscillator in enumerate(oscillators):
                row_num = i + 2
                
                if oscillator == 'RSI' and 'RSI' in data.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['RSI'],
                            mode='lines',
                            name='RSI',
                            line=dict(color=self.colors['rsi'])
                        ),
                        row=row_num, col=1
                    )
                    
                    # Add RSI reference lines
                    fig.add_hline(y=70, line_dash="dash", line_color="red", 
                                 annotation_text="Overbought", row=row_num, col=1)
                    fig.add_hline(y=30, line_dash="dash", line_color="green", 
                                 annotation_text="Oversold", row=row_num, col=1)
                
                elif oscillator == 'MACD' and all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['MACD'],
                            mode='lines',
                            name='MACD',
                            line=dict(color=self.colors['macd'])
                        ),
                        row=row_num, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['MACD_Signal'],
                            mode='lines',
                            name='Signal',
                            line=dict(color=self.colors['signal'])
                        ),
                        row=row_num, col=1
                    )
                    
                    fig.add_trace(
                        go.Bar(
                            x=data.index,
                            y=data['MACD_Histogram'],
                            name='Histogram',
                            marker_color=self.colors['volume'],
                            opacity=0.7
                        ),
                        row=row_num, col=1
                    )
                
                elif oscillator == 'Stochastic' and all(col in data.columns for col in ['Stoch_K', 'Stoch_D']):
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['Stoch_K'],
                            mode='lines',
                            name='%K',
                            line=dict(color='blue')
                        ),
                        row=row_num, col=1
                    )
                    
                    fig.add_trace(
                        go.Scatter(
                            x=data.index,
                            y=data['Stoch_D'],
                            mode='lines',
                            name='%D',
                            line=dict(color='red')
                        ),
                        row=row_num, col=1
                    )
                    
                    # Add Stochastic reference lines
                    fig.add_hline(y=80, line_dash="dash", line_color="red", 
                                 annotation_text="Overbought", row=row_num, col=1)
                    fig.add_hline(y=20, line_dash="dash", line_color="green", 
                                 annotation_text="Oversold", row=row_num, col=1)
        
        # Update layout
        fig.update_layout(
            template=self.theme,
            xaxis_rangeslider_visible=False,
            height=200 * num_subplots + 200
        )
        
        return fig

    def create_performance_chart(self, data, benchmark_data=None, title="Performance Analysis"):
      
        if data.empty:
            logger.error("Cannot create chart with empty data")
            return go.Figure()

        fig = go.Figure()

        # Calculate cumulative returns
        if 'Daily_Return' in data.columns:
            cumulative_returns = (1 + data['Daily_Return'] / 100).cumprod()
            fig.add_trace(
                go.Scatter(
                    x=data.index,
                    y=cumulative_returns,
                    mode='lines',
                    name='Stock Performance',
                    line=dict(color=self.colors['bullish'])
                )
            )

        # Add benchmark if provided
        if benchmark_data is not None and 'Daily_Return' in benchmark_data.columns:
            benchmark_cumulative = (1 + benchmark_data['Daily_Return'] / 100).cumprod()
            fig.add_trace(
                go.Scatter(
                    x=benchmark_data.index,
                    y=benchmark_cumulative,
                    mode='lines',
                    name='Benchmark',
                    line=dict(color=self.colors['bearish'])
                )
            )

        fig.update_layout(
            title=title,
            xaxis_title="Date",
            yaxis_title="Cumulative Returns",
            template=self.theme,
            height=400
        )

        return fig

    def create_volume_profile(self, data, title="Volume Profile"):
       
        if data.empty or 'Volume' not in data.columns or 'Close' not in data.columns:
            logger.error("Cannot create volume profile with missing data")
            return go.Figure()

        # Create price bins
        price_min = data['Close'].min()
        price_max = data['Close'].max()
        price_bins = np.linspace(price_min, price_max, 50)

        # Calculate volume for each price level
        volume_profile = []
        for i in range(len(price_bins) - 1):
            mask = (data['Close'] >= price_bins[i]) & (data['Close'] < price_bins[i + 1])
            volume_at_level = data.loc[mask, 'Volume'].sum()
            volume_profile.append(volume_at_level)

        # Create horizontal bar chart
        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=volume_profile,
                y=price_bins[:-1],
                orientation='h',
                name='Volume Profile',
                marker_color=self.colors['volume'],
                opacity=0.7
            )
        )

        fig.update_layout(
            title=title,
            xaxis_title="Volume",
            yaxis_title="Price",
            template=self.theme,
            height=600
        )

        return fig
