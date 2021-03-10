import datetime
from typing import List, Dict, Tuple, Optional
from xml.etree import ElementTree

import dateparser
import requests

from .category import categories

url = 'http://cds.cern.ch/search?'

tags = {
    'title': '245',
    'supersedes': '780',
    'superseded': '785',
    'abstract': '520',
    'date': '269',
    'report_number': '037',
    'doi': '024',
    'cds_id': '001',
    'files': '856'
}


def search(search_category: str) -> Tuple[List[ElementTree.Element], str]:
    index = 1
    previous_index = 0
    batch = 200
    results = []

    while index != previous_index:
        params = {
            'ot': ','.join(tags.values()),
            # Output format = XML
            'of': 'xm',
            # Search category
            'cc': categories[search_category]['cds_cc'],
            # Language
            'ln': 'en',
            # Number of results
            'rg': batch,
            # Start from result
            'jrec': index,
            # Pattern 1
            'p1': 'higgs',
            # Pattern 1 location
            'f1': 'title'
        }
        response = requests.get(url, params)
        collection = ElementTree.fromstring(response.text)

        previous_index = index
        index += len(collection)
        results += collection

    return results, search_category


def parse_date(date: str) -> Optional[datetime.datetime]:
    options = ['DMY', 'YMD', 'MDY']
    for option in options:
        parsed_date = dateparser.parse(date, settings={'DATE_ORDER': option})
        if parsed_date is not None:
            return parsed_date
    return None


def extract(search_result: Tuple[List[ElementTree.Element], str]) -> List[Dict]:
    ns = '{http://www.loc.gov/MARC21/slim}'

    records, search_category = search_result
    results = []

    for record in records:
        title = record.find(f"{ns}datafield[@tag='{tags['title']}']//{ns}subfield[@code='a']")
        abstract = record.find(f"{ns}datafield[@tag='{tags['abstract']}']//{ns}subfield[@code='a']")
        superseded = record.find(f"{ns}datafield[@tag='{tags['superseded']}']//{ns}subfield[@code='w']")
        supersedes = record.find(f"{ns}datafield[@tag='{tags['supersedes']}']//{ns}subfield[@code='w']")
        report_numbers = record.findall(f"{ns}datafield[@tag='{tags['report_number']}']//{ns}subfield[@code='a']")
        dois = record.findall(f"{ns}datafield[@tag='{tags['doi']}']//{ns}subfield[@code='a']")
        cds_id = record.find(f"{ns}controlfield[@tag='{tags['cds_id']}']")
        date = record.find(f"{ns}datafield[@tag='{tags['date']}']//{ns}subfield[@code='c']")
        files = record.findall(f"{ns}datafield[@tag='{tags['files']}']//{ns}subfield[@code='u']")

        results.append({
            'cds_id': cds_id.text if cds_id is not None else None,
            'category': search_category,
            'experiment': categories[search_category]['experiment'],
            'type': categories[search_category]['type'],
            'title': title.text if title is not None else None,
            'abstract': abstract.text if abstract is not None else None,
            'date': parse_date(date.text) if date is not None else None,
            'superseded': superseded.text if superseded is not None else None,
            'supersedes': supersedes.text if supersedes is not None else None,
            'report_number': [report_number.text for report_number in report_numbers],
            'doi': [doi.text for doi in dois],
            'files': [file.text for file in files if file is not None and '.pdf' in file.text]
        })

    return results


def get(search_category: str) -> List[Dict]:
    return extract(search(search_category))


def get_all() -> List[Dict]:
    results = []
    for category in categories.keys():
        result = get(category)
        results += result
    return results
