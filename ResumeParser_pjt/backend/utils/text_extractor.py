"""
Text extraction utilities for PDF and DOCX files
"""
import fitz  # PyMuPDF
from docx import Document
import re
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class TextExtractor:
    """Handles text extraction from various file formats"""
    
    @staticmethod
    def extract_from_pdf(file_path: str) -> Optional[str]:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = fitz.open(file_path)
            text = ""
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text += page.get_text()
                
            doc.close()
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            return None
    
    @staticmethod
    def extract_from_docx(file_path: str) -> Optional[str]:
        """
        Extract text from DOCX file
        
        Args:
            file_path: Path to the DOCX file
            
        Returns:
            Extracted text or None if extraction fails
        """
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
                
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from DOCX: {str(e)}")
            return None
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> Optional[str]:
        """
        Extract text based on file type
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('pdf' or 'docx')
            
        Returns:
            Extracted text or None if extraction fails
        """
        if file_type.lower() == 'pdf':
            return TextExtractor.extract_from_pdf(file_path)
        elif file_type.lower() == 'docx':
            return TextExtractor.extract_from_docx(file_path)
        else:
            logger.error(f"Unsupported file type: {file_type}")
            return None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            text: Raw extracted text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace and normalize line breaks
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # Remove special characters but keep important punctuation
        text = re.sub(r'[^\w\s\n\-\.\@\(\)\+\,\:\;]', '', text)
        
        return text.strip()
    
    @staticmethod
    def extract_and_clean(file_path: str, file_type: str) -> Optional[str]:
        """
        Extract and clean text in one step
        
        Args:
            file_path: Path to the file
            file_type: Type of file ('pdf' or 'docx')
            
        Returns:
            Cleaned extracted text or None if extraction fails
        """
        raw_text = TextExtractor.extract_text(file_path, file_type)
        if raw_text:
            return TextExtractor.clean_text(raw_text)
        return None
