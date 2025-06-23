import pdfplumber
from model import extract_job_keywords_with_gemini

def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() or '' for page in pdf.pages)
    return text

def extract_text_from_txt(txt_path):
    with open(txt_path, 'r', encoding='utf-8') as f:
        return f.read()

def extract_resume_info(resume_path):
    if resume_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(resume_path)
    elif resume_path.lower().endswith('.txt'):
        text = extract_text_from_txt(resume_path)
    else:
        raise ValueError('Unsupported file type. Please use PDF or TXT.')
    keywords = extract_job_keywords_with_gemini(text)
    return text, keywords