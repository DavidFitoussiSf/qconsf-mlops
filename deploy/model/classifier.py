from typing import List
import numpy as np
import joblib

import gensim.downloader as gensim_downloader
from gensim.utils import tokenize as gensim_tokenizer
from loguru import logger

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression

class WordVectorFeaturizer(BaseEstimator, TransformerMixin):
    def __init__(self, dim: int, word_vector_model: str):
        self.dim = dim
        self.word_vector_model = gensim_downloader.load(word_vector_model)

    #estimator. Since we don't have to learn anything in the featurizer, this is a no-op
    def fit(self, X, y=None):
        return self

    #transformation: return the average word vector of each token in the document
    def transform(self, X, y=None):
        """
        Goal: WordVectorFeaturizer's transform() method converts the raw text document
        into a feature vector to be passed as input to the classifier.
            
        (1) Convert the raw text document into a list of tokens
        (2) Map each token to a word vector (using self.word_vector_model)
        (3) Return the mean vector of the sequence of word vectors
        This will be our feature representation of the document
        """
        X_t = []
        for doc in X:
            tokens = gensim_tokenizer(doc, lowercase=True, deacc=True)
            tokens = [
                word for word in tokens if word in self.word_vector_model.vocab]
            if len(tokens) == 0:
                X_t.append(np.zeros(self.dim))
            else:
                X_t.append(np.mean(self.word_vector_model[tokens], axis=0))
        return X_t


class NewsCategoryClassifier:

    DEFAULT_WORD_VECTOR_MODEL = 'glove-wiki-gigaword-100'
    DEFAULT_DIM = 100

    def __init__(self, config: dict) -> None:
        self.config = config
        self.pipeline: Pipeline = None
        self.classes: List = []
    
    def _initialize_pipeline(self, verbose: bool = False) -> Pipeline:
        # Initialize the word vector model
        word_vector_model = self.config.get(
            'word_vector_model', self.DEFAULT_WORD_VECTOR_MODEL
        )
        dimensionality = self.config.get(
            'word_vector_dim', self.DEFAULT_DIM
        )
        pipeline = Pipeline([
            ('featurizer',
             WordVectorFeaturizer(
                 dim=dimensionality,
                 word_vector_model=word_vector_model
             )
            ),
            ('classifier',
             LogisticRegression(
                 multi_class='multinomial',
                 tol=0.001,
                 solver='saga',
             )
            )
        ], verbose=verbose)
        return pipeline
    
    def fit(self, X_train: List, y_train: List, verbose: bool = False) -> None:
        logger.info("Beginning model training ...")
        if not self.pipeline:
            self.pipeline = self._initialize_pipeline(verbose)
        self.pipeline.fit(X_train, y_train)
        self.classes = self.pipeline['classifier'].classes_
    
    def dump(self, model_path: str) -> None:
        joblib.dump(self.pipeline, model_path)
        logger.info(f"Saved trained model pipeline to: {model_path}")

    def load(self, model_path: str) -> None:
        logger.info(f"Loaded trained model pipeline from: {model_path}")
        self.pipeline = joblib.load(model_path)
        self.classes = self.pipeline['classifier'].classes_

    def predict_proba(self, model_input: str) -> dict:
        prediction = self.pipeline.predict_proba([model_input])
        classes_to_probs = dict(zip(self.classes, prediction[0].tolist()))
        return classes_to_probs

    def predict_label(self, model_input: str) -> str:
        prediction = self.pipeline.predict([model_input])
        return prediction[0]
