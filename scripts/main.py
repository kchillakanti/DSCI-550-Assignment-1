# main.py

"""
Main script for loading raw data and making it accessible to modules A, B, and C.
"""

import pandas as pd
from modules import module_a, module_b, module_c

data_path = "raw_data.csv"
raw_data = pd.read_csv(data_path)

def main():
    """Main function to load raw data and make it accessible to all modules."""
    raw_data = load_raw_data(RAW_DATA_PATH)
    
    print("Initial Raw Data Preview:")
    print(raw_data.head())
    
    # Pass the raw data to different modules
    processed_data_a = module_a.process_dataframe(raw_data)
    processed_data_b = function_1(processed_data_a)
    processed_data_c = function_2(processed_data_b) 
    
        
        

if __name__ == "__main__":
    main()


