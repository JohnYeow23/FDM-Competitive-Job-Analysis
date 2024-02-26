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

options = Options()
# options.add_argument('--headless=new')  # Runs Chrome in headless mode.
options.add_argument('--no-sandbox')  # Bypass OS security model
options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
options.binary_location = '/usr/bin/chromium-browser'  # Path to Chromium binary
options.add_experimental_option("detach", True)  # Prevent auto-closure
wd = webdriver.Chrome(options=options)
actions = ActionChains(wd)

page_counter = 0
titlel = []
col = []
briefl = []
datel = []
descl = []


try:
    url = "https://au.prosple.com/"
    wd.get(url)
    # Input search parameters
    search_box = WebDriverWait(wd, 5).until(EC.presence_of_element_located((By.ID, "keyword-search")))
    search_box.send_keys("Graduate")
    search_box.send_keys(Keys.ENTER)
    # Select "Newest Opportunities"
    r_dropdown = WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, "//div[@class='SearchSelectSortDropdownstyle__SelectDropdownWrapper-sc-kz5wuv-4 iLzpZo']")))
    r_dropdown.click()
    r_select = WebDriverWait(wd, 5).until(EC.element_to_be_clickable((By.XPATH, "//li[text()='Newest Opportunities']")))
    r_select.click()

    while True:
        # Wait for results to load
        results = WebDriverWait(wd, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "SearchResultsstyle__SearchResultsWrapper-sc-c560t5-0.iFrLVp")))
        # Loop through search results
        job_panels = WebDriverWait(wd, 10).until(EC.presence_of_all_elements_located((By.XPATH, "//section[contains(@role, 'button')]")))
        for i in job_panels:
            try:
                # Scroll into view
                wd.execute_script("window.scrollTo(0, 0);")
                wd.execute_script("arguments[0].scrollIntoView();", i)
                # Click on the panel
                i.click()
                time.sleep(5)
                #Scrape data from main job panel
                title = i.find_element(By.XPATH,
                                   "//h2[@class='sc-eCssSg kgSmcY heading SearchOpportunityContentstyle__OpportunityTitle-sc-k2tet-12 htCSOp']").text
                titlel.append(title)
                co = i.find_element(By.XPATH,"//a[@class = 'SearchOpportunityContentstyle__StyledLink-sc-k2tet-15 iSykQe']").text
                col.append(co)
                try:
                    br = i.find_element(By.XPATH, "//p[@class ='SearchOpportunityContentstyle__OverviewSummary-sc-k2tet-29 oeIuV']").text
                except NoSuchElementException:
                    br = "N/A"
                briefl.append(br)
                try:
                    date = i.find_element(By.XPATH, "//*[@id='__next']/div[2]/section/main/div[2]/div[2]/div[2]/div[2]/section/div[2]/section/div[1]/div[3]/div/div[2]").text
                except NoSuchElementException:
                    date = "N/A"
                datel.append(date)
                try:
                    desc = i.find_element(By.XPATH, "//*[@id='__next']/div[2]/section/main/div[2]/div[2]/div[2]/div[2]/section/div[2]/section/div[2]/div[1]").text
                except NoSuchElementException:
                    desc = "N/A"
                descl.append(desc)
                time.sleep(5)
            except:
                continue

        try:
            time.sleep(5)
            next_page = WebDriverWait(wd, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@aria-label,'Goto next page')]"))
            )
            next_page.location_once_scrolled_into_view
            time.sleep(5)
            next_page.click()
            time.sleep(5)
            new_page = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "SearchResultsstyle__SearchResultsWrapper-sc-c560t5-0.iFrLVp")))
            new_page.location_once_scrolled_into_view
            new_url = wd.current_url
            time.sleep(5)
            page_counter += 1
            print(f"At page number: {page_counter}")
            if page_counter % 5 == 0:
                wd.quit()
                wd = webdriver.Chrome(options=options)
                wd.get(new_url)
        except NoSuchElementException:
            print("No more pages to click to.")
            break

except Exception as e:
    print(f"An error occurred: {str(e)}")

finally:
    # Close the WebDriver
    wd.quit()

df = pd.DataFrame(zip(titlel, col, briefl, datel, descl),
                  columns=['Job Title', 'Company', 'Job Brief', 'Deadline Date', 'Job Description'])

df.to_csv('ProspleAU_data', index=False)
df.to_excel('ProspleAU_data.xlsx')
