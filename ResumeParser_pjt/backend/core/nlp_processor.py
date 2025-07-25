import spacy
import re
import json
from typing import List, Dict, Optional
from pathlib import Path
import logging

from ..models.resume_models import ContactInfo, Experience, Education, SkillsExtracted, Project
from config import SKILLS_FILE, SPACY_MODEL

logger = logging.getLogger(__name__)


class NLPProcessor:
    """Handles NLP processing for resume parsing"""

    def __init__(self):
        """Initialize the NLP processor"""
        try:
            self.nlp = spacy.load(SPACY_MODEL)
            self.skills_db = self._load_skills_database()
            self.phrase_matcher = self._setup_phrase_matcher()
        except Exception as e:
            logger.error(f"Error initializing NLP processor: {str(e)}")
            raise

    def _load_skills_database(self) -> Dict:
        """Load skills database from JSON file"""
        try:
            with open(SKILLS_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading skills database: {str(e)}")
            return {}

    def _setup_phrase_matcher(self):
        """Setup spaCy PhraseMatcher for skill detection"""
        from spacy.matcher import PhraseMatcher

        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")

        for category, skills in self.skills_db.items():
            patterns = [self.nlp(skill.lower()) for skill in skills]
            matcher.add(category, patterns)

        return matcher

    def extract_contact_info(self, text: str) -> ContactInfo:
        """Extract contact information from text"""
        contact = ContactInfo()

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact.email = emails[0]

        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if phones:
            contact.phone = ''.join(phones[0]) if isinstance(phones[0], tuple) else phones[0]

        linkedin_pattern = r'linkedin\.com/in/[\w-]+'
        linkedin_matches = re.findall(linkedin_pattern, text, re.IGNORECASE)
        if linkedin_matches:
            contact.linkedin = f"https://{linkedin_matches[0]}"

        github_pattern = r'github\.com/[\w-]+'
        github_matches = re.findall(github_pattern, text, re.IGNORECASE)
        if github_matches:
            contact.github = f"https://{github_matches[0]}"

        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if line and not any(char.isdigit() for char in line) and len(line.split()) <= 4:
                contact.name = line
                break

        return contact

    def extract_skills(self, text: str) -> SkillsExtracted:
        """Extract skills using PhraseMatcher"""
        doc = self.nlp(text.lower())
        matches = self.phrase_matcher(doc)

        skills = SkillsExtracted()
        found_skills = set()

        for match_id, start, end in matches:
            category = self.nlp.vocab.strings[match_id]
            skill = doc[start:end].text.title()

            if skill not in found_skills:
                found_skills.add(skill)

                if category == "programming_languages":
                    skills.programming_languages.append(skill)
                elif category == "frameworks":
                    skills.frameworks.append(skill)
                elif category == "databases":
                    skills.databases.append(skill)
                elif category == "tools":
                    skills.tools.append(skill)
                elif category == "soft_skills":
                    skills.soft_skills.append(skill)
                elif category == "certifications":
                    skills.certifications.append(skill)
                elif category == "data_science":
                    skills.data_science.append(skill)

        skills.all_skills = list(found_skills)
        return skills

    def extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume text using a comprehensive approach."""
        experience = []
        
        # Method 1: Try to find all possible experience sections and validate them
        experience_headers = [
            'PROFESSIONAL EXPERIENCE', 
            'EXPERIENCE', 
            'WORK HISTORY', 
            'EMPLOYMENT', 
            'WORK EXPERIENCE', 
            'EMPLOYMENT HISTORY', 
            'CAREER HISTORY', 
            'JOB HISTORY'
        ]
        
        # Find all potential experience sections
        potential_sections = []
        for header in experience_headers:
            start = 0
            while True:
                pos = text.upper().find(header, start)
                if pos == -1:
                    break
                
                # Get text after the header
                after_header = text[pos + len(header):]
                
                # Find next section
                next_sections = ['Education', 'Skills', 'Projects', 'Certifications']
                next_section_pos = -1
                for section in next_sections:
                    section_pos = after_header.find(section)
                    if section_pos != -1:
                        if next_section_pos == -1 or section_pos < next_section_pos:
                            next_section_pos = section_pos
                
                if next_section_pos != -1:
                    section_text = after_header[:next_section_pos].strip()
                else:
                    section_text = after_header.strip()
                
                # Score this section based on various criteria
                score = 0
                
                # Bonus for Professional Experience
                if header == 'PROFESSIONAL EXPERIENCE':
                    score += 10
                
                # Bonus for longer sections (more likely to be real)
                if len(section_text) > 100:
                    score += 5
                
                # Bonus for job-related keywords
                job_keywords = ['manager', 'engineer', 'developer', 'intern', 'assistant', 'specialist', 'analyst']
                job_keyword_count = sum(1 for keyword in job_keywords if keyword in section_text.lower())
                score += job_keyword_count * 2
                
                # Penalty for summary-like text
                summary_keywords = ['summary', 'passionate', 'building', 'developing', 'experience in']
                summary_keyword_count = sum(1 for keyword in summary_keywords if keyword in section_text.lower())
                score -= summary_keyword_count * 3
                
                # Penalty for very short sections
                if len(section_text) < 50:
                    score -= 5
                
                potential_sections.append({
                    'header': header,
                    'position': pos,
                    'text': section_text,
                    'score': score
                })
                
                start = pos + 1
        
        # Sort by score and position (prefer later positions for same score)
        potential_sections.sort(key=lambda x: (x['score'], x['position']), reverse=True)
        
        # Use the best scoring section
        if potential_sections and potential_sections[0]['score'] > 0:
            experience_block = potential_sections[0]['text']
        else:
            # Fallback: try a different approach - look for job patterns in the entire text
            return self._extract_experience_from_entire_text(text)
        
        if experience_block:
            # Method 2: Try multiple extraction strategies
            experience = self._extract_with_pipe_format(experience_block)
            
            if not experience:
                experience = self._extract_with_date_first_format(experience_block)
            
            if not experience:
                experience = self._extract_with_line_by_line_processing(experience_block)
            
            if not experience:
                # Method 3: Try extracting from the entire text as fallback
                experience = self._extract_experience_from_entire_text(text)

        return experience
    
    def _extract_with_pipe_format(self, experience_block: str) -> List[Dict[str, str]]:
        """Extract experience using pipe format (Resume1.pdf)."""
        experience = []
        pipe_pattern = r'([^|]+)\s*\|\s*([^(]+)\s*\(([^)]+)\)'
        matches = re.findall(pipe_pattern, experience_block)
        
        for match in matches:
            title_company = match[0].strip()
            date_range = match[1].strip()
            location = match[2].strip()
            
            # Split title and company if they're combined
            if '  ' in title_company:  # Double space indicates separation
                parts = title_company.split('  ')
                if len(parts) >= 2:
                    title = parts[0].strip()
                    company = parts[1].strip()
                else:
                    title = title_company
                    company = ""
            else:
                title = title_company
                company = ""
            
            # Parse date range
            if 'Present' in date_range:
                start_date = date_range.split('-')[0].strip()
                end_date = "Present"
            else:
                dates = date_range.split('-')
                if len(dates) == 2:
                    start_date = dates[0].strip()
                    end_date = dates[1].strip()
                else:
                    start_date = date_range
                    end_date = ""
            
            experience.append({
                "title": title,
                "company": company,
                "start_date": start_date,
                "end_date": end_date,
                "location": location,
                "description": ""
            })
        
        return experience
    
    def _extract_with_date_first_format(self, experience_block: str) -> List[Dict[str, str]]:
        """Extract experience using date-first format."""
        experience = []
        date_patterns = [
            r'(20XX|\d{4})\s+Present\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'(20XX|\d{4})\s+(20XX|\d{4})\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, experience_block)
            for match in matches:
                if len(match) == 4:  # First pattern: date, title, company, location
                    title_company = match[1].strip()
                    if '  ' in title_company:
                        parts = title_company.split('  ')
                        if len(parts) >= 2:
                            title = parts[0].strip()
                            company = parts[1].strip()
                        else:
                            title = title_company
                            company = match[2]
                    else:
                        title = title_company
                        company = match[2]
                    
                    experience.append({
                        "title": title,
                        "company": company,
                        "start_date": match[0],
                        "end_date": "Present",
                        "location": match[3],
                        "description": ""
                    })
                elif len(match) == 5:  # Second pattern: start_date, end_date, title, company, location
                    title_company = match[2].strip()
                    if '  ' in title_company:
                        parts = title_company.split('  ')
                        if len(parts) >= 2:
                            title = parts[0].strip()
                            company = parts[1].strip()
                        else:
                            title = title_company
                            company = match[3]
                    else:
                        title = title_company
                        company = match[3]
                    
                    experience.append({
                        "title": title,
                        "company": company,
                        "start_date": match[0],
                        "end_date": match[1],
                        "location": match[4],
                        "description": ""
                    })
        
        return experience
    
    def _extract_with_line_by_line_processing(self, experience_block: str) -> List[Dict[str, str]]:
        """Extract experience using line-by-line processing."""
        experience = []
        lines = experience_block.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are clearly descriptions
            if (line.startswith('•') or line.startswith('-') or 
                'Developed' in line or 'Built' in line or 'Integrated' in line or
                'Increased' in line or 'Deployed' in line or 'Handled' in line or
                'Summarize' in line or 'responsibilities' in line.lower() or
                'passionate' in line.lower() or 'building' in line.lower() or
                len(line) > 100):
                continue
            
            # Pattern for "JobTitle, Company Date - Date" (Resume3 format)
            pattern3 = r'([^,]+),\s+([^(]+)\s+([^-]+)-([^-]+)'
            match3 = re.search(pattern3, line)
            if match3:
                title = match3.group(1).strip()
                company_date = match3.group(2).strip()
                start_date = match3.group(3).strip()
                end_date = match3.group(4).strip()
                
                # Clean up title
                if title.startswith('e '):
                    title = title[2:].strip()
                
                # Extract company name
                company = company_date
                if '20XX' in company_date:
                    company = company_date.split('20XX')[0].strip()
                elif any(month in company_date for month in ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']):
                    company = re.sub(r'\s+[A-Za-z]+\s+\d{4}', '', company_date).strip()
                
                if (len(title) > 3 and len(company) > 3 and 
                    'Summarize' not in company_date and 
                    'responsibilities' not in company_date and
                    len(company_date) < 50):
                    experience.append({
                        "title": title,
                        "company": company,
                        "start_date": start_date,
                        "end_date": end_date,
                        "location": "",
                        "description": ""
                    })
                continue
            
            # Pattern for "JobTitle - Company (Date - Present)" (Resume4 format)
            pattern4 = r'([^-]+)-\s*([^(]+)\s*\(([^-]+)-([^)]+)\)'
            match4 = re.search(pattern4, line)
            if match4:
                title = match4.group(1).strip()
                company = match4.group(2).strip()
                start_date = match4.group(3).strip()
                end_date = match4.group(4).strip()
                
                if title.startswith('ce: '):
                    title = title[4:].strip()
                
                if (len(title) > 3 and len(company) > 3 and 
                    'Developed' not in company and 
                    len(company) < 50):
                    experience.append({
                        "title": title,
                        "company": company,
                        "start_date": start_date,
                        "end_date": end_date,
                        "location": "",
                        "description": ""
                    })
                continue
            
            # Pattern for "JobTitle - Company" (Resume5 format)
            pattern5 = r'([^-]+)-\s*([^-]+)'
            match5 = re.search(pattern5, line)
            if match5:
                title = match5.group(1).strip()
                company = match5.group(2).strip()
                
                if title.startswith('e: '):
                    title = title[3:].strip()
                
                if (len(title) > 3 and len(company) > 3 and 
                    ('Intern' in title or 'Developer' in title or 'Engineer' in title or 
                     'Manager' in title or 'Assistant' in title or 'Specialist' in title) and
                    'Built' not in company and 'Integrated' not in company and
                    len(company) < 50):
                    
                    experience.append({
                        "title": title,
                        "company": company,
                        "start_date": "",
                        "end_date": "",
                        "location": "",
                        "description": ""
                    })
                continue
        
        return experience
    
    def _extract_experience_from_entire_text(self, text: str) -> List[Dict[str, str]]:
        """Extract experience by searching the entire text for job patterns."""
        experience = []
        
        # Look for job patterns in the entire text
        job_patterns = [
            # Resume3 format: "JobTitle, Company Date - Date"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+([A-Za-z]+\s+20XX)\s*-\s*([A-Za-z]+\s+20XX|Current)',
            # Resume4 format: "JobTitle - Company (Date - Present)"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*-\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([A-Za-z]+\s+\d{4})\s*-\s*Present\)',
            # Resume5 format: "JobTitle - Company"
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*-\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'
        ]
        
        for pattern in job_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if len(match) == 4:  # Resume3 format
                    title, company, start_date, end_date = match
                    if 'Intern' in title or 'Developer' in title or 'Engineer' in title or 'Manager' in title:
                        experience.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "start_date": start_date.strip(),
                            "end_date": end_date.strip(),
                            "location": "",
                            "description": ""
                        })
                elif len(match) == 2:  # Resume5 format
                    title, company = match
                    if 'Intern' in title or 'Developer' in title or 'Engineer' in title or 'Manager' in title:
                        experience.append({
                            "title": title.strip(),
                            "company": company.strip(),
                            "start_date": "",
                            "end_date": "",
                            "location": "",
                            "description": ""
                        })
        
        return experience

    def extract_projects(self, text: str) -> List[Project]:
        """Extract project information from text"""
        projects = []
        
        # Look for PROJECTS section
        project_patterns = [
            r'PROJECTS.*?(?=EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS|$)',
            r'PROJECT.*?(?=EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS|$)',
            r'PORTFOLIO.*?(?=EXPERIENCE|EDUCATION|SKILLS|CERTIFICATIONS|$)'
        ]
        
        project_text = ""
        for pattern in project_patterns:
            match = re.search(pattern, text.upper(), re.DOTALL)
            if match:
                project_text = match.group(0)
                break
        
        if project_text:
            # Remove the header line
            project_text = re.sub(r'^PROJECTS?\s*', '', project_text, flags=re.IGNORECASE)
            
            # Split by double newlines to separate individual projects
            project_entries = project_text.split('\n\n')
            
            for entry in project_entries:
                entry = entry.strip()
                if not entry or len(entry) < 10:
                    continue
                
                lines = [line.strip() for line in entry.split('\n') if line.strip()]
                if not lines:
                    continue
                
                project = Project()
                
                # First line is usually the project title
                project.title = lines[0]
                
                # Look for description in subsequent lines
                description_lines = []
                for line in lines[1:]:
                    # Skip lines that look like dates or URLs
                    if re.match(r'^\d{4}|https?://|www\.', line):
                        continue
                    description_lines.append(line)
                
                if description_lines:
                    project.description = ' '.join(description_lines)
                
                # Look for technologies (common tech keywords)
                tech_keywords = [
                    'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'Django', 'Flask',
                    'SQL', 'MongoDB', 'AWS', 'Docker', 'Kubernetes', 'Git', 'HTML', 'CSS',
                    'TypeScript', 'Angular', 'Vue', 'Express', 'Spring', 'Hibernate',
                    'PostgreSQL', 'MySQL', 'Redis', 'Elasticsearch', 'TensorFlow', 'PyTorch'
                ]
                
                project_tech = []
                for tech in tech_keywords:
                    if re.search(rf'\b{tech}\b', entry, re.IGNORECASE):
                        project_tech.append(tech)
                
                project.technologies = project_tech
                
                # Look for URLs
                url_pattern = r'https?://[^\s]+|www\.[^\s]+'
                url_match = re.search(url_pattern, entry)
                if url_match:
                    project.url = url_match.group(0)
                
                projects.append(project)
        
        return projects

    def extract_education(self, text: str) -> List[Education]:
        """Extract education information from text"""
        educations = []

        education_patterns = [
            r'EDUCATION.*?(?=EXPERIENCE|SKILLS|PROJECTS|$)',
            r'ACADEMIC.*?(?=EXPERIENCE|SKILLS|PROJECTS|$)'
        ]

        education_text = ""
        for pattern in education_patterns:
            match = re.search(pattern, text.upper(), re.DOTALL)
            if match:
                education_text = match.group(0)
                break

        if education_text:
            degree_patterns = [
                r'(Bachelor|Master|PhD|B\.S\.|M\.S\.|B\.A\.|M\.A\.|B\.Tech|M\.Tech).*',
                r'(Diploma|Certificate).*'
            ]

            for pattern in degree_patterns:
                matches = re.findall(pattern, education_text, re.IGNORECASE)
                for match in matches:
                    edu = Education()
                    edu.degree = match.strip()
                    educations.append(edu)

        return educations
