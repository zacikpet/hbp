import re
import nltk
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords

nltk.data.path.append('/app/nltk_data')

stemmer = WordNetLemmatizer()


def preprocess_text(text: str):
    # Remove all the special characters
    text = re.sub(r'\W', ' ', text)

    # remove all single characters
    text = re.sub(r'\s+[a-zA-Z]\s+', ' ', text)

    # Remove single characters from the start
    text = re.sub(r'\^[a-zA-Z]\s+', ' ', text)

    # Substituting multiple spaces with single space
    text = re.sub(r'\s+', ' ', text, flags=re.I)

    # Removing prefixed 'b'
    text = re.sub(r'^b\s+', '', text)

    # Converting to Lowercase
    text = text.lower()

    # Remove numbers
    text = re.sub(r'[0-9]+', '', text)

    # Lemmatization
    text = text.split()

    text = [stemmer.lemmatize(word) for word in text]

    # Remove stop words

    text = [word for word in text if word not in stopwords.words('english')]

    text = ' '.join(text)

    return text
