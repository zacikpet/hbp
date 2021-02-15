from .cds import CdsScraper


class L3Scraper(CdsScraper):
    name = 'l3'

    urls = [
        'https://cds.cern.ch/search?cc=L3+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=L3+Papers&ln=en&jrec=201&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=L3+Papers&ln=en&jrec=401&rg=200&p=higgs'
    ]
