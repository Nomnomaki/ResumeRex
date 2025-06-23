import os
import csv
import serpapi
from dotenv import load_dotenv

load_dotenv()
serpapi.api_key = os.getenv("SERPAPI_API_KEY")  # set the API key here

def search_jobs_from_skills(skills, location="India", max_results=10):
    cleaned_skills = [skill.strip() for skill in skills if skill.strip()][:6]
    query = " OR ".join(cleaned_skills)
    location = location.strip().split(",")[0]

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": location,
        "hl": "en",
        "api_key": serpapi.api_key
    }

    try:
        search = serpapi.GoogleSearch(params)
        results = search.get_dict()

        jobs = results.get("jobs_results", [])
        if not jobs:
            print("[INFO] No jobs found for this query.")
            return []

        # Save to CSV and prepare jobs list as before
        csv_file = "matched_jobs.csv"
        with open(csv_file, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Title", "Company", "Location", "Posted", "Apply Link"])

            final_jobs = []

            for idx, job in enumerate(jobs[:max_results], start=1):
                title = job.get("title", "N/A")
                company = job.get("company_name", "N/A")
                loc = job.get("location", "N/A")
                posted = job.get("detected_extensions", {}).get("posted_at", "N/A")

                apply_link = "N/A"
                if "apply_options" in job and job["apply_options"]:
                    apply_link = job["apply_options"][0].get("link", "N/A")
                elif "link" in job:
                    apply_link = job.get("link", "N/A")

                print(f"{idx}. {title} | {company} | {loc} | {posted}\n   Apply: {apply_link}\n")

                writer.writerow([title, company, loc, posted, apply_link])
                final_jobs.append({
                    "title": title,
                    "company": company,
                    "location": loc,
                    "posted": posted,
                    "apply_link": apply_link
                })

        print(f"\n✅ Saved {len(final_jobs)} jobs to {csv_file}")
        return final_jobs

    except Exception as e:
        print(f"[ERROR] SerpAPI error: {e}")
        return []

def search_jobs(skills, location="India"):
    return search_jobs_from_skills(skills, location)

def save_jobs_to_csv(jobs, filename="matched_jobs.csv"):
    if not jobs:
        return
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Company", "Location", "Posted", "Apply Link"])
        for job in jobs:
            writer.writerow([job['title'], job['company'], job['location'], job['posted'], job['apply_link']])
