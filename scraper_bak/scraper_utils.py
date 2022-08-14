from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import DesiredCapabilities  # https://gist.github.com/lorey/079c5e178c9c9d3c30ad87df7f70491d
import json
import time
from icecream import ic
import random
from scraper_properties import *
import html
import os
import logging
import re

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait



def start_driver():
    # browser settings
    caps = webdriver.DesiredCapabilities.CHROME.copy()
    options = webdriver.ChromeOptions()
    options.add_argument("disable-gpu")
    #options.add_argument("--headless")

    # options.add_argument("headless")
    options.add_experimental_option("prefs", {
        # "download.default_directory": r"/Volumes/GoogleDrive/My Drive/Notion/",
        "download.Prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    })
    options.add_argument("no-default-browser-check")
    options.add_argument("no-first-run")
    options.add_argument("no-sandbox")

    # make chrome log requests
    capabilities = DesiredCapabilities.CHROME
    capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(ChromeDriverManager().install(), desired_capabilities=capabilities, options=options)
    driver.maximize_window()

    global logs_raw
    global logs
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]
    return (driver)

def login(driver, login, pwd):
    start_page = 'https://www.linkedin.com/login'

    #Open LinkedIn Login Page
    driver.get(start_page)
    ic('Opened page: ' + driver.title)
    time.sleep(1)
    email_input = driver.find_element(by=By.XPATH, value='//*[@id="username"]')
    time.sleep(1)
    email_input.send_keys(login)
    time.sleep(2)
    pass_input = driver.find_element(by=By.XPATH, value='//*[@id="password"]')
    pass_input.send_keys(pwd)
    pass_input.send_keys(Keys.ENTER)
    time.sleep(5)

def get_title_and_company(url,driver):

    user_page_url_list = []
    user_names_list = []
    user_role_list = []
    user_company_list = []

    curr_page = 1



    while curr_page is not None:
        user_page_url_list.append(driver.find_elements_by_xpath('//a[@class="app-aware-link"]'))
        user_names_list.append(driver.find_elements_by_xpath('//a[@span="aria-hidden="true""]'))
        user_role_list.append([i.split('at')[0] for i in )


# def get_json(driver, url, searched_json):
#     # 3 arguments: active driver, url to scrape, search json
#     driver.get(url)
#     time.sleep(INTERVAL)
#
#     # Filter Json logs
#     def log_filter(log_):
#         return (
#             # is an actual response
#                 log_["method"] == "Network.responseReceived"
#                 # and json type only
#                 and "json" in log_["params"]["response"]["mimeType"]
#         )
#
#     logs_raw = driver.get_log("performance")  # get all responses
#     logs = [json.loads(lr["message"])["message"] for lr in logs_raw]  # get message for each response
#
#     # iterate for all json responses from logs
#     for log in filter(log_filter, logs):
#         # api response name
#         response_name = json.dumps(log["params"]["response"]["url"])
#         #         print(response_name)
#
#         # if search_json name is equal to current json response name then get the response body
#         if searched_json in response_name:
#             request_id = log["params"]["requestId"]
#             json_code = (driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id}))['body']
#             json_code_loaded = json.loads(json_code)
#             json_code_parsed = json.dumps(json_code_loaded)
#             response = html.unescape(json_code_parsed)
#
#             return (response)


def get_connections(driver):
    driver.get(LI_USER)
    element = driver.find_element_by_xpath('//a[contains(@href, "connectionOf")]')
    time.sleep(2)
    element.click()
    time.sleep(2)
    return driver.getCurrentUrl()

def run_paginator(driver, num_pages):
    page_number = 1
    while page_number < num_pages:
        page_number += 1
        connection_page_url = CONNECTION_PAGE_ROOT_URL + str(page_number)

        # Continue looping when error occur for a page
        try:
            json_code = get_json(driver, connection_page_url, SEARCHED_JSON)
            file_name = str(PROFILE_ID) + '__page' + str(page_number) + '.json'

            with open('temp/' + file_name, 'w') as outfile:
                ic('Writing file with code {}'.format(json_code))
                outfile.write(json_code)

        except Exception as error:
            ic(error)


def json_merge():
    final_data = dict()
    for file in os.listdir('temp/'):
        if file.startswith(PROFILE_ID) and file.endswith('.json'):
            try:
                with open(file) as f:
                    data = json.load(f)

                final_data[file] = data
            except Exception as error:
                ic(error)

    final_data_json = json.dumps(final_data, sort_keys=True) #indent=2
    ic('--Writing final data file {}--'.format(PROFILE_ID + '.json'))
    with open(PROFILE_ID + '.json', 'w') as outfile:
        outfile.write('fin/' + final_data_json)