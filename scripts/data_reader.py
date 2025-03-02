
import pandas as pd

data_path = "../data/haunted_places.tsv" 
raw_data = pd.read_csv(data_path,sep='\t')
print(f'raw_data: {data_path}')
print(f'pd.head(5):\n{raw_data.head(5)}')