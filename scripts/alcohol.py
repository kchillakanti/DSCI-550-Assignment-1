import pandas as pd 
from data_reader import raw_data
import requests 
import requests
from bs4 import BeautifulSoup

def webcrawl_alcohol():
   # URL of the webpage
    url = "https://drugabusestatistics.org/alcohol-abuse-statistics/"

    # Send a GET request to fetch the webpage content
    response = requests.get(url)
    response.raise_for_status()  # Raise an error if the request fails

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    # Find the table containing the data
    table = soup.find("table")

    # Extract headers
    headers = [th.text.strip() for th in table.find_all("th")]

    # Extract rows
    data = []
    for row in table.find_all("tr")[1:]:  # Skip header row
        cols = row.find_all("td")
        cols = [col.text.strip() for col in cols]
        data.append(cols)

    # Create a DataFrame
    df = pd.DataFrame(data, columns=headers)
    df.columns = ['state','total_deaths','%_under_21'] 

    return df 

def generate_merge_df(df):
    # Convert numeric columns
    df["total_deaths"] = df["total_deaths"].str.replace(",", "").astype(int)
    df["%_under_21"] = df["%_under_21"].str.replace("%", "").astype(float) / 100

    # Display the DataFrame
    print(df)

    # Save the data to a CSV file
    df.to_csv("./data/alcohol_abuse_statistics.csv", index=False)
    alcohol_df = pd.read_csv("./data/alcohol_abuse_statistics.csv")  

    # standardize state names (convert to uppercase for consistency)
    raw_data['state'] = raw_data['state'] #.str.upper()
    alcohol_df['state'] = alcohol_df['state'] #.str.upper()

    print("Unique states in Haunted Dataset:", raw_data['state'].unique())
    print("Unique states in Alcohol Dataset:", alcohol_df['state'].unique())

    #  Merge datasets on the 'State' column
    merged_df = pd.merge(raw_data, alcohol_df, on="state", how="left")
    print("Total rows:", merged_df.shape[0])
    print("NA in Total_Death:", merged_df[merged_df['total_deaths'].isna()].shape[0])
    print("NA in % Under 21:", merged_df[merged_df['%_under_21'].isna()].shape[0]) 
    return merged_df
    # Save the enriched dataset
    #merged_df.to_csv("haunted_places_with_alcohol.csv", index=False)
    #print("Merged dataset saved as 'haunted_places_with_alcohol.csv'.")

def correlation_df(alcohol_df):
    state_counts = raw_data['state'].value_counts().reset_index()
    state_counts.columns = ['state', 'haunted_places_count']


    correlation_df = state_counts.merge(alcohol_df, on="State", how="left")

    # Compute correlation
    correlation = correlation_df[['haunted_places_count', 'Alcohol Abuse Rate']].corr()

    # Print correlation results
    print("\n🔍 Correlation between Alcohol Abuse and Haunted Places:")
    print(correlation)


if __name__ == "__main__": 
    df = webcrawl_alcohol()
    alcohol_df = generate_merge_df(df) 


