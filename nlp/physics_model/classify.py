import pickle
from .util import preprocess_text


def predict_model(paper: str):

    vectorizer = pickle.load(open('nlp/physics_model/vectorizer', 'rb'))
    classifier = pickle.load(open('nlp/physics_model/classifier', 'rb'))

    processed_paper = preprocess_text(paper)

    feature_vector = vectorizer.transform([processed_paper])

    paper_model = classifier.predict(feature_vector)

    return paper_model[0].lower()
