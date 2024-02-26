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

page_counter = 0
title_list = []
co_list = []
brief_list = []
date_list = []
desc_list = []
deadline_date_list = []
deadline_time_list = []
def parse_date_with_suffix(date_str):
    suffixes = ['th', 'st', 'nd', 'rd']
    for suffix in suffixes:
        if suffix in date_str:
            date_str = date_str.replace(suffix, '')
    return date_str

def scrape_job_details(job_url):
    try:
        wd.execute_script("window.open();")
        wd.switch_to.window(wd.window_handles[-1])
        wd.get(job_url)
        time.sleep(2)  # Consider replacing with an explicit wait
        idv_title = wd.find_element(By.XPATH, "//h1[@class='employers-profile-h1']").text
        if "Notify Me" in idv_title:
            print("Title contains 'Notify Me'. Stopping scraping.")
            return None, None, None

        current_url = wd.current_url
        request = requests.get(current_url)
        url_data = request.text
        soup = BeautifulSoup(url_data, 'html.parser')
        desc = soup.find('div', {'class': 'campaign-content-container'}).get_text()
        content = soup.find('ul', {'class': 'box-content'})
        date = content.find_all('li', {'class': 'box-content-catagories catagories-list'})[-1].get_text()
        if 'Closing Date:' in date:
            date_mod = date.replace('Closing Date:', '')
        else:
            date_mod = 0
        return idv_title, desc, date_mod

    except Exception as e:
        print("Error scraping job details:", e)
        return None, None, None

try:
    url = "https://au.gradconnection.com/"
    wd.get(url)

    search_box = wd.find_element(By.ID, "keyword")
    search_box.send_keys("Graduate")

    l_dropdown = wd.find_element(By.CSS_SELECTOR, "#location > div")
    l_dropdown.click()
    l_select = wd.find_element(By.XPATH, "//span[text()='All of Australia']")
    l_select.click()
    search = wd.find_element(
        By.CSS_SELECTOR, "#app > span > div.dashboard-site-container.grey-bg > main > div > "
                         "section.header-banner-container.no-border-bottom > div > div > header > div > div > "
                         "div.job-search-filters__group > div.job-search-filters__button > button")
    search.click()

    r_dropdown = WebDriverWait(wd, 2).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "#\[object\ Object\] > div"))
    )
    r_dropdown.click()
    time.sleep(1)
    r_select = WebDriverWait(wd, 2).until(
        EC.element_to_be_clickable((By.XPATH, "//span[text()='Newest Jobs']"))
    )
    r_select.click()
    time.sleep(3)

    while True:
        try:
            try:
                search_results = WebDriverWait(wd, 3).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "jobs-container"))
                )
                title_links = wd.find_elements(By.CLASS_NAME, "box-header-title")
                for link in title_links:
                    title_link_url = link.get_attribute("href")
                    idv_title, desc, date_mod = scrape_job_details(title_link_url)
                    if idv_title is None or desc is None or date_mod is None:
                        print("Scraping stopped due to 'None' values returned by scrape_job_details.")
                        break
                    if idv_title and desc and date_mod:
                        title_list.append(idv_title)
                        desc_list.append(desc)
                        if date_mod != 0:
                            parsed_date = parse_date_with_suffix(date_mod)
                            deadline_datetime = datetime.strptime(parsed_date, "%d %b %Y, %I:%M %p")
                            deadline_date_list.append(deadline_datetime.strftime("%d/%m/%Y"))
                            deadline_time_list.append(deadline_datetime.strftime("%H%M"))
                        else:
                            deadline_date_list.append(0)
                            deadline_time_list.append(0)

                    wd.close()
                    wd.switch_to.window(wd.window_handles[0])
            except:
                print("title,desc,date scrape failed")

            if idv_title is None or desc is None or date_mod is None:
                break

            try:
                co_search = wd.find_elements(By.CLASS_NAME, "box-employer-name")
                for i in co_search:
                    idv_co = i.find_element(By.TAG_NAME, "p").text
                    co_list.append(idv_co)
            except:
                print("company scrape failed")

            try:
                brief_search = wd.find_elements(By.CLASS_NAME, "box-description")
                for i in brief_search:
                    idv_brief = i.find_element(By.CLASS_NAME, "box-description-para").text
                    brief_list.append(idv_brief)
            except:
                print("brief scrape failed")

            try:
                time.sleep(2)
                next_page = WebDriverWait(wd, 3).until(
                    EC.presence_of_element_located((By.XPATH, "//li[@class='rc-pagination-next']"))
                )
                next_page.location_once_scrolled_into_view
                time.sleep(1)
                next_page.click()
                time.sleep(2)
                new_page = WebDriverWait(wd, 3).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "#seek-gc-logo-mobile3"))
                )
                new_page.location_once_scrolled_into_view
                new_url = wd.current_url
                time.sleep(1)
                page_counter += 1
                print(f"At page number: {page_counter}")
                if page_counter % 5 == 0:
                    wd.quit()
                    wd = webdriver.Chrome(options=options)
                    wd.get(new_url)
            except:
                print("next page error")
                break
        except Exception as e:
            print("Error in scraping loop:", e)

finally:
    if wd:
        wd.quit()

len_lists = [len(title_list), len(co_list), len(brief_list),
             len(deadline_date_list), len(deadline_time_list), len(desc_list)]
max_length = max(len_lists)

for lst, length in zip([title_list, co_list, brief_list,
                        deadline_date_list, deadline_time_list, desc_list], len_lists):
    if length < max_length:
        lst.extend([0] * (max_length - length))

df = pd.DataFrame(zip(title_list, co_list, brief_list, deadline_date_list, deadline_time_list, desc_list),
                  columns=['Job Title', 'Company', 'Job Brief', 'Deadline Date', 'Deadline Time', 'Job Description'])

df_e = df[(df != 0).all(1)]

df_e.info()
df_e.to_csv('GradConnectionAU_data',index=False)
