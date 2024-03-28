#Scraping of Company Profiles (FDM vs Competitors)
##Grad Connection

import pandas as pd
from bs4 import BeautifulSoup
import urllib
import urllib.request
import requests
from pprint import pprint
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize WebDriver
options = Options()
#options.add_argument('--headless=new')  # Runs Chrome in headless mode.
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Path to Chromium binary
options.add_experimental_option("detach", True)  # Prevent auto-closure
wd = webdriver.Chrome(options=options)

# Example nested dictionary structure for company URLs
companies_info = {
    "FDM Group - Australia": {
        "Jobs": "https://au.gradconnection.com/employers/fdm-group/jobs/"

    },
    "Accenture - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/accenture/jobs/"
    },
    "Amazon - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/amazon/jobs/"

    },
    "Aurecon - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/aurecon/jobs/"
    },
    "Arup - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/arup/jobs/"

    },
    "Aecom - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/aecom/jobs/"
    },
    "HSBC - Hong Kong":{
        "Jobs": "https://au.gradconnection.com/employers/hsbc-hk/jobs/"
    },
    "OKX - Hong Kong":{
        "Jobs": "https://au.gradconnection.com/employers/okx-hk/jobs/"
    },
    "Wiley Edge - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/wiley-edge/jobs/"

    },
    "Jane Street - Australia":{
        "Jobs": "https://au.gradconnection.com/employers/jane-street/"
    }

    # Add more companies and their URLs as needed
}

#scraping job listings on each company profile

def scrape_job_listings(job_url):
    """Scrapes job listings and their details from the given URL."""
    wd.get(job_url)
    job_details = []
    try:
        # Scroll down to load all job listings
        wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Adjust sleep time as needed

        # Scraping job details
        job_elements = wd.find_elements(By.CLASS_NAME, "box-header-title")  # Example class name
        for job_element in job_elements:

            job_link_url = job_element.get_attribute("href")

            # Switching to the new window
            wd.execute_script("window.open();")
            wd.switch_to.window(wd.window_handles[-1])
            wd.get(job_link_url)

            # Wait for the detail page to load
            WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "campaign-content-container")))

            # Scraping from individual job detail page
            job_detail_element = wd.find_element(By.CLASS_NAME, "campaign-content-container")
            job_detail_text = job_detail_element.text.strip()
            job_title_element = wd.find_element(By.CLASS_NAME, "employers-profile-h1")
            job_title = job_title_element.text.strip()
            job_detail = {"title": job_title, "detail": job_detail_text}
            job_details.append(job_detail)

            # Closing the new window and switching back to the main window
            wd.close()
            wd.switch_to.window(wd.window_handles[0])

        return job_details
    except Exception as e:
        print(f"Error scraping job listings from {job_url}: {e}")
        return []

# Scraping job listings for each company
job_listings = {}

for company_name, urls in companies_info.items():
    if "Jobs" in urls:
        job_url = urls["Jobs"]
        job_listings[company_name] = scrape_job_listings(job_url)

# Close Selenium WebDriver
wd.quit()

import csv

# Save job listings to CSV
with open("job_listings.csv", "w", newline="", encoding="utf-8") as csvfile:
    fieldnames = ["Company Name", "Job Title", "Job Details"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for company_name, jobs in job_listings.items():
        for job in jobs:
            writer.writerow({"Company Name": company_name, "Job Title": job["title"], "Job Details": job["detail"]})



