from jobspy import scrape_jobs
import pandas as pd
import requests
import os
from datetime import datetime

# TELEGRAM SETTINGS
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

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

# LOCATION (INDIA ONLY)
location = "India"

print("Starting AI Job Hunter for India...")

all_jobs = []

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

jobs_df = pd.concat(all_jobs)

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

filtered_jobs = jobs_df[
    jobs_df["title"].str.lower().str.contains("|".join(exp_keywords), na=False)
]

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
dashboard.to_excel(r"C:\Users\meerg\Desktop\AI_JOB_DASHBOARD.xlsx", index=False)

# LOAD SENT JOBS
if os.path.exists("sent_jobs.csv"):
    old = pd.read_csv("sent_jobs.csv")
    sent_links = set(old["Apply Link"])
else:
    sent_links = set()

new_jobs = []

# SEND TELEGRAM ALERTS
for index,row in dashboard.iterrows():

    if row["Apply Link"] not in sent_links:

        message=f"""
New Job Alert

Company: {row['Company']}
Role: {row['Job Role']}
Apply: {row['Apply Link']}
"""

        url=f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

        requests.post(url,data={"chat_id":CHAT_ID,"text":message})

        new_jobs.append(row)

# SAVE NEW JOBS
if new_jobs:

    new_df=pd.DataFrame(new_jobs)

    if os.path.exists("sent_jobs.csv"):
        old_df=pd.read_csv("sent_jobs.csv")
        combined=pd.concat([old_df,new_df])
    else:
        combined=new_df

    combined.to_csv("sent_jobs.csv",index=False)

print("Job alerts sent successfully.")






