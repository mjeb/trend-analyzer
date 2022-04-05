import logging
from typing import List
from hashlib import sha256

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
import numpy as np

log = logging.getLogger(__name__)

nltk.download("stopwords")
nltk.download('punkt')

_STOP_WORDS = set(stopwords.words("dutch"))
_MIN_WORD_LEN = 4


def analyze(websites: pd.DataFrame, corpus: List[str]):
    tokenized_corpus = []
    url_hashes = [(link.split("/")[2], sha256(link.encode("utf-8")).hexdigest()) for link in websites["link"].values]
    for document in corpus:
        tokenized_str = _tokenize(document)
        tokenized_corpus.append(tokenized_str)

    vectorizer = TfidfVectorizer()
    tf_idf_scores = vectorizer.fit_transform(tokenized_corpus).toarray()
    words = vectorizer.get_feature_names_out()

    keywords = []
    for doc_idx, document in enumerate(corpus):
        log.info("...Most standout words for %s (%s)", *url_hashes[doc_idx])
        best_word_indices = np.argsort(tf_idf_scores[doc_idx, :])[-10:]
        for word_idx in best_word_indices:
            if tf_idf_scores[doc_idx, word_idx] > .1:
                log.info("...%s: %s", words[word_idx], round(tf_idf_scores[doc_idx, word_idx], 3))
                keywords.append(words[word_idx])
    return keywords


def _tokenize(document: str) -> str:
    result = []
    words = word_tokenize(document)
    stemmer = SnowballStemmer(language="dutch")
    for word in words:
        if word not in _STOP_WORDS and len(word) >= _MIN_WORD_LEN:

            result.append(stemmer.stem(word.lower()))
    return " ".join(result)
