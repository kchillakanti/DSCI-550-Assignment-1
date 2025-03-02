
import pandas as pd
from data_reader import raw_data
from ryan import output_for_chain as chain_1 #-- pd.DataFrame
from lance import output_for_chain as chain_2 #-- pd.DataFrame
from witness_count import output_for_chain as chain_3 #-- pd.DataFrame
from alcohol_abuse import merged_df as chain_4 

def temp():
    print("Chain 1: \n\n")
    print("shape:",chain_1.shape)
    print("\n",chain_1.head(5))

    print("Chain 2: \n\n")
    print("shape:",chain_2.shape)
    print("\n",chain_2.head(5)) 

    print("Chain 3: \n\n")
    print("shape:",chain_3.shape)
    print("\n",chain_3.head(5)) 

    
    return 0 

def main():
    """Main function to load raw data and make it accessible to all modules."""
    
    print(raw_data.head(2))
    
    # Put together the features from ryan, lance, and kirthi
    combined_df = pd.concat(raw_data, chain_1,chain_2, chain_3, axis=1)

    # Joining alchol abuse and daylight data 

    # Join Alcohol Abuse Dataset





    # Joining 3 additional dataset
    

if __name__ == "__main__":
    main()
