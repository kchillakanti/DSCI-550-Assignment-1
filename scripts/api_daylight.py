import pandas as pd
import re
import requests
from datetime import datetime, timedelta
import time
from scripts.data_reader import raw_data

# Bring daylight hours through API
def hours_to_minutes(hours:str):

    temp = hours.strip().split(":")
    minutes = 0
    for idx, t in enumerate(temp):
        minutes += (idx==0)*(int(t)*60)+(idx==1)*(int(t))

    return minutes


def daylight_retriever(latitude, longitude, date_occured):
    base_url = "https://aa.usno.navy.mil/api/rstt/oneday"
    params = {'date':f'{date_occured}','coords':f'{round(latitude,2)}, {round(longitude,2)}'}
    temp= requests.get(base_url, params)
    temp_json = temp.json()
    try:
        sunrise_time = temp_json['properties']['data']['sundata'][1]['time']
        sunset_time = temp_json['properties']['data']['sundata'][3]['time']
        daylight_h = datetime.strptime(sunset_time,'%H:%M')-datetime.strptime(sunrise_time,'%H:%M')
        daylight_m = hours_to_minutes(str(daylight_h))

    except:
        #print(f"{date_occured}:")
        return None

    return daylight_m


def batch_run(raw_data, chunk_size=500):
    data = raw_data

    # Define chunk size (e.g., 500 rows per batch)
    chunk_size = chunk_size
    num_chunks = len(data) // chunk_size + 1

    # Create an empty list to store results
    daylight_results = []

    # Process data in chunks
    for i in range(num_chunks):
        start_idx = i * chunk_size
        end_idx = min((i + 1) * chunk_size, len(data))

        print(f"Processing batch {i+1}/{num_chunks} (rows {start_idx} to {end_idx})...")

        # Apply function to the chunk
        batch_results = data.iloc[start_idx:end_idx].apply(
            lambda x: daylight_retriever(x['city_latitude'], x['city_longitude'], x['date_occured']),
            axis=1
        )

        # Store results
        daylight_results.extend(batch_results)

        # Pause to prevent API rate limiting
        time.sleep(3)  # Adjust the delay based on API response time

    # Assign results to the dataframe
    data['daylight_minutes'] = daylight_results
    data.to_csv('../data/daylight_added.tsv',sep='\t')
    return data[['daylight_minutes']]

output_for_chain = batch_run(raw_data, chunk_size=500)  