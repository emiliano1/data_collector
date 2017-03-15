import os
import time
import random
import ConfigParser
import argparse
import urlparse

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

COMPANY_SIZE = {0: 'A',
                1:'B',
                11:'C',
                51: 'D',
                201: 'E',
                501: 'F',
                1001: 'G',
                5001: 'H',
                10001: 'I',
                }

DEF_SETTINGS = {
    'keywords': (),
    'location': '',
    'industry_code': '',
    'company_size': COMPANY_SIZE[0],
}


FACET = ".//*[@id='%s']"
FACET_I = 'facet-I'
FACET_CCR = 'facet-CCR'
FACET_CS = 'facet-CS'


S_SECTION_MAIN = 'Main'
S_KEYWORDS = 'keywords'
S_LOCATION = 'location'
S_IND_CODE = 'industry'
S_COMP_SIZE = 'size'

def login(browser):
    parser = argparse.ArgumentParser()
    parser.add_argument('email', help='linkedin mail')
    parser.add_argument('password', help='linkedin password')
    args = parser.parse_args()

    name = browser.find_element_by_id('session_key-login')
    name.send_keys(args.email)

    password = browser.find_element_by_id('session_password-login')
    password.send_keys(args.password)

    password.submit()

def set_find_companies(browser):
    time.sleep(random.uniform(3.0, 5.0))
    browser.find_element_by_id('global-search').submit()

    time.sleep(random.uniform(1.0, 2.0))
    browser.find_element_by_link_text('Companies').click()

def expand_facet(facet):
    if 'collapsed' in facet.get_attribute('class'):
        facet.find_element_by_xpath('.//fieldset/button').click()

def expand_facet_values(browser, facet):
    wait = WebDriverWait(browser, 10)
    time.sleep(random.uniform(1.0, 2.0))
    expand_button = wait.until(EC.element_to_be_clickable((By.XPATH, facet+'/fieldset/div/div/div/button')))
    expand_button.click()

def set_text_value(browser, facet, value):
    expand_facet_values(browser, facet)

    wait = WebDriverWait(browser, 10)
    time.sleep(random.uniform(1.0, 2.0))
    text_field = wait.until(EC.element_to_be_clickable((By.XPATH, facet+'/fieldset/div/div/input')))
    text_field.send_keys(value)
    text_field.click()

    time.sleep(random.uniform(1.0, 2.0))
    list = browser.find_element_by_class_name('typeahead-results-container')
    list.find_element_by_xpath('.//div/div[2]/ul/li[1]').click()

def set_select_value(browser, facet, value):
    wait = WebDriverWait(browser, 10)
    time.sleep(random.uniform(1.0, 2.0))
    select_field = wait.until(EC.element_to_be_clickable((By.XPATH, facet+"/fieldset/div/ol" )))
    select_field.find_element_by_xpath(".//*[@value='%s']" % (value)).click()

def get_companies(source):
    urls = []
    for link in source.find_all('a'):
        url = link.get('href')
        title = link.contents[0]
        if url:
            if 'vsrp_companies_res_name' in url:
                urls.append((title,url))
    return urls

def get_settings():
    global S_SECTION_MAIN, S_LOCATION, S_KEYWORDS, S_IND_CODE

    config_file = ConfigParser.ConfigParser()
    settings = DEF_SETTINGS

    try:
        config_file.read('settings.ini')
        settings['location'] = config_file.get(S_SECTION_MAIN, S_LOCATION)
        settings['industry_code'] = config_file.get(S_SECTION_MAIN, S_IND_CODE)
        settings['company_size'] = COMPANY_SIZE[config_file.getint(S_SECTION_MAIN, S_COMP_SIZE)]
        s = config_file.get(S_SECTION_MAIN, S_KEYWORDS)
        settings['keywords'] = s.split(',')

    except:
        pass

    return settings


def Main():
    settings = get_settings()

    browser = webdriver.Firefox('')
    browser.get('https://www.linkedin.com/uas/login')

    login(browser)

    set_find_companies(browser)

    expand_facet(browser.find_element_by_id(FACET_CCR))
    expand_facet(browser.find_element_by_id(FACET_I))
    expand_facet(browser.find_element_by_id(FACET_CS))

    if settings['location'] != '':
        set_text_value(browser, FACET%(FACET_CCR), settings['location'])

    if settings['industry_code'] != '':
        set_text_value(browser, FACET%(FACET_I), settings['industry_code'])

    if settings['company_size'] != COMPANY_SIZE[0]:
        set_select_value(browser, FACET%(FACET_CS), settings['company_size'])

    compList = []
    page_index = 0
    old_page_index = 0

    while True:
        while True:
            time.sleep(2)
            try:
                page_index = browser.find_element_by_id("results-pagination").find_element_by_class_name("active").text
            except:
                continue

            if page_index != old_page_index:
                old_page_index = page_index
                break

        source = BeautifulSoup(browser.page_source, 'html.parser')
        companies = get_companies(source)
        for company in companies:
            if settings['keywords']:
                for keyword in settings['keywords']:
                    if keyword.strip() in company[0]:
                        compList.append(company[1]+'\n')
                        break
            else:
                compList.append(company[1] + '\n')

        try:
            time.sleep(random.uniform(1.0, 2.0))
            browser.find_element_by_xpath(".//div[@id='results-pagination']/ul/li[@class='next']/a").click()
        except:
            f = open('company_log.csv', 'w')
            f.writelines(compList)
            f.close()
            break


    # browser.close()


if __name__ == '__main__':
    Main()
