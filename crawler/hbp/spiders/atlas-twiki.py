import scrapy


class AtlasScraper(scrapy.Spider):
    name = 'atlas-twiki'

    def start_requests(self):
        urls = [
            'https://twiki.cern.ch/twiki/bin/view/AtlasPublic/Publications',  # the target URL to be scrapped
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response, **kwargs):
        for row in response.xpath('//table//tr'):  # locates the table including the data
            if row.xpath('td[2]//text()').get() in ["HIGG",
                                                    "HDBS"]:  # checks if current row belongs to the "HIGG" category
                yield {
                    scrapy.Request(row.xpath('td[7]//@href').get(), self.parse_sub)
                }

                # yield {  # scrapes the needed cells from the table
                #     'title': row.xpath('td[1]//text()').get(),
                #     'group': row.xpath('td[2]//text()').get(),
                #     'journal_reference': row.xpath('td[3]//text()').get(),
                #     'submitted_on': row.xpath('td[4]//text()').get(),
                #     'energy': row.xpath('td[5]//text()').get(),
                #     'luminosity': row.xpath('td[6]//text()').get(),
                #     'link': row.xpath('td[7]//@href').get(),
                # }

    def parse_sub(self, response):

        pdf = response.xpath()
