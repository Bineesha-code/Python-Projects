.PHONY: setup install backend frontend test clean help

# Default target
help:
	@echo "🤖 Smart Resume Parser - Available Commands:"
	@echo "  setup     - Install dependencies and setup the project"
	@echo "  backend   - Run the FastAPI backend server"
	@echo "  frontend  - Run the Streamlit frontend"
	@echo "  test      - Run unit tests"
	@echo "  clean     - Clean temporary files"
	@echo "  install   - Install Python dependencies"

# Setup the project
setup:
	@echo "🚀 Setting up Smart Resume Parser..."
	python setup.py

# Install dependencies
install:
	pip install -r requirements.txt
	python -m spacy download en_core_web_sm

# Run backend server
backend:
	@echo "🔧 Starting backend server..."
	python run_backend.py

# Run frontend
frontend:
	@echo "🎨 Starting frontend..."
	python run_frontend.py

# Run tests
test:
	@echo "🧪 Running tests..."
	python -m pytest tests/ -v

# Clean temporary files
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
