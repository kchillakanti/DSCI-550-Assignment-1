
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

    # Joining 3 additional dataset
    

if __name__ == "__main__":
    main()
