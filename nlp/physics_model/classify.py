import pickle
from sklearn.naive_bayes import GaussianNB
from sklearn.feature_extraction.text import TfidfVectorizer
from .util import preprocess_text

with open('nlp/physics_model/classifier', 'rb') as pickefile:
    classifier: GaussianNB = pickle.load(pickefile)

with open('nlp/physics_model/vectorizer', 'rb') as pickefile:
    vectorizer: TfidfVectorizer = pickle.load(pickefile)


def get_paper_model(paper: str):
    paper = preprocess_text(paper)

    vectorized = vectorizer.transform([paper])

    paper_model = classifier.predict(vectorized.toarray())

    return paper_model[0]
