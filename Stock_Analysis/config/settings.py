"""
Configuration settings for the Stock Analysis Dashboard
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Data settings
DATA_CONFIG = {
    'cache_dir': BASE_DIR / 'data',
    'cache_expiry_hours': 24,
    'default_period': '1y',
    'default_interval': '1d',
    'max_data_points': 10000
}

# Chart settings
CHART_CONFIG = {
    'theme': 'plotly_white',
    'height': 600,
    'colors': {
        'bullish': '#00CC96',
        'bearish': '#FF6692',
        'volume': '#636EFA',
        'sma': '#FFA15A',
        'ema': '#19D3F3',
        'rsi': '#B6E880',
        'macd': '#FF97FF',
        'signal': '#FECB52'
    }
}

# Technical indicators settings
INDICATORS_CONFIG = {
    'sma_periods': [10, 20, 50, 100, 200],
    'ema_periods': [12, 26, 50],
    'rsi_period': 14,
    'rsi_overbought': 70,
    'rsi_oversold': 30,
    'macd_fast': 12,
    'macd_slow': 26,
    'macd_signal': 9,
    'bollinger_period': 20,
    'bollinger_std': 2,
    'stochastic_k': 14,
    'stochastic_d': 3,
    'atr_period': 14
}

# Trading signals settings
SIGNALS_CONFIG = {
    'signal_threshold': 0.2,
    'combine_signals': True,
    'signal_weights': {
        'ma_crossover': 0.3,
        'rsi': 0.2,
        'macd': 0.25,
        'bollinger': 0.15,
        'stochastic': 0.1
    }
}

# Dashboard settings
DASHBOARD_CONFIG = {
    'page_title': 'Stock Analysis Dashboard',
    'page_icon': '📈',
    'layout': 'wide',
    'sidebar_state': 'expanded',
    'default_tickers': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX'],
    'max_rows_display': 1000,
    'pagination_sizes': [10, 25, 50, 100]
}

# Export settings
EXPORT_CONFIG = {
    'formats': ['csv', 'json', 'excel'],
    'include_indicators': True,
    'include_signals': True,
    'date_format': '%Y-%m-%d',
    'float_precision': 4
}

# Logging settings
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'log_file': BASE_DIR / 'logs' / 'dashboard.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5
}

# API settings (for future enhancements)
API_CONFIG = {
    'rate_limit': 100,  # requests per minute
    'timeout': 30,  # seconds
    'retry_attempts': 3,
    'retry_delay': 1  # seconds
}

# Performance settings
PERFORMANCE_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 3600,  # seconds
    'max_memory_usage': 1024 * 1024 * 1024,  # 1GB
    'enable_compression': True
}

# Security settings
SECURITY_CONFIG = {
    'allowed_tickers_pattern': r'^[A-Z0-9.-]{1,10}$',
    'max_date_range_days': 3650,  # 10 years
    'sanitize_inputs': True
}

def get_config(section=None):
    """
    Get configuration settings
    
    Args:
        section (str): Configuration section name
        
    Returns:
        dict: Configuration dictionary
    """
    configs = {
        'data': DATA_CONFIG,
        'chart': CHART_CONFIG,
        'indicators': INDICATORS_CONFIG,
        'signals': SIGNALS_CONFIG,
        'dashboard': DASHBOARD_CONFIG,
        'export': EXPORT_CONFIG,
        'logging': LOGGING_CONFIG,
        'api': API_CONFIG,
        'performance': PERFORMANCE_CONFIG,
        'security': SECURITY_CONFIG
    }
    
    if section:
        return configs.get(section, {})
    
    return configs

def update_config(section, key, value):
    """
    Update configuration setting
    
    Args:
        section (str): Configuration section name
        key (str): Configuration key
        value: New value
    """
    configs = get_config()
    
    if section in configs and key in configs[section]:
        configs[section][key] = value
        return True
    
    return False

# Environment-specific overrides
if os.getenv('ENVIRONMENT') == 'development':
    LOGGING_CONFIG['level'] = 'DEBUG'
    PERFORMANCE_CONFIG['enable_caching'] = False

elif os.getenv('ENVIRONMENT') == 'production':
    LOGGING_CONFIG['level'] = 'WARNING'
    PERFORMANCE_CONFIG['enable_caching'] = True
    SECURITY_CONFIG['sanitize_inputs'] = True
