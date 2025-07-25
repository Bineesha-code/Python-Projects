#!/usr/bin/env python3
"""
Setup script for Smart Resume Parser
"""
import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"📦 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:\n{e.stderr.strip()}")
        return False

def main():
    """Main setup function"""
    print("🤖 Smart Resume Parser Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

    # Warn if not in a virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️  It looks like you're not in a virtual environment.")
        print("💡 It's recommended to run this setup inside a virtualenv.")

    # Check for requirements.txt
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found. Please ensure it exists in the project root.")
        sys.exit(1)

    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("❌ Failed to install dependencies. Please check your Python environment.")
        sys.exit(1)

    # Download spaCy model
    if not run_command("python -m spacy download en_core_web_sm", "Downloading spaCy English model"):
        print("⚠️  spaCy model download failed. You may need to download it manually.")

    # Create .env file if missing
    if not os.path.exists('.env'):
        if os.path.exists('.env.example'):
            print("📝 Creating .env file...")
            subprocess.run("cp .env.example .env", shell=True)
            print("✅ .env file created from .env.example")
        else:
            print("⚠️  .env.example not found. Skipping .env creation.")

    print("\n🎉 Setup completed successfully!")
    print("\n🚀 To start the application:")
    print("1. Backend:  python run_backend.py")
    print("2. Frontend: python run_frontend.py")
    print("\n📚 API Docs: http://localhost:8000/docs")
    print("🎨 UI:       http://localhost:8501")

if __name__ == "__main__":
    main()
