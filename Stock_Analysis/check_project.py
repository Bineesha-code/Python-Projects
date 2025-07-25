#!/usr/bin/env python3
"""
Project Health Check Script
Comprehensive validation of the Stock Analysis Dashboard project
"""

import os
import sys
import importlib.util
from pathlib import Path

def check_project_structure():
    """Check if all required files and directories exist"""
    print("🔍 Checking project structure...")
    
    required_structure = {
        'files': [
            'README.md',
            'requirements.txt',
            'dashboard/app.py',
            'src/__init__.py',
            'src/data/__init__.py',
            'src/data/stock_data.py',
            'src/data/data_validator.py',
            'src/indicators/__init__.py',
            'src/indicators/technical_indicators.py',
            'src/indicators/trading_signals.py',
            'src/visualization/__init__.py',
            'src/visualization/charts.py',
            'src/utils/__init__.py',
            'src/utils/helpers.py',
            'config/settings.py',

            'docs/USER_GUIDE.md',
            'docs/DEVELOPER_GUIDE.md'
        ],
        'directories': [
            'src',
            'src/data',
            'src/indicators', 
            'src/visualization',
            'src/utils',
            'dashboard',
            'config',

            'docs',
            'data'
        ]
    }
    
    missing_files = []
    missing_dirs = []
    
    # Check directories
    for directory in required_structure['directories']:
        if not os.path.exists(directory):
            missing_dirs.append(directory)
        else:
            print(f"✅ Directory: {directory}")
    
    # Check files
    for file_path in required_structure['files']:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✅ File: {file_path}")
    
    if missing_dirs:
        print(f"\n❌ Missing directories: {missing_dirs}")
    
    if missing_files:
        print(f"\n❌ Missing files: {missing_files}")
    
    return len(missing_dirs) == 0 and len(missing_files) == 0

def check_python_imports():
    """Check if all Python modules can be imported"""
    print("\n🐍 Checking Python module imports...")
    
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    if src_path not in sys.path:
        sys.path.insert(0, src_path)
    
    modules_to_test = [
        ('data.stock_data', 'StockData'),
        ('data.data_validator', 'DataValidator'),
        ('indicators.technical_indicators', 'TechnicalIndicators'),
        ('indicators.trading_signals', 'TradingSignals'),
        ('visualization.charts', 'StockCharts'),
        ('utils.helpers', 'DateUtils'),
    ]
    
    failed_imports = []
    
    for module_name, class_name in modules_to_test:
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, class_name):
                print(f"✅ {module_name}.{class_name}")
            else:
                print(f"❌ {module_name}.{class_name} - class not found")
                failed_imports.append(f"{module_name}.{class_name}")
        except ImportError as e:
            print(f"❌ {module_name} - import failed: {str(e)}")
            failed_imports.append(module_name)
    
    return len(failed_imports) == 0

def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n📦 Checking dependencies...")
    
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
            print(f"❌ {package} - not installed")
        else:
            try:
                module = importlib.import_module(package)
                version = getattr(module, '__version__', 'unknown')
                print(f"✅ {package} - version {version}")
            except:
                print(f"✅ {package} - installed")
    
    if missing_packages:
        print(f"\n💡 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
    
    return len(missing_packages) == 0

def check_configuration():
    """Check configuration files"""
    print("\n⚙️ Checking configuration...")
    
    try:
        sys.path.append('config')
        import settings
        
        # Check if main config sections exist
        config_sections = ['DATA_CONFIG', 'CHART_CONFIG', 'INDICATORS_CONFIG', 'DASHBOARD_CONFIG']
        
        for section in config_sections:
            if hasattr(settings, section):
                print(f"✅ Config section: {section}")
            else:
                print(f"❌ Config section missing: {section}")
                return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Configuration import failed: {str(e)}")
        return False

def run_basic_tests():
    """Run basic functionality tests"""
    print("\n🧪 Running basic tests...")
    
    try:
        # Add src to path
        sys.path.append('src')
        
        # Test data validator
        from data.data_validator import DataValidator
        
        test_cases = [
            (DataValidator.validate_ticker('AAPL'), True, "Ticker validation - valid"),
            (DataValidator.validate_ticker(''), False, "Ticker validation - empty"),
            (DataValidator.validate_date('2023-01-01'), True, "Date validation - valid"),
            (DataValidator.validate_date('invalid'), False, "Date validation - invalid"),
        ]
        
        for result, expected, description in test_cases:
            if result == expected:
                print(f"✅ {description}")
            else:
                print(f"❌ {description} - expected {expected}, got {result}")
                return False
        
        # Test technical indicators import
        from indicators.technical_indicators import TechnicalIndicators
        print("✅ Technical indicators import")
        
        # Test charts import  
        from visualization.charts import StockCharts
        print("✅ Charts import")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic tests failed: {str(e)}")
        return False

def generate_report():
    """Generate a comprehensive project health report"""
    print("\n" + "="*60)
    print("📊 PROJECT HEALTH REPORT")
    print("="*60)
    
    checks = [
        ("Project Structure", check_project_structure),
        ("Python Imports", check_python_imports), 
        ("Dependencies", check_dependencies),
        ("Configuration", check_configuration),
        ("Basic Tests", run_basic_tests)
    ]
    
    results = {}
    
    for check_name, check_function in checks:
        print(f"\n{check_name}:")
        print("-" * 40)
        results[check_name] = check_function()
    
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    
    all_passed = True
    for check_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("Your Stock Analysis Dashboard is ready to run!")
        print("\n💡 To start the dashboard:")
        print("  python3 run_dashboard.py")
        print("  OR")
        print("  streamlit run dashboard/app.py")
    else:
        print("❌ SOME CHECKS FAILED")
        print("Please fix the issues above before running the dashboard.")
        print("\n💡 Common fixes:")
        print("  • Install missing dependencies: pip install -r requirements.txt")
        print("  • Check file paths and permissions")
        print("  • Verify Python version (3.8+ required)")
    
    return all_passed

if __name__ == "__main__":
    print("🔍 Stock Analysis Dashboard - Project Health Check")
    success = generate_report()
    sys.exit(0 if success else 1)
