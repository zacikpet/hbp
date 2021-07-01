import csv
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from util import preprocess_text

vectorizer = pickle.load(open('vectorizer', 'rb'))
classifier = pickle.load(open('classifier', 'rb'))


def perf_measure(y_actual, y_pred):
    TP = 0
    FP = 0
    TN = 0
    FN = 0

    for i in range(len(y_pred)):

        if y_actual[i] == 'BSM' and y_pred[i] == 'BSM':
            TP += 1
        if y_pred[i] == 'BSM' and y_actual[i] == 'SM':
            FP += 1
        if y_actual[i] == 'BSM' and y_pred[i] == 'SM':
            FN += 1
        if y_pred[i] == 'SM' and y_pred[i] == 'SM':
            TN += 1

    return(TP, FP, TN, FN)


with open('test.csv') as csv_file:

    reader = csv.reader(csv_file)
    test_data = [item for item in reader]

    texts = [preprocess_text(text) for text, model in test_data]
    models = [model for text, model in test_data]

    tfidf_matrix = vectorizer.transform(texts)

    prediction = classifier.predict(tfidf_matrix)

    print(classification_report(models, prediction))
    print(accuracy_score(models, prediction))
    print(perf_measure(models, prediction))
