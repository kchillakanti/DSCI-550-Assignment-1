# lance.py - This module is created to extract dates from the description using the LLM, parser and Regex
import pandas as pd
import re
from dateutil import parser
import spacy
from datetime import datetime
from scripts.data_reader import raw_data

# Load the spaCy model for NLP
nlp = spacy.load("en_core_web_sm")

def extract_date(description):
    if pd.isna(description) or not isinstance(description, str):
        return datetime(2025, 1, 1).date()  # Default date
    
    # Try regex patterns for common date formats
    date_patterns = [
        r'\b(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\b',  # e.g., 04/15/2019 or 15-04-2019
        r'\b(\d{4}-\d{1,2}-\d{1,2})\b',           # e.g., 2019-04-15
        r'\b(\d{4})\b'                           # e.g., 2019
    ]
    
    for pattern in date_patterns:
        match = re.search(pattern, description)
        if match:
            try:
                return parser.parse(match.group(0), fuzzy=True).date()
            except Exception:
                continue

    # Use spaCy's NLP to identify natural language dates
    doc = nlp(description)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            try:
                return parser.parse(ent.text, fuzzy=True).date()
            except Exception:
                continue

    # Return default date if no date is found
    return datetime(2025, 1, 1).date()

def add_date_occured_column():
    #new_df = pd.read_csv("../data/haunted_places.tsv", sep = "\t")
    new_df = raw_data
    if 'description' not in new_df.columns:
        raise ValueError("DataFrame must contain a 'description' column.")
    new_df['date_occured'] = new_df['description'].apply(extract_date)
    # Return just the new column (sliced out as a DataFrame)
    return new_df[['date_occured']]

output_for_chain = add_date_occured_column()