from .cds import CdsScraper


class TestScraper(CdsScraper):
    name = 'test'
    experiment = 'test'
    type = 'test'

    urls = [
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=1&rg=3'
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=100&rg=3'
    ]
