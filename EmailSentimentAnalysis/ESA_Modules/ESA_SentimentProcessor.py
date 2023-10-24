# This file will contain all logic for the class Sentiment Processor
import pandas as pd
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV

from sklearn.pipeline import Pipeline

import joblib

class Sentiment_Classifier:
    def __init__(self):
        self.__clf = joblib.load("Gridsearched Linear-SVM.joblib")
    