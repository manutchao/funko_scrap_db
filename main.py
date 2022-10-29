from bs4 import BeautifulSoup
import requests
import logging
from math import *
import pandas as pd
import urllib.parse
import os
import sys
import re
import json
import time
from selenium import webdriver
from urllib.parse import urlunsplit, urlencode
import urllib.parse as urlparse
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

logging.basicConfig(level=logging.INFO)

# url = [
#     {'website':'https://www.fye.com/toys-collectibles/action-figures/funko/?sz=60', 'bloc_item':'st-tile-grid__wrapper', 'item':'st-tile-grid__item'}
# ]

# class PopScrapper:
#     headers = {"User-Agent": "Chrome/5.0"}
#     parser = 'html.parser'


#     def __init__(self, url):
#         self.url = url


#     def request_url(self):
#         response = requests.get(self.url)
#         html = response.content
#         return BeautifulSoup(requests.get(self.url, headers=self.headers).text,self.parser)


#     @staticmethod
#     def get_website_url_info(url):
#         '''
#         Returns domain name from an url.

#         Returns:
#             string:Domain name.
#         '''
#         return urllib.parse.urlparse(url)


#     def get_nb_total_elem(self):
#         response = requests.get(self.url)
#         html = response.content
#         soup = BeautifulSoup(requests.get(self.url, headers=self.headers).text,self.parser)
#         if soup.title.text == 'Queue-it':
#             logging.warning('page {} - not available for the function {}'.format(self.url, 'get_nb_total_elem'))
#             return None
#         else:
#             return int(soup.find('p', attrs={'id' : 'toolbar-amount'}).find('span', attrs={'class' : 'toolbar-number'}).text)


#     def get_nb_elem_by_page(self):
#         response = requests.get(self.url)
#         html = response.content
#         soup = BeautifulSoup(requests.get(self.url, headers=self.headers).text,self.parser)
#         if soup.title.text == 'Queue-it':
#             logging.warning('page {} - not available for the function {}'.format(self.url, 'get_nb_elem_by_page'))
#             return None
#         else:
#             return int(soup.find('select', attrs={'id' : 'limiter'}).find('option', attrs={'selected' : 'selected'}).text)

#     def scrollDown(browser, numberOfScrollDowns):
#         body = browser.find_element_by_tag_name("body")
#         while numberOfScrollDowns >=0:
#             body.send_keys(Keys.PAGE_DOWN)
#             numberOfScrollDowns -= 1
#         return browser

NB_PAGE = 4
NB_RESULT_BY_PAGE = 6
URL = {'host':'https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series', 
     'filter':{'filters[related_to]':'49962',
               'filters[in_collection]':'all',
               'filters[in_wishlist]':'all',
               'filters[on_sale]':'all',
               'id=49962&order[name]':'name',
               'order[sort]':'asc',
               'page':'1',
               'subject_id':'49962',
               'subvariants':'true'
               }
     }





