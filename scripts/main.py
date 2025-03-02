
import os 
import pandas as pd
from scripts.data_reader import raw_data
from scripts.extractor_audio_visual import output_for_chain as chain_1 #-- pd.DataFrame
from scripts.extractor_date import output_for_chain as chain_2 #-- pd.DataFrame
from scripts.extractor_witness_count import output_for_chain as chain_3 #-- pd.DataFrame
from scripts.combiner import data_join
from scripts.tika import run_tika 


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
    first_processed_data = pd.concat(raw_data, chain_1, chain_2, chain_3, axis=1)
    second_processed_data = data_join(first_processed_data)
    tika_similarities = run_tika(second_processed_data) 

if __name__ == "__main__":
    temp()
