from typing import List

import parsel
import scrapy
import re


class Result(scrapy.Item):
    papers = scrapy.Field()


class D0Scraper(scrapy.Spider):
    name = 'd0'

    urls = ['https://www-d0.fnal.gov/d0_publications/']

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):

        def is_ordinal(_, texts: List[str]) -> bool:
            return re.match('^[0-9]+[.]$', texts[0]) is not None

        parsel.xpathfuncs.set_xpathfunc('is_ordinal', is_ordinal)
        ordinals = response.xpath('//font[@size=2 and is_ordinal(text())]')

        for ordinal in ordinals:
            yield {
                'title': ordinal.xpath('following-sibling::a/text()').get(),
                'link': ordinal.xpath('following-sibling::a/@href').get(),
                'luminosity': ordinal.xpath('following-sibling::font[@color="#cc00cc"]/text()').get()
            }
