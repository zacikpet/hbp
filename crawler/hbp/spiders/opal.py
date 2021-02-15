from .cds import CdsScraper


class OpalScraper(CdsScraper):
    name = 'opal'

    urls = [
        'https://cds.cern.ch/search?cc=OPAL+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=OPAL+Papers&ln=en&jrec=201&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=OPAL+Papers&ln=en&jrec=401&rg=200&p=higgs'
    ]
