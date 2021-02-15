from .cds import CdsScraper


class TestScraper(CdsScraper):
    name = 'test'

    urls = [
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=1&rg=5'
    ]
