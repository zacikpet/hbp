#! /bin/bash

source ../env/bin/activate
ner_annotator --config=ner_annotator_data.json --config-model=hbp --model=model --input=shuffled.txt