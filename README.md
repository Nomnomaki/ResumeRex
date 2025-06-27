# 📄 ResumeRex
**ResumeRex** is a fun and smart GenAI-powered Streamlit web app that analyzes your resume, provides actionable feedback, and recommends matching job listings in your preferred location — all in seconds!
---
## 🚀 Features
- 📤 Upload your resume (PDF or TXT)  
- 🧠 Extracts and highlights key skills using AI  
- ✅ Instant resume feedback via Google Gemini  
- 🌍 Enter preferred job location  
- 🔍 Finds real-time matching jobs from Google Jobs using SerpAPI  
- 🔗 Direct apply links included for each job
---
## 🛠️ Tech Stack
- **Frontend/UI**: Streamlit  
- **Backend**: Python  
- **AI/GenAI**: Google Gemini API (via `model.py`)  
- **PDF Processing**: pdfplumber  
- **Job Scraping**: SerpAPI (Google Jobs engine)
---
## 🧑‍💻 Getting Started
### 1. Clone the repository
```bash
git clone https://github.com/your-username/resumerex.git
cd resumerex
```
### 2. Install dependencies
```bash
pip install -r requirements.txt
```
### 3. Setup environment variables
Create a `.env` file in the root folder:
```ini
SERPAPI_API_KEY=your_serpapi_api_key
GOOGLE_API_KEY=your_gemini_api_key
```
> 🚨 Keep this file private and **never push it to GitHub**.
### 4. Run the Streamlit app
```bash
streamlit run app.py
```
---
## 📂 Project Structure
```text
resumerex/
│
├── app.py               # Main Streamlit app  
├── extractor.py         # Resume parser and keyword extractor  
├── model.py             # Resume feedback via Google Gemini  
├── scap.py              # Job search via SerpAPI  
├── requirements.txt  
├── .env                 # API keys (excluded from Git)  
├── .gitignore  
└── README.md
```
---
## 💡 Why ResumeRex?
Job seekers often struggle with resume quality and finding the right opportunities. **ResumeRex** helps solve both problems using the power of generative AI and real-time job search — all wrapped in a playful and easy-to-use interface.
---
