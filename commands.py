from typing import Type, List

import click
import pymongo
from flask.cli import with_appcontext
from cds.search import get_all, get
from config import db_uri
from ner import nlp
from ner.extractors.extract import get_luminosity, get_energy, get_collision, get_production
from ner.converters import get_article_text
from crawler.hbp.spiders.atlas import AtlasScraper, AtlasNotesScraper
from crawler.hbp.spiders.cms import CmsScraper, CmsNotesScraper
from crawler.hbp.spiders.aleph import AlephScraper
from crawler.hbp.spiders.delphi import DelphiScraper
from crawler.hbp.spiders.l3 import L3Scraper
from crawler.hbp.spiders.opal import OpalScraper
from crawler.hbp.spiders.cds import CdsScraper
from crawler.hbp.spiders.test import TestScraper
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.signals import item_passed
from scrapy.signalmanager import dispatcher

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers

experiments = ['atlas', 'cms', 'aleph', 'delphi', 'l3', 'opal', 'atlas_notes', 'cms_notes']


def get_spider(name: str) -> Type[CdsScraper]:
    if name == 'atlas':
        return AtlasScraper
    elif name == 'atlas_notes':
        return AtlasNotesScraper
    elif name == 'cms':
        return CmsScraper
    elif name == 'cms_notes':
        return CmsNotesScraper
    elif name == 'aleph':
        return AlephScraper
    elif name == 'delphi':
        return DelphiScraper
    elif name == 'l3':
        return L3Scraper
    elif name == 'opal':
        return OpalScraper
    elif name == 'test':
        return TestScraper
    else:
        raise Exception('No such spider.')


def filter_duplicate(lst: List) -> List:
    return list(set(lst))


@click.command('crawl')
@click.option('--experiment', default=None, type=str)
@with_appcontext
def crawl(experiment: str = None):
    if experiment is None:
        print('Crawling all')
        spiders = [get_spider(name) for name in experiments]
    else:
        print('Crawling' + experiment)
        spiders = [get_spider(experiment)]

    process = CrawlerProcess(get_project_settings())

    for spider in spiders:
        process.crawl(spider)

    results = []

    def add_result(item):
        results.append(item)

    dispatcher.connect(add_result, signal=item_passed)

    process.start()

    if experiment is None:
        papers.delete_many({})
    else:
        papers.delete_many({'experiment': experiment})

    papers.insert_many(results)


@click.command('search')
@click.option('--category', default=None, type=str)
@with_appcontext
def search_cds(category: str = None):
    if category is None:
        print('Search all')
        results = get_all()
    else:
        print('Searching ' + category)
        results = get(category)

    if category is None:
        papers.delete_many({})
    else:
        papers.delete_many({'category': category})

    papers.insert_many(results)


def flatten(list_of_lists):
    result = []
    for sublist in list_of_lists:
        for item in sublist:
            result.append(item)
    return result


def process_pipeline(item, pipes):
    for pipe in pipes:
        item = pipe(item)
    return item


def extract_entities(item):
    text = get_article_text(item['title'], item['abstract'])
    doc = nlp(text)

    return {
        **item,
        'entities': [{'name': ent.label_, 'value': ent.text} for ent in doc.ents]
    }


def extract_luminosity(item):
    entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'LUMINOSITY']

    return {
        **item,
        'luminosity': filter_duplicate(flatten([get_luminosity(entity) for entity in entities]))
    }


def extract_energy(item):
    entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'ENERGY']

    return {
        **item,
        'energy': filter_duplicate(flatten([get_energy(entity) for entity in entities]))
    }


def extract_collision(item):
    if item['experiment'] in ['aleph', 'delphi', 'l3', 'opal']:
        return {**item, 'collision': ['ee']}

    else:
        entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'COLLISION']
        return {
            **item,
            'collision': filter_duplicate([get_collision(entity) for entity in entities])
        }


def extract_production(item):
    entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'PRODUCTION']
    productions = [get_production(entity) for entity in entities]

    return {
        **item,
        'production': filter_duplicate(
            [prod for prod in productions if prod is not None]
        )
    }


def delete_entities(item):
    del item['entities']
    return item


@click.command('update')
@click.option('--category', default=None)
@with_appcontext
def update(category: str = None):
    if category is None:
        print('Updating all')
        queryset = papers.find({})
    else:
        print('Updating ' + category)
        queryset = papers.find({'category': category})

    data = list(queryset)

    processed = [
        process_pipeline(item,
                         [extract_entities, extract_luminosity, extract_energy, extract_collision, extract_production,
                          delete_entities])
        for item in data
    ]

    if category is None:
        papers.delete_many({})
    else:
        papers.delete_many({'category': category})

    papers.insert_many(processed)


@click.command('connect')
@with_appcontext
def connect():
    data = papers.find({})
    for item in data:
        supersedes = papers.find_one({'report_number': item['supersedes']})
        superseded = papers.find_one({'report_number': item['superseded']})

        papers.update_one(item, {'$set': {'supersedes_id': supersedes['_id'] if supersedes is not None else None}})
        papers.update_one(item, {'$set': {'superseded_id': superseded['_id'] if superseded is not None else None}})


@click.command('erase')
@with_appcontext
def erase():
    papers.delete_many({})
