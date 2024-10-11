import pandas as pd
import unicodedata
import re

def clean_isbn(isbn):
    # Remove spaces and hyphens
    return isbn.replace('-', '').replace(' ', '')

def is_valid_isbn(isbn):
    isbn_cleaned = clean_isbn(isbn)
    pattern = r'^(?:\d{9}[\dXx]|\d{13})$'
    return bool(re.match(pattern, isbn_cleaned))

def remove_invalid_isbn(books):
    return books[books['ISBN'].apply(is_valid_isbn)]

def string_normalize(text):
    # Normalize the text to NFKD form to separate characters and diacritics
    text = unicodedata.normalize('NFKD', text)
    
    # Remove all non-alphanumeric characters except whitespace
    text = re.sub(r'[^\w\s]', '', text)
    
    # Convert text to lowercase and strip leading/trailing whitespace
    text = text.lower().strip()
    
    return text