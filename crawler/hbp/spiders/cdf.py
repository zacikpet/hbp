import re
import scrapy
import urllib.parse as urlparse
import dateparser


class CdfScraper(scrapy.Spider):
    name = 'cdf'

    urls = ['https://www-cdf.fnal.gov/physics/new/hdg/Published_files/widget1_markup.html']

    def start_requests(self):
        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for paper in response.xpath('//body/p'):
            url = paper.xpath('.//a/@href').get()

            paper = {
                'experiment': self.name,
                'category': 'cdf_papers',
                'type': 'paper',
                'title': paper.xpath('.//b//text()').get().strip()
            }

            yield scrapy.Request(url=url, callback=self.parse_arxiv, cb_kwargs={'paper': paper})

    @staticmethod
    def parse_arxiv(response, paper):

        pdf = response.css('.download-pdf').xpath('./@href').get()
        pdf = urlparse.urljoin(response.url, pdf.strip())

        dateline = ''.join(response.xpath('.//div[@class="dateline"]//text()').getall())
        date = re.search('[0-9]+ (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [0-9][0-9][0-9][0-9]',
                         dateline).group()
        date = dateparser.parse(date)

        abstract = ''.join(response.css('.abstract').xpath('.//text()').getall())
        abstract = re.sub('Abstract:', '', abstract).strip()
        abstract = re.sub('\n', ' ', abstract)

        yield {
            **paper,
            'files': [pdf],
            'date': date,
            'abstract': abstract
        }
