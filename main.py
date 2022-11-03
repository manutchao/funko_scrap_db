""" Script to scrap data from website """
from PopScrapper import PopScrapper


if __name__ == "__main__":
    with PopScrapper() as scrapper:
        WEBSITE = "https://www.hobbydb.com/marketplaces/hobbydb/subjects/pop-vinyl-series"
        all_links = scrapper.get_all_links(WEBSITE)
        content_url = list(map(scrapper.get_content_from_url, all_links))
        PopScrapper.save_as_json(content_url)
        