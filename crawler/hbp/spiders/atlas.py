from .cds import CdsScraper


class AtlasScraper(CdsScraper):
    name = 'atlas_papers'
    experiment = 'atlas'
    type = 'paper'

    urls = [
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=1&rg=200',
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=201&rg=400',
        'https://cds.cern.ch/search?cc=ATLAS+Papers&p=higgs&ln=en&jrec=401&rg=600',
    ]


class AtlasNotesScraper(CdsScraper):
    name = 'atlas_notes'
    experiment = 'atlas'
    type = 'note'

    urls = [
        'https://cds.cern.ch/search?cc=ATLAS+Conference+Notes&p=higgs&ln=en&jrec=1&rg=200',
        'https://cds.cern.ch/search?cc=ATLAS+Conference+Notes&p=higgs&ln=en&jrec=201&rg=400',
        'https://cds.cern.ch/search?cc=ATLAS+Conference+Notes&p=higgs&ln=en&jrec=401&rg=600',
    ]
