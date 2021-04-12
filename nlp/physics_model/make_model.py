import csv
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import ComplementNB
from util import preprocess_text


with open('train.csv') as csv_file:
    train_data = csv.reader(csv_file)

    texts, models = zip(*train_data)

    texts = [preprocess_text(text) for text in texts]

    vectorizer = TfidfVectorizer(min_df=5, max_df=0.7)

    tfidf_matrix = vectorizer.fit_transform(texts)

    classifier = ComplementNB()

    classifier.fit(tfidf_matrix, models)

    with open('vectorizer', 'wb') as pickefile:
        pickle.dump(vectorizer, pickefile)

    with open('classifier', 'wb') as pickefile:
        pickle.dump(classifier, pickefile)
