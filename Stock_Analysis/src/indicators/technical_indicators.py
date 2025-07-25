"""
Technical Indicators Module - Calculates various technical indicators for stock analysis
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class TechnicalIndicators:
  
    @staticmethod
    def simple_moving_average(data, window=20, column='Close'):
       
        if column not in data.columns:
            logger.error(f"Column {column} not found in data")
            return pd.Series()

        # Ensure the column is numeric
        try:
            numeric_data = pd.to_numeric(data[column], errors='coerce')
            return numeric_data.rolling(window=window).mean()
        except Exception as e:
            logger.error(f"Error calculating SMA for {column}: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def exponential_moving_average(data, window=20, column='Close'):
        
        if column not in data.columns:
            logger.error(f"Column {column} not found in data")
            return pd.Series()

        # Ensure the column is numeric
        try:
            numeric_data = pd.to_numeric(data[column], errors='coerce')
            return numeric_data.ewm(span=window).mean()
        except Exception as e:
            logger.error(f"Error calculating EMA for {column}: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def relative_strength_index(data, window=14, column='Close'):
       
        if column not in data.columns:
            logger.error(f"Column {column} not found in data")
            return pd.Series()

        try:
            # Ensure the column is numeric
            numeric_data = pd.to_numeric(data[column], errors='coerce')

            delta = numeric_data.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

            # Avoid division by zero
            rs = gain / loss.replace(0, np.nan)
            rsi = 100 - (100 / (1 + rs))

            return rsi
        except Exception as e:
            logger.error(f"Error calculating RSI for {column}: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def bollinger_bands(data, window=20, num_std=2, column='Close'):
       
        if column not in data.columns:
            logger.error(f"Column {column} not found in data")
            return pd.Series(), pd.Series(), pd.Series()

        try:
            # Ensure the column is numeric
            numeric_data = pd.to_numeric(data[column], errors='coerce')

            middle_band = numeric_data.rolling(window=window).mean()
            std = numeric_data.rolling(window=window).std()

            upper_band = middle_band + (std * num_std)
            lower_band = middle_band - (std * num_std)

            return upper_band, middle_band, lower_band
        except Exception as e:
            logger.error(f"Error calculating Bollinger Bands for {column}: {str(e)}")
            return pd.Series(), pd.Series(), pd.Series()
    
    @staticmethod
    def macd(data, fast_period=12, slow_period=26, signal_period=9, column='Close'):
       
        if column not in data.columns:
            logger.error(f"Column {column} not found in data")
            return pd.Series(), pd.Series(), pd.Series()

        try:
            # Ensure the column is numeric
            numeric_data = pd.to_numeric(data[column], errors='coerce')

            ema_fast = numeric_data.ewm(span=fast_period).mean()
            ema_slow = numeric_data.ewm(span=slow_period).mean()

            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal_period).mean()
            histogram = macd_line - signal_line

            return macd_line, signal_line, histogram
        except Exception as e:
            logger.error(f"Error calculating MACD for {column}: {str(e)}")
            return pd.Series(), pd.Series(), pd.Series()
    
    @staticmethod
    def stochastic_oscillator(data, k_period=14, d_period=3):
       
        required_columns = ['High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Required columns {required_columns} not found in data")
            return pd.Series(), pd.Series()

        try:
            # Ensure columns are numeric
            high = pd.to_numeric(data['High'], errors='coerce')
            low = pd.to_numeric(data['Low'], errors='coerce')
            close = pd.to_numeric(data['Close'], errors='coerce')

            lowest_low = low.rolling(window=k_period).min()
            highest_high = high.rolling(window=k_period).max()

            # Avoid division by zero
            denominator = highest_high - lowest_low
            denominator = denominator.replace(0, np.nan)

            percent_k = 100 * ((close - lowest_low) / denominator)
            percent_d = percent_k.rolling(window=d_period).mean()

            return percent_k, percent_d
        except Exception as e:
            logger.error(f"Error calculating Stochastic Oscillator: {str(e)}")
            return pd.Series(), pd.Series()
    
    @staticmethod
    def williams_percent_r(data, window=14):
     
        required_columns = ['High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Required columns {required_columns} not found in data")
            return pd.Series()

        try:
            # Ensure columns are numeric
            high = pd.to_numeric(data['High'], errors='coerce')
            low = pd.to_numeric(data['Low'], errors='coerce')
            close = pd.to_numeric(data['Close'], errors='coerce')

            highest_high = high.rolling(window=window).max()
            lowest_low = low.rolling(window=window).min()

            # Avoid division by zero
            denominator = highest_high - lowest_low
            denominator = denominator.replace(0, np.nan)

            williams_r = -100 * ((highest_high - close) / denominator)

            return williams_r
        except Exception as e:
            logger.error(f"Error calculating Williams %R: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def average_true_range(data, window=14):

        required_columns = ['High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Required columns {required_columns} not found in data")
            return pd.Series()

        try:
            # Ensure columns are numeric
            high = pd.to_numeric(data['High'], errors='coerce')
            low = pd.to_numeric(data['Low'], errors='coerce')
            close = pd.to_numeric(data['Close'], errors='coerce')

            high_low = high - low
            high_close_prev = np.abs(high - close.shift())
            low_close_prev = np.abs(low - close.shift())

            true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            atr = true_range.rolling(window=window).mean()

            return atr
        except Exception as e:
            logger.error(f"Error calculating ATR: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def commodity_channel_index(data, window=20):
       
        required_columns = ['High', 'Low', 'Close']
        if not all(col in data.columns for col in required_columns):
            logger.error(f"Required columns {required_columns} not found in data")
            return pd.Series()

        try:
            # Ensure columns are numeric
            high = pd.to_numeric(data['High'], errors='coerce')
            low = pd.to_numeric(data['Low'], errors='coerce')
            close = pd.to_numeric(data['Close'], errors='coerce')

            typical_price = (high + low + close) / 3
            sma_tp = typical_price.rolling(window=window).mean()
            mean_deviation = typical_price.rolling(window=window).apply(
                lambda x: np.abs(x - x.mean()).mean()
            )

            # Avoid division by zero
            denominator = 0.015 * mean_deviation
            denominator = denominator.replace(0, np.nan)

            cci = (typical_price - sma_tp) / denominator

            return cci
        except Exception as e:
            logger.error(f"Error calculating CCI: {str(e)}")
            return pd.Series()
    
    @staticmethod
    def add_all_indicators(data, sma_windows=[20, 50], ema_windows=[12, 26], rsi_window=14):
        
        result = data.copy()

        # Ensure timezone-naive index for all calculations
        if hasattr(result.index, 'tz') and result.index.tz is not None:
            logger.info("Converting timezone-aware index to timezone-naive for indicator calculations")
            result.index = result.index.tz_convert('UTC').tz_localize(None)

        # Simple Moving Averages
        for window in sma_windows:
            result[f'SMA_{window}'] = TechnicalIndicators.simple_moving_average(data, window)
        
        # Exponential Moving Averages
        for window in ema_windows:
            result[f'EMA_{window}'] = TechnicalIndicators.exponential_moving_average(data, window)
        
        # RSI
        result['RSI'] = TechnicalIndicators.relative_strength_index(data, rsi_window)
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(data)
        result['BB_Upper'] = bb_upper
        result['BB_Middle'] = bb_middle
        result['BB_Lower'] = bb_lower
        
        # MACD
        macd_line, signal_line, histogram = TechnicalIndicators.macd(data)
        result['MACD'] = macd_line
        result['MACD_Signal'] = signal_line
        result['MACD_Histogram'] = histogram
        
        # Stochastic Oscillator
        percent_k, percent_d = TechnicalIndicators.stochastic_oscillator(data)
        result['Stoch_K'] = percent_k
        result['Stoch_D'] = percent_d
        
        # Williams %R
        result['Williams_R'] = TechnicalIndicators.williams_percent_r(data)
        
        # ATR
        result['ATR'] = TechnicalIndicators.average_true_range(data)
        
        # CCI
        result['CCI'] = TechnicalIndicators.commodity_channel_index(data)
        
        return result
