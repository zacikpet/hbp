from .cds import CdsScraper


# TODO
class CdfScraper(CdsScraper):
    name = 'cdf'

    urls = [
        'https://cds.cern.ch/search?cc=CDF+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=CDF+Papers&ln=en&jrec=201&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=CDF+Papers&ln=en&jrec=401&rg=200&p=higgs'
    ]
