import pandas as pd
import spacy
from nltk.corpus import stopwords
import nltk
from collections import Counter
import string
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.model_selection import train_test_split

df = pd.read_csv('sm.csv')
nlp = spacy.load('en_core_web_sm')
punctuations = string.punctuation


# Define function to cleanup text by removing personal pronouns, stopwords, and puncuation
def cleanup_text(docs, logging=False):
    texts = []
    counter = 1
    for doc in docs:
        if counter % 1000 == 0 and logging:
            print("Processed %d out of %d documents." % (counter, len(docs)))
        counter += 1
        doc = nlp(doc, disable=['parser', 'ner'])
        tokens = [tok.lemma_.lower().strip() for tok in doc if tok.lemma_ != '-PRON-']
        tokens = [tok for tok in tokens if tok not in stopwords.words() and tok not in punctuations]
        tokens = ' '.join(tokens)
        texts.append(tokens)
    return pd.Series(texts)


SM_TEXT = [text for text in df[df['model'] == 'SM']['text']]
BSM_TEXT = [text for text in df[df['model'] == 'BSM']['text']]


SM_CLEAN = cleanup_text(SM_TEXT)
SM_CLEAN = ' '.join(SM_CLEAN).split()

BSM_CLEAN = cleanup_text(BSM_TEXT)
BSM_CLEAN = ' '.join(BSM_CLEAN).split()

vectorizer = TfidfVectorizer(max_features=1500, stop_words=stopwords.words('english'))

SM = vectorizer.fit_transform(SM_CLEAN).toarray()


print(SM)