import os 
import pandas as pd 
from data_reader import raw_data

def file_chekcer(keyword:str, file_type:str):
    """
    File checker inspect a file of given name is available and, if yes, return it. 
    This function is used in data_join() function. 
    """
    # check raw data is prepared for joining 
    found_csvs = []
    for filename in os.listdir('../data'):
        # We check that it's a CSV file (filename ends with .tsv)
        # and that 'keyword' appears in the filename
        if filename.endswith(file_type) and keyword in filename:
            found_csvs.append(filename)
    return found_csvs
 


def data_join(first_processed_df): 
    """
    This function first asks whether the data is prepared by using file_checker().
    If the data is ready, it produces merged_df. 
    If not, run the data collecting function.
    Don't forget to keep merging your dataset on previous merged_df.  
    """

    first_processed_df = first_processed_df
    #########################################################################
    # Join1 - alcohol abuse data
    alcohol_csv = file_chekcer('alcohol','tsv') 
    if alcohol_csv:
        print("Your alcohol abuse data is ready to be joined.")
        alcohol_df = pd.read_csv(f"../data/{alcohol_csv[0]}", )
        merged_df = pd.merge(first_processed_df, alcohol_df, on="state", how="left")
    else: 
        print("You don't have alcohol abuse dataset to join. Initiating web crawling protocol...")
        from alcohol import generate_merge_df, webcrawl_alcohol
        df = webcrawl_alcohol()
        merged_df = generate_merge_df(df) 
    print('--df.shape(alcohol added):',merged_df.shape)

    #########################################################################
    # Join2 - daylight data 
    daylight_tsv = file_chekcer('daylight','tsv')  
    if daylight_tsv:  
        print("Your daylight data is ready to be joined.")  
        daylight_df = pd.read_csv(f"../data/{daylight_tsv[0]}", sep='\t') 
    else: 
        # If raw data to join is not prepared, go and get it. 
        print("You need to download your dataset through API. Initiating the protocol...")
        print("="*30,"Estimated time cost: 100 minutes","="*30)
        from api_daylight import batch_run
        output_for_chain = batch_run(raw_data, chunk_size=500)  
        print("Total rows(daylight)",output_for_chain.shape[0])
        daylight_df = output_for_chain


    try: 
        print("Attempt to join daylight_source: USNO")
        # Slice out only the columns you need.
        daylight_df = daylight_df[['city_latitude','city_longitude','daylight_minutes']]
        merged_df = pd.merge(merged_df, daylight_df, on=('city_latitude','city_longitude'), how='left')

        print("Attempt to daylight_source: timeanddata.com")
        from api_daylight import generate_daylight_avg_by_state
        avg_daylight_of_major_cities = generate_daylight_avg_by_state()
        merged_df['daylight_diff'] = merged_df['daylight_minutes'] - avg_daylight_of_major_cities
        merged_df.to_csv('../data/join_s2.tsv',sep='\t', index=False) 

    except Exception as e : 
        print("Error occured - ", e)  
        
    finally: 
        #print("daylight added-- .head(3):\n", merged_df.head(3)) 
        print('--df.shape(daylight added):',merged_df.shape)
    ########################################################################
    # Join3 - otherMIME type
    print("Attemp to join otherMIME type -(1)public school data, (2)weather data, (3)arcgis images")
    from otherMIME import add_external_datasets
    final_df = add_external_datasets(merged_df)
    print('--df.shape(arcgis added):',final_df.shape) 

    return final_df 

