import os 
import pandas as pd 

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
        alcohol_df = pd.read_csv(f"{alcohol_csv[0]}")
        merged_df = pd.merge(first_processed_df, alcohol_df, on="state", how="left")
    else: 
        from alcohol import generate_merge_df, webcrawl_alcohol
        df = webcrawl_alcohol()
        merged_df = generate_merge_df(df) 

    #########################################################################
    # Join2 - daylight data 
    daylight_csv = file_chekcer('daylight','tsv')  
    if daylight_csv:  
        print("Your daylight data is ready to be joined.")  
        daylight_df = pd.read_csv(daylight_csv[0]) 
    else: 
        # If raw data to join is not prepared, go and get it. 
        print("You need to download your dataset through API.")
        print("="*30,"Estimated time cost: 100 minutes","="*30)
        from api_daylight import output_for_chain as daylight_df

    try: 
        print("Attempt to join daylight_source: USNO")
        # Slice out only the columns you need.
        daylight_df = daylight_df[['city_latitude','city_longitude','daylight_minutes']]
        merged_df = pd.merge(merged_df, daylight_df, on=('city_latitude','city_longitude'), how='left')

        print("Attempt to daylight_source: timeanddata.com")
        from api_daylight import avg_daylight_of_major_cities
        merged_df['daylight_diff'] = merged_df['daylight_minutes'] - avg_daylight_of_major_cities

    except Exception as e : 
        print("Error occured - ", e)  
        
    finally: 
        print("df.head(5):", merged_df.head(5)) 
    
    ########################################################################
    # Join3 - rafayel's data 
    your_dataset = file_chekcer('keyword_for_filename','type_of_your_file') 
    if your_dataset: 
        print("Your daylight data is ready to be joined.")  
        your_df = pd.read_csv(your_dataset[0]) #[0] means the first file of the searched list of files. If you have multiple files to read, go for-loop or list comprehension. 
    
    else: # if your dataset is not ready, run data collecting function
        # from rafayel.py import func_1, func_2 
        # write your code here
        pass 