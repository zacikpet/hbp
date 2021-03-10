import click
import pymongo
import json
from bson import json_util
from flask.cli import with_appcontext
from cds.search import get_all, get
from ner import nlp
from ner.extractors.extract import get_luminosity, get_energy, get_collision, get_production, get_particles
from ner.converters import get_article_text
from ner.decay_a import nlp_decay_a
from config import db_uri
from typing import List
from nlp.physics_model.classify import get_paper_model

mongo = pymongo.MongoClient(db_uri)
papers: pymongo.collection.Collection = mongo.hbp.papers


def filter_duplicate(lst: List) -> List:
    return list(set(lst))


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

    with open('latest.json', 'w') as latest:
        json.dump(results, latest, default=json_util.default)

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
    entities = (entity['value'] for entity in item['entities'] if entity['name'] == 'LUMINOSITY')

    return {
        **item,
        'luminosity': filter_duplicate(flatten([get_luminosity(entity) for entity in entities]))
    }


def extract_energy(item):
    entities = (entity['value'] for entity in item['entities'] if entity['name'] == 'ENERGY')

    return {
        **item,
        'energy': filter_duplicate(flatten([get_energy(entity) for entity in entities]))
    }


def extract_collision(item):
    if item['experiment'] in ['aleph', 'delphi', 'l3', 'opal']:
        return {**item, 'collision': ['ee']}

    else:
        entities = (entity['value'] for entity in item['entities'] if entity['name'] == 'COLLISION')
        return {
            **item,
            'collision': filter_duplicate([get_collision(entity) for entity in entities])
        }


def extract_production(item):
    entities = (entity['value'] for entity in item['entities'] if entity['name'] == 'PRODUCTION')
    productions = (get_production(entity) for entity in entities)

    return {
        **item,
        'production': filter_duplicate(
            [prod for prod in productions if prod is not None]
        )
    }


def extract_decay_a(item):
    entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'DECAY_A']
    return {**item, 'decay_a': entities}


def extract_decay_b(item):
    entities = [entity['value'] for entity in item['entities'] if entity['name'] == 'DECAY_B']
    return {**item, 'decay_b': entities}


def extract_decay_particles(item):
    result = []
    for text in item['decay_a']:
        doc = nlp_decay_a(text)
        result += [{'name': ent.label_, 'value': ent.text} for ent in doc.ents]

    return {
        **item,
        'particles': {
            'original': filter_duplicate(flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'ORIGINAL'])),
            'intermediate': filter_duplicate(flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'INTERMEDIATE'])),
            'product': filter_duplicate(flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'PRODUCT']))
        },
        'decay': {
            'original': [entity['value'] for entity in result if entity['name'] == 'ORIGINAL'],
            'intermediate': [entity['value'] for entity in result if entity['name'] == 'INTERMEDIATE'],
            'product': [entity['value'] for entity in result if entity['name'] == 'PRODUCT']
        }
    }


def classify_model(item):
    text = get_article_text(item['title'], item['abstract'])
    model = get_paper_model(text)

    if model == 0:
        model_text = 'bsm'
    else:
        model_text = 'sm'

    return {
        ** item,
        'model': model_text
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
                         [classify_model, extract_entities, extract_luminosity, extract_energy, extract_collision, extract_production,
                          extract_decay_a, extract_decay_b, extract_decay_particles, delete_entities])
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
    relevant = papers.find({'$or': [
        {'supersedes': {'$ne': None, '$exists': True}},
        {'superseded': {'$ne': None, '$exists': True}}
    ]})

    for paper in relevant:
        supersedes = papers.find_one({'cds_id': paper['supersedes']})
        superseded = papers.find_one({'cds_id': paper['superseded']})

        papers.update_one(paper, {'$set': {
            'supersedes_id': supersedes['_id'] if supersedes is not None else None,
            'superseded_id': superseded['_id'] if superseded is not None else None,
        }})


@click.command('erase')
@with_appcontext
def erase():
    papers.delete_many({})
