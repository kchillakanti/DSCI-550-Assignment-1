"""
If you want to test your code, there are two options:  
1. run 'python ryan.py' at your command line. 
   Be careful on your current directory(cd) - it should be run when cd is at ..{your directory}/scripts 
2. Copy your code and check it works at ipynb. I made sanbox.ipynb for this purpose. 

"""

from main import raw_data
import pandas as pd
import re


# Load the TSV file
# raw_data = pd.read_csv('haunted_places.tsv', sep='\t')
print(raw_data.head(2))
haunted_places_df = raw_data

# Ensure the description column exists
description_col = "description"  # Update if your column name differs
if description_col not in haunted_df.columns:
    raise ValueError(f"Column '{description_col}' not found in the file.")

# Define flexible keyword mappings for multiple features
keyword_categories = {
    "Audio": {
        "keywords": ["hear", "heard", "hearing"]
    },
    "Visual": {
        "keywords": ["saw", "see", "seeing", "seen", "appears", "appeared"]
    },
    "Time of Day": {
        "categories": {
            "Morning": ["morning", "sunrise"],
            "Afternoon": ["afternoon", "midday"],
            "Evening": ["evening", "nightfall"],
            "Dusk": ["dusk", "sunset"],
            "Night": ["night", "midnight"]
        }
    },
    "Apparition Type": {
        "categories": {
            "Ghost": ["ghost", "spirit", "phantom", "specter"],
            "Orb": ["orb", "floating light"],
            "UFO": ["ufo"],
            "UAP": ["uap"],
            "Male": ["male figure", "man", "gentleman"],
            "Female": ["female figure", "woman", "lady"],
            "Child": ["child", "boy", "girl", "young figure"],
            "Several Ghosts": ["several ghosts", "multiple spirits", "many apparitions"]
        }
    },
    "Event Type": {
        "categories": {
            "Murder": ["murder", "homicide", "killed", "stabbed", "shot", "strangled", "assassinated"],
            "Death": ["died", "corpse", "dead body", "passed away", "deceased", "remains", "funeral"],
            "Supernatural Phenomenon": ["haunted", "paranormal", "poltergeist", "possession", "supernatural", "entity", "demonic"]
        }
    }
}

# Function to check for single-category matches (e.g., Audio -> True/False)
def contains_keywords(text, keywords):
    if pd.isna(text):
        return False
    text = text.lower()
    return any(re.search(rf"\b{kw}s?\b", text) for kw in keywords)


# Function to determine multi-category matches (e.g., Time of Day -> "Morning")
def determine_category(text, categories):
    if pd.isna(text):
        return "Unknown"
    text = text.lower()
    found_categories = [category for category, keywords in categories.items()
                        if any(re.search(rf"\b{kw}s?\b", text) for kw in keywords)]

    return ", ".join(found_categories) if found_categories else "Unknown"


# Apply keyword detection dynamically
for column, config in keyword_categories.items():
    if "keywords" in config:  # Single-category (True/False)
        haunted_df[column] = haunted_df[description_col].apply(lambda x: contains_keywords(str(x), config["keywords"]))
    elif "categories" in config:  # Multi-category (e.g., Time of Day, Apparition Type, Event Type)
        haunted_df[column] = haunted_df[description_col].apply(
            lambda x: determine_category(str(x), config["categories"]))

"""
# This code for Jupyter Notebook checks
# Save the updated file
output_file = "c1_updated_flexible_columns.tsv"
haunted_df.to_csv(output_file, sep="\t", index=False)

# print(f"Updated file saved as: {output_file}")
"""

# Output_for_chain : this conveys your output to next person
# Put your sliced column(use df[['col_name']]), not the whole dataframe"
output_for_chain = haunted_places_df[['Audio', 'Visual', 'Time of Day', 'Apparition Type', 'Event Type']]
