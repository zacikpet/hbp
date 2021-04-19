import spacy
import random
from spacy.training import Example
from spacy.util import minibatch

from converters import json_to_spacy

TRAIN_DATA = json_to_spacy('traindata_v1.3.json')


def train_spacy(train_data, iterations):
    nlp = spacy.blank('en')  # create blank Language class
    # create the built-in pipeline components and add them to the pipeline
    # nlp.create_pipe works for built-ins that are registered with spaCy
    ner = nlp.add_pipe('ner')

    for _, annotations in train_data:
        for _, _, label in annotations.get('entities'):
            ner.add_label(label)

    # get names of other pipes to disable them during training
    other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']
    with nlp.disable_pipes(*other_pipes):  # only train NER

        examples = []
        for text, annotations in train_data:
            examples.append(Example.from_dict(nlp.make_doc(text), annotations))

        nlp.initialize(lambda: examples)

        for itn in range(iterations):
            print("Starting iteration " + str(itn))
            random.shuffle(examples)
            losses = {}
            for batch in minibatch(examples, size=8):
                nlp.update(batch, losses=losses)

            print(losses)
    return nlp


if __name__ == '__main__':
    nlp = train_spacy(TRAIN_DATA, 50)

    # Save our trained Model
    modelfile = input("Enter your Model Name: ")
    nlp.to_disk(modelfile)
    print('Saved model ' + modelfile)
