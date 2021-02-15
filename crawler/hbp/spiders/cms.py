from .cds import CdsScraper


class CmsScraper(CdsScraper):
    name = 'cms'

    urls = [
        'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=201&rg=200&p=higgs',
        #'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=401&rg=200',
        #'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=601&rg=200',
        #'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=801&rg=200',
        #'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=1001&rg=200',
        #'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=1201&rg=200',
    ]