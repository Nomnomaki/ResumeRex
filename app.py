# CLI version. For web interface, see streamlit_app.py
import argparse
from extractor import extract_resume_info
from model import generate_report
from scap import search_jobs, save_jobs_to_csv


def main():
    parser = argparse.ArgumentParser(description='Job-GenAI: Resume Analyzer and Job Finder')
    parser.add_argument('--resume', required=True, help='Path to resume file (PDF or TXT)')
    parser.add_argument('--location', default='Remote', help='Job search location (default: Remote)')
    parser.add_argument('--num_jobs', type=int, default=10, help='Number of jobs to fetch (default: 10)')
    args = parser.parse_args()

    print(f"\n[1/5] Extracting info from {args.resume} ...")
    text, keywords = extract_resume_info(args.resume)
    print(f"Extracted {len(keywords)} keywords: {keywords}\n")

    print("[2/5] Generating report ...")
    report = generate_report(text, keywords)
    print(report)

    print("\n[3/5] Searching for jobs ...")
    jobs = search_jobs(keywords, location=args.location, num_results=args.num_jobs)
    print(f"Found {len(jobs)} jobs.")

    print("[4/5] Saving jobs to job_results.csv ...")
    save_jobs_to_csv(jobs)
    print("Jobs saved to job_results.csv\n")

    print("[5/5] Done!")

if __name__ == '__main__':
    main()
