# Stock Analysis Dashboard 📈

A comprehensive dashboard for analyzing stock market data, calculating technical indicators, and visualizing trends.

## Features

- 📈 **Stock Search**: Search for any stock by symbol (e.g., AAPL, MSFT, INFY)
- ⏳ **Date Range Selection**: Analyze data for custom time periods
- 📊 **Interactive Charts**: View candlestick charts, line plots with interactive features
- 🔄 **Technical Indicators**: Calculate and visualize SMA, EMA, RSI, and more
- 📤 **Export Functionality**: Download data as CSV or analysis reports
- 📱 **Responsive UI**: User-friendly interface built with Streamlit

## Project Structure

```
Stock_Analysis/
├── data/                  # Data storage and cache
├── src/                   # Source code
│   ├── data/              # Data fetching and processing modules
│   ├── indicators/        # Technical indicator calculations
│   ├── visualization/     # Chart generation and plotting functions
│   └── utils/             # Utility functions and helpers
├── dashboard/             # Streamlit dashboard files
├── tests/                 # Test files
├── config/                # Configuration files
├── requirements.txt       # Project dependencies
└── README.md              # Project documentation
```

## Quick Start

### Option 1: Automated Setup (Recommended)
```bash
# Check project health (optional)
python3 check_project.py

# Run with automatic setup
python3 run_dashboard.py
```

### Option 2: Manual Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard/app.py
```

## Installation Requirements

- **Python**: 3.8 or higher
- **Dependencies**: Listed in `requirements.txt`
- **Internet**: Required for fetching stock data

## Technologies Used

- **Data Fetching**: yfinance
- **Data Analysis**: pandas, numpy
- **Visualization**: plotly, matplotlib
- **Dashboard**: Streamlit
- **Technical Analysis**: Custom implementations and ta library (optional)

## License

MIT
