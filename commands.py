import click
import pymongo
import scrapy
from ner import nlp
from ner.extractors.extract import get_luminosity, get_energy, get_collision, get_production
from ner.converters import get_article_text
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from flask.cli import with_appcontext
from config import db_uri
from crawler.hbp.spiders.atlas import AtlasScraper
from crawler.hbp.spiders.cms import CmsScraper
from crawler.hbp.spiders.aleph import AlephScraper
from crawler.hbp.spiders.delphi import DelphiScraper
from crawler.hbp.spiders.l3 import L3Scraper
from crawler.hbp.spiders.opal import OpalScraper
from crawler.hbp.spiders.test import TestScraper
from scrapy.signals import item_passed
from scrapy.signalmanager import dispatcher

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers

spider_names = ['atlas', 'cms', 'aleph', 'delphi', 'l3', 'opal']


def get_spider(name: str) -> scrapy.Spider:
    if name == 'atlas':
        return AtlasScraper
    elif name == 'cms':
        return CmsScraper
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


@click.command('crawl')
@click.option('--experiment', default=None, type=str)
@with_appcontext
def crawl(experiment: str = None):
    if experiment is None:
        print('Crawling all')
        spiders = [get_spider(name) for name in spider_names]
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
    update(experiment)


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
    return {
        **item,
        'luminosity': flatten(
            [get_luminosity(ent['value']) for ent in item['entities'] if ent['name'] == 'LUMINOSITY']
        )
    }


def extract_energy(item):
    return {
        **item,
        'energy': flatten(
            [get_energy(ent['value']) for ent in item['entities'] if ent['name'] == 'ENERGY']
        )
    }


def extract_collision(item):
    if item['experiment'] in ['aleph', 'delphi', 'l3', 'opal']:
        return {
            **item,
            'collision': 'ee'
        }
    else:
        return {
            **item,
            'collision': [get_collision(ent['value']) for ent in item['entities'] if ent['name'] == 'COLLISION']
        }


def extract_production(item):
    return {
        **item,
        'production': list(set([prod for prod in [get_production(ent['value']) for ent in item['entities'] if ent['name'] == 'PRODUCTION'] if prod is not None]))
    }


def delete_entities(item):
    del item['entities']
    return item


@click.command('update')
@click.option('--experiment', default=None)
@with_appcontext
def update(experiment: str = None):
    if experiment is None:
        print('Updating all')
        queryset = papers.find({})
    else:
        print('Updating ' + experiment)
        queryset = papers.find({'experiment': experiment})

    data = list(queryset)

    processed = [
        process_pipeline(item,
                         [extract_entities, extract_luminosity, extract_energy, extract_collision, extract_production,
                          delete_entities])
        for item in data
    ]

    if experiment is None:
        papers.delete_many({})
    else:
        papers.delete_many({'experiment': experiment})

    papers.insert_many(processed)
