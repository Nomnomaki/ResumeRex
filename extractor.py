import pdfplumber
import os
from model import extract_job_keywords_with_gemini

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = "\n".join(page.extract_text() or '' for page in pdf.pages)
        return text.strip()
    except Exception as e:
        raise ValueError(f"Error reading PDF: {str(e)}")

def extract_text_from_txt(txt_path):
    """Extract text from TXT file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        raise ValueError(f"Error reading TXT file: {str(e)}")

def extract_resume_info(resume_path, keyword_count=10):
    """Extract text and keywords from resume file"""
    if not os.path.exists(resume_path):
        raise FileNotFoundError(f"Resume file not found: {resume_path}")
    
    file_extension = resume_path.lower().split('.')[-1]
    
    if file_extension == 'pdf':
        text = extract_text_from_pdf(resume_path)
    elif file_extension == 'txt':
        text = extract_text_from_txt(resume_path)
    else:
        raise ValueError('Unsupported file type. Please use PDF or TXT files only.')
    
    if not text.strip():
        raise ValueError("No text found in the resume file.")
    
    # Extract keywords using Gemini
    keywords = extract_job_keywords_with_gemini(text, keyword_count)
    
    return text, keywords

def validate_resume_content(text):
    """Basic validation to check if text looks like a resume"""
    resume_indicators = [
        'experience', 'education', 'skills', 'work', 'job', 'project',
        'university', 'college', 'degree', 'certification', 'email'
    ]
    
    text_lower = text.lower()
    found_indicators = sum(1 for indicator in resume_indicators if indicator in text_lower)
    
    return found_indicators >= 3  # At least 3 resume-like terms
