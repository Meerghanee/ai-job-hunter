from jobspy import scrape_jobs
import pandas as pd
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup


# TELEGRAM SETTINGS
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


# WELLFOUND STARTUP SCRAPER
def scrape_wellfound_jobs():

    url = "https://wellfound.com/jobs"
    jobs = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a", {"data-test": "job-link"})

        for job in listings[:10]:

            title = job.text.strip()
            link = "https://wellfound.com" + job.get("href")

            jobs.append({
                "Company": "Startup",
                "Job Role": title,
                "Apply Link": link,
                "Source": "Wellfound"
            })

    except:
        pass

    return jobs


# NAUKRI SCRAPER
def scrape_naukri_jobs():

    url = "https://www.naukri.com/data-analyst-jobs-in-india"
    jobs = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a", class_="title")

        for job in listings[:20]:

            title = job.text.strip()
            link = job.get("href")

            jobs.append({
                "Company": "Various",
                "Job Role": title,
                "Apply Link": link,
                "Source": "Naukri"
            })

    except:
        pass

    return jobs


# GREENHOUSE ATS SCRAPER
def scrape_greenhouse_jobs():

    url = "https://boards.greenhouse.io/embed/job_board?for=stripe"
    jobs = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a")

        for job in listings[:20]:

            title = job.text.strip()
            link = job.get("href")

            if link and "greenhouse.io" in link:

                jobs.append({
                    "Company": "Startup",
                    "Job Role": title,
                    "Apply Link": link,
                    "Source": "Greenhouse"
                })

    except:
        pass

    return jobs


# WORKDAY ATS SCRAPER
def scrape_workday_jobs():

    url = "https://deloitte.wd1.myworkdayjobs.com/External"
    jobs = []

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a")

        for job in listings[:20]:

            title = job.text.strip()
            link = job.get("href")

            if link and "myworkdayjobs" in link:

                jobs.append({
                    "Company": "Workday Company",
                    "Job Role": title,
                    "Apply Link": link,
                    "Source": "Workday"
                })

    except:
        pass

    return jobs


# JOB ROLES
roles = [
    "data analyst",
    "financial analyst",
    "business analyst",
    "investment analyst",
    "equity research analyst",
    "research analyst",
    "esg analyst",
    "corporate finance analyst",
    "risk analyst",
    "credit analyst",
    "valuation analyst",
    "finance associate",
    "data science intern",
    "business analyst intern"
]


# LOCATION
location = "India"

print("Starting AI Job Hunter for India...")

all_jobs = []


# SCRAPE MAIN JOB PORTALS
for role in roles:

    print(f"Searching for: {role} in India")

    jobs = scrape_jobs(
        site_name=["linkedin", "indeed", "glassdoor"],
        search_term=role,
        location=location,
        results_wanted=80,
        hours_old=2
    )

    all_jobs.append(jobs)


# SAFER CONCAT
jobs_df = pd.concat([df for df in all_jobs if not df.empty])


# EXPERIENCE FILTER
exp_keywords = [
    "entry",
    "junior",
    "associate",
    "intern",
    "trainee",
    "0 year",
    "0-1",
    "0-2",
    "0-3",
    "fresher"
]

filtered_jobs = jobs_df


# CLEAN DASHBOARD
dashboard = pd.DataFrame({
    "Company": filtered_jobs["company"],
    "Job Role": filtered_jobs["title"],
    "Job Level": filtered_jobs["title"],
    "Date Posted": datetime.now().date(),
    "Time Posted": datetime.now().strftime("%H:%M"),
    "Apply Link": filtered_jobs["job_url"],
    "Source": filtered_jobs["site"]
})


# REMOVE DUPLICATES
dashboard.drop_duplicates(subset="Apply Link", inplace=True)


# SAVE EXCEL DASHBOARD
dashboard.to_excel("AI_JOB_DASHBOARD.xlsx", index=False)


# LOAD SENT JOBS
if os.path.exists("sent_jobs.csv"):
    old = pd.read_csv("sent_jobs.csv")
    sent_links = set(old["Apply Link"])
else:
    sent_links = set()


new_jobs = []


# TELEGRAM ALERTS FROM MAIN PORTALS
for index, row in dashboard.iterrows():

    if row["Apply Link"] not in sent_links:

        message = f"""
New Job Alert

Company: {row['Company']}
Role: {row['Job Role']}
Apply: {row['Apply Link']}
Source: {row['Source']}
"""

        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(url, data={"chat_id": CHAT_ID, "text": message})

        new_jobs.append(row)


# WELLFOUND JOBS
for job in scrape_wellfound_jobs():

    if job["Apply Link"] not in sent_links:

        message = f"""
New Startup Job

Company: {job['Company']}
Role: {job['Job Role']}
Apply: {job['Apply Link']}
Source: {job['Source']}
"""

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        new_jobs.append(job)


# NAUKRI JOBS
for job in scrape_naukri_jobs():

    if job["Apply Link"] not in sent_links:

        message = f"""
New Job (Naukri)

Company: {job['Company']}
Role: {job['Job Role']}
Apply: {job['Apply Link']}
Source: {job['Source']}
"""

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        new_jobs.append(job)


# GREENHOUSE JOBS
for job in scrape_greenhouse_jobs():

    if job["Apply Link"] not in sent_links:

        message = f"""
New Startup Job (Greenhouse)

Company: {job['Company']}
Role: {job['Job Role']}
Apply: {job['Apply Link']}
Source: {job['Source']}
"""

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        new_jobs.append(job)


# WORKDAY JOBS
for job in scrape_workday_jobs():

    if job["Apply Link"] not in sent_links:

        message = f"""
New Job (Workday)

Company: {job['Company']}
Role: {job['Job Role']}
Apply: {job['Apply Link']}
Source: {job['Source']}
"""

        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message}
        )

        new_jobs.append(job)


# SAVE NEW JOBS
if new_jobs:

    new_df = pd.DataFrame(new_jobs)

    if os.path.exists("sent_jobs.csv"):
        old_df = pd.read_csv("sent_jobs.csv")
        combined = pd.concat([old_df, new_df])
    else:
        combined = new_df

    combined.to_csv("sent_jobs.csv", index=False)


print("Job alerts sent successfully.")


