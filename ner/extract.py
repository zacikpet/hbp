import spacy

model_name = 'model_v1.1'

test_text = input("Enter text:")

nlp = spacy.load(model_name)

doc = nlp(test_text)

for ent in doc.ents:
    print(ent.label_ + ': ' + ent.text)
