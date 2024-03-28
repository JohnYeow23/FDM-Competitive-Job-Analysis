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

# Example nested dictionary structure for company URLs
companies_info = {
    "FDM Group - Australia": {
        "Overview": "https://au.gradconnection.com/employers/fdm-group/",
        "Programmes": "https://au.gradconnection.com/employers/fdm-group-sg/#our-graduate-programme",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/fdm-group-sg/#diversity-and-inclusion",
        "Programmes_XPath": '//*[@id="our-graduate-programme"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity-and-inclusion"]/div/article/div'

    },
    "Accenture - Australia":{
        "Overview": "https://au.gradconnection.com/employers/accenture/",
        "Programmes": "https://au.gradconnection.com/employers/accenture/#graduate-roles",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/accenture/#diversity-inclusion",
        "Life & Culture": "https://au.gradconnection.com/employers/accenture/#life-culture",
        "Programmes_XPath": '//*[@id="graduate-roles"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity-inclusion"]/div/article',
        "Life_XPath": '//*[@id="life-culture"]/div[2]/article/div'
    },
    "Amazon - Australia":{
        "Overview": "https://au.gradconnection.com/employers/amazon/",
        "Programmes": "https://au.gradconnection.com/employers/amazon/#graduate-program",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/amazon/#diversity-and-inclusion",
        "Programmes_XPath": '//*[@id="graduate-program"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity-and-inclusion"]/div/article/div',

    },
    "Aurecon - Australia":{
        "Overview": "https://au.gradconnection.com/employers/aurecon/",
        "Programmes": "https://au.gradconnection.com/employers/aurecon/#graduate-programme",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/aurecon/#embracing-difference",
        "Life & Culture": "https://au.gradconnection.com/employers/aurecon/#life-culture",
        "Programmes_XPath": '//*[@id="graduate-programme"]/div/article/div',
        "Diversity_XPath": '//*[@id="embracing-difference"]/div/article/div',
        "Life_XPath": '//*[@id="life-culture"]/div[1]/article/div'
    },
    "Arup - Australia":{
        "Overview": "https://au.gradconnection.com/employers/arup/",
        "Programmes": "https://au.gradconnection.com/employers/arup/#our-graduate-program",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/arup/#diversity",
        "Life & Culture": "https://au.gradconnection.com/employers/arup/#life-culture",
        "Programmes_XPath": '//*[@id="our-graduate-program"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity"]/div/article/div',
        "Life_XPath": '//*[@id="life-culture"]/div[1]/article/div'
    },
    "Aecom - Australia":{
        "Overview": "https://au.gradconnection.com/employers/aecom/",
        "Programmes": "https://au.gradconnection.com/employers/aecom/#our-graduate-program",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/aecom/#diversity",
        "Life & Culture": "https://au.gradconnection.com/employers/aecom/#life-culture",
        "Programmes_XPath": '//*[@id="our-graduate-program"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity"]/div/article/div',
        "Life_XPath": '//*[@id="life-culture"]/div/article/div'
    },
    "HSBC - Hong Kong":{
        "Overview": "https://au.gradconnection.com/employers/hsbc-hk/",
        "Programmes": "https://au.gradconnection.com/employers/hsbc-hk/#students-and-graduates-programmes",
        "Programmes_XPath": '//*[@id="students-and-graduates-programmes"]/div/article/div'
    },
    "OKX - Hong Kong":{
        "Overview": "https://au.gradconnection.com/employers/okx-hk/",
        "Programmes": "https://au.gradconnection.com/employers/okx-hk/#supernova-program",
        "Programmes_XPath": '//*[@id="supernova-program"]/div/article/div',
        "Life & Culture": "https://au.gradconnection.com/employers/okx-hk/#life-culture",
        "Life_XPath": '//*[@id="life-culture"]/div[1]/article/div'
    },
    "Wiley Edge - Australia":{
        "Overview": "https://au.gradconnection.com/employers/wiley-edge/",
        "Programmes": "https://au.gradconnection.com/employers/wiley-edge/#graduate-program",
        "Diversity & Inclusion": "https://au.gradconnection.com/employers/wiley-edge/#diversity",
        "Programmes_XPath": '//*[@id="graduate-program"]/div/article/div',
        "Diversity_XPath": '//*[@id="diversity"]/div/article/div'
    },
    "Jane Street - Australia":{
        "Overview": "https://au.gradconnection.com/employers/jane-street/",
        "Programmes": "https://www.janestreet.com/join-jane-street/programs-and-events/?location=australia&program-type=all-programs&event-type=all-events&show-programs=true&show-events=true",
        "Programmes_XPath": '/html/body/div[2]/main/div/div[3]/div/div/div/div/div[3]/a[7]/div/div'
    }

    # Add more companies and their URLs as needed
}

# Initialize WebDriver
options = Options()
#options.add_argument('--headless=new')  # Runs Chrome in headless mode.
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.binary_location = 'C:\Program Files\Google\Chrome\Application\chrome.exe'  # Path to Chromium binary
options.add_experimental_option("detach", True)  # Prevent auto-closure
wd = webdriver.Chrome(options=options)


#scraping data
def get_text_by_class(url, class_name):
    wd.get(url)
    try:
        WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CLASS_NAME, class_name)))
        element = wd.find_element(By.CLASS_NAME, class_name)
        return element.text.strip()
    except Exception as e:
        return f"Error: {e}"

def get_text_by_xpath(url, xpath):
    wd.get(url)
    try:
        WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.XPATH, xpath)))
        element = wd.find_element(By.XPATH, xpath)
        return element.text.strip()
    except Exception as e:
        return f"Error: {e}"

company_data_list = []

for company_name, urls in companies_info.items():
    data = {"Company Name": company_name}
    data["Overview"] = get_text_by_class(urls["Overview"], 'employer-profile-header-container')
    data["Programmes"] = get_text_by_xpath(urls["Programmes"], urls["Programmes_XPath"])
    if "Diversity & Inclusion" in urls:
        data["Diversity & Inclusion"] = get_text_by_xpath(urls["Diversity & Inclusion"], urls["Diversity_XPath"])
    else:
        data["Diversity & Inclusion"] = "N/A"
    if "Life & Culture" in urls:
        data["Life & Culture"] = get_text_by_xpath(urls["Life & Culture"], urls["Life_XPath"])
    else:
        data["Life & Culture"] = "N/A"

    company_data_list.append(data)


wd.quit()

df = pd.DataFrame(company_data_list)
df.to_csv("company_profiles.csv", index=False)


