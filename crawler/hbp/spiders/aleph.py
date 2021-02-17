from .cds import CdsScraper


class AlephScraper(CdsScraper):
    name = 'aleph_papers'
    experiment = 'aleph'
    type = 'paper'

    urls = [
        'https://cds.cern.ch/search?cc=ALEPH+Papers&ln=en&jrec=1&rg=200&p=higgs'
    ]
