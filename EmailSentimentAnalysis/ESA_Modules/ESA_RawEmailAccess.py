# This file will contain the class Raw Email Access and all its logic

from email.parser import Parser
import re
import time
import pandas as pd
from spellchecker import SpellChecker
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import string
import datetime
from dateutil import parser

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

class Preprocessor:
    def __init__(self):
        self.__emails = [['Subject', 'From', 'To', 'Year', 'Month', 'Day', 'Time', 'Message-ID', 'Content']]
        self.__lemmatizer = WordNetLemmatizer()
        self.__stop_words = set(stopwords.words('english'))
        self.__spellChecker = SpellChecker()
                

    def get_dataframe(self):
        email_df = pd.DataFrame(self.__emails)
        email_df.columns = email_df.iloc[0]
        email_df = email_df[1:]
        return email_df

    def __extract_email_body(self, email_content):
        # Exclude Outlook Migration Emails
        if "Outlook Migration" in email_content:
            return ""

        # Split the content using the forwarded message separator
        content_parts = email_content.split("---------------------- Forwarded by")
        content_body = ""
        if len(content_parts) > 1:
            # if there is forwarded content, keep only the first part
            content_body = content_parts[0]
        else:
            # if no forwarded content, keep the entire email content
            content_body = email_content

        # Remove metadata, lines starting with ">", and other unwanted elements
        email_lines = content_body.split("\n")
        cleaned_lines = [
            line
            for line in email_lines
            if not line.strip().startswith(
                (
                    "From:",
                    "Subject:",
                    "To:",
                    "Date:",
                    "Message-ID:",
                    "Mime-Version:",
                    "Content-Type:",
                    "Content-Transfer-Encoding:",
                    "X-From:",
                    "X-To:",
                    "X-Folder:",
                    "X-Origin:",
                    "X-FileName:",
                    "X-cc:",
                    "X-bcc:",
                    "Cc:",
                    "Bcc:",
                    "-----Original Message-----",
                )
            )
            and not line.startswith(">")
        ]

        cleaned_email_body = "\n".join(cleaned_lines)

        return cleaned_email_body.strip()

    def __remove_urls(self, text):
        url_pattern = re.compile(r"https?://\S+|www\.\S+")
        return url_pattern.sub("", text)

    def __remove_email_addresses(self, text):
        email_pattern = re.compile(r"\S+@\S+")
        return email_pattern.sub("", text)

    def __remove_punctuation(self, text):
        text = [x.replace('-', ' ') for x in text]
        punctuation_free = "".join([character for character in text if character not in string.punctuation])
        return punctuation_free
    
    def __tokenize(self, text):
        tokens = re.split(r'(?u)(?![_/&@.])\W+|(?<!Mr|Dr)\.(?!\w)\W*', text)
        return tokens

    def __remove_stopwords(self, tokens):
        removed_stopwords = []
        for token in tokens:
            if token not in self.__stop_words:
                removed_stopwords.append(token)
        return removed_stopwords

    def __correct_spelling(self, text):
        corrected_words = []
        for word in text:
            corrected = self.__spellChecker.correction(word)
            if corrected is not None:
                corrected_words.append(corrected)
            else:
                corrected_words.append(word)
        return corrected_words

    def __Lemmatization(self, text):
        lemm_text = [self.__lemmatizer.lemmatize(word) for word in text]
        return lemm_text

    def CleanEmails(self, raw_email_content):
        self.__emails = [['Subject', 'From', 'To', 'Date', 'Message-ID', 'Content', 'No Punctuation', 'Lowered', 'Tokenized', 'No-Stop-Words', 'Lemmatized']]
        preprocessed_email_content = self.__extract_email_body(raw_email_content)
        preprocessed_email_content = self.__remove_urls(preprocessed_email_content)
        preprocessed_email_content = self.__remove_email_addresses(preprocessed_email_content)
        cleaned_email_content = self.__remove_punctuation(preprocessed_email_content)
        lower_case_content = cleaned_email_content.lower()
        tokenized_content = word_tokenize(lower_case_content)
        spell_checked_content = self.__correct_spelling(tokenized_content)
        stopword_free_content = self.__remove_stopwords(spell_checked_content)
        lemmatized_content = self.__Lemmatization(stopword_free_content)

        # email content
        if preprocessed_email_content and not preprocessed_email_content.isspace():
            email = Parser().parsestr(raw_email_content)
            self.__emails.append([email.get("subject", "N/A"), email.get("from", "N/A"), email.get("to", "N/A"), email.get("date", "N/A"), email.get("message-id", "N/A"), preprocessed_email_content, cleaned_email_content, lower_case_content, tokenized_content,stopword_free_content, lemmatized_content])

    def Simple_Clean(self, raw_email_content):
        preprocessed_email_content = self.__extract_email_body(raw_email_content)
        preprocessed_email_content = self.__remove_urls(preprocessed_email_content)
        preprocessed_email_content = self.__remove_email_addresses(preprocessed_email_content)
        cleaned_email_content = self.__remove_punctuation(preprocessed_email_content)
        lower_case_content = cleaned_email_content.lower()
        stripped_content = lower_case_content.strip()
        no_new_lines_content = stripped_content.replace('\n', ' ').replace('\r', '')

        email = Parser().parsestr(raw_email_content)
        email_datetime = parser.parse(email.get("date", "N/A"))
        email_year = email_datetime.strftime("%Y")
        email_month = email_datetime.strftime("%m")
        email_day = email_datetime.strftime("%d")
        email_time = email_datetime.strftime("%H:%M")

        # email content
        if preprocessed_email_content and not preprocessed_email_content.isspace():
            email = Parser().parsestr(raw_email_content)
            self.__emails.append([email.get("subject", "N/A"), email.get("from", "N/A"), email.get("to", "N/A"), email_year, email_month, email_day, email_time, email.get("message-id", "N/A"), no_new_lines_content])