"""
Trading Signals Module - Generates trading signals based on technical indicators
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TradingSignals:
  
    
    @staticmethod
    def moving_average_crossover(data, fast_col, slow_col):
        if fast_col not in data.columns or slow_col not in data.columns:
            logger.error(f"Columns {fast_col} or {slow_col} not found in data")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        # Generate signals
        signals[data[fast_col] > data[slow_col]] = 1  # Buy signal
        signals[data[fast_col] < data[slow_col]] = -1  # Sell signal
        
        # Only consider signal changes
        return signals.diff().fillna(0)
    
    @staticmethod
    def rsi_signals(data, rsi_col='RSI', overbought=70, oversold=30):
       
        if rsi_col not in data.columns:
            logger.error(f"Column {rsi_col} not found in data")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        # Generate signals
        # Buy when RSI crosses above oversold level
        signals[(data[rsi_col] > oversold) & (data[rsi_col].shift() <= oversold)] = 1
        
        # Sell when RSI crosses below overbought level
        signals[(data[rsi_col] < overbought) & (data[rsi_col].shift() >= overbought)] = -1
        
        return signals
    
    @staticmethod
    def bollinger_band_signals(data, close_col='Close', upper_band_col='BB_Upper', lower_band_col='BB_Lower'):
       
        required_cols = [close_col, upper_band_col, lower_band_col]
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Required columns {required_cols} not found in data")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when price crosses below lower band and then back above it
        lower_band_cross_below = (data[close_col].shift() >= data[lower_band_col].shift()) & (data[close_col] < data[lower_band_col])
        lower_band_cross_above = (data[close_col].shift() <= data[lower_band_col].shift()) & (data[close_col] > data[lower_band_col])
        signals[lower_band_cross_above & lower_band_cross_below.shift(1)] = 1
        
        # Sell when price crosses above upper band and then back below it
        upper_band_cross_above = (data[close_col].shift() <= data[upper_band_col].shift()) & (data[close_col] > data[upper_band_col])
        upper_band_cross_below = (data[close_col].shift() >= data[upper_band_col].shift()) & (data[close_col] < data[upper_band_col])
        signals[upper_band_cross_below & upper_band_cross_above.shift(1)] = -1
        
        return signals
    
    @staticmethod
    def macd_signals(data, macd_col='MACD', signal_col='MACD_Signal'):
       
        required_cols = [macd_col, signal_col]
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Required columns {required_cols} not found in data")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when MACD crosses above signal line
        signals[(data[macd_col] > data[signal_col]) & (data[macd_col].shift() <= data[signal_col].shift())] = 1
        
        # Sell when MACD crosses below signal line
        signals[(data[macd_col] < data[signal_col]) & (data[macd_col].shift() >= data[signal_col].shift())] = -1
        
        return signals
    
    @staticmethod
    def stochastic_signals(data, k_col='Stoch_K', d_col='Stoch_D', overbought=80, oversold=20):
        
        required_cols = [k_col, d_col]
        if not all(col in data.columns for col in required_cols):
            logger.error(f"Required columns {required_cols} not found in data")
            return pd.Series(0, index=data.index)
        
        signals = pd.Series(0, index=data.index)
        
        # Buy when %K crosses above %D in oversold region
        signals[(data[k_col] > data[d_col]) & 
                (data[k_col].shift() <= data[d_col].shift()) & 
                (data[k_col] < oversold)] = 1
        
        # Sell when %K crosses below %D in overbought region
        signals[(data[k_col] < data[d_col]) & 
                (data[k_col].shift() >= data[d_col].shift()) & 
                (data[k_col] > overbought)] = -1
        
        return signals
    
    @staticmethod
    def combine_signals(data, signal_columns, weights=None):
       
        if not all(col in data.columns for col in signal_columns):
            logger.error(f"Not all signal columns found in data")
            return pd.Series(0, index=data.index)
        
        if weights is None:
            weights = [1] * len(signal_columns)
        
        if len(weights) != len(signal_columns):
            logger.error(f"Number of weights ({len(weights)}) does not match number of signal columns ({len(signal_columns)})")
            weights = [1] * len(signal_columns)
        
        # Normalize weights
        weights = np.array(weights) / sum(weights)
        
        # Combine signals
        combined = pd.Series(0, index=data.index)
        for col, weight in zip(signal_columns, weights):
            combined += data[col] * weight
        
        # Threshold for final signal
        final_signals = pd.Series(0, index=data.index)
        final_signals[combined > 0.2] = 1
        final_signals[combined < -0.2] = -1
        
        return final_signals
    
    @staticmethod
    def add_all_signals(data):
        
        result = data.copy()

        # Ensure timezone-naive index for all calculations
        if hasattr(result.index, 'tz') and result.index.tz is not None:
            logger.info("Converting timezone-aware index to timezone-naive for signal calculations")
            result.index = result.index.tz_convert('UTC').tz_localize(None)

        # Moving Average Crossover Signals
        if 'SMA_20' in result.columns and 'SMA_50' in result.columns:
            result['Signal_MA_Crossover'] = TradingSignals.moving_average_crossover(
                result, 'SMA_20', 'SMA_50'
            )
        
        # RSI Signals
        if 'RSI' in result.columns:
            result['Signal_RSI'] = TradingSignals.rsi_signals(result)
        
        # Bollinger Band Signals
        if 'BB_Upper' in result.columns and 'BB_Lower' in result.columns:
            result['Signal_BB'] = TradingSignals.bollinger_band_signals(result)
        
        # MACD Signals
        if 'MACD' in result.columns and 'MACD_Signal' in result.columns:
            result['Signal_MACD'] = TradingSignals.macd_signals(result)
        
        # Stochastic Signals
        if 'Stoch_K' in result.columns and 'Stoch_D' in result.columns:
            result['Signal_Stoch'] = TradingSignals.stochastic_signals(result)
        
        # Combine all signals
        signal_columns = [col for col in result.columns if col.startswith('Signal_')]
        if signal_columns:
            result['Signal_Combined'] = TradingSignals.combine_signals(result, signal_columns)
        
        return result
