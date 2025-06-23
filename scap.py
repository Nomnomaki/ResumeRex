import os
import csv
import time
import requests
from serpapi import GoogleSearch
from dotenv import load_dotenv

# Load API Key
load_dotenv()
API_KEY = os.getenv("SERPAPI_API_KEY")

if not API_KEY:
    print("⚠️  Warning: SERPAPI_API_KEY not found. Job search functionality will be limited.")

def normalize_location(location):
    """Normalize location format for better search results"""
    # if not location or location.strip().lower() in ["remote", "anywhere"]:
    #     return "Remote"
    
    location = location.strip()
    if "," in location:
        return location
    
    # # Add country if not specified
    # common_cities = ["mumbai", "delhi", "bangalore", "pune", "chennai", "hyderabad"]
    # if location.lower() in common_cities:
    #     return f"{location}, India"
    # return location

def search_jobs_from_skills(skills, location="Remote", max_results=10, use_and_logic=False):
    """Enhanced job search with better error handling and filtering"""
    if not API_KEY:
        print("[ERROR] SerpAPI key not configured. Cannot search jobs.")
        return []
        
    if not skills or not isinstance(skills, list):
        print("[ERROR] Skills must be a non-empty list.")
        return []

    # Clean and prepare skills
    cleaned_skills = [skill.strip() for skill in skills if skill.strip()][:6]
    
    if not cleaned_skills:
        print("[ERROR] No valid skills provided.")
        return []
    
    # Smart query construction
    if use_and_logic or len(cleaned_skills) <= 3:
        query = " AND ".join(cleaned_skills[:3])
    else:
        # Use most important skills with OR logic
        query = " OR ".join(cleaned_skills[:5])
    
    normalized_location = normalize_location(location)
    
    print(f"\n🔍 Searching for: {query}")
    print(f"📍 Location: {normalized_location}")

    params = {
        "engine": "google_jobs",
        "q": query,
        "location": normalized_location,
        "hl": "en",
        "api_key": API_KEY,
        "num": min(max_results, 50)
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict()
        
        # Respect rate limits
        time.sleep(0.5)
        
        if "error" in results:
            print(f"[ERROR] API Error: {results['error']}")
            return []

        jobs = results.get("jobs_results", [])
        if not jobs:
            print("[INFO] No jobs found. Try different keywords or location.")
            return []

        print(f"✅ Found {len(jobs)} potential matches")
        final_jobs = []

        for idx, job in enumerate(jobs[:max_results], start=1):
            # Extract job details with better error handling
            title = job.get("title", "N/A")
            company = job.get("company_name", "N/A")
            location_job = job.get("location", "N/A")
            description = job.get("description", "")
            
            # Extract posting date
            posted = "Recently"
            if job.get("detected_extensions") and job["detected_extensions"].get("posted_at"):
                posted = job["detected_extensions"]["posted_at"]
            
            # Extract apply link
            apply_link = "#"
            if job.get("apply_options") and len(job["apply_options"]) > 0:
                apply_link = job["apply_options"][0].get("link", "#")
            elif job.get("link"):
                apply_link = job.get("link", "#")
            
            # Extract salary
            salary = "Not specified"
            if job.get("detected_extensions") and job["detected_extensions"].get("salary"):
                salary = job["detected_extensions"]["salary"]
            
            # Skill matching
            job_content = f"{title} {description}".lower()
            matched_skills = [skill for skill in cleaned_skills 
                            if skill.lower() in job_content]
            
            # Calculate relevance score
            relevance_score = len(matched_skills) / len(cleaned_skills) * 100
            
            print(f"{idx}. {title}")
            print(f"   🏢 {company} | 📍 {location_job}")
            print(f"   📅 {posted} | 💰 {salary}")
            print(f"   🎯 Match: {relevance_score:.0f}% ({len(matched_skills)}/{len(cleaned_skills)} skills)")
            print(f"   🔗 {apply_link[:50]}{'...' if len(apply_link) > 50 else ''}\n")

            final_jobs.append({
                "title": title,
                "company": company,
                "location": location_job,
                "posted": posted,
                "salary": salary,
                "description": description[:300] + "..." if len(description) > 300 else description,
                "apply_link": apply_link,
                "matched_skills": ", ".join(matched_skills),
                "relevance_score": round(relevance_score, 1)
            })

        # Sort by relevance score
        final_jobs.sort(key=lambda x: x['relevance_score'], reverse=True)
        return final_jobs

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error: {e}")
        return []
    except Exception as e:
        print(f"[ERROR] Search error: {e}")
        return []

def search_jobs(skills, location="Remote", max_results=10):
    """Wrapper function for compatibility"""
    return search_jobs_from_skills(skills, location, max_results)

def save_jobs_to_csv(jobs, filename="job_matches.csv"):
    """Save jobs to CSV with enhanced data"""
    if not jobs:
        print("[INFO] No jobs to save.")
        return False
    
    try:
        with open(filename, mode="w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([
                "Title", "Company", "Location", "Posted", "Salary", 
                "Matched Skills", "Relevance %", "Apply Link", "Description"
            ])
            
            for job in jobs:
                writer.writerow([
                    job.get('title', 'N/A'),
                    job.get('company', 'N/A'),
                    job.get('location', 'N/A'),
                    job.get('posted', 'N/A'),
                    job.get('salary', 'N/A'),
                    job.get('matched_skills', 'N/A'),
                    job.get('relevance_score', 0),
                    job.get('apply_link', 'N/A'),
                    job.get('description', 'N/A')
                ])
        
        print(f"✅ Saved {len(jobs)} jobs to '{filename}'")
        return True
        
    except Exception as e:
        print(f"[ERROR] Failed to save CSV: {e}")
        return False
