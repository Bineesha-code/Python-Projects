"""
Main resume parser that orchestrates the parsing process
"""
import time
import logging
from typing import Optional
from pathlib import Path

from ..models.resume_models import ParsedResume
from ..utils.text_extractor import TextExtractor
from .nlp_processor import NLPProcessor

logger = logging.getLogger(__name__)


class ResumeParser:
    """Main resume parser class"""
    
    def __init__(self):
        """Initialize the resume parser"""
        self.text_extractor = TextExtractor()
        self.nlp_processor = NLPProcessor()
    
    def parse_resume(self, file_path: str, file_type: str) -> Optional[ParsedResume]:
        """
        Parse a resume file and extract structured information
        
        Args:
            file_path: Path to the resume file
            file_type: Type of file ('pdf' or 'docx')
            
        Returns:
            ParsedResume object with extracted information
        """
        start_time = time.time()
        
        try:
            # Step 1: Extract text from file
            logger.info(f"Extracting text from {file_type} file: {file_path}")
            raw_text = self.text_extractor.extract_and_clean(file_path, file_type)
            
            if not raw_text:
                logger.error("Failed to extract text from file")
                return None
            
            # Step 2: Initialize parsed resume object
            parsed_resume = ParsedResume()
            parsed_resume.raw_text = raw_text
            
            # Step 3: Extract contact information
            logger.info("Extracting contact information")
            parsed_resume.contact_info = self.nlp_processor.extract_contact_info(raw_text)
            
            # Step 4: Extract skills
            logger.info("Extracting skills")
            parsed_resume.skills = self.nlp_processor.extract_skills(raw_text)
            
            # Step 5: Extract experience
            logger.info("Extracting work experience")
            parsed_resume.experience = self.nlp_processor.extract_experience(raw_text)
            
            # Step 6: Extract education
            logger.info("Extracting education")
            parsed_resume.education = self.nlp_processor.extract_education(raw_text)
            
            # Step 7: Extract projects
            logger.info("Extracting projects")
            parsed_resume.projects = self.nlp_processor.extract_projects(raw_text)
            
            # Step 8: Extract summary (first paragraph or section)
            logger.info("Extracting summary")
            parsed_resume.summary = self._extract_summary(raw_text)
            
            # Step 9: Add parsing metadata
            processing_time = time.time() - start_time
            parsed_resume.parsing_metadata = {
                "processing_time": processing_time,
                "file_type": file_type,
                "text_length": len(raw_text),
                "skills_found": len(parsed_resume.skills.all_skills),
                "experience_entries": len(parsed_resume.experience),
                "education_entries": len(parsed_resume.education),
                "project_entries": len(parsed_resume.projects)
            }
            
            logger.info(f"Resume parsing completed in {processing_time:.2f} seconds")
            return parsed_resume
            
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            return None
    
    def _extract_summary(self, text: str) -> Optional[str]:
        """
        Extract summary/objective section from resume text
        
        Args:
            text: Raw resume text
            
        Returns:
            Summary text or None
        """
        import re
        
        # Look for summary section
        summary_patterns = [
            r'SUMMARY.*?(?=EXPERIENCE|EDUCATION|SKILLS|$)',
            r'OBJECTIVE.*?(?=EXPERIENCE|EDUCATION|SKILLS|$)',
            r'PROFILE.*?(?=EXPERIENCE|EDUCATION|SKILLS|$)',
            r'ABOUT.*?(?=EXPERIENCE|EDUCATION|SKILLS|$)'
        ]
        
        for pattern in summary_patterns:
            match = re.search(pattern, text.upper(), re.DOTALL)
            if match:
                summary_text = match.group(0)
                # Remove the header and clean up
                lines = summary_text.split('\n')[1:]  # Skip header line
                summary = '\n'.join(line.strip() for line in lines if line.strip())
                if summary:
                    return summary[:500]  # Limit to 500 characters
        
        # If no explicit summary section, take first paragraph
        paragraphs = text.split('\n\n')
        if paragraphs and len(paragraphs[0]) > 50:
            return paragraphs[0][:500]
        
        return None
    
    def get_parsing_stats(self, parsed_resume: ParsedResume) -> dict:
        """
        Get statistics about the parsed resume
        
        Args:
            parsed_resume: ParsedResume object
            
        Returns:
            Dictionary with parsing statistics
        """
        if not parsed_resume:
            return {}
        
        return {
            "contact_fields_found": sum([
                bool(parsed_resume.contact_info.name),
                bool(parsed_resume.contact_info.email),
                bool(parsed_resume.contact_info.phone),
                bool(parsed_resume.contact_info.linkedin),
                bool(parsed_resume.contact_info.github)
            ]),
            "total_skills": len(parsed_resume.skills.all_skills),
            "skill_categories": {
                "programming_languages": len(parsed_resume.skills.programming_languages),
                "frameworks": len(parsed_resume.skills.frameworks),
                "databases": len(parsed_resume.skills.databases),
                "tools": len(parsed_resume.skills.tools),
                "soft_skills": len(parsed_resume.skills.soft_skills),
                "data_science": len(parsed_resume.skills.data_science)
            },
            "experience_entries": len(parsed_resume.experience),
            "education_entries": len(parsed_resume.education),
            "has_summary": bool(parsed_resume.summary),
            "processing_time": parsed_resume.parsing_metadata.get("processing_time", 0)
        }
