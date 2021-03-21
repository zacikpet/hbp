from typing import List

from scrapy.crawler import CrawlerProcess
from scrapy.signals import item_passed
from scrapy.utils.project import get_project_settings
from scrapy.signalmanager import dispatcher
from crawler.hbp.spiders.cdf import CdfScraper
from crawler.hbp.spiders.d0 import D0Scraper


def crawl() -> List:
    spiders = [D0Scraper, CdfScraper]

    results = []

    process = CrawlerProcess(get_project_settings())

    for spider in spiders:
        process.crawl(spider)

    def add_result(item):
        results.append(item)

    dispatcher.connect(add_result, signal=item_passed)

    process.start()

    return results
