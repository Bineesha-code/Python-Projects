#!/usr/bin/env python3
"""
Script to run the Streamlit frontend
"""
import subprocess
import sys

if __name__ == "__main__":
    print("🎨 Starting Smart Resume Parser Frontend...")
    print("📍 Frontend will be available at: http://localhost:8501")
    print("🔄 Auto-reload enabled for development")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "frontend/app.py", 
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Frontend server stopped.")
