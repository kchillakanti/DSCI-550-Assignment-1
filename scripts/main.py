
import pandas as pd
from ryan import output_for_chain as chain_1 #-- pd.DataFrame
from lance import output_for_chain as chain_2 #-- pd.DataFrame
from kirthi import output_for_chain as chain_3 #-- pd.DataFrame

data_path = "../data/haunted_places.tsv" 
raw_data = pd.read_csv(data_path,sep='\t')

def main():
    """Main function to load raw data and make it accessible to all modules."""
    
    print(raw_data.head(2))
    
    # Put together the features from ryan, lance, and kirthi
    combined_df = pd.concat(raw_data, chain_1,chain_2, chain_3, axis=1)

    # Joining alchol abuse and daylight data 

    # Join Alcohol Abuse Dataset


    alcohol_df = pd.read_csv("alcohol_abuse_statistics.csv")  

    # standardize state names (convert to uppercase for consistency)
    raw_data['State'] = raw_data['State'].str.upper()
    alcohol_df['State'] = alcohol_df['State'].str.upper()


    print("Unique states in Haunted Dataset:", raw_data['State'].unique())
    print("Unique states in Alcohol Dataset:", alcohol_df['State'].unique())

    #  Merge datasets on the 'State' column
    merged_df = pd.merge(raw_data, alcohol_df, on="State", how="left")

    # Save the enriched dataset
    merged_df.to_csv("haunted_places_with_alcohol.csv", index=False)
    print("Merged dataset saved as 'haunted_places_with_alcohol.csv'.")


    state_counts = raw_data['State'].value_counts().reset_index()
    state_counts.columns = ['State', 'Haunted_Places_Count']


    correlation_df = state_counts.merge(alcohol_df, on="State", how="left")

    # Compute correlation
    correlation = correlation_df[['Haunted_Places_Count', 'Alcohol Abuse Rate']].corr()

    # Print correlation results
    print("\n🔍 Correlation between Alcohol Abuse and Haunted Places:")
    print(correlation)



    # Joining 3 additional dataset
    

if __name__ == "__main__":
    main()
