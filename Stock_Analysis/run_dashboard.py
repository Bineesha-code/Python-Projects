#!/usr/bin/env python3
"""
Stock Analysis Dashboard Runner
Comprehensive script to run the dashboard with proper setup and error handling
"""

import sys
import os
import subprocess
import importlib.util

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'plotly',
        'yfinance',
        'matplotlib'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        spec = importlib.util.find_spec(package)
        if spec is None:
            missing_packages.append(package)
        else:
            print(f"✅ {package} is installed")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("Installing missing packages...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                *missing_packages
            ])
            print("✅ All packages installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install packages")
            print("Please run: pip install -r requirements.txt")
            return False
    
    print("✅ All required packages are installed")
    return True

def setup_environment():
    """Setup the environment for the dashboard"""
    # Add src directory to Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    # Create necessary directories
    directories = ['data', 'logs']
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")

def test_basic_functionality():
    """Test basic functionality before starting the dashboard"""
    print("\n🧪 Testing basic functionality...")
    
    try:
        # Test data validator
        sys.path.append('src')
        from data.data_validator import DataValidator
        
        # Test ticker validation
        assert DataValidator.validate_ticker('AAPL') == True
        assert DataValidator.validate_ticker('') == False
        print("✅ Data validator working")
        
        # Test date validation
        assert DataValidator.validate_date('2023-01-01') == True
        assert DataValidator.validate_date('invalid') == False
        print("✅ Date validation working")
        
        # Test technical indicators import
        from indicators.technical_indicators import TechnicalIndicators
        print("✅ Technical indicators module imported")
        
        # Test charts import
        from visualization.charts import StockCharts
        print("✅ Charts module imported")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic functionality test failed: {str(e)}")
        return False

def run_dashboard():
    """Run the Streamlit dashboard"""
    print("\n🚀 Starting Stock Analysis Dashboard...")
    print("=" * 50)
    
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'app.py')
    
    if not os.path.exists(dashboard_path):
        print(f"❌ Dashboard file not found: {dashboard_path}")
        return False
    
    try:
        # Run streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", dashboard_path,
            "--server.headless", "false",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
        return True
    except Exception as e:
        print(f"❌ Error running dashboard: {str(e)}")
        return False

def main():
    """Main function to run the dashboard with all checks"""
    print("🎯 Stock Analysis Dashboard Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return 1
    
    # Setup environment
    setup_environment()
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Test basic functionality
    if not test_basic_functionality():
        print("\n💡 Try running: pip install -r requirements.txt")
        return 1
    
    print("\n✅ All checks passed!")
    print("\n📋 Dashboard Features:")
    print("  • Real-time stock data fetching")
    print("  • Technical indicators (SMA, EMA, RSI, MACD, etc.)")
    print("  • Interactive charts with Plotly")
    print("  • Trading signals generation")
    print("  • Data export functionality")
    
    print("\n💡 Usage Tips:")
    print("  • Try popular tickers: AAPL, MSFT, GOOGL, TSLA")
    print("  • Use longer time periods for better analysis")
    print("  • Combine multiple indicators for robust signals")
    
    # Run the dashboard
    success = run_dashboard()
    
    return 0 if success else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
