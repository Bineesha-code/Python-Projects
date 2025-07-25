"""
Configuration settings for the Smart Resume Parser
"""
import os
from pathlib import Path
from typing import List

# Base directory
BASE_DIR = Path(__file__).parent

# Environment settings
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))

# File upload settings
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx").split(",")

# NLP settings
SPACY_MODEL = os.getenv("SPACY_MODEL", "en_core_web_sm")

# Paths
DATA_DIR = BASE_DIR / "data"
SKILLS_DIR = DATA_DIR / "skills"
SAMPLES_DIR = DATA_DIR / "samples"
STATIC_DIR = BASE_DIR / "static"

# Skills database
SKILLS_FILE = SKILLS_DIR / "skills_database.json"

# Supported file types
SUPPORTED_FORMATS = {
    "application/pdf": ".pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx"
}

# Resume sections to extract
RESUME_SECTIONS = [
    "contact_info",
    "summary",
    "experience",
    "education",
    "skills",
    "certifications",
    "projects"
]

# Skill categories
SKILL_CATEGORIES = [
    "programming_languages",
    "frameworks",
    "databases",
    "tools",
    "soft_skills",
    "certifications"
]
