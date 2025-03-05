import pandas as pd
import re
import requests
from datetime import datetime, timedelta
import time
from scripts.data_reader import raw_data

import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime

##################################################################################3
# Source 1 : https://www.timeanddate.com/astronomy/usa

def webcrawl_daylight():
    # URL of interest
    url = "https://www.timeanddate.com/astronomy/usa"
    
    # 1. Fetch the page content
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve page, status code: {response.status_code}")
        return None, None

    # 2. Parse the HTML
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # 3. Find the target table (class="zebra fw tb-sm zebra")
    table = soup.find('table', {'class': 'zebra fw tb-sm zebra'})
    if not table:
        print("Could not find the expected table on the page.")
        return None, None

    data = []

    # 4. Loop over each row in the table (skipping the header)
    rows = table.find_all('tr')[1:]  # first row is the header
    for row in rows:
        cols = row.find_all('td')
        if len(cols) < 3:
            # Not a valid data row
            continue

        # Column 0: City/State info (e.g. "Adak (AK)")
        city_state_full = cols[0].get_text(strip=True)

        # Attempt to parse city and state. 
        # The format might be something like "Adak (AK)" or "Akron – Ohio – USA"
        # Adjust parsing logic according to actual structure you see on the site.
        # For demonstration, let's do a simple split:
        if " – " in city_state_full:
            parts = [p.strip() for p in city_state_full.split("–")]
            if len(parts) >= 2:
                city = parts[0]
                state = parts[1]
            else:
                city = city_state_full
                state = "Unknown"
        else:
            # If the string is like "Adak (AK)"
            city = city_state_full
            # Extract something in parentheses as state, e.g. (AK)
            # This is optional and depends on the site’s structure
            if "(" in city_state_full and ")" in city_state_full:
                state = city_state_full[city_state_full.index("(")+1 : city_state_full.index(")")]
                # Also remove the parentheses from city name
                city = city_state_full.split("(")[0].strip()
            else:
                state = "Unknown"

        # Column 1: Sunrise time (might include '↑')
        sunrise_str = cols[1].get_text(strip=True)
        # Column 2: Sunset time (might include '↓')
        sunset_str = cols[2].get_text(strip=True)

        # Remove unwanted symbols/characters
        for arrow in ['↑', '↓']:
            sunrise_str = sunrise_str.replace(arrow, '').strip()
            sunset_str = sunset_str.replace(arrow, '').strip()

        # 5. Parse times into datetime objects so we can compute the difference
        # Use a dummy date to parse times
        date_str = "2025-01-01"  
        
        try:
            sunrise_dt = datetime.strptime(date_str + " " + sunrise_str, "%Y-%m-%d %I:%M %p")
            sunset_dt = datetime.strptime(date_str + " " + sunset_str, "%Y-%m-%d %I:%M %p")
            # Compute difference in hours
            daylight_minutes = (sunset_dt - sunrise_dt).total_seconds() / 60
        except Exception as e:
            # If parsing fails, skip
            print(f"Parsing error for city={city}, sunrise={sunrise_str}, sunset={sunset_str}, error={e}")
            continue
        
        data.append({
            "city": city,
            "state": state,
            "sunrise": sunrise_dt.strftime("%I:%M %p"),
            "sunset": sunset_dt.strftime("%I:%M %p"),
            "daylight_minutes": daylight_minutes
        })

    # 6. Create a DataFrame
    df = pd.DataFrame(data)

    avg_major_cities = df['daylight_minutes'].mean()

    # 7. Calculate average daylight hours by State
    #avg_by_state = (
    #    df.groupby("state")["daylight_minutes"]
    #      .mean()
    #      .reset_index()
    #      .rename(columns={"daylight_minutes": "avg_daylight_minutes"})
    #)

    return df, avg_major_cities

def generate_daylight_avg_by_state():
    # avg_by_state has two columns: [state, avg_daylight_minutes]
    df, avg_daylight_of_major_cities = webcrawl_daylight()
    if df is not None and avg_daylight_of_major_cities is not None:
        print("\n--- Raw Data (City-Level) ---")
        print(df.head(20))

        print("\n--- Average Daylight Hours of major cities ---")
        #print(avg_daylight_of_major_cities.sort_values("avg_daylight_minutes", ascending=False))
    #avg_daylight_of_major_cities.to_csv('../data/daylight_s1')
    return round(avg_daylight_of_major_cities,1)

avg_daylight_of_major_cities = generate_daylight_avg_by_state()

#####################################################################################
# Source 2 : https://aa.usno.navy.mil/data/Dur_OneYear

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