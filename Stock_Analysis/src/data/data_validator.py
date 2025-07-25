"""
Data Validation Module - Validates stock data and ticker symbols
"""

import re
import pandas as pd
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DataValidator:
    """
    Class for validating stock data and ticker symbols
    """
    
    @staticmethod
    def validate_ticker(ticker):
        """
        Validate ticker symbol format
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not ticker or not isinstance(ticker, str):
            return False
        
        # Remove whitespace and convert to uppercase
        ticker = ticker.strip().upper()
        
        # Basic validation: alphanumeric characters, dots, and hyphens
        pattern = r'^[A-Z0-9.-]+$'
        
        if not re.match(pattern, ticker):
            return False
        
        # Length validation (most tickers are 1-5 characters)
        if len(ticker) < 1 or len(ticker) > 10:
            return False
        
        return True
    
    @staticmethod
    def validate_date(date_string):
        """
        Validate date string format
        
        Args:
            date_string (str): Date in 'YYYY-MM-DD' format
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not date_string:
            return False
        
        try:
            datetime.strptime(date_string, '%Y-%m-%d')
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_date_range(start_date, end_date):
        """
        Validate date range
        
        Args:
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not DataValidator.validate_date(start_date):
            return False, "Invalid start date format. Use YYYY-MM-DD"
        
        if not DataValidator.validate_date(end_date):
            return False, "Invalid end date format. Use YYYY-MM-DD"
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start >= end:
            return False, "Start date must be before end date"
        
        # Check if date range is too far in the future
        if start > datetime.now():
            return False, "Start date cannot be in the future"
        
        # Check if date range is reasonable (not too old)
        if start < datetime(1970, 1, 1):
            return False, "Start date is too old"
        
        return True, "Valid date range"
    
    @staticmethod
    def validate_period(period):
        """
        Validate period string for yfinance
        
        Args:
            period (str): Period string (e.g., '1d', '5d', '1mo', '3mo', '1y', '5y', 'max')
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
        return period in valid_periods
    
    @staticmethod
    def validate_interval(interval):
        """
        Validate interval string for yfinance
        
        Args:
            interval (str): Interval string (e.g., '1m', '5m', '1h', '1d', '1wk', '1mo')
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
        return interval in valid_intervals
    
    @staticmethod
    def validate_stock_data(data):
        """
        Validate stock data DataFrame
        
        Args:
            data (pandas.DataFrame): Stock data
            
        Returns:
            tuple: (is_valid, error_message)
        """
        if not isinstance(data, pd.DataFrame):
            return False, "Data must be a pandas DataFrame"
        
        if data.empty:
            return False, "Data is empty"
        
        # Check for required columns
        required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            return False, f"Missing required columns: {missing_columns}"
        
        # Check for negative values in price columns
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if (data[col] < 0).any():
                return False, f"Negative values found in {col} column"
        
        # Check for logical consistency (High >= Low, etc.)
        if (data['High'] < data['Low']).any():
            return False, "High price is less than Low price in some records"
        
        if (data['High'] < data['Open']).any() or (data['High'] < data['Close']).any():
            return False, "High price is less than Open or Close price in some records"
        
        if (data['Low'] > data['Open']).any() or (data['Low'] > data['Close']).any():
            return False, "Low price is greater than Open or Close price in some records"
        
        # Check for reasonable volume values
        if (data['Volume'] < 0).any():
            return False, "Negative volume values found"
        
        return True, "Data is valid"
    
    @staticmethod
    def clean_ticker(ticker):
        """
        Clean and format ticker symbol
        
        Args:
            ticker (str): Raw ticker symbol
            
        Returns:
            str: Cleaned ticker symbol
        """
        if not ticker:
            return ""
        
        # Remove whitespace and convert to uppercase
        cleaned = ticker.strip().upper()
        
        # Remove any invalid characters
        cleaned = re.sub(r'[^A-Z0-9.-]', '', cleaned)
        
        return cleaned

    @staticmethod
    def suggest_alternative_tickers(ticker):
        """
        Suggest alternative ticker symbols if the original fails

        Args:
            ticker (str): Original ticker symbol

        Returns:
            list: List of suggested alternative tickers
        """
        suggestions = []

        # Common ticker patterns and alternatives
        common_alternatives = {
            'GOOGL': ['GOOG', 'ALPHABET'],
            'GOOG': ['GOOGL', 'ALPHABET'],
            'META': ['FB'],
            'FB': ['META'],
            'TSLA': ['TESLA'],
            'BRK.A': ['BRK-A', 'BERKSHIRE'],
            'BRK.B': ['BRK-B', 'BERKSHIRE'],
        }

        # Add direct alternatives
        if ticker.upper() in common_alternatives:
            suggestions.extend(common_alternatives[ticker.upper()])

        # Add exchange suffixes for international stocks
        if '.' not in ticker and '-' not in ticker:
            suggestions.extend([
                f"{ticker}.L",    # London Stock Exchange
                f"{ticker}.TO",   # Toronto Stock Exchange
                f"{ticker}.AX",   # Australian Securities Exchange
                f"{ticker}.HK",   # Hong Kong Stock Exchange
            ])

        # Popular fallback tickers
        popular_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']
        if ticker.upper() not in popular_tickers:
            suggestions.extend(popular_tickers[:5])  # Add top 5 popular tickers

        return list(set(suggestions))  # Remove duplicates

    @staticmethod
    def is_likely_valid_ticker(ticker):
        """
        Check if a ticker is likely to be valid based on common patterns

        Args:
            ticker (str): Ticker symbol to check

        Returns:
            tuple: (is_likely_valid, confidence_score, reason)
        """
        if not ticker or not isinstance(ticker, str):
            return False, 0.0, "Empty or invalid ticker"

        ticker = ticker.strip().upper()

        # Length check
        if len(ticker) < 1 or len(ticker) > 10:
            return False, 0.1, "Ticker length outside normal range (1-10 characters)"

        # Character check
        if not re.match(r'^[A-Z0-9.-]+$', ticker):
            return False, 0.2, "Contains invalid characters"

        # Common patterns
        confidence = 0.5  # Base confidence
        reasons = []

        # Length-based confidence
        if 1 <= len(ticker) <= 5:
            confidence += 0.3
            reasons.append("Standard length")
        elif len(ticker) <= 8:
            confidence += 0.1
            reasons.append("Acceptable length")

        # Pattern-based confidence
        if ticker.isalpha():
            confidence += 0.2
            reasons.append("All letters")
        elif '.' in ticker or '-' in ticker:
            confidence += 0.1
            reasons.append("Contains exchange separator")

        # Known good patterns
        if ticker in ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX']:
            confidence = 0.95
            reasons.append("Popular ticker")

        # Known problematic patterns
        if ticker.startswith('TEST') or ticker in ['INVALID', 'FAKE', 'DUMMY']:
            confidence = 0.1
            reasons.append("Test/dummy ticker")

        is_likely_valid = confidence > 0.6
        reason = "; ".join(reasons) if reasons else "Basic validation"

        return is_likely_valid, confidence, reason
