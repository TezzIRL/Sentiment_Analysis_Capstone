# This file will contain all logic for the class Sentiment Processor
import pandas as pd
from .Linear_SVM_Model import L_SVM
from pathlib import Path

class Sentiment_Classifier:
    def __init__(self):
        self.__clf = L_SVM()
        self.__check_for_saved_model('LinearCLF.joblib')
        self.__classified_list = [[]]
        self.__cleaned_data_to_process = [[]]

    def __build_clf(self):
        p = Path(__file__).with_name('4763_oversampled.csv')
        self.__clf.load_training(p)
        self.__clf.test_split(0.2, 102)
        self.__clf.create_pipeline(1e-5, 100000)
        self.__clf.fit_classifier()
        self.__clf.save("LinearCLF.joblib")

    def __check_for_saved_model(self, file_name):
        try:
            p =  Path(__file__).with_name(file_name)
            print("classifier was found")
            self.__clf.load(p)
        except Exception as err:
            #file doesnt exist create a new classifier
            print(f"Unexpected {err}")
            self.__build_clf()
        
    def Classify(self, dataframe):
        tempDF = dataframe
        predicted = self.__clf.predict(tempDF["Content"])
        tempDF["Labelled"] = predicted
        return tempDF 