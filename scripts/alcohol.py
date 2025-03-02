import pandas as pd 
from scripts.data_reader import raw_data

def generate_merge_df(raw_data):
    alcohol_df = pd.read_csv("alcohol_abuse_statistics.csv")  

    # standardize state names (convert to uppercase for consistency)
    raw_data['State'] = raw_data['State'].str.upper()
    alcohol_df['State'] = alcohol_df['State'].str.upper()


    print("Unique states in Haunted Dataset:", raw_data['State'].unique())
    print("Unique states in Alcohol Dataset:", alcohol_df['State'].unique())

    #  Merge datasets on the 'State' column
    merged_df = pd.merge(raw_data, alcohol_df, on="State", how="left")
    return merged_df
    # Save the enriched dataset
    #merged_df.to_csv("haunted_places_with_alcohol.csv", index=False)
    #print("Merged dataset saved as 'haunted_places_with_alcohol.csv'.")

def correlation_df(alcohol_df):
    state_counts = raw_data['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Haunted_Places_Count']


    correlation_df = state_counts.merge(alcohol_df, on="State", how="left")

    # Compute correlation
    correlation = correlation_df[['Haunted_Places_Count', 'Alcohol Abuse Rate']].corr()

    # Print correlation results
    print("\n🔍 Correlation between Alcohol Abuse and Haunted Places:")
    print(correlation)
