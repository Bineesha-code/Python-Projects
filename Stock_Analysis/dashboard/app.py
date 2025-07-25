"""
Stock Analysis Dashboard - Main Streamlit Application
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime, timedelta

try:
    import plotly.express as px
except ImportError:
    px = None

# Add src directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data.stock_data import StockData
from data.data_validator import DataValidator
from indicators.technical_indicators import TechnicalIndicators
from indicators.trading_signals import TradingSignals
from visualization.charts import StockCharts
from utils.helpers import DateUtils, DataUtils, FormatUtils

# Page configuration
st.set_page_config(
    page_title="Stock Analysis Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .sidebar-header {
        font-size: 1.5rem;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'stock_info' not in st.session_state:
    st.session_state.stock_info = None

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">📈 Smart Stock Analyser</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown('<h2 class="sidebar-header">📊 Configuration</h2>', unsafe_allow_html=True)
        
        # Stock symbol input
        ticker = st.text_input(
            "Stock Symbol",
            value="AAPL",
            help="Enter a stock ticker symbol (e.g., AAPL, MSFT, GOOGL)"
        ).upper()
        
        # Date range selection
        st.subheader("📅 Date Range")
        date_option = st.selectbox(
            "Select Date Range",
            ["Custom", "1 Week", "1 Month", "3 Months", "6 Months", "1 Year", "2 Years", "5 Years"]
        )
        
        if date_option == "Custom":
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=datetime.now() - timedelta(days=365)
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=datetime.now()
                )
        else:
            date_ranges = DateUtils.get_date_range_options()
            if date_option in date_ranges:
                start_date, end_date = date_ranges[date_option]
                start_date = start_date.date()
                end_date = end_date.date()
        
        # Technical indicators selection
        st.subheader("📊 Technical Indicators")
        st.session_state.show_sma = st.checkbox("Simple Moving Average (SMA)", value=True)
        if st.session_state.show_sma:
            st.session_state.sma_periods = st.multiselect(
                "SMA Periods",
                [10, 20, 50, 100, 200],
                default=[20, 50]
            )

        st.session_state.show_ema = st.checkbox("Exponential Moving Average (EMA)")
        if st.session_state.show_ema:
            st.session_state.ema_periods = st.multiselect(
                "EMA Periods",
                [12, 26, 50],
                default=[12, 26]
            )

        st.session_state.show_rsi = st.checkbox("RSI", value=True)
        st.session_state.show_macd = st.checkbox("MACD", value=True)
        st.session_state.show_bollinger = st.checkbox("Bollinger Bands")
        st.session_state.show_stochastic = st.checkbox("Stochastic Oscillator")
        
        # Chart options
        st.subheader("📈 Chart Options")
        st.session_state.chart_type = st.selectbox(
            "Chart Type",
            ["Candlestick", "Line", "OHLC"]
        )
        st.session_state.show_volume = st.checkbox("Show Volume", value=True)
        
        # Fetch data button
        if st.button("📥 Fetch Data", type="primary"):
            fetch_stock_data(ticker, start_date, end_date)
    
    # Main content area
    if st.session_state.stock_data is not None and not st.session_state.stock_data.empty:
        display_dashboard()
    else:
        display_welcome_message()

def fetch_stock_data(ticker, start_date, end_date):
    """Fetch and process stock data"""
    
    # Validate inputs
    if not DataValidator.validate_ticker(ticker):
        st.error("❌ Invalid ticker symbol. Please enter a valid stock symbol.")

        # Provide suggestions
        suggestions = DataValidator.suggest_alternative_tickers(ticker)
        if suggestions:
            st.info(f"💡 **Suggested alternatives:** {', '.join(suggestions[:5])}")
        return

    # Check if ticker is likely valid
    is_likely_valid, confidence, reason = DataValidator.is_likely_valid_ticker(ticker)
    if not is_likely_valid:
        st.warning(f"⚠️ Ticker '{ticker}' might not be valid (confidence: {confidence:.1%}): {reason}")
        suggestions = DataValidator.suggest_alternative_tickers(ticker)
        if suggestions:
            st.info(f"💡 **Try these instead:** {', '.join(suggestions[:3])}")
    
    if not DataValidator.validate_date_range(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))[0]:
        st.error("❌ Invalid date range. Please check your dates.")
        return
    
    # Show loading spinner
    with st.spinner(f"Fetching data for {ticker}..."):
        try:
            # Initialize data fetcher
            stock_data_fetcher = StockData()
            
            # Fetch stock data with multiple attempts
            data = pd.DataFrame()

            # Try with date range first
            try:
                data = stock_data_fetcher.get_stock_data(
                    ticker=ticker,
                    start_date=start_date.strftime('%Y-%m-%d'),
                    end_date=end_date.strftime('%Y-%m-%d')
                )
            except Exception as e:
                st.warning(f"⚠️ Date range fetch failed: {str(e)}")

            # If date range failed, try with period
            if data.empty:
                try:
                    # Calculate approximate period
                    days_diff = (end_date - start_date).days
                    if days_diff <= 7:
                        period = '1wk'
                    elif days_diff <= 30:
                        period = '1mo'
                    elif days_diff <= 90:
                        period = '3mo'
                    elif days_diff <= 365:
                        period = '1y'
                    else:
                        period = '2y'

                    st.info(f"🔄 Trying alternative fetch with period: {period}")
                    data = stock_data_fetcher.get_stock_data(ticker=ticker, period=period)

                except Exception as e:
                    st.warning(f"⚠️ Period fetch also failed: {str(e)}")

            # Final check
            if data.empty:
                st.error(f"❌ No data found for {ticker}. Please check the ticker symbol.")
                return
            
            # Fetch company info
            info = stock_data_fetcher.get_stock_info(ticker)
            
            # Ensure data index is datetime and timezone-naive
            if not isinstance(data.index, pd.DatetimeIndex):
                data.index = pd.to_datetime(data.index)

            # Handle timezone-aware index
            if hasattr(data.index, 'tz') and data.index.tz is not None:
                data.index = data.index.tz_convert('UTC').tz_localize(None)

            # Process data
            processed_data = stock_data_fetcher.process_data(data)

            # Add technical indicators
            processed_data = TechnicalIndicators.add_all_indicators(processed_data)

            # Add trading signals
            processed_data = TradingSignals.add_all_signals(processed_data)
            
            # Store in session state
            st.session_state.stock_data = data
            st.session_state.processed_data = processed_data
            st.session_state.stock_info = info
            st.session_state.ticker = ticker
            
            st.success(f"✅ Successfully fetched data for {ticker}")
            
        except Exception as e:
            error_msg = str(e)
            st.error(f"❌ Error fetching data: {error_msg}")

            # Provide specific guidance based on error type
            if "Tz-aware datetime" in error_msg:
                st.info("💡 **Timezone Error Detected:**")
                st.info("• This is a timezone conversion issue")
                st.info("• Try clearing the cache and fetching again")
                st.info("• If the error persists, try a different date range")

                # Offer to clear cache
                if st.button("🗑️ Clear Cache and Retry"):
                    import glob
                    cache_files = glob.glob("data/*.csv")
                    for file in cache_files:
                        try:
                            os.remove(file)
                        except:
                            pass
                    st.success("Cache cleared! Please try fetching data again.")
                    st.rerun()

            elif "Unknown datetime string format" in error_msg:
                st.info("💡 **Troubleshooting Tips:**")
                st.info("• This ticker might not be available on Yahoo Finance")
                st.info("• Try a different ticker symbol (e.g., AAPL, MSFT, GOOGL)")
                st.info("• Check if the ticker symbol is correct")
                st.info("• Some international tickers may need exchange suffixes (e.g., TSLA.L for London)")
            elif "No data found" in error_msg:
                st.info("💡 **Troubleshooting Tips:**")
                st.info("• Check if the ticker symbol is correct")
                st.info("• Try a different date range")
                st.info("• Some stocks may not have data for the selected period")
            elif "HTTP" in error_msg or "connection" in error_msg.lower():
                st.info("💡 **Troubleshooting Tips:**")
                st.info("• Check your internet connection")
                st.info("• Yahoo Finance servers might be temporarily unavailable")
                st.info("• Try again in a few minutes")
            else:
                st.info("💡 **Troubleshooting Tips:**")
                st.info("• Try a popular ticker like AAPL, MSFT, or GOOGL")
                st.info("• Check your internet connection")
                st.info("• Verify the date range is valid")

def display_welcome_message():
    """Display welcome message when no data is loaded"""
    
    st.markdown("""
    ## Stock Analysis Dashboard! 🎯
    
    This dashboard provides comprehensive stock analysis with the following features:
    
    ### 📊 Features
    - **Real-time Stock Data**: Fetch current and historical stock prices
    - **Technical Indicators**: SMA, EMA, RSI, MACD, Bollinger Bands, and more
    - **Interactive Charts**: Candlestick, line charts with zoom and pan
    - **Trading Signals**: Automated buy/sell signals based on technical analysis
    - **Performance Analysis**: Returns, volatility, and drawdown analysis
    - **Export Functionality**: Download data and reports
    
   
    
    ### 💡 Tips
    - Use popular tickers like AAPL, MSFT, GOOGL, TSLA, AMZN for best results
    - Longer time periods provide better technical analysis
    - Combine multiple indicators for more robust signals
    """)
    
    # Sample tickers
    st.markdown("### 🔥 Popular Stocks to Try")
    col1, col2, col3, col4 = st.columns(4)
    
    sample_tickers = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft"),
        ("GOOGL", "Alphabet"),
        ("TSLA", "Tesla"),
        ("AMZN", "Amazon"),
        ("NVDA", "NVIDIA"),
        ("META", "Meta"),
        ("NFLX", "Netflix")
    ]
    
    for i, (ticker, name) in enumerate(sample_tickers):
        col = [col1, col2, col3, col4][i % 4]
        with col:
            st.code(f"{ticker}\n{name}", language=None)

def display_dashboard():
    """Display the main dashboard with charts and analysis"""
    
    data = st.session_state.processed_data
    info = st.session_state.stock_info
    ticker = st.session_state.ticker
    
    # Company information header
    if info and info.get('name', 'N/A') != 'N/A':
        st.markdown(f"## {info['name']} ({ticker})")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Current Price",
                FormatUtils.format_currency(data['Close'].iloc[-1]),
                delta=FormatUtils.format_percentage(data['Daily_Return'].iloc[-1])
            )
        
        with col2:
            st.metric(
                "Market Cap",
                FormatUtils.format_large_number(info.get('market_cap', 0)) if info.get('market_cap') != 'N/A' else 'N/A'
            )
        
        with col3:
            st.metric(
                "P/E Ratio",
                FormatUtils.format_number(info.get('pe_ratio', 0)) if info.get('pe_ratio') != 'N/A' else 'N/A'
            )
        
        with col4:
            st.metric(
                "52W High/Low",
                f"{FormatUtils.format_currency(info.get('fifty_two_week_high', 0))} / {FormatUtils.format_currency(info.get('fifty_two_week_low', 0))}"
                if info.get('fifty_two_week_high') != 'N/A' else 'N/A'
            )
    else:
        st.markdown(f"## {ticker} Stock Analysis")
    
    # Main chart
    st.subheader("📈 Price Chart")
    charts = StockCharts()

    # Create main price chart with indicators
    price_indicators = []

    # Add SMA indicators based on user selection
    if 'show_sma' in st.session_state and st.session_state.show_sma:
        sma_periods = st.session_state.get('sma_periods', [20, 50])
        price_indicators.extend([f'SMA_{period}' for period in sma_periods if f'SMA_{period}' in data.columns])
    else:
        # Default SMA indicators
        price_indicators.extend([f'SMA_{period}' for period in [20, 50] if f'SMA_{period}' in data.columns])

    # Add EMA indicators based on user selection
    if 'show_ema' in st.session_state and st.session_state.show_ema:
        ema_periods = st.session_state.get('ema_periods', [12, 26])
        price_indicators.extend([f'EMA_{period}' for period in ema_periods if f'EMA_{period}' in data.columns])

    # Add Bollinger Bands if selected
    if st.session_state.get('show_bollinger', False):
        bb_indicators = ['BB_Upper', 'BB_Middle', 'BB_Lower']
        price_indicators.extend([ind for ind in bb_indicators if ind in data.columns])

    oscillators = []
    if st.session_state.get('show_rsi', True) and 'RSI' in data.columns:
        oscillators.append('RSI')
    if st.session_state.get('show_macd', True) and 'MACD' in data.columns:
        oscillators.append('MACD')
    if st.session_state.get('show_stochastic', False) and 'Stoch_K' in data.columns:
        oscillators.append('Stochastic')
    
    main_chart = charts.create_indicator_chart(
        data,
        price_indicators=price_indicators,
        oscillators=oscillators,
        title=f"{ticker} Technical Analysis"
    )
    
    st.plotly_chart(main_chart, use_container_width=True)
    
    # Additional analysis tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Performance", "📈 Signals", "📋 Data", "📥 Export"])
    
    with tab1:
        display_performance_analysis(data)
    
    with tab2:
        display_trading_signals(data)
    
    with tab3:
        display_data_table(data)
    
    with tab4:
        display_export_options(data, ticker)

def display_performance_analysis(data):
    """Display performance analysis section"""

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📊 Performance Metrics")

        # Calculate performance metrics
        total_return = ((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100
        volatility = DataUtils.calculate_volatility(data)
        max_drawdown = DataUtils.calculate_drawdown(data).min()

        st.metric("Total Return", FormatUtils.format_percentage(total_return))
        st.metric("Volatility (Annualized)", FormatUtils.format_percentage(volatility.iloc[-1]) if not volatility.empty else "N/A")
        st.metric("Max Drawdown", FormatUtils.format_percentage(max_drawdown))

        # Sharpe ratio (simplified, assuming risk-free rate = 0)
        if 'Daily_Return' in data.columns:
            avg_return = data['Daily_Return'].mean()
            std_return = data['Daily_Return'].std()
            sharpe_ratio = (avg_return / std_return) * np.sqrt(252) if std_return != 0 else 0
            st.metric("Sharpe Ratio", FormatUtils.format_number(sharpe_ratio))

    with col2:
        st.subheader("📈 Returns Distribution")

        if 'Daily_Return' in data.columns:
            returns_data = data['Daily_Return'].dropna()

            # Create histogram
            if px is not None:
                fig = px.histogram(
                    x=returns_data,
                    nbins=50,
                    title="Daily Returns Distribution",
                    labels={'x': 'Daily Return (%)', 'y': 'Frequency'}
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Plotly Express not available for histogram")

def display_trading_signals(data):
    """Display trading signals section"""

    st.subheader("🎯 Trading Signals")

    # Get recent signals
    signal_columns = [col for col in data.columns if col.startswith('Signal_')]

    if signal_columns:
        # Display recent signals
        recent_data = data.tail(10)[['Close'] + signal_columns]

        # Format signals for display
        for col in signal_columns:
            recent_data[col] = recent_data[col].map({1: '🟢 BUY', -1: '🔴 SELL', 0: '⚪ HOLD'})

        st.dataframe(recent_data, use_container_width=True)

        # Signal summary
        st.subheader("📊 Signal Summary")

        col1, col2, col3 = st.columns(3)

        for i, col in enumerate(signal_columns[:3]):  # Show first 3 signals
            with [col1, col2, col3][i]:
                signal_name = col.replace('Signal_', '').replace('_', ' ').title()
                recent_signal = data[col].iloc[-1]

                if recent_signal == 1:
                    st.success(f"🟢 {signal_name}: BUY")
                elif recent_signal == -1:
                    st.error(f"🔴 {signal_name}: SELL")
                else:
                    st.info(f"⚪ {signal_name}: HOLD")
    else:
        st.info("No trading signals available. Technical indicators may need more data.")

def display_data_table(data):
    """Display data table section"""

    st.subheader("📋 Stock Data")

    # Select columns to display
    display_columns = st.multiselect(
        "Select columns to display:",
        data.columns.tolist(),
        default=['Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Return']
    )

    if display_columns:
        # Display data with pagination
        page_size = st.selectbox("Rows per page:", [10, 25, 50, 100], index=1)

        total_rows = len(data)
        total_pages = (total_rows - 1) // page_size + 1

        page = st.selectbox(f"Page (1 to {total_pages}):", range(1, total_pages + 1))

        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)

        display_data = data.iloc[start_idx:end_idx][display_columns]

        # Format numeric columns
        formatted_data = display_data.copy()
        for col in formatted_data.columns:
            if formatted_data[col].dtype in ['float64', 'int64']:
                formatted_data[col] = formatted_data[col].apply(lambda x: FormatUtils.format_number(x))

        st.dataframe(formatted_data, use_container_width=True)

        st.info(f"Showing rows {start_idx + 1} to {end_idx} of {total_rows}")

def display_export_options(data, ticker):
    """Display export options section"""

    st.subheader("📥 Export Data")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 Export Raw Data")

        # CSV export
        csv_data = data.to_csv()
        st.download_button(
            label="📄 Download CSV",
            data=csv_data,
            file_name=f"{ticker}_stock_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

        # JSON export
        json_data = data.to_json(orient='index', date_format='iso')
        st.download_button(
            label="📋 Download JSON",
            data=json_data,
            file_name=f"{ticker}_stock_data_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json"
        )

    with col2:
        st.markdown("### 📈 Export Analysis Report")

        # Generate summary report
        report = generate_analysis_report(data, ticker)

        st.download_button(
            label="📑 Download Analysis Report",
            data=report,
            file_name=f"{ticker}_analysis_report_{datetime.now().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

        # Show preview of report
        with st.expander("📖 Preview Report"):
            st.text(report[:1000] + "..." if len(report) > 1000 else report)

def generate_analysis_report(data, ticker):
    """Generate a text analysis report"""

    # Handle date formatting safely
    try:
        if hasattr(data.index[0], 'strftime'):
            start_date = data.index[0].strftime('%Y-%m-%d')
            end_date = data.index[-1].strftime('%Y-%m-%d')
        else:
            # Convert to datetime if it's not already
            start_date = pd.to_datetime(data.index[0]).strftime('%Y-%m-%d')
            end_date = pd.to_datetime(data.index[-1]).strftime('%Y-%m-%d')
    except:
        # Fallback to string representation
        start_date = str(data.index[0])[:10]
        end_date = str(data.index[-1])[:10]

    report = f"""
