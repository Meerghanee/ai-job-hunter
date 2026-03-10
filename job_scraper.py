from jobspy import scrape_jobs
import pandas as pd
import requests
import os
from datetime import datetime
from bs4 import BeautifulSoup

# TELEGRAM SETTINGS
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT TOKEN:", BOT_TOKEN)
print("CHAT ID:", CHAT_ID)

def send_telegram(message):
    try:
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message},
            timeout=10
        )
    except:
        pass


# TEST TELEGRAM
send_telegram("AI Job Hunter is running")


headers = {
    "User-Agent": "Mozilla/5.0"
}


# WELLFOUND SCRAPER
def scrape_wellfound_jobs():

    jobs = []

    try:
        url = "https://wellfound.com/jobs"

        response = requests.get(url, headers=headers)
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

    jobs = []

    try:
        url = "https://www.naukri.com/data-analyst-jobs-in-india"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a", class_="title")

        for job in listings[:15]:

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


# GREENHOUSE SCRAPER
def scrape_greenhouse_jobs():

    jobs = []

    try:
        url = "https://boards.greenhouse.io/embed/job_board?for=stripe"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a")

        for job in listings[:15]:

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


# WORKDAY SCRAPER
def scrape_workday_jobs():

    jobs = []

    try:
        url = "https://deloitte.wd1.myworkdayjobs.com/External"

        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")

        listings = soup.find_all("a")

        for job in listings[:15]:

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
    "credit analyst"
]


location = "India"

print("Starting AI Job Hunter...")


all_jobs = []

for role in roles:

    try:

        print("Searching:", role)

        jobs = scrape_jobs(
            site_name=["linkedin", "indeed"],   # removed glassdoor
            search_term=role,
            location=location,
            results_wanted=60,
            hours_old=2
        )

        if not jobs.empty:
            all_jobs.append(jobs)

    except:
        pass


# CONCAT JOBS
if all_jobs:
    jobs_df = pd.concat(all_jobs)
else:
    jobs_df = pd.DataFrame()


if not jobs_df.empty:

    dashboard = pd.DataFrame({
        "Company": jobs_df["company"],
        "Job Role": jobs_df["title"],
        "Date Posted": datetime.now().date(),
        "Apply Link": jobs_df["job_url"],
        "Source": jobs_df["site"]
    })

else:
    dashboard = pd.DataFrame()


dashboard.drop_duplicates(subset="Apply Link", inplace=True)

dashboard.to_excel("AI_JOB_DASHBOARD.xlsx", index=False)


# LOAD OLD JOBS
if os.path.exists("sent_jobs.csv"):
    old = pd.read_csv("sent_jobs.csv")
    sent_links = set(old["Apply Link"])
else:
    sent_links = set()


new_jobs = []


# TELEGRAM ALERTS
for index, row in dashboard.iterrows():

    link = row["Apply Link"]

    if link not in sent_links:

        message = f"""
New Job Alert

Company: {row['Company']}
Role: {row['Job Role']}
Apply: {link}
Source: {row['Source']}
"""

        send_telegram(message)

        new_jobs.append(row)


# EXTRA SOURCES
extra_jobs = []

extra_jobs.extend(scrape_wellfound_jobs())
extra_jobs.extend(scrape_naukri_jobs())
extra_jobs.extend(scrape_greenhouse_jobs())
extra_jobs.extend(scrape_workday_jobs())


for job in extra_jobs:

    link = job["Apply Link"]

    if link not in sent_links:

        message = f"""
New Job Alert

Company: {job['Company']}
Role: {job['Job Role']}
Apply: {link}
Source: {job['Source']}
"""

        send_telegram(message)

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
