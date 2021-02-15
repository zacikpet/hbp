from .cds import CdsScraper


class AtlasScraper(CdsScraper):
    name = 'atlas'

    urls = [
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=1&rg=200',
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=201&rg=400',
        # 'https://cds.cern.ch/search?cc=ATLAS+Papers&ln=en&jrec=401&rg=200',
        # 'https://cds.cern.ch/search?cc=ATLAS+Papers&ln=en&jrec=601&rg=200',
        # 'https://cds.cern.ch/search?cc=ATLAS+Papers&ln=en&jrec=801&rg=200',
        # 'https://cds.cern.ch/search?cc=ATLAS+Papers&ln=en&jrec=1001&rg=200',
    ]
