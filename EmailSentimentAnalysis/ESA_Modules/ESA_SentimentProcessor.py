# This file will contain all logic for the class Sentiment Processor
import pandas as pd
import csv
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.svm import LinearSVC
from sklearn.model_selection import GridSearchCV
from sklearn.feature_extraction.text import CountVectorizer, TfidfTransformer

from sklearn.pipeline import Pipeline

import joblib

class Sentiment_Classifier:
    def __init__(self):
        self.__clf = joblib.load("Gridsearched Linear-SVM.joblib")
        self.__classified_list = [[]]
        self.__cleaned_data_to_process = [[]]

    def Load_Data_To_Process(self, dataframe):
        self.__cleaned_data_to_process = dataframe
        self.__classified_list = dataframe
        self.__classified_list["Labelled"] = ""

    def Classify(self, dataframe):
        tempDF = dataframe
        predicted = self.__clf.predict(tempDF["Content"])
        tempDF["Labelled"] = predicted
        return tempDF
        

    def Get_Classified(self):
        return pd.DataFrame(self.__classified_list)
    
    def Get_Unprocessed_Data(self):
        return pd.DataFrame(self.__cleaned_data_to_process)
        
