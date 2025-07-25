"""
Pydantic models for resume parsing
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class ContactInfo(BaseModel):
    """Contact information model"""
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    website: Optional[str] = None


class Experience(BaseModel):
    """Work experience model"""
    title: Optional[str] = None
    company: Optional[str] = None
    location: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[str] = None


class Education(BaseModel):
    """Education model"""
    degree: Optional[str] = None
    institution: Optional[str] = None
    location: Optional[str] = None
    graduation_date: Optional[str] = None
    gpa: Optional[str] = None
    field_of_study: Optional[str] = None


class Project(BaseModel):
    """Project model"""
    title: Optional[str] = None
    description: Optional[str] = None
    technologies: List[str] = Field(default_factory=list)
    url: Optional[str] = None
    duration: Optional[str] = None


class Certification(BaseModel):
    """Certification model"""
    name: Optional[str] = None
    issuer: Optional[str] = None
    date: Optional[str] = None
    expiry_date: Optional[str] = None
    credential_id: Optional[str] = None


class SkillsExtracted(BaseModel):
    """Extracted skills model"""
    programming_languages: List[str] = Field(default_factory=list)
    frameworks: List[str] = Field(default_factory=list)
    databases: List[str] = Field(default_factory=list)
    tools: List[str] = Field(default_factory=list)
    soft_skills: List[str] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    data_science: List[str] = Field(default_factory=list)
    all_skills: List[str] = Field(default_factory=list)


class ParsedResume(BaseModel):
    """Complete parsed resume model"""
    contact_info: ContactInfo = Field(default_factory=ContactInfo)
    summary: Optional[str] = None
    experience: List[Experience] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    skills: SkillsExtracted = Field(default_factory=SkillsExtracted)
    projects: List[Project] = Field(default_factory=list)
    certifications: List[Certification] = Field(default_factory=list)
    raw_text: Optional[str] = None
    parsing_metadata: Dict[str, Any] = Field(default_factory=dict)


class ResumeUploadResponse(BaseModel):
    """Response model for resume upload"""
    success: bool
    message: str
    file_id: Optional[str] = None
    parsed_data: Optional[ParsedResume] = None
    processing_time: Optional[float] = None


class ErrorResponse(BaseModel):
    """Error response model"""
    success: bool = False
    message: str
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
