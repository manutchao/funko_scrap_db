import logging
import json
import time
import urllib.parse as urlparse
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("__name__")

NB_PAGE = 4
NB_RESULT_BY_PAGE = 6
URL = {
    "host": "https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series",
    "filter": {
        "filters[related_to]": "49962",
        "filters[in_collection]": "all",
        "filters[in_wishlist]": "all",
        "filters[on_sale]": "all",
        "id=49962&order[name]": "name",
        "order[sort]": "asc",
        "page": "1",
        "subject_id": "49962",
        "subvariants": "true",
    },
}


class PopScrapper:
    """
    Class with all necessary tools to scrap data from a website

    ...

    Attributes
    ----------


    Methods
    -------

    """

    def __enter__(self):
        """ """
        return self

    def __init__(self):
        """Constructor"""
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(
            options=options,
            service=Service(executable_path=GeckoDriverManager().install()),
        )

    @staticmethod
    def get_website_url_info(url):
        """
        Returns domain name from an url.

        Returns:
            string:Domain name.
        """
        return urlparse.urlparse(url)

    @staticmethod
    def build_url(host: str, param: dict) -> str:
        """Build url from host and param"""
        url_parse = urlparse.urlparse(host)
        query = url_parse.query
        url_dict = dict(urlparse.parse_qsl(query))
        url_dict.update(param)
        url_new_query = urlparse.urlencode(url_dict)
        url_parse = url_parse._replace(query=url_new_query)
        return urlparse.urlunparse(url_parse)

    @staticmethod
    def update_param_url(param: dict, key: str, value: str) -> dict:
        """Update param url

        Args:
            param (dict): dictonnary of url param
            key (str): key of the param you want to update
            value (str): new value

        Returns:
            dict: dictonnary of url param updated
        """
        if key in param.keys():
            param.update({key: value})
        return param


    @staticmethod
    def save_as_json(content: list, name_file="database.json", mode="w", nb_indent=4, style_encoding="utf-8", ascii=False):
        if content:
            with open(name_file, mode, encoding=style_encoding) as f:
                json.dump(content, f, ensure_ascii=ascii, indent=int(nb_indent))

        
        
        
    def get_all_links(self, url: str) -> list:
        """
        Get list of all url of a page.

            Parameters:
                url (str): url of the page
            Returns:
                list_items (list): List of url string
        """
        self.driver.get(url)
        list_items = []
        root_xpath = "//*[@id='related-items']/catalog-item-search-results/div[1]/div[2]/div[3]/catalog-items-list"

        # Accept cookies
        self.driver.find_element(
            by="xpath", value="/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]"
        ).click()

        for num_page in range(2, NB_PAGE):

            url_updated = PopScrapper.build_url(
                str(URL["host"]),
                PopScrapper.update_param_url(URL["filter"], "page", str(num_page)),
            )
            self.driver.get(url_updated)
            time.sleep(3)
            for i in range(1, NB_RESULT_BY_PAGE):
                if (
                    len(
                        self.driver.find_elements(
                            by=By.XPATH,
                            value=f"{root_xpath}/div[{str(i)}]/div/div[3]/div[2]/ul/li[1]",
                        )
                    )
                    > 0
                    or len(
                        self.driver.find_elements(
                            by=By.XPATH,
                            value=f"{root_xpath}/div[{str(i)}]/div/div[3]/div/ul/li[1]",
                        )
                    )
                    > 0
                ):
                    link = self.driver.find_element(
                        by=By.XPATH,
                        value=f"{root_xpath}/div[{str(i)}]/div/div[3]/a",
                    ).get_attribute("href")
                    list_items.append(link)
        return list_items

    def get_content_from_url(self, url: str) -> dict:
        """
        Get content from url.

            Parameters:
                url (str): url of the page
            Returns:
                atom (list): Content
        """
        log.info(url)
        list_items = []
        self.driver.get(url)
        cookie_xpath = "/html/body/div[3]/div[2]/div[1]/div[2]/div[2]/button[1]"

        # Accept cookies
        if (
            len(
                self.driver.find_elements(
                    by="xpath",
                    value=cookie_xpath,
                )
            )
            > 0
        ):
            self.driver.find_element(
                by="xpath",
                value=cookie_xpath,
            ).click()

        time.sleep(5)
        bloc = self.driver.find_element(
            by="xpath",
            value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div/div/div[2]",
        )

        atom = {
            "name": self.driver.find_element(
                by=By.XPATH, value="//h1[@class='item-name']"
            ).text,
            "img": self.driver.find_element(
                by=By.XPATH, value="//a[@ng-click='showPhotos()']//img"
            ).get_attribute("src"),
            "data_origin": PopScrapper.get_website_url_info(url).netloc,
        }
        atom["characteristics"] = {}
        xpath_root = "/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div"

        # If the block characeristic is divide in two block, we use the first
        if (
            len(
                bloc.find_elements(
                    by="xpath",
                    value="/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div",
                )
            )
            != 1
        ):
            xpath_root = "/html/body/div[2]/div[3]/div[2]/catalog-item-field-definitions/div[2]/div/div[1]"

        nb_characteristics = len(
            (
                bloc.find_elements(
                    by="xpath",
                    value=xpath_root + "/div/div[2]/div",
                )
            )
        )

        for cpt in range(1, nb_characteristics - 1):
            key = bloc.find_element(
                by="xpath",
                value=xpath_root + "/div/div[2]/div[" + str(cpt) + "]/div[1]/b",
            ).text
            value = bloc.find_element(
                by="xpath",
                value=xpath_root
                + "/div/div[2]/div["
                + str(cpt)
                + "]/div[2]/span/span[2]",
            ).text
            atom["characteristics"][key] = value
            if "," in value:
                atom["characteristics"][key] = value.split(",")

        if (
            len(
                self.driver.find_elements(
                    by=By.XPATH, value="//editable[@class='ng-isolate-scope']"
                )
            )
            > 0
        ):
            atom["barcode"] = self.driver.find_element(
                by=By.XPATH, value="//editable[@class='ng-isolate-scope']"
            ).text

        list_items.append(atom)
        return atom

    def __exit__(self, exc_type, exc_value, traceback):
        """Close selenium driver"""
        self.driver.quit()