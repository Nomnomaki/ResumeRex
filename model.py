import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-06-17")

def get_resume_feedback(resume_text):
    """Get structured feedback on resume using Gemini AI"""
    prompt = f"""
    Analyze this resume and provide structured feedback in the following format:
    
    **STRENGTHS:**
    - [List 2-3 key strengths]
    
    **WEAKNESSES:**
    - [List 2-3 areas for improvement]
    
    **SKILLS DETECTED:**
    - [List key technical and soft skills found]
    
    **IMPROVEMENT SUGGESTIONS:**
    - [List 2-3 actionable suggestions]
    
    **OVERALL SCORE:** [X/10]
    
    Resume:
    {resume_text}
    
    Keep feedback concise and actionable.
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error generating feedback: {str(e)}"

def extract_job_keywords_with_gemini(resume_text, top_n=10):
    """Extract relevant job keywords from resume using Gemini AI"""
    prompt = f"""
    From this resume, extract the top {top_n} most relevant job-search keywords.
    Focus on:
    - Programming languages (Python, Java, JavaScript, etc.)
    - Frameworks and libraries (React, Django, Spring, etc.)
    - Tools and technologies (Docker, AWS, Git, etc.)
    - Job roles and domains (Data Science, Web Development, etc.)
    - Certifications and skills
    
    Return ONLY a comma-separated list of keywords, nothing else.
    
    Resume:
    {resume_text}
    """
    
    try:
        response = model.generate_content(prompt)
        raw_keywords = response.text.strip()
        # Clean and deduplicate keywords
        keywords = [kw.strip() for kw in raw_keywords.split(',') if kw.strip()]
        # Remove duplicates while preserving order
        unique_keywords = []
        seen = set()
        for kw in keywords:
            kw_lower = kw.lower()
            if kw_lower not in seen:
                unique_keywords.append(kw)
                seen.add(kw_lower)
        return unique_keywords[:top_n]
    except Exception as e:
        print(f"Error extracting keywords: {e}")
        return ["Python", "JavaScript", "React", "Django", "AWS"]  # Fallback keywords

def generate_report(resume_text, keywords):
    """Generate a summary report of the resume analysis"""
    sentences = resume_text.split('.')
    summary = '.'.join(sentences[:3]).strip() + '.' if len(sentences) >= 3 else resume_text.strip()
    
    report = f"""**RESUME ANALYSIS REPORT**

**Summary:**
{summary}

**Extracted Skills & Keywords ({len(keywords)}):**
{', '.join(f'`{kw}`' for kw in keywords)}

**Keywords for Job Search:**
These keywords will be used to find relevant job opportunities that match your profile.
"""
    return report

def suggest_skill_improvements(resume_text, keywords):
    """Suggest additional skills based on current profile"""
    prompt = f"""
    Based on this resume and extracted keywords: {', '.join(keywords)}
    
    Suggest 5-7 additional skills or technologies that would complement this profile and make the candidate more marketable.
    
    Focus on trending technologies, complementary skills, and industry-relevant certifications.
    
    Return as a comma-separated list.
    
    Resume: {resume_text}
    """
    
    try:
        response = model.generate_content(prompt)
        suggestions = [skill.strip() for skill in response.text.split(',') if skill.strip()]
        return suggestions[:7]
    except Exception as e:
        return ["Cloud Computing", "Machine Learning", "Docker", "Kubernetes", "MongoDB"]
