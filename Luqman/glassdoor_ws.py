import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time

def get_jobs(graduate, num_jobs, verbose):
    options = Options()
    options.add_argument('--headless=new')  # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36")
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.binary_location = '/usr/bin/chromium-browser'  # Path to Chromium binary
    options.add_experimental_option("detach", True)   # Prevent auto-closure
    options.add_argument('--window-size=1920,1080')
    wd = webdriver.Chrome(options=options)


    url = "https://www.glassdoor.com.au/Job/australia-graduate-jobs-SRCH_IL.0,9_IN16_KO10,18.htm?sortBy=date_desc"
    wd.get(url)
    jobs = []
    while len(jobs) < num_jobs:
        time.sleep(5)
        job_buttons = wd.find_elements(By.CLASS_NAME,"JobCard_jobCardContainer___hKKI")
        try:
            wd.find_element(By.CSS_SELECTOR,'body > div.ModalContainer > div.Modal > div.ContentSection > div.closeButtonWrapper > button').click()  # clicking to the X.
        except NoSuchElementException:
            pass

        for job_button in job_buttons:
            print("Progress: {}".format("" + str(len(jobs)) + "/" + str(num_jobs)))
            if len(jobs) >= num_jobs:
                break
            print("here")

            try:
                job_button.click()
                show_button = WebDriverWait(wd,5).until(EC.element_to_be_clickable((By.CLASS_NAME, "JobDetails_showMore___Le6L")))
                show_button.click()

            except:
                try:
                    wd.find_element(By.CSS_SELECTOR,'body > div.ModalContainer > div.Modal > div.ContentSection > div.closeButtonWrapper > button').click()  # clicking to the X.
                except NoSuchElementException:
                    pass

            time.sleep(2)
            # while not collected_successfully:
            try:
                company_names = wd.find_elements(By.CLASS_NAME,'EmployerProfile_employerName__qujuA')
                company_name = company_names[-1].text
                job_title = wd.find_element(By.XPATH, "//span[starts-with(@id, 'jd')]").text
                job_descriptions = wd.find_elements(By.XPATH,
                    "//div[starts-with(@class,'JobDetails_jobDescription')]")
                job_description = job_descriptions[-1].get_attribute('innerText')
            # collected_successfully = True
            except:
                time.sleep(5)

                # Printing for debugging
            if verbose:
                print("Job Title: {}".format(job_title))
                print("Job Description: {}".format(job_description[:500]))
                print("Company Name: {}".format(company_name))
                print("Location: {}".format(location))
            jobs.append({"Job Title": job_title,
                         "Job Description": job_description,
                         "Company Name": company_name
                         })

        print('should move to more jobs')
        # Clicking on the "next page" button
        try:
            wd.find_element(By.XPATH,'//*[@id="left-column"]/div[2]/div/button').click()
            print('moved to more jobs')
        except NoSuchElementException:
            print("Scraping terminated before reaching target number of jobs. Needed {}, got {}.".format(num_jobs,
                                                                                                         len(jobs)))
            break
    return pd.DataFrame(jobs)

df = get_jobs('graduate',5, False)

df.to_csv('glassdoor_jobs.csv')