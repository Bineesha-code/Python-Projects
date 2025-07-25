# 🤖 Smart Resume Parser

An intelligent application that automatically extracts structured information from resume documents (PDFs and DOCX files) using Natural Language Processing (NLP) techniques.

## 🌟 Features

- **Automatic Text Extraction**: Supports PDF and DOCX formats
- **Intelligent Parsing**: Uses spaCy NLP for named entity recognition
- **Skills Matching**: Advanced skill detection and categorization
- **Clean UI**: Minimal and attractive Streamlit interface
- **REST API**: FastAPI backend for integration
- **Structured Output**: JSON and CSV export formats

## 🏗️ Project Structure

```
ResumeParser/
├── backend/
│   ├── core/           # Core parsing logic
│   ├── api/            # FastAPI endpoints
│   ├── models/         # Data models
│   └── utils/          # Utility functions
├── frontend/           # Streamlit UI
├── data/
│   ├── skills/         # Skills database
│   └── samples/        # Sample resumes
├── tests/              # Unit and integration tests
├── docs/               # Documentation
└── static/             # CSS, JS, images
```

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd ResumeParser
   pip install -r requirements.txt
   ```

2. **Download spaCy Model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

3. **Run the Application**
   ```bash
   # Start the backend API
   uvicorn backend.api.main:app --reload --port 8000
   
   # Start the frontend (in another terminal)
   streamlit run frontend/app.py --server.port 8501
   ```

4. **Access the Application**
   - Frontend UI: http://localhost:8501
   - API Documentation: http://localhost:8000/docs

## 📋 Usage

1. Upload a resume (PDF or DOCX)
2. Wait for processing
3. View extracted information
4. Download results as JSON or CSV

## 🛠️ Development

- **Backend**: FastAPI with spaCy NLP
- **Frontend**: Streamlit with drag-and-drop
- **Testing**: pytest
- **Code Quality**: black, flake8

## 📄 License

MIT License
