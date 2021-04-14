import csv
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from .util import preprocess_text

vectorizer = pickle.load(open('vectorizer', 'rb'))
classifier = pickle.load(open('classifier', 'rb'))

with open('test.csv') as csv_file:

    reader = csv.reader(csv_file)
    test_data = [item for item in reader]

    texts = [preprocess_text(text) for text, model in test_data]
    models = [model for text, model in test_data]

    tfidf_matrix = vectorizer.transform(texts)

    prediction = classifier.predict(tfidf_matrix)

    print(classification_report(models, prediction))
    print(accuracy_score(models, prediction))
