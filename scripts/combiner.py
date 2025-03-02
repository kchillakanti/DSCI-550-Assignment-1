import os 
import pandas as pd 

def file_chekcer(keyword):
    # check raw data is prepared for joining 
    found_csvs = []
    for filename in os.listdir('../data'):
        # We check that it's a CSV file (filename ends with .tsv)
        # and that 'keyword' appears in the filename
        if filename.endswith('.tsv') and keyword in filename:
            found_csvs.append(filename)
    return found_csvs
 

def data_join(first_processed_df): 
    first_processed_df = first_processed_df

    #########################################################################
    # Join1 - alcohol abuse data
    alcohol_csv = file_chekcer('alcohol')
    if alcohol_csv:
        print("Your alcohol abuse data is ready to be joined.")
        alcohol_df = pd.read_csv(f"{alcohol_csv[0]}")
        merged_df = pd.merge(first_processed_df, alcohol_df, on="State", how="left")
    else: 
        raise ValueError("Error - Alcohol abuse data is not available!")

    #########################################################################
    # Join2 - daylight data 
    daylight_csv = file_chekcer('daylight')
    if daylight_csv:
        print("Your daylight data is ready to be joined.")
        daylight_df = pd.read_csv(daylight_csv[0]) 
    else: 
        # If raw data to join is not prepared, go and get it. 
        print("You need to download your dataset through API.")
        print("="*30,"Estimated time cost: 100 minutes","="*30)
        from scripts.api_daylight import output_for_chain as daylight_df

    try: 
        print("Attempt to join...")
        daylight_df = daylight_df[['city_latitude','city_longitude','daylight_minutes']]
        merged_df = pd.merge(merged_df, daylight_df, on=('city_latitude','city_longitude'), how='left') 
    except Exception as e : 
        print("Error occured - ", e)  
        
    finally: 
        print("df.head(5):", merged_df.head(5)) 
    
    ########################################################################
    # Join3 - rafayel's data 
