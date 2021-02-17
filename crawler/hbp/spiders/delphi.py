from .cds import CdsScraper


class DelphiScraper(CdsScraper):
    name = 'delphi_papers'
    experiment = 'delphi'
    type = 'paper'

    urls = [
        'https://cds.cern.ch/search?cc=DELPHI+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=DELPHI+Papers&ln=en&jrec=201&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=DELPHI+Papers&ln=en&jrec=401&rg=200&p=higgs'
    ]
