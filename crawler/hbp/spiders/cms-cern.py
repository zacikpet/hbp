import scrapy
import urllib.parse as urlparse

URL_PRELIMINARY = 'http://cms-results.web.cern.ch/cms-results/public-results/preliminary-results/HIG/index.html'
URL_PUBLICATIONS = 'http://cms-results.web.cern.ch/cms-results/public-results/publications/HIG/HIG.html'


class CmsScraper(scrapy.Spider):
    name = 'cms-cern'

    def start_requests(self):
        urls = [URL_PRELIMINARY, URL_PUBLICATIONS]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):

        for row in response.xpath('//table[1]//tr'):

            a_element = row.xpath('td[@class="cadi"]//a')

            if a_element.get() is None:
                continue

            link = a_element.attrib['href']

            url = urlparse.urljoin(response.url, link.strip())

            yield scrapy.Request(url, self.parse_sub)

    def parse_sub(self, response):

        pdf = response.xpath('//table[1]//tr[7]//a[2]').attrib['href']

        yield {
            'url': pdf
        }
