import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("models/gemini-2.5-flash-lite-preview-06-17")

def get_resume_feedback(resume_text):
    prompt = f"""
    This is a resume. Analyze it and give structured feedback:
    - Strengths
    - Weaknesses
    - Skills detected
    - Suggestions for improvement
    Resume:
    {resume_text}
    (dont make it too detailed)
    """
    response = model.generate_content(prompt)
    return response.text

def extract_job_keywords_with_gemini(resume_text, top_n=10):
    prompt = f"""
    Given this resume text, extract the top {top_n} relevant job-related **skills or technologies** 
    (such as programming languages, tools, job roles, domains etc). 
    Return them as a comma-separated list, no full sentences.

    Resume:
    {resume_text}
    """
    response = model.generate_content(prompt)
    raw_keywords = response.text.strip()
    keywords = [kw.strip().lower() for kw in raw_keywords.split(',') if kw.strip()]
    return list(dict.fromkeys(keywords))[:top_n]

def generate_report(resume_text, keywords):
    sentences = resume_text.split('.')
    summary = '.'.join(sentences[:3]).strip() + '.' if len(sentences) >= 3 else resume_text.strip()
    report = f"Resume Summary:\n{summary}\n\nTop Keywords ({len(keywords)}):\n- " + '\n- '.join(keywords)
    return report
