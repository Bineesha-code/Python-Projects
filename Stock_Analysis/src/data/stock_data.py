"""
Stock Data Module - Handles fetching and processing of stock market data
"""

import os
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StockData:
    """
    Class for fetching and processing stock market data using yfinance
    """
    
    def __init__(self, cache_dir='data'):
        """
        Initialize the StockData class
        
        Args:
            cache_dir (str): Directory to cache downloaded data
        """
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
            
        logger.info(f"StockData initialized with cache directory: {cache_dir}")
    
    def get_stock_data(self, ticker, start_date=None, end_date=None, period=None, interval='1d', use_cache=True):
        """
        Fetch stock data for a given ticker and time range
        
        Args:
            ticker (str): Stock ticker symbol (e.g., 'AAPL', 'MSFT')
            start_date (str): Start date in 'YYYY-MM-DD' format
            end_date (str): End date in 'YYYY-MM-DD' format
            period (str): Period to fetch (e.g., '1d', '5d', '1mo', '3mo', '1y', '5y', 'max')
            interval (str): Data interval (e.g., '1d', '1wk', '1mo')
            use_cache (bool): Whether to use cached data if available
            
        Returns:
            pandas.DataFrame: Stock data with columns Open, High, Low, Close, Volume
        """
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        if not start_date and not period:
            # Default to 1 year if neither start_date nor period is provided
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Create cache filename
        cache_filename = f"{ticker}_{start_date}_{end_date}_{interval}.csv" if start_date else f"{ticker}_{period}_{interval}.csv"
        cache_path = os.path.join(self.cache_dir, cache_filename)
        
        # Check if cached data exists and is recent
        if use_cache and os.path.exists(cache_path):
            cache_modified_time = os.path.getmtime(cache_path)
            cache_age = datetime.now().timestamp() - cache_modified_time
            
            # Use cache if it's less than 24 hours old
            if cache_age < 86400:  # 24 hours in seconds
                logger.info(f"Loading cached data for {ticker} from {cache_path}")
                return pd.read_csv(cache_path, index_col=0, parse_dates=True)
        
        # Fetch data from yfinance with multiple fallback methods
        data = pd.DataFrame()

        # Method 1: Try Ticker object first (most reliable)
        try:
            logger.info(f"Fetching data for {ticker} using Ticker object method")
            ticker_obj = yf.Ticker(ticker)

            if period:
                data = ticker_obj.history(period=period, interval=interval)
            else:
                data = ticker_obj.history(start=start_date, end=end_date, interval=interval)

            if not data.empty:
                logger.info(f"✅ Ticker object method successful: {len(data)} rows")
            else:
                logger.warning("Ticker object method returned empty data")

        except Exception as e:
            logger.warning(f"Ticker object method failed: {str(e)}")

        # Method 2: Try download function if Ticker object failed
        if data.empty:
            try:
                logger.info(f"Fetching data for {ticker} using download function")

                if period:
                    data = yf.download(
                        ticker,
                        period=period,
                        interval=interval,
                        auto_adjust=True,
                        prepost=False,
                        threads=False,
                        group_by=None,
                        progress=False
                    )
                else:
                    data = yf.download(
                        ticker,
                        start=start_date,
                        end=end_date,
                        interval=interval,
                        auto_adjust=True,
                        prepost=False,
                        threads=False,
                        group_by=None,
                        progress=False
                    )

                if not data.empty:
                    logger.info(f"✅ Download function successful: {len(data)} rows")
                else:
                    logger.warning("Download function returned empty data")

            except Exception as e:
                logger.warning(f"Download function failed: {str(e)}")

        # Method 3: Try minimal parameters as last resort
        if data.empty:
            try:
                logger.info(f"Fetching data for {ticker} using minimal parameters")

                if period:
                    data = yf.download(ticker, period=period, progress=False)
                else:
                    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

                if not data.empty:
                    logger.info(f"✅ Minimal parameters successful: {len(data)} rows")

            except Exception as e:
                logger.warning(f"Minimal parameters failed: {str(e)}")

        # If all methods failed, return empty DataFrame
        if data.empty:
            logger.error(f"All fetch methods failed for {ticker}")
            return pd.DataFrame()

        # Now clean and validate the data
        try:
            # Step 1: Handle multi-level columns
            if isinstance(data.columns, pd.MultiIndex):
                logger.info("Handling multi-level columns")
                # Flatten columns - take the first level or combine levels
                new_columns = []
                for col in data.columns:
                    if isinstance(col, tuple):
                        # Take the first non-empty level
                        if col[0] and col[0] != '':
                            new_columns.append(col[0])
                        elif len(col) > 1 and col[1] and col[1] != '':
                            new_columns.append(col[1])
                        else:
                            new_columns.append('_'.join(str(c) for c in col if c))
                    else:
                        new_columns.append(col)

                data.columns = new_columns
                logger.info(f"Flattened columns to: {list(data.columns)}")

            # Step 2: Clean column names
            data.columns = [str(col).strip() for col in data.columns]

            # Step 3: Map alternative column names
            column_mapping = {
                'Adj Close': 'Close',
                'close': 'Close',
                'open': 'Open',
                'high': 'High',
                'low': 'Low',
                'volume': 'Volume',
                'Close*': 'Close',
                'Open*': 'Open',
                'High*': 'High',
                'Low*': 'Low',
                'Volume*': 'Volume'
            }

            for old_name, new_name in column_mapping.items():
                if old_name in data.columns:
                    data[new_name] = data[old_name]
                    if old_name != new_name:
                        data.drop(columns=[old_name], inplace=True)
                    logger.info(f"Mapped {old_name} to {new_name}")

            # Step 4: Ensure we have required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in data.columns]

            if missing_columns:
                logger.error(f"Missing required columns: {missing_columns}")
                logger.info(f"Available columns: {list(data.columns)}")
                return pd.DataFrame()

            # Step 5: Clean the index (most critical part)
            logger.info(f"Cleaning index. Current type: {type(data.index)}")

            # Reset index to work with it as a column
            data_reset = data.reset_index()

            # Find the date column
            date_column = None
            for col in data_reset.columns:
                if col.lower() in ['date', 'datetime', 'timestamp', 'index']:
                    date_column = col
                    break

            if date_column is None:
                # If no explicit date column, assume first column is date
                date_column = data_reset.columns[0]

            logger.info(f"Using '{date_column}' as date column")

            # Clean the date column
            date_series = data_reset[date_column]

            # Filter out invalid entries
            valid_rows = []
            for i, date_val in enumerate(date_series):
                try:
                    # Skip obviously invalid values
                    if pd.isna(date_val):
                        continue

                    date_str = str(date_val)
                    if 'Ticker' in date_str or len(date_str.strip()) < 8:
                        logger.warning(f"Skipping invalid date value: {date_val}")
                        continue

                    # Try to parse as datetime
                    parsed_date = pd.to_datetime(date_val)
                    if pd.notna(parsed_date):
                        valid_rows.append(i)

                except Exception as e:
                    logger.warning(f"Skipping unparseable date: {date_val} - {str(e)}")
                    continue

            if not valid_rows:
                logger.error("No valid dates found in data")
                return pd.DataFrame()

            # Keep only valid rows
            data_clean = data_reset.iloc[valid_rows].copy()

            # Set the cleaned dates as index
            try:
                clean_dates = pd.to_datetime(data_clean[date_column])

                # Remove timezone information to avoid conversion issues
                if clean_dates.dt.tz is not None:
                    clean_dates = clean_dates.dt.tz_convert('UTC').dt.tz_localize(None)
                    logger.info("Converted timezone-aware dates to UTC and removed timezone info")

                data_clean = data_clean.drop(columns=[date_column])
                data_clean.index = clean_dates
                data_clean.index.name = 'Date'

                logger.info(f"✅ Successfully cleaned data: {len(data_clean)} rows")
                data = data_clean

            except Exception as e:
                logger.error(f"Failed to set cleaned dates as index: {str(e)}")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Data cleaning failed: {str(e)}")
            return pd.DataFrame()

        # Final validation
        if data.empty:
            logger.warning("Data is empty after cleaning")
            return pd.DataFrame()

        # Save to cache
        try:
            data.to_csv(cache_path)
            logger.info(f"Data saved to cache: {cache_path}")
        except Exception as e:
            logger.warning(f"Could not save to cache: {str(e)}")

        return data
    
    def get_stock_info(self, ticker):
        """
        Get company information for a given ticker
        
        Args:
            ticker (str): Stock ticker symbol
            
        Returns:
            dict: Company information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract relevant information
            relevant_info = {
                'name': info.get('shortName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'website': info.get('website', 'N/A'),
                'description': info.get('longBusinessSummary', 'N/A')
            }
            
            return relevant_info
            
        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {str(e)}")
            return {}
    
    def process_data(self, data):
        """
        Process and clean the stock data
        
        Args:
            data (pandas.DataFrame): Raw stock data
            
        Returns:
            pandas.DataFrame: Processed stock data
        """
        if data.empty:
            return data
        
        # Make a copy to avoid modifying the original data
        processed_data = data.copy()

        # Handle timezone-aware index first
        if hasattr(processed_data.index, 'tz') and processed_data.index.tz is not None:
            logger.info("Converting timezone-aware index to timezone-naive")
            processed_data.index = processed_data.index.tz_convert('UTC').tz_localize(None)

        # Ensure numeric columns are properly typed
        numeric_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in numeric_columns:
            if col in processed_data.columns:
                processed_data[col] = pd.to_numeric(processed_data[col], errors='coerce')

        # Handle missing values
        processed_data = processed_data.ffill()

        # Add date-related columns (only if index is datetime)
        try:
            if hasattr(processed_data.index, 'year'):
                processed_data['Year'] = processed_data.index.year
                processed_data['Month'] = processed_data.index.month
                processed_data['Day'] = processed_data.index.day
                processed_data['Weekday'] = processed_data.index.day_name()
            else:
                # Convert index to datetime if it's not already
                processed_data.index = pd.to_datetime(processed_data.index)
                processed_data['Year'] = processed_data.index.year
                processed_data['Month'] = processed_data.index.month
                processed_data['Day'] = processed_data.index.day
                processed_data['Weekday'] = processed_data.index.day_name()
        except Exception as e:
            logger.warning(f"Could not add date-related columns: {str(e)}")
            # Continue without date columns if there's an issue
        
        # Calculate daily returns
        processed_data['Daily_Return'] = processed_data['Close'].pct_change() * 100
        
        return processed_data
    
    def export_to_csv(self, data, filename):
        """
        Export data to CSV file
        
        Args:
            data (pandas.DataFrame): Data to export
            filename (str): Output filename
            
        Returns:
            str: Path to the exported file
        """
        if data.empty:
            logger.warning("Cannot export empty data")
            return None
        
        output_path = os.path.join(self.cache_dir, filename)
        data.to_csv(output_path)
        logger.info(f"Data exported to {output_path}")
        
        return output_path
