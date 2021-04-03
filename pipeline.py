from typing import List

from ner import nlp
from ner.extractors.extract import get_luminosity, get_energy, get_collision, get_production, get_particles
from ner.converters import get_article_text
from ner.decay_a import nlp_decay_a
from nlp.physics_model.classify import get_paper_model


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
    print(item)

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


def extract_collision(item):
    if item['experiment'] in ['aleph', 'delphi', 'l3', 'opal']:
        return {**item, 'collision': ['ee']}

    else:
        entities = (entity['value'] for entity in item['entities']
                    if entity['name'] == 'COLLISION')
        return {
            **item,
            'collision': filter_duplicate([get_collision(entity) for entity in entities])
        }


def extract_production(item):
    entities = (entity['value'] for entity in item['entities']
                if entity['name'] == 'PRODUCTION')
    productions = (get_production(entity) for entity in entities)

    return {
        **item,
        'production': filter_duplicate(
            [prod for prod in productions if prod is not None]
        )
    }


def extract_decay_a(item):
    entities = [entity['value']
                for entity in item['entities'] if entity['name'] == 'DECAY_A']
    return {**item, 'decay_a': entities}


def extract_decay_b(item):
    entities = [entity['value']
                for entity in item['entities'] if entity['name'] == 'DECAY_B']
    return {**item, 'decay_b': entities}


def extract_decay_particles(item):
    result = []
    for text in item['decay_a']:
        doc = nlp_decay_a(text)
        result += [{'name': ent.label_, 'value': ent.text} for ent in doc.ents]

    return {
        **item,
        'particles': {
            'original': filter_duplicate(
                flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'ORIGINAL'])),
            'intermediate': filter_duplicate(
                flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'INTERMEDIATE'])),
            'product': filter_duplicate(
                flatten([get_particles(entity['value']) for entity in result if entity['name'] == 'PRODUCT']))
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
        **item,
        'model': model_text
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
        [classify_model, extract_entities, extract_luminosity, extract_energy, extract_collision,
         extract_production, extract_decay_a, extract_decay_b, extract_decay_particles,
         delete_entities, classify_stage]
    )
