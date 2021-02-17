import scrapy
import urllib.parse as urlparse
from typing import Optional


class CdsScraper(scrapy.Spider):
    experiment = None
    type = None
    urls = []

    def start_requests(self):

        if not self.urls:
            print("This is an abstract spider. Please run a subclass spider.")

        for url in self.urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):

        # locate the table
        table = response.xpath('//div[@class="pagebody"]//form[3]/table[1]/tr')

        for row in table:

            title = self.extract_title(row)
            links = self.extract_links(row)

            if not links:
                # TODO log failure
                print("No link found!")
                link = ''
            else:
                link = self.get_preferred_link(links)
                # sometimes the path is relative to the current location
                # if so, we join it with the base url
                if link.startswith('/'):
                    link = urlparse.urljoin(response.url, link.strip())

            detail_link = self.extract_detail_link(row)

            callback_kwargs = dict(
                title=title,
                link=link
            )

            yield scrapy.Request(detail_link, self.parse_detail, cb_kwargs=callback_kwargs)

    def parse_detail(self, response, title, link):
        date = self.extract_date(response)
        abstract = self.extract_abstract(response)
        doi = self.extract_doi(response)
        report_number = self.extract_report_number(response)
        related = self.extract_related(response)

        yield {
            'experiment': self.experiment,
            'type': self.type,
            'report_number': report_number,
            'related': related,
            'title': title,
            'link': link,
            'date': date,
            'abstract': abstract,
            'doi': doi
        }

    @staticmethod
    def valid(link):
        # If a link at least contains one of these patterns,
        # mark it as invalid
        forbidden_patterns = [
            'dx.doi.org',
            '/search?',
            'draft',
            'holdings?'
        ]

        # If a link does not contain at least one of these
        # patterns, mark it as invalid
        required_patterns = [
            '.pdf',
            '.ps.gz',
            '.ps'
        ]

        for ignored_pattern in forbidden_patterns:
            if ignored_pattern in link:
                return False

        for required_pattern in required_patterns:
            if required_pattern in link:
                return True

        return False

    @staticmethod
    def get_preferred_link(links):
        # If a link contains one of these patterns, it is returned immediately
        # The patterns are checked in this order
        order_of_preference = [
            'cds',
            'record'
            'arxiv.org'
        ]

        for pattern in order_of_preference:
            for link in links:
                if pattern in link:
                    return link

        # If no pattern was found, return the first link
        return links[0]

    @staticmethod
    def extract_title(row) -> str:
        # the title is always the first bold text
        return row.xpath('td[2]//strong[1]//text()').get()

    @staticmethod
    def extract_detail_link(row) -> str:
        # the title links to the details
        return row.xpath('td[2]//a[1]//@href').get()

    def extract_links(self, row) -> list:
        # select all the <a> elements in this row
        a_elements = row.xpath('td[2]//a')

        # extract all valid links from all <a> elements
        return [
            a_element.attrib['href'] for a_element in a_elements
            if 'href' in a_element.attrib and self.valid(a_element.attrib['href'])
        ]

    @staticmethod
    def extract_date(document) -> str:
        dates_info: str = document.xpath('//div[@class = "recordlastmodifiedbox"]//text()').get()
        date_created: str = dates_info.split(sep=' ')[2].strip(',')
        return date_created

    @staticmethod
    def table_item(document, name_match: str):

        results = document.xpath(
            '//table[@class = "formatRecordTableFullWidth"]//'
            'td[1][contains(translate(normalize-space(.), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", '
            '"abcdefghijklmnopqrstuvwxyz"), "' + name_match.lower() + '")]/following-sibling::td//text()').getall()

        return ' '.join(results)

    @classmethod
    def extract_abstract(cls, document) -> str:
        return cls.table_item(document, 'abstract')

    @classmethod
    def extract_report_number(cls, document) -> str:
        return cls.table_item(document, 'report number')

    @classmethod
    def extract_related(cls, document) -> Optional[str]:
        return cls.table_item(document, 'related')

    @staticmethod
    def extract_doi(document) -> str:
        return document.xpath('//a[@title = "DOI"]//text()').get()
