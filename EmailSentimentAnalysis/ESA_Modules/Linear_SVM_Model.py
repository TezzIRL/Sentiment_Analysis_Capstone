###########################################################################################################################################################################
# AUTHOR: Daniel Terry
# Last Modified: 1/11/2023
# Description: This class creates a linear and grid searched classifier for use within a sentiment classifying framework for Project Capstone Team B 2023
###########################################################################################################################################################################

import joblib
import numpy as np
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.model_selection import train_test_split
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC

from sklearn.pipeline import Pipeline
from sklearn import metrics
import os
from joblib import dump

parameters = {
    "vect__ngram_range": [(1, 1), (1, 2)],
    "tfidf__use_idf": (True, False),
    "clf__C": (1, 10),
}


class L_SVM:
    def __init__(self):
        self.__parameters = {
            "vect__ngram_range": [(1, 1), (1, 2)],
            "tfidf__use_idf": (True, False),
            "clf__C": (1, 10),
        }
        # Master Data
        self.__data = None
        # Master Corpus Data
        self.__corpus_data = None
        # Master Target Data
        self.__target_data = None
        
        # TRAIN/TEST SPLIT VARs
        self.__corpus_train = None
        self.__corpus_test = None
        self.__target_train = None
        self.__target_test = None

        # Holds the Seed to Return Consistent Results
        self.__seed = 0
        # Linear CLF
        self.__linear_clf = None
        # Gridsearched CLF
        self.__grid_clf = None

    def load_training(self, file_name):
        try:
            # Read file containing training data
            with open(file_name, "r") as f:
                reader = csv.reader(f)
                data = list(reader)

                # convert data to np array
                self.__data = np.array(data)
                
                # Seperate out corpus and labels
                self.__corpus_data = self.__data[1:-1, 5:6]
                self.__target_data = self.__data[1:-1, 6:7]
        except:
            print("Failed to Load Training Data")
            exit()
            

    def test_split(self, test_ratio, seed):
        self.__seed = seed
        
        self.__corpus_train, self.__corpus_test, self.__target_train, self.__target_test = train_test_split(self.__corpus_data, self.__target_data, test_size=test_ratio, random_state=self.__seed)
        # Flatten Arrays
        self.__corpus_train = self.__corpus_train.flatten()
        self.__corpus_test = self.__corpus_test.flatten()
        self.__target_train = self.__target_train.flatten()
        self.__target_test = self.__target_test.flatten()

    def create_pipeline(self, tolerance, max_iterations):
        self.__linear_clf = Pipeline(
            [
                ("vect", CountVectorizer()),
                ("tfidf", TfidfTransformer()),
                (
                    "clf",
                    LinearSVC(
                        loss="hinge",
                        penalty="l2",
                        random_state=self.__seed,
                        dual=True,
                        tol=tolerance,
                        max_iter=max_iterations,
                    ),
                ),
            ]
        )

    def fit_classifier(self):
        # Fit Linear Classifier
        print("Beginning to fit classifier...")
        self.__linear_clf.fit(self.__corpus_train, self.__target_train)
        print("Classifier fit")
        # Create Gridsearched Classifier
        grid_search = GridSearchCV(self.__linear_clf, self.__parameters, cv=5, n_jobs=-1)
        # Assign
        print("Beginning to Grisearch")
        self.__grid_clf = grid_search.fit(self.__corpus_train, self.__target_train)
        print("Gridsearch finished")

    def save(self, file_name):
        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, file_name)
        dump(self.__grid_clf, path)
        print(f"classified saved as: {file_name}")
        
    def load(self, file_name):
        self.__grid_clf = joblib.load(file_name)
        print(f"classified loaded: {file_name}")
        
    def predict(self, content):
        predicted = self.__grid_clf.predict(content)
        return predicted
    
