import streamlit as st
from extractor import extract_resume_info
from model import get_resume_feedback, generate_report
from scap import search_jobs, save_jobs_to_csv

st.set_page_config(page_title="ResumeRex", layout="wide")
st.title("🦖 ResumeRex")

st.markdown(
    """
    _**Your AI-powered job hunting buddy!**_  
    ResumeRex analyzes your resume, gives smart feedback, and finds job listings based on your skills & location preferences.
    """
)

uploaded_file = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"])

if uploaded_file:
    with st.spinner("Processing your resume..."):
        # Save file temporarily
        with open("temp_resume.pdf", "wb") as f:
            f.write(uploaded_file.read())

        resume_text, keywords = extract_resume_info("temp_resume.pdf")
        feedback = get_resume_feedback(resume_text)
        report = generate_report(resume_text, keywords)

        st.subheader("✅ Resume Feedback")
        st.markdown(feedback)

        st.subheader("🧠 Keyword-Based Resume Summary")
        st.text(report)

        # 🔥 Ask the user where they want job recommendations for
        job_location = st.text_input("🌍 Enter Preferred Job Location (e.g., India, Remote, Mumbai)", value="Remote")

        if st.button("🔍 Find Matching Jobs"):
            with st.spinner("Searching for matching jobs..."):
                # ✅ Limit keywords to top 6 before sending to search
                filtered_keywords = keywords[:6]

                st.info(f"🔍 Searching for: `{', '.join(filtered_keywords)}` in `{job_location}`")

                jobs = search_jobs(filtered_keywords, location=job_location)
                save_jobs_to_csv(jobs)

                if jobs:
                    st.success(f"✅ Found {len(jobs)} jobs for you!")
                    for job in jobs:
                        st.markdown(f"""
                        ### {job['title']}
                        **Company**: {job['company']}  
                        **Location**: {job['location']}  
                        **Posted**: {job['posted']}  
                        [👉 Apply Here]({job['apply_link']})
                        """)
                else:
                    st.warning("⚠️ No jobs found. Try changing keywords or location.")
