"""
Helper Utilities Module - Common utility functions for the stock analysis dashboard
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class DateUtils:
    """
    Utility class for date-related operations
    """
    
    @staticmethod
    def get_date_range_options():
        """
        Get predefined date range options for the dashboard
        
        Returns:
            dict: Dictionary of date range options
        """
        today = datetime.now()
        
        return {
            '1 Week': (today - timedelta(days=7), today),
            '1 Month': (today - timedelta(days=30), today),
            '3 Months': (today - timedelta(days=90), today),
            '6 Months': (today - timedelta(days=180), today),
            '1 Year': (today - timedelta(days=365), today),
            '2 Years': (today - timedelta(days=730), today),
            '5 Years': (today - timedelta(days=1825), today),
        }
    
    @staticmethod
    def format_date_for_display(date):
        """
        Format date for display in the dashboard
        
        Args:
            date (datetime): Date to format
            
        Returns:
            str: Formatted date string
        """
        return date.strftime('%Y-%m-%d')
    
    @staticmethod
    def parse_date_string(date_string):
        """
        Parse date string to datetime object
        
        Args:
            date_string (str): Date string in various formats
            
        Returns:
            datetime: Parsed datetime object
        """
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y-%m-%d %H:%M:%S']
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse date string: {date_string}")

class DataUtils:
    """
    Utility class for data processing operations
    """
    
    @staticmethod
    def calculate_returns(data, column='Close'):
        """
        Calculate various types of returns
        
        Args:
            data (pandas.DataFrame): Stock data
            column (str): Column to calculate returns for
            
        Returns:
            pandas.DataFrame: Data with return columns added
        """
        result = data.copy()
        
        # Daily returns
        result['Daily_Return'] = result[column].pct_change() * 100
        
        # Weekly returns
        result['Weekly_Return'] = result[column].pct_change(periods=5) * 100
        
        # Monthly returns (approximate)
        result['Monthly_Return'] = result[column].pct_change(periods=21) * 100
        
        # Cumulative returns
        result['Cumulative_Return'] = ((result[column] / result[column].iloc[0]) - 1) * 100
        
        return result
    
    @staticmethod
    def calculate_volatility(data, window=21, column='Close'):
        """
        Calculate rolling volatility
        
        Args:
            data (pandas.DataFrame): Stock data
            window (int): Rolling window for volatility calculation
            column (str): Column to calculate volatility for
            
        Returns:
            pandas.Series: Volatility values
        """
        returns = data[column].pct_change()
        volatility = returns.rolling(window=window).std() * np.sqrt(252) * 100  # Annualized
        
        return volatility
    
    @staticmethod
    def calculate_drawdown(data, column='Close'):
        """
        Calculate drawdown from peak
        
        Args:
            data (pandas.DataFrame): Stock data
            column (str): Column to calculate drawdown for
            
        Returns:
            pandas.Series: Drawdown values
        """
        peak = data[column].expanding().max()
        drawdown = ((data[column] - peak) / peak) * 100
        
        return drawdown
    
    @staticmethod
    def resample_data(data, frequency='D'):
        """
        Resample data to different frequency
        
        Args:
            data (pandas.DataFrame): Stock data
            frequency (str): Target frequency ('D', 'W', 'M', etc.)
            
        Returns:
            pandas.DataFrame: Resampled data
        """
        if data.empty:
            return data
        
        # Define aggregation rules
        agg_rules = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }
        
        # Only use rules for columns that exist
        available_rules = {k: v for k, v in agg_rules.items() if k in data.columns}
        
        resampled = data.resample(frequency).agg(available_rules)
        
        return resampled.dropna()

class FileUtils:
    """
    Utility class for file operations
    """
    
    @staticmethod
    def ensure_directory_exists(directory):
        """
        Ensure a directory exists, create if it doesn't
        
        Args:
            directory (str): Directory path
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
    
    @staticmethod
    def save_config(config, filepath):
        """
        Save configuration to JSON file
        
        Args:
            config (dict): Configuration dictionary
            filepath (str): Path to save the config file
        """
        try:
            with open(filepath, 'w') as f:
                json.dump(config, f, indent=2, default=str)
            logger.info(f"Configuration saved to {filepath}")
        except Exception as e:
            logger.error(f"Error saving configuration: {str(e)}")
    
    @staticmethod
    def load_config(filepath, default_config=None):
        """
        Load configuration from JSON file
        
        Args:
            filepath (str): Path to the config file
            default_config (dict): Default configuration if file doesn't exist
            
        Returns:
            dict: Configuration dictionary
        """
        if not os.path.exists(filepath):
            if default_config:
                return default_config
            else:
                return {}
        
        try:
            with open(filepath, 'r') as f:
                config = json.load(f)
            logger.info(f"Configuration loaded from {filepath}")
            return config
        except Exception as e:
            logger.error(f"Error loading configuration: {str(e)}")
            return default_config if default_config else {}
    
    @staticmethod
    def get_file_size(filepath):
        """
        Get file size in human-readable format
        
        Args:
            filepath (str): Path to the file
            
        Returns:
            str: File size in human-readable format
        """
        if not os.path.exists(filepath):
            return "File not found"
        
        size_bytes = os.path.getsize(filepath)
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(np.floor(np.log(size_bytes) / np.log(1024)))
        p = np.power(1024, i)
        s = round(size_bytes / p, 2)
        
        return f"{s} {size_names[i]}"

class FormatUtils:
    """
    Utility class for formatting operations
    """
    
    @staticmethod
    def format_number(number, decimal_places=2):
        """
        Format number with appropriate decimal places and thousand separators
        
        Args:
            number (float): Number to format
            decimal_places (int): Number of decimal places
            
        Returns:
            str: Formatted number string
        """
        if pd.isna(number):
            return "N/A"
        
        return f"{number:,.{decimal_places}f}"
    
    @staticmethod
    def format_percentage(number, decimal_places=2):
        """
        Format number as percentage
        
        Args:
            number (float): Number to format as percentage
            decimal_places (int): Number of decimal places
            
        Returns:
            str: Formatted percentage string
        """
        if pd.isna(number):
            return "N/A"
        
        return f"{number:.{decimal_places}f}%"
    
    @staticmethod
    def format_currency(number, currency_symbol="$", decimal_places=2):
        """
        Format number as currency
        
        Args:
            number (float): Number to format as currency
            currency_symbol (str): Currency symbol
            decimal_places (int): Number of decimal places
            
        Returns:
            str: Formatted currency string
        """
        if pd.isna(number):
            return "N/A"
        
        return f"{currency_symbol}{number:,.{decimal_places}f}"
    
    @staticmethod
    def format_large_number(number):
        """
        Format large numbers with appropriate suffixes (K, M, B, T)
        
        Args:
            number (float): Number to format
            
        Returns:
            str: Formatted number string with suffix
        """
        if pd.isna(number):
            return "N/A"
        
        if abs(number) < 1000:
            return f"{number:.2f}"
        elif abs(number) < 1000000:
            return f"{number/1000:.2f}K"
        elif abs(number) < 1000000000:
            return f"{number/1000000:.2f}M"
        elif abs(number) < 1000000000000:
            return f"{number/1000000000:.2f}B"
        else:
            return f"{number/1000000000000:.2f}T"
