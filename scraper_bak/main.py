
from scraper_utils import *
from scraper_properties import *
import re
import math
from icecream import ic
import pandas as pd


def main():
    ic('--initiate driver--')
    driver = start_driver()

    ic('--login with onboarding specialist credentials--')
    login(driver, USER_LOGIN, USER_PASS)

    ic('--Navigate to user page and get connections list--')
    conn_url = get_connections(driver)

    # for each page get the json saved in requests
    try:
        json_code = get_json(driver, conn_url, SEARCHED_JSON)
        file_name = str(PROFILE_ID) + '__page' + str(1) + '.json'
        #     print(json_code)
        with open(file_name, 'w') as outfile:
            outfile.write(json_code)

        total_results = re.sub('\D', '', json.loads(json_code)['metadata']['totalDisplayCount'])
        num_pages = math.ceil(int(total_results) / 25)  # dividate number of connection per 25 connection per page

        # pagination
        ic('--Running through pages of LinkedIn to query parameters--')
        run_paginator(driver, num_pages)

        ic('--Merge jsons into final json--')
        json_merge()


    except Exception as error:
        ic(error)


if __name__ == '__main__':
    main()
