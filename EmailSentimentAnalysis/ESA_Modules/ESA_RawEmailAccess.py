# This file will contain the class Raw Email Access and all its logic

from email.parser import Parser
import csv
import os
import re
import pandas as pd


class Preprocessor:
    def __init__(self):
        self.__emails = [['Subject', 'From', 'To', 'Date', 'Message-ID', 'Content']]

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

    def CleanEmails(self, raw_email_content):
        preprocessed_email_content = self.__extract_email_body(raw_email_content)
        preprocessed_email_content = self.__remove_urls(preprocessed_email_content)
        preprocessed_email_content = self.__remove_email_addresses(preprocessed_email_content)

        # email content
        if preprocessed_email_content and not preprocessed_email_content.isspace():
            email = Parser().parsestr(raw_email_content)
            self.__emails.append([email.get("subject", "N/A"), email.get("from", "N/A"), email.get("to", "N/A"), email.get("date", "N/A"), email.get("message-id", "N/A"), preprocessed_email_content])

