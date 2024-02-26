import numpy as np
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from selenium import webdriver
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

url = "https://hk.gradconnection.com/"
wd.get(url)

'''
First page actions (Selenium)
'''

try:
    search_box = wd.find_element(By.ID, "keyword")
    search_box.send_keys("Graduate")
except:
    print("invalid url")
# location dropdown actions + Search click
try:
    l_dropdown = wd.find_element(By.CSS_SELECTOR, "#location > div")
    l_dropdown.click()
    l_select = wd.find_element(By.XPATH, "//span[text()='Hong Kong']")
    l_select.click()
    search = wd.find_element(
        By.CSS_SELECTOR, "#app > span > div.dashboard-site-container.grey-bg > main > div > "
                         "section.header-banner-container.no-border-bottom > div > div > header > div > div > "
                         "div.job-search-filters__group > div.job-search-filters__button > button")
    search.click()
except:
    print("invalid location OR search click")

'''
Second page actions (Selenium) 
'''
# relevance dropdown actions
try:
    r_dropdown = WebDriverWait(wd, 5).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR,"#\[object\ Object\] > div"))
    )
    r_dropdown.click()
    time.sleep(1)
    r_select = WebDriverWait(wd, 1).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Newest Jobs']"))
    )
    r_select.click()
    time.sleep(5)
except:
    print("invalid relevance dropdown")

'''
Scraping Data (Selenium, BS4, JS)
'''
title_list = []
co_list = []
brief_list = []
date_list = []
desc_list = []

while True:
    try:
        search_results = WebDriverWait(wd, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jobs-container"))
        )
        title_links = wd.find_elements(By.CLASS_NAME, "box-header-title")
        for link in title_links:
            title_link_url = link.get_attribute("href")
            wd.execute_script("window.open();")
            wd.switch_to.window(wd.window_handles[-1])
            wd.get(title_link_url)
            try:
                time.sleep(2)
                idv_title = wd.find_element(By.XPATH,"//h1[@class='employers-profile-h1']").text
                title_list.append(idv_title)
            except:
                print("title scrape failed")
            try:
                current_url = wd.current_url
                request = requests.get(current_url)
                url_data = request.text
                soup = BeautifulSoup(url_data, 'html.parser')
                desc = soup.find('div', {'class': 'campaign-content-container'}).get_text()
                desc_list.append(desc)
                content = soup.find('ul',{'class': 'box-content'})
                date = content.find_all('li',{'class': 'box-content-catagories catagories-list'})[-1].get_text()
                date_mod = date.replace('Closing Date:','')
                date_list.append(date_mod)
                time.sleep(2)
            except:
                print("desc + time scrape failed")

            wd.close()
            wd.switch_to.window(wd.window_handles[0])

    except:
        print("title,desc,time scrape failed")
    try:
        co_search = wd.find_elements(By.CLASS_NAME, "box-employer-name")
        for i in co_search:
            idv_co = i.find_element(By.TAG_NAME,"p").text
            co_list.append(idv_co)
    except:
        print("co list failed")
    try:
        brief_search = wd.find_elements(By.CLASS_NAME, "box-description")
        for i in brief_search:
            idv_brief = i.find_element(By.CLASS_NAME, "box-description-para").text
            brief_list.append(idv_brief)
    except:
        print("brief list failed")

    try:
        time.sleep(2)
        next_page = wd.find_element(By.XPATH,"//li[@class='rc-pagination-next']")
        next_page.location_once_scrolled_into_view
        time.sleep(1)
        next_page.click()
        time.sleep(2)
        new_page = WebDriverWait(wd, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#seek-gc-logo-mobile3"))
        )
        new_page.location_once_scrolled_into_view
        time.sleep(1)
    except:
        print("no more pages to scrape")
        break

wd.close()

# Data cleaning; creating dataframe + excel of lists
def parse_date_with_suffix(date_str):
    suffixes = ['th', 'st', 'nd', 'rd']
    for suffix in suffixes:
        if suffix in date_str:
            date_str = date_str.replace(suffix, '')
    return date_str

deadline_date_list = []
deadline_time_list = []

for x in date_list:
    deadline_datetime = datetime.strptime(parse_date_with_suffix(x), "%d %b %Y, %I:%M %p")

    deadline_date_formatted = deadline_datetime.strftime("%d/%m/%Y")
    deadline_date_list.append(deadline_date_formatted)

    deadline_time_formatted = deadline_datetime.strftime("%H%M")
    deadline_time_list.append(deadline_time_formatted)


df = pd.DataFrame(np.column_stack([title_list, co_list, brief_list, deadline_date_list, deadline_time_list, desc_list]),
                  columns=['Job Title', 'Company', 'Job Brief', 'Deadline Date', 'Deadline Time', 'Job Description'])


df.to_csv('GradConnectionHK_data', index=False)