STOCK ANALYSIS REPORT
=====================
Symbol: {ticker}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Period: {start_date} to {end_date}

PRICE SUMMARY
=============
Current Price: ${data['Close'].iloc[-1]:.2f}
Opening Price: ${data['Open'].iloc[0]:.2f}
Highest Price: ${data['High'].max():.2f}
Lowest Price: ${data['Low'].min():.2f}
Average Volume: {data['Volume'].mean():,.0f}

PERFORMANCE METRICS
==================
Total Return: {((data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1) * 100:.2f}%
Daily Return (Avg): {data['Daily_Return'].mean():.2f}%
Volatility: {data['Daily_Return'].std():.2f}%
Max Drawdown: {DataUtils.calculate_drawdown(data).min():.2f}%

TECHNICAL INDICATORS (Latest Values)
===================================
"""

    # Add technical indicators if available
    indicators = ['SMA_20', 'SMA_50', 'EMA_12', 'EMA_26', 'RSI', 'MACD']
    for indicator in indicators:
        if indicator in data.columns:
            latest_value = data[indicator].iloc[-1]
            if not pd.isna(latest_value):
                report += f"{indicator}: {latest_value:.2f}\n"

    # Add trading signals
    report += "\nTRADING SIGNALS (Latest)\n"
    report += "========================\n"

    signal_columns = [col for col in data.columns if col.startswith('Signal_')]
    for col in signal_columns:
        signal_name = col.replace('Signal_', '').replace('_', ' ').title()
        latest_signal = data[col].iloc[-1]

        if latest_signal == 1:
            signal_text = "BUY"
        elif latest_signal == -1:
            signal_text = "SELL"
        else:
            signal_text = "HOLD"

        report += f"{signal_name}: {signal_text}\n"

    report += f"\n\nStock Analysis Report\n"

    return report

if __name__ == "__main__":
    main()
