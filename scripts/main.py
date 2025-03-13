
import pandas as pd
from extractor_audio_visual import output_for_chain as chain_1 #-- pd.DataFrame
from extractor_date import output_for_chain as chain_2 #-- pd.DataFrame
from extractor_witness_count import output_for_chain as chain_3 #-- pd.DataFrame
from combiner import data_join
from tqdm import tqdm 
import time 

data_path = "../data/haunted_places.tsv" 
raw_data = pd.read_csv(data_path,sep='\t')

def main():
    """Main function to load raw data and make it accessible to all modules."""
    # Put together the features from ryan, lance, and kirthi
    print("★ Initiate first stage of data processing...")
    with tqdm(total=1, desc="Processing Stage 1") as pbar:
        first_processed_data = pd.concat([raw_data, chain_1,chain_2, chain_3], axis=1)
        print("Total rows(first_processed_data):", first_processed_data.shape[0])
        pbar.update(1) 
    print("First process was done! :\n", first_processed_data.head(5))

    # Joining alchol abuse data, daylight data, and three other MIME dataset
    print("★ Initiate second stage of data processing...")
    with tqdm(total=1, desc="Processing Stage 2") as pbar:
        second_processed_data = data_join(first_processed_data) 
        print("Total rows(first_processed_data):", second_processed_data.shape[0])
        pbar.update(1) 
    print("Second process was done! :\n", second_processed_data.head(5)) 
    # Calculate Tika Similarities
    

if __name__ == "__main__":
    main()
