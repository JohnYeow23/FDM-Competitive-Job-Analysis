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
    # options.add_argument('--headless=new')  # Runs Chrome in headless mode.
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    options.binary_location = '/usr/bin/chromium-browser'  # Path to Chromium binary
    options.add_experimental_option("detach", True)  # Prevent auto-closure
    wd = webdriver.Chrome(options=options)
    wd.set_window_size(1120, 1000)

    url = "https://www.glassdoor.com.au/Job/australia-graduate-jobs-SRCH_IL.0,9_IN16_KO10,18.htm?sortBy=date_desc"
    wd.get(url)
    jobs = []
    while len(jobs) < num_jobs:
        time.sleep(4)
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
                job_button.click()  # You might
            except:
                try:
                    wd.find_element(By.CSS_SELECTOR,'body > div.ModalContainer > div.Modal > div.ContentSection > div.closeButtonWrapper > button').click()  # clicking to the X.
                except NoSuchElementException:
                    pass

            time.sleep(1)
            # while not collected_successfully:
            try:
                company_name = wd.find_element(By.XPATH,'//*[@id="695311"]/div[2]/span').text
                job_title = wd.find_element(By.XPATH,'//*[@id="jd-job-title-1009178847654"]').text
                job_description = wd.find_element(By.XPATH,
                    '//*[@id="app-navigation"]/div[3]/div[2]/div[2]/div[1]/section/div[1]/div[1]').get_attribute('innerText')
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

df = get_jobs('graduate',31, False)

df.to_csv('glassdoor_jobs.csv')
df.to_excel('glassdoor_jobs.xlsx')