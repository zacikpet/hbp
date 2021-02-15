from .cds import CdsScraper


class AlephScraper(CdsScraper):
    name = 'aleph'

    urls = [
        'https://cds.cern.ch/search?cc=ALEPH+Papers&ln=en&jrec=1&rg=200&p=higgs',
        #'https://cds.cern.ch/search?cc=ALEPH+Papers&ln=en&jrec=201&rg=200&p=higgs',
        #'https://cds.cern.ch/search?cc=ALEPH+Papers&ln=en&jrec=401&rg=200'
    ]
