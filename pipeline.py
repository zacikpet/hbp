from typing import List

from ner import nlp
from ner.extractors.extract import get_luminosity, get_energy, get_collision, get_production, get_associated_production, get_particles
from ner.converters import get_article_text
from ner.decay_a import nlp_decay_a
from nlp.physics_model.classify import predict_model


def filter_duplicate(lst: List) -> List:
    return list(set(lst))


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
    if 'luminosity' in item:
        return item
    else:
        entities = [entity['value']
                    for entity in item['entities'] if entity['name'] == 'LUMINOSITY']

    return {
        **item,
        'luminosity': filter_duplicate(flatten([get_luminosity(entity) for entity in entities]))
    }


def extract_energy(item):
    entities = (entity['value']
                for entity in item['entities'] if entity['name'] == 'ENERGY')

    if item['experiment'] in ['cdf', 'd0']:
        return {**item, 'energy': [1960000]}

    lhc_energies = [7000000, 8000000, 13000000, 14000000]

    energies = filter_duplicate(
        flatten([get_energy(entity) for entity in entities])
    )

    if item['experiment'] in ['atlas', 'cms']:
        energies = [energy for energy in energies if energy in lhc_energies]

    return {
        **item,
        'energy': energies
    }


def extract_production(item):
    production_entities = [entity['value'] for entity in item['entities']
                           if entity['name'] == 'PRODUCTION']

    productions = [get_production(entity) for entity in production_entities]

    associated_entites = [
        entity['value'] for entity in item['entities'] if entity['name'] == 'ASSOCIATED'
    ]

    associated_productions = [
        get_associated_production(entity) for entity in associated_entites
    ]

    return {
        **item,
        'production': filter_duplicate(
            [prod for prod in productions +
                associated_productions if prod is not None]
        )
    }


def parse_notation_products(text: str):
    text = text.lower()

    split = text.replace('→', '->').replace('to',
                                            '->').replace('â', '->').split('->')

    if len(split) < 2:
        return []

    decay_mode = split[1]

    return get_particles(decay_mode)


def is_notation(text: str):
    return '->' in text or '→' in text


def extract_decay_particles(item):
    decay_products = [entity['value']
                      for entity in item['entities'] if entity['name'] == 'DECAY_PRODUCT']

    decay_channels = [entity['value']
                      for entity in item['entities'] if entity['name'] == 'DECAY_CHANNEL']

    decay_channels_notations = [c for c in decay_channels if is_notation(c)]

    decay_channels_particles = [
        c for c in decay_channels if not is_notation(c)]

    decay_notations = [entity['value']
                       for entity in item['entities'] if entity['name'] == 'DECAY_NOTATION']

    all_notations = decay_channels_notations + decay_notations

    particles = (
        flatten([get_particles(text) for text in decay_products]) +
        flatten([get_particles(text) for text in decay_channels_particles]) +
        flatten([parse_notation_products(text) for text in all_notations])
    )

    return {
        **item,
        'particles': {
            'product': filter_duplicate([p for p in particles if p is not None and p != 'gluon'])
        }
    }


def classify_model(item):
    text = get_article_text(item['title'], item['abstract'])
    model = predict_model(text)

    return {
        **item,
        'model': model
    }


def classify_stage(item):
    if item['type'] == 'note':
        stage = 'preliminary'
    else:
        if 'doi' in item and len(item['doi']) == 1:
            stage = 'submitted'
        else:
            stage = 'published'

    return {
        **item,
        'stage': stage
    }


def delete_entities(item):
    del item['entities']
    return item


def pipeline(article):
    return process_pipeline(
        article,
        [classify_model, extract_entities, extract_luminosity, extract_energy,
         extract_production, extract_decay_particles,
         delete_entities, classify_stage]
    )