class PopScrapper:

    def __init__(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options, service=Service(executable_path=GeckoDriverManager().install())) 
    
    @staticmethod
    def build_url(host: str, param: dict) -> str:
        url_parse = urlparse.urlparse(host)
        query = url_parse.query
        url_dict = dict(urlparse.parse_qsl(query))
        url_dict.update(param)
        url_new_query = urlparse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        return urlparse.urlunparse(url_parse)
    
    
    
    
    def get_all_links(self, url: str) ->list[str]:
        self.driver.get('https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series?filters[related_to]=49962&filters[in_collection]=all&filters[in_wishlist]=all&filters[on_sale]=all&id=49962&order[name]=name&order[sort]=asc&page=1&subject_id=49962&subvariants=true')
        list_items = []
            
        # Accept cookies
        self.driver.find_element(by='xpath', value='/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]').click()
            
        for num_page in range(2, NB_PAGE):
            self.driver.get('https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series?filters[related_to]=49962&filters[in_collection]=all&filters[in_wishlist]=all&filters[on_sale]=all&id=49962&order[name]=name&order[sort]=asc&page={}&subject_id=49962&subvariants=true'.format(str(num_page)))
            time.sleep(3)
            for i in range(1, NB_RESULT_BY_PAGE):
                if len(self.driver.find_elements(by=By.XPATH, value="//*[@id='related-items']/catalog-item-search-results/div[1]/div[2]/div[3]/catalog-items-list/div[{}]/div/div[3]/div[2]/ul/li[1]".format(str(i)))) > 0 or len(self.driver.find_elements(by=By.XPATH, value="//*[@id='related-items']/catalog-item-search-results/div[1]/div[2]/div[3]/catalog-items-list/div[{}]/div/div[3]/div/ul/li[1]".format(str(i)))) > 0:
                    link = self.driver.find_element(by=By.XPATH, value="//*[@id='related-items']/catalog-item-search-results/div[1]/div[2]/div[3]/catalog-items-list/div[{}]/div/div[3]/a".format(str(i))).get_attribute('href')
                    list_items.append(link)
        self.driver.quit()
        return list_items



    def get_content_from_url(self, url: str) ->list[str]:
        list_items = []

        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options, service=Service(executable_path=GeckoDriverManager().install()))
        
        driver.get(url)

        # Accept cookies
        if len(driver.find_elements(by='xpath', value='/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]')) > 0:
            driver.find_element(by='xpath', value='/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]').click()

        time.sleep(3)
        bloc = driver.find_element(by='xpath', value='/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]')
        list_sub_bloc = bloc.find_elements(by="xpath", value="//div[@class='col-md-6 spaced-field ng-scope']//div")    

        print(driver.find_element(by=By.XPATH, value="//h1[@class='item-name']").text)

        atom = {
            'name': driver.find_element(by=By.XPATH, value="//h1[@class='item-name']").text,
            'img': driver.find_element(by=By.XPATH, value="//a[@ng-click='showPhotos()']//img").get_attribute('src')
        }
        atom['characteristics'] = {}
        nb_characteristics = len((bloc.find_elements(by="xpath", value='/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div')))
        
        for cpt in range(1,nb_characteristics-1):
            key = bloc.find_element(by="xpath", value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div["+str(cpt)+"]/div[1]/b").text
            value = bloc.find_element(by="xpath", value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div["+str(cpt)+"]/div[2]/span/span[2]").text
            atom['characteristics'][key]= value
            if "," in value:
                atom['characteristics'][key] = value.split(",") 

        if len(driver.find_elements(by=By.XPATH, value="//editable[@class='ng-isolate-scope']")) > 0:
            atom['barcode'] = driver.find_element(by=By.XPATH, value="//editable[@class='ng-isolate-scope']").text    
            
        list_items.append(atom)
        driver.quit()
        return atom
        
        # # Save as json
        # with open('database.json', 'w', encoding='utf-8') as f:
        #     json.dump(list_items, f, ensure_ascii=False, indent=4)




if __name__ == "__main__":

    # url = "https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series?filters[related_to]=49962&filters[in_collection]=all&filters[in_wishlist]=all&filters[on_sale]=all&id=49962&order[name]=name&order[sort]=asc&page=1&subject_id=49962&subvariants=true"
    url = PopScrapper.build_url(URL['host'], URL['filter'])
    scrapper = PopScrapper()
    all_links = scrapper.get_all_links(url)  
    content_url = map(scrapper.get_content_from_url, all_links)
    
    # Save as json
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(list(content_url), f, ensure_ascii=False, indent=4)
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    # for link in all_links:
    #     print(link)
    #     driver.get(link)
        
    #     # Accept cookies
    #     if len(driver.find_elements(by='xpath', value='/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]')) > 0:
    #         driver.find_element(by='xpath', value='/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]').click()

    #     time.sleep(3)
    #     bloc = driver.find_element(by='xpath', value='/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]')
    #     list_sub_bloc = bloc.find_elements(by="xpath", value="//div[@class='col-md-6 spaced-field ng-scope']//div")    

    #     atom = {
    #         'name': driver.find_element(by=By.XPATH, value="//h1[@class='item-name']").text,
    #         'img': driver.find_element(by=By.XPATH, value="//a[@ng-click='showPhotos()']//img").get_attribute('src')
    #     }
    #     atom['characteristics'] = {}
    #     atom['color'] = {}
    #     nb_characteristics = len((bloc.find_elements(by="xpath", value='/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div')))
        
    #     for cpt in range(1,nb_characteristics-1):
    #         key = bloc.find_element(by="xpath", value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div["+str(cpt)+"]/div[1]/b").text
    #         value = bloc.find_element(by="xpath", value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]/div["+str(cpt)+"]/div[2]/span/span[2]").text
    #         atom['characteristics'][key]= value
    #         if "," in value:
    #             atom['characteristics'][key] = value.split(",") 

    #     if len(driver.find_elements(by=By.XPATH, value="//editable[@class='ng-isolate-scope']")) > 0:
    #         atom['barcode'] = driver.find_element(by=By.XPATH, value="//editable[@class='ng-isolate-scope']").text    
            
    #     list_items.append(atom)
    
    # driver.quit()
    
    # # Save as json
    # with open('database.json', 'w', encoding='utf-8') as f:
    #     json.dump(list_items, f, ensure_ascii=False, indent=4)