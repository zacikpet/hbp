import nltk

DATA_PATH = '/app/nltk_data'

nltk.download('stopwords', download_dir=DATA_PATH)
nltk.download('wordnet', download_dir=DATA_PATH)

nltk.data.path.append(DATA_PATH)
