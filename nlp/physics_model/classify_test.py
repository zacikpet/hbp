from sklearn.datasets import load_files
import pickle
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
from sklearn.naive_bayes import GaussianNB
from util import preprocess_text

papers_data = load_files('examples')

papers, models = papers_data.data, papers_data.target

papers = [preprocess_text(paper) for paper in papers]

vectorizer = TfidfVectorizer(max_features=200, min_df=5, max_df=0.7, stop_words=stopwords.words('english'))

papers = vectorizer.fit_transform(papers).toarray()

papers_train, papers_test, models_train, models_test = train_test_split(papers, models, test_size=0.2, random_state=0)

classifier = GaussianNB()

classifier.fit(papers_train, models_train)

models_pred = classifier.predict(papers_test)

print(confusion_matrix(models_test, models_pred))
print(classification_report(models_test, models_pred))
print(accuracy_score(models_test, models_pred))

with open('classifier', 'wb') as pickefile:
    pickle.dump(classifier, pickefile)

with open('vectorizer', 'wb') as pickefile:
    pickle.dump(vectorizer, pickefile)
