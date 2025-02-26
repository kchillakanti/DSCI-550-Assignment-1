"""
If you want to test your code, 
1. run 'python ryan.py' at your command line. 
   Be careful on your current directory(cd) - it should be run when cd is at ..{your directory}/scripts 
2. Copy your code and check it works at ipynb. I made sanbox.ipynb for this purpose. 

"""

from main import raw_data
import pandas as pd

# raw_data = pd.read_csv('haunted_places.tsv', sep='\t')
print(raw_data.head(2))


haunted_places_df = raw_data 

# Define keywords (values) and their corresponding Indicator ("True" as the key)
audio_keywords = {
    "True": ["hear", "heard", "hearing", "knocking", "appeared", "noise", "noises"]
}

image_keywords = {
    "True": ["saw", "see", "seeing", "seen", "appears", "appeared"]
}

time_of_day_keywords = {
    "Morning": ["morning", "sunrise"],
    "Dusk": ["dusk", "sunset"],
    "Evening": ["evening", "midnight", "night", "nighttime"]
}

# this one wil require some more thought for sub-types of ghosts
apparition_keywords = {
    "Ghost":[{"Male Ghost": ["?"]}, {"Female Ghost": ["?"]}, {"Child Ghost": ["?"]}],
    "Orb": ["orb", "orbs", "ball of light", "floating balls", "hovering ball"],
    "UFO": ["ufo", "unidentified flying object", "unidentified flying objects"],
    "UAP": ["unidentified aerial phenomenon", "unidentified aerial phenomena"],
}

event_keywords = {
    "Murder": ["murder", "murdered"],
    "Suicide": ["killed himself", "killed herself", "killed themselves", "suicide"],
    "Random Death": ["died", "expired", "unexplained death"],
    "Disappearance": ["disappeared", "vanished", "kidnapped"],
    "Supernatural Phenomenon": ["?"]
}


# Function to extract Indicator from text description
def extract_audio(description):
    if pd.isna(description):
        return "False"
    description = description.lower() # do I need to strip punctuation?
    for audio_evidence, keywords in audio_keywords.items():
        if any(keyword in description for keyword in keywords):
            return audio_evidence
        else: return "False"

# Apply extraction function to the Description column and populate the Audio column
for row in haunted_places_df:
    df["Audio"] = df["description"].apply(extract_audio)
    df["Visual"] = df["description"].apply(extract_image)
    # Continue applying functions if these work as expected



# output_for_chain : this conveys your output to next person
output_for_chain = "put your sliced column(use df[['col_name']]), not the whole dataframe"