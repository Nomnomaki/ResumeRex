import streamlit as st
import os
import tempfile
from extractor import extract_resume_info, validate_resume_content
from model import get_resume_feedback, generate_report, suggest_skill_improvements
from scap import search_jobs, save_jobs_to_csv
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="ResumeRex - AI Job Hunter", 
    page_icon="🦖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #2E8B57;
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .job-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .relevance-high { border-left: 5px solid #28a745; }
    .relevance-medium { border-left: 5px solid #ffc107; }
    .relevance-low { border-left: 5px solid #dc3545; }
    .stButton > button[disabled] {
        background-color: #e9ecef !important;
        color: #6c757d !important;
        border: 1px solid #dee2e6 !important;
        cursor: not-allowed !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'resume_processed' not in st.session_state:
    st.session_state.resume_processed = False
if 'resume_text' not in st.session_state:
    st.session_state.resume_text = ""
if 'keywords' not in st.session_state:
    st.session_state.keywords = []

# Main header
st.markdown('<h1 class="main-header">🦖 ResumeRex</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Your AI-powered job hunting companion</p>', unsafe_allow_html=True)

st.markdown("""
**ResumeRex** analyzes your resume, provides intelligent feedback, and finds matching job opportunities 
based on your skills and preferences. Get started by uploading your resume below! 📄✨
""")

# Sidebar for settings
with st.sidebar:
    st.header("⚙️ Settings")
    max_jobs = st.slider("Max jobs to find", 5, 25, 10)
    keyword_count = st.slider("Keywords to extract", 5, 20, 10)
    search_logic = st.radio("Search logic", ["Smart (Recommended)", "Broad (OR)", "Precise (AND)"])
    
    st.header("📊 Quick Stats")
    if st.session_state.resume_processed:
        st.metric("Resume Length", f"{len(st.session_state.resume_text.split())} words")
        st.metric("Keywords Found", len(st.session_state.keywords))

# File upload
uploaded_file = st.file_uploader(
    "📤 Upload your Resume (PDF or TXT)", 
    type=["pdf", "txt"],
    help="Upload your resume in PDF or TXT format for analysis"
)

if uploaded_file:
    # Create columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        with st.spinner("🔄 Processing your resume..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    temp_path = tmp_file.name

                # Extract resume information
                resume_text, keywords = extract_resume_info(temp_path, keyword_count)
                
                # Validate resume content
                if not validate_resume_content(resume_text):
                    st.warning("⚠️ This doesn't appear to be a typical resume. Please check your file.")
                
                # Store in session state
                st.session_state.resume_processed = True
                st.session_state.resume_text = resume_text
                st.session_state.keywords = keywords
                
                # Clean up temp file
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                
                st.success("✅ Resume processed successfully!")
                
            except Exception as e:
                st.error(f"❌ Error processing resume: {str(e)}")
                # Clean up temp file in case of error
                if 'temp_path' in locals() and os.path.exists(temp_path):
                    os.unlink(temp_path)

    with col2:
        if st.session_state.resume_processed:
            st.info(f"📊 **File:** {uploaded_file.name}\n\n📝 **Words:** {len(st.session_state.resume_text.split())}\n\n🏷️ **Keywords:** {len(st.session_state.keywords)}")

if st.session_state.resume_processed:
    
    # Resume Analysis Section
    st.header("📋 Resume Analysis")
    
    # Create tabs for different analyses
    tab1, tab2, tab3 = st.tabs(["💬 AI Feedback", "🏷️ Keywords & Summary", "💡 Skill Suggestions"])
    
    with tab1:
        with st.spinner("🤖 Getting AI feedback..."):
            try:
                feedback = get_resume_feedback(st.session_state.resume_text)
                st.markdown(feedback)
            except Exception as e:
                st.error(f"❌ Error getting AI feedback: {str(e)}")
    
    with tab2:
        try:
            report = generate_report(st.session_state.resume_text, st.session_state.keywords)
            st.markdown(report)
            
            # Display keywords as badges
            if st.session_state.keywords:
                st.subheader("🏷️ Extracted Keywords")
                keyword_cols = st.columns(4)
                for i, keyword in enumerate(st.session_state.keywords):
                    with keyword_cols[i % 4]:
                        st.button(keyword, disabled=True, key=f"keyword_{i}")
            else:
                st.info("No keywords extracted from the resume.")
        except Exception as e:
            st.error(f"❌ Error generating report: {str(e)}")
    
    with tab3:
        with st.spinner("💡 Generating skill suggestions..."):
            try:
                suggestions = suggest_skill_improvements(st.session_state.resume_text, st.session_state.keywords)
                st.subheader("💡 Recommended Skills to Learn")
                st.write("Consider adding these trending skills to boost your profile:")
                if suggestions:
                    for suggestion in suggestions:
                        st.write(f"• **{suggestion}**")
                else:
                    st.info("No specific skill suggestions available at the moment.")
            except Exception as e:
                st.error(f"❌ Error generating skill suggestions: {str(e)}")

    # Job Search Section
    st.header("🔍 Job Search")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        job_location = st.text_input(
            "🌍 Preferred Job Location", 
            value="Mumbai, India",
            placeholder="e.g., Mumbai, Delhi, Bangalore",
            help="Enter your preferred job location"
        )
    
    with col2:
        custom_keywords = st.text_input(
            "🔧 Additional Keywords (optional)",
            placeholder="React, Node.js",
            help="Add custom keywords separated by commas"
        )
    
    with col3:
        st.write("")  # Spacing
        search_button = st.button("🚀 Find Matching Jobs", type="primary")

    if search_button:
        if not st.session_state.keywords and not custom_keywords:
            st.warning("⚠️ No keywords available for job search. Please ensure your resume is processed or add custom keywords.")
        else:
            with st.spinner("🔍 Searching for matching jobs..."):
                try:
                    # Prepare search keywords
                    search_keywords = st.session_state.keywords.copy()
                    
                    # Add custom keywords if provided
                    if custom_keywords:
                        custom_kw = [kw.strip() for kw in custom_keywords.split(',') if kw.strip()]
                        search_keywords = custom_kw + search_keywords
                    
                    # Limit keywords for search
                    final_keywords = search_keywords[:8]
                    
                    # Determine search logic
                    use_and = search_logic == "Precise (AND)"
                    
                    st.info(f"🔍 Searching for: `{', '.join(final_keywords)}` in `{job_location}`")

                    # Search for jobs
                    jobs = search_jobs(final_keywords, location=job_location, max_results=max_jobs)

                    if jobs:
                        st.success(f"✅ Found {len(jobs)} matching jobs!")
                        
                        # Save to CSV
                        csv_filename = f"jobs_{job_location.replace(' ', '_').replace(',', '')}.csv"
                        try:
                            csv_saved = save_jobs_to_csv(jobs, csv_filename)
                        except Exception as e:
                            st.warning(f"Could not save to CSV: {str(e)}")
                            csv_saved = False
                        
                        # Display jobs
                        st.subheader("💼 Job Matches")
                        
                        # Sort jobs by relevance if relevance_score exists
                        try:
                            jobs.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
                        except (TypeError, KeyError):
                            pass  # Keep original order if sorting fails
                        
                        for i, job in enumerate(jobs):
                            # Debug: Print job structure to understand the data format
                            
                            
                            # Handle different possible job data structures
                            if isinstance(job, dict):
                                title = job.get('title') or job.get('job_title') or job.get('position') or 'Position Available'
                                company = job.get('company') or job.get('company_name') or job.get('employer') or 'Company Not Specified'
                                location = job.get('location') or job.get('job_location') or job.get('place') or 'Location TBD'
                                posted = job.get('posted') or job.get('date_posted') or job.get('posted_date') or 'Recently'
                                apply_link = job.get('apply_link') or job.get('url') or job.get('link') or '#'
                                relevance = job.get('relevance_score', 0)
                                matched_skills = job.get('matched_skills') or job.get('skills') or 'Skills matching resume'
                            else:
                                # If job is not a dict, try to handle it as a string or other format
                                title = str(job)
                                company = 'Unknown Company'
                                location = 'Unknown Location'
                                posted = 'Unknown Date'
                                apply_link = '#'
                                relevance = 0
                                matched_skills = 'N/A'
                            
                            # Determine relevance class for styling
                            if relevance >= 70:
                                relevance_class = "relevance-high"
                                relevance_emoji = "🟢"
                            elif relevance >= 40:
                                relevance_class = "relevance-medium" 
                                relevance_emoji = "🟡"
                            else:
                                relevance_class = "relevance-low"
                                relevance_emoji = "🔴"
                            
                            # Use Streamlit components instead of HTML for better compatibility
                            with st.container():
                                # Create a styled container using columns
                                col1, col2 = st.columns([4, 1])
                                
                                with col1:
                                    st.subheader(f"🎯 {title}")
                                    st.write(f"**🏢 Company:** {company}")
                                    st.write(f"**📍 Location:** {location}")
                                    st.write(f"**📅 Posted:** {posted}")
                                    st.write(f"**🎯 Match:** {relevance_emoji} {relevance}% | **Skills:** {matched_skills}")
                                
                                with col2:
                                    if apply_link != '#':
                                        st.link_button("👥 Apply Now", apply_link)
                                    else:
                                        st.button("👥 Apply Now", disabled=True, help="No application link available")
                                
                                st.divider()
                        
                        # Download CSV option
                        if csv_saved and os.path.exists(csv_filename):
                            try:
                                with open(csv_filename, 'rb') as file:
                                    st.download_button(
                                        label="📥 Download Job Results (CSV)",
                                        data=file.read(),
                                        file_name=f"jobs_{job_location.replace(' ', '_')}.csv",
                                        mime="text/csv"
                                    )
                            except Exception as e:
                                st.warning(f"⚠️ Could not create download button: {str(e)}")
                    else:
                        st.warning("⚠️ No matching jobs found. Try:")
                        st.write("• Different keywords or location")
                        st.write("• Broader search terms")
                        st.write("• Different job titles")
                        
                except Exception as e:
                    st.error(f"❌ Error searching for jobs: {str(e)}")

