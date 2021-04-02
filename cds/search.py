from typing import List, Dict, Tuple
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
    'files': '856',
    'timestamp': '005'
}


def search(search_category: str) -> Tuple[List[Tuple[ElementTree.Element, str]], str]:
    index = 1
    previous_index = 0
    batch = 200
    results: List[Tuple[ElementTree.Element, str]] = []

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

        xml_params = {
            ** params,
            'ot': ','.join(tags.values()),
            'of': 'xm'
        }

        xml_response = requests.get(url, xml_params)
        collection = ElementTree.fromstring(xml_response.text)

        json_params = {
            ** params,
            'ot': 'creation_date',
            'of': 'recjson'
        }

        json_response = requests.get(url, json_params).json()

        creation_dates = [item.get('creation_date', None) for item in json_response]

        previous_index = index
        index += len(collection)
        results += zip(collection, creation_dates)

    return results, search_category


def extract(search_result: Tuple[List[Tuple[ElementTree.Element, str]], str]) -> List[Dict]:
    ns = '{http://www.loc.gov/MARC21/slim}'

    records, search_category = search_result
    results = []

    for record, creation_date in records:
        title = record.find(f"{ns}datafield[@tag='{tags['title']}']//{ns}subfield[@code='a']")
        abstract = record.find(f"{ns}datafield[@tag='{tags['abstract']}']//{ns}subfield[@code='a']")
        superseded = record.find(f"{ns}datafield[@tag='{tags['superseded']}']//{ns}subfield[@code='w']")
        supersedes = record.find(f"{ns}datafield[@tag='{tags['supersedes']}']//{ns}subfield[@code='w']")
        report_numbers = record.findall(f"{ns}datafield[@tag='{tags['report_number']}']//{ns}subfield[@code='a']")
        dois = record.findall(f"{ns}datafield[@tag='{tags['doi']}']//{ns}subfield[@code='a']")
        cds_id = record.find(f"{ns}controlfield[@tag='{tags['cds_id']}']")
        timestamp = record.find(f"{ns}controlfield[@tag='{tags['timestamp']}']")
        signed_date = record.find(f"{ns}datafield[@tag='{tags['date']}']//{ns}subfield[@code='c']")
        files = record.findall(f"{ns}datafield[@tag='{tags['files']}']//{ns}subfield[@code='u']")

        date_preference = ['creation_date', 'signed_dmy_date', 'signed_ymd_date', 'timestamp_date']

        dates = dict()

        if creation_date is not None:
            dates['creation_date'] = dateparser.parse(creation_date)

        if signed_date is not None:
            dates['signed_dmy_date'] = dateparser.parse(signed_date.text, settings={'DATE_ORDER': 'DMY'})
            dates['signed_ymd_date'] = dateparser.parse(signed_date.text, settings={'DATE_ORDER': 'YMD'})

        if timestamp is not None:
            dates['timestamp_date'] = dateparser.parse(
                ' '.join([timestamp.text[0:4], timestamp.text[4:6], timestamp.text[6:8]]),
                settings={'DATE_ORDER': 'YMD'}
            )

        for option in date_preference:
            if option in dates and dates[option] is not None:
                final_date = dates[option]
                break
        else:
            final_date = None

        results.append({
            'cds_id': cds_id.text if cds_id is not None else None,
            'category': search_category,
            'experiment': categories[search_category]['experiment'],
            'type': categories[search_category]['type'],
            'title': title.text if title is not None else None,
            'abstract': abstract.text if abstract is not None else None,
            'date': final_date,
            'superseded': superseded.text if superseded is not None else None,
            'supersedes': supersedes.text if supersedes is not None else None,
            'report_number': [report_number.text for report_number in report_numbers],
            'doi': [doi.text for doi in dois],
            'files': [file.text for file in files if file is not None and '.pdf' in file.text]
        })

    return results


def get(search_category: str) -> List[Dict]:
    return extract(search(search_category))


def get_many(search_categories: List[str]) -> List[Dict]:
    results = []
    for category in search_categories:
        result = get(category)
        results += result
    return results


def get_all() -> List[Dict]:
    results = []
    for category in categories.keys():
        result = get(category)
        results += result
    return results
