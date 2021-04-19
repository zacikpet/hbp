import json
from pylatexenc import latex2text
import random


def get_article_text(title, abstract):
    text = (title or '') + ' . ' + (abstract or '')

    text = text.replace('%', '\\%').replace('\rightarrow', '->')

    try:
        unicode_text = latex2text.latex2text(text, tolerant_parsing=True)
    except latex2text.latexwalker.LatexWalkerError as e:
        print(e)
        unicode_text = text
    except TypeError as t:
        print(t)
        unicode_text = text

    unicode_text = ' '.join(unicode_text.split())

    unicode_text = unicode_text.replace('\rightarrow', '->')

    unicode_text = unicode_text.replace('\n', ' ').replace('\r', '')

    return unicode_text


def json_to_text(input_filename: str, output_filename: str) -> None:
    with open(input_filename) as json_file:
        with open(output_filename, 'w') as txt_file:
            json_data = json.load(json_file)

            for item in json_data:
                title = item['title']
                abstract = item['abstract']
                text = get_article_text(title, abstract)
                txt_file.write(text + '\n')


def shuffle_txt(input_filename: str, output_filename: str) -> None:
    data = []
    with open(input_filename) as input_file:
        for line in input_file:
            data.append(line)

    random.shuffle(data)

    with open(output_filename, 'w') as output_file:
        for line in data:
            output_file.write(line)


def json_to_spacy(file):
    with open(file) as json_file:
        data = json.load(json_file)

        return [
            (
                item['content'],
                {'entities': [
                    entity
                    for entity in item['entities']
                ]}
            )
            for item in data]
