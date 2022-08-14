from scrape_linkedin import ConnectionScraper
import re
import math
from icecream import ic
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from scrape_linkedin.utils import HEADLESS_OPTIONS

def main():
    ic('--initiate scraper in headless mode--')
    url = 'https://www.linkedin.com/in/joshua-budman-7496b933/'
    with ConnectionScraper(driver_options=HEADLESS_OPTIONS) as scraper:
        start = time.time()
        scrape_results = scraper.scrape(url=url)
        end = time.time()

    time_delta = end - start
    ic('Results scraped in {} seconds'.format(time_delta))
    #scrape_results.to_csv('joshua_budman_test_results.csv')





if __name__ == '__main__':
    main()
