from .cds import CdsScraper


class CmsScraper(CdsScraper):
    name = 'cms_papers'
    experiment = 'cms'
    type = 'paper'

    urls = [
        'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=201&rg=400&p=higgs',
        'https://cds.cern.ch/search?cc=CMS+Papers&ln=en&jrec=401&rg=600&p=higgs',
    ]


class CmsNotesScraper(CdsScraper):
    name = 'cms_notes'
    experiment = 'cms'
    type = 'note'

    urls = [
        'https://cds.cern.ch/search?cc=CMS+Physics+Analysis+Summaries&ln=en&jrec=1&rg=200&p=higgs',
        'https://cds.cern.ch/search?cc=CMS+Physics+Analysis+Summaries&ln=en&jrec=201&rg=400&p=higgs',
        'https://cds.cern.ch/search?cc=CMS+Physics+Analysis+Summaries&ln=en&jrec=401&rg=600&p=higgs',
    ]
