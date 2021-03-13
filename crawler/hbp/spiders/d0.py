from typing import List

import parsel
import dateparser
import scrapy
import re
import urllib.parse as urlparse


class D0Scraper(scrapy.Spider):
    name = 'd0'

    urls = ['https://www-d0.fnal.gov/d0_publications/']

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        def is_ordinal(_, texts: List[str]) -> bool:
            return re.match('^[0-9]+[.]$', texts[0]) is not None

        def is_date(_, texts: List[str]) -> bool:
            if len(texts) == 0:
                return False

            if re.search('[0-9]+/[0-9]+/[0-9]+', texts[0]) is not None:
                return True
            else:
                return False

        parsel.xpathfuncs.set_xpathfunc('is_ordinal', is_ordinal)
        parsel.xpathfuncs.set_xpathfunc('is_date', is_date)
        ordinals = response.xpath('//font[@size=2 and is_ordinal(text())]')

        results = [
            {
                'title': ''.join(ordinal.xpath('(./following-sibling::a)[1]//text()').getall()),
                'link': ordinal.xpath('following-sibling::a/@href').get(),
                'luminosity': ordinal.xpath('following-sibling::font[@color="#cc00cc"]/text()').get(),
                'date': dateparser.parse(re.search(
                    '[0-9]+/[0-9]+/[0-9]+',
                    ordinal.xpath('following-sibling::font[@size=2 and is_date(text())]//text()').get()
                ).group())
            }
            for ordinal in ordinals
        ]

        results = [result for result in results if 'higgs' in result['title'].lower()]

        for result in results:
            yield scrapy.Request(result['link'], self.parse_aps, cb_kwargs={'paper': result})

    def parse_aps(self, response, paper):

        pdf = response.xpath('//a[text() = "PDF"]/@href').get()
        pdf = urlparse.urljoin(response.url, pdf.strip())

        yield {
            **paper,
            'experiment': self.name,
            'type': 'paper',
            'category': 'd0_papers',
            'abstract': ''.join(response.css('.abstract').xpath('(.//div[@class="content"]//p)[1]//text()').getall()),
            'files': [pdf]
        }
