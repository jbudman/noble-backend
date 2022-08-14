import logging
import re

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from scraper import Scraper
from utils import AnyEC
from icecream import ic
import time
import pandas as pd
logger = logging.getLogger(__name__)
COL_LIST = ['Name', 'ID', 'Position', 'Company', 'Image URLs', 'Location']
MAX_PAGE_RETRIES = 3


class ConnectionScraper(Scraper):
    """
    Scraper for Personal LinkedIn Profiles. See inherited Scraper class for
    details about the constructor.
    """

    def __init__(self, first_only=True, *args, **kwargs):
        super(ConnectionScraper, self).__init__(*args, **kwargs)
        self.first_only = first_only



    def scrape_email(self, url='', user=None):
        self.load_profile_page(url, user)
        email = self.get_user_email()
        return email

    def scrape_connections(self, url='', user=None):
        self.load_profile_page(url, user)
        return self.get_first_connections()

    def load_profile_page(self, url='', user=None):
        """Load profile page and all async content

        Params:
            - url {str}: url of the profile to be loaded
        Raises:
            ValueError: If link doesn't match a typical profile url
        """
        if user:
            url = 'https://www.linkedin.com/in/' + user
        if 'com/in/' not in url and 'comm/in/' not in url:
            raise ValueError("Url must look like ...linkedin.com/in/NAME")

        self.driver.get(url)
        self.driver.refresh()

        # Wait for page to load dynamically via javascript


        # Check if we got the 'profile unavailable' page
        # try:
        #     self.driver.find_element_by_css_selector('.pv-top-card-section')
        # except:
        #     raise ValueError(
        #         'Profile Unavailable: Profile link does not match any current Linkedin Profiles')

    def get_user_email(self):
        try:
            time.sleep(3)
            element = self.driver.find_element('xpath', '//a[contains(@href, "contact-info")]')
            element.click()
            time.sleep(1)
            email_element = self.driver.find_element('xpath', '//a[contains(@href, "mailto")]')
            email = email_element.text.split(':')[-1]
            ic('Obtaining user email {}'.format(email))




        except TimeoutException as e:
            raise Exception(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

        return email

    def get_first_connections(self):
        try:
            time.sleep(8)
            element = self.driver.find_element('xpath','//a[contains(@href, "connectionOf")]')
            element.click()
            time.sleep(2)
            ic('Received connections!')
        except TimeoutException as e:
            raise Exception(
                """Took too long to load profile.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

        return self.scrape_all_pages()

    def next_page(self):
        next_btn = self.driver.find_element('css selector', '[aria-label="Next"]')
        next_btn.click()
        self.page_num += 1

    def scrape_all_pages(self):
        self.page_num = 1
        all_results = pd.DataFrame(columns=COL_LIST)
        more_pages = True
        while more_pages:
            more_pages, page_results, retry_page = self.scrape_page()
            page_retry_count = 0

            while retry_page and page_retry_count < MAX_PAGE_RETRIES:

                page_retry_count += 1
                ic('Retry attempt {} for page {}'.format(page_retry_count, self.page_num))
                more_pages, page_results, retry_page = self.scrape_page()

            all_results = pd.concat([all_results,page_results])
            if more_pages:
                self.next_page()
                time.sleep(1)
        return all_results

    def scrape_page(self):
        ic("SCRAPING PAGE: ", self.page_num)
        time.sleep(3)
        urls = self.driver.find_elements('xpath','//a[contains(@href, "www.linkedin.com/in/")]')
        name_link_tuple_list = []
        for url in urls:
            if 'ACoAA' not in url.get_attribute('href') and len(url.text) > 0 and 'Status is reachable' not in url.text:
                name_link_tuple_list.append((url.text.split('\n')[0],url.get_attribute('href')))

        name_link_tuple_list_fin = list(dict.fromkeys(name_link_tuple_list).keys())
        ic(name_link_tuple_list_fin)

        name_link_pd = pd.DataFrame(name_link_tuple_list_fin, columns=['Name', 'Link'])

        image_links = self.driver.find_elements('xpath','//img[contains(@class, "presence-entity__image")]')


        name_image_link_tuple_list = []
        for image_link in image_links:
                ic(image_link.get_attribute('alt'))
                name_image_link_tuple_list.append((image_link.get_attribute('alt'), image_link.get_attribute('src')))

        name_image_link_tuple_list_fin = list(dict.fromkeys(name_image_link_tuple_list).keys())
        name_image_pd = pd.DataFrame(name_image_link_tuple_list_fin, columns=['Name', 'Image Link'])

        fin_name_image_link_pd = pd.merge(name_link_pd, name_image_pd, on='Name', how='left').fillna('No Image')

        ic(fin_name_image_link_pd)

        positions = self.driver.find_elements('xpath','//div[contains(@class, "entity-result__primary-subtitle t-14 t-black t-normal")]')
        position_list = []
        company_list = []

        for position in positions:
            if ' at ' in position.text:
                position_list.append(position.text.split(' at ')[0])
                company_list.append(position.text.split(' at ')[-1])

            elif ' @ ' in position.text:
                position_list.append(position.text.split(' @ ')[0])
                company_list.append(position.text.split(' @ ')[-1])

            elif ',' in position.text:
                position_list.append(position.text.split(',')[0])
                company_list.append(position.text.split(',')[-1])

            else:
                position_list.append(position.text)
                company_list.append('None Found')

        locations = self.driver.find_elements('xpath','//div[contains(@class, "entity-result__secondary-subtitle t-14 t-normal")]')
        location_list = []

        for location in locations:
            location_list.append(location.text)

        ic(fin_name_image_link_pd.shape)
        ic(len(position_list))
        ic(len(company_list))
        ic(len(location_list))

        self.scroll_to_bottom()
        try:
            next_btn = self.driver.find_element('css selector', '[aria-label="Next"]')
        except NoSuchElementException:
            ic('No such element')
            next_btn = None



        fin_dict = {"Name": fin_name_image_link_pd['Name'],"ID": fin_name_image_link_pd['Link'],
                               "Position": position_list, "Company" : company_list, "Image URLs": fin_name_image_link_pd['Image Link'], "Location" : location_list}

        try:
            page_pd = pd.DataFrame(fin_dict)
            retry_page = False

        except ValueError as e:
            ic('Page not loaded, try again')
            ic(e)
            page_pd = None
            retry_page = True

        except AttributeError:
            ic('Page not loaded, try again')
            page_pd = None
            retry_page = True


        next_button_enabled = next_btn.is_enabled()
        return next_button_enabled, page_pd, retry_page
