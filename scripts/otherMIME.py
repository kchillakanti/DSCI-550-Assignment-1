import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import Point
from sklearn.neighbors import BallTree
import glob
import os
from datetime import datetime, timedelta
from scipy.spatial import cKDTree
import cv2
import pytesseract
import shutil
import re


def add_public_school_dataset(previous_haunted_df):
    """
    This function takes a TSV file input, joins it with a public school dataset,
    and adds 3 new features to the initial input.
    """
    # Load haunted places dataset from TSV
    #haunted_df = pd.read_csv(file_path, sep="\t")
    haunted_df = previous_haunted_df

    # Load the Public Schools GeoJSON File
    schools_gdf = gpd.read_file("../data/Public_Schools_-5088709809754466635.geojson")

    # Extract latitude and longitude from the geometry
    schools_gdf["latitude"] = schools_gdf.geometry.y
    schools_gdf["longitude"] = schools_gdf.geometry.x

    # Convert to DataFrame (removing geometry)
    schools_df = schools_gdf.drop(columns=["geometry"])

    
    # Convert Haunted Places to GeoDataFrame
    haunted_gdf = gpd.GeoDataFrame(
        haunted_df,
        geometry=gpd.points_from_xy(haunted_df["longitude"], haunted_df["latitude"]),
        crs="EPSG:4326"
    )

    # Convert Schools CSV to GeoDataFrame
    schools_gdf = gpd.GeoDataFrame(
        schools_df,
        geometry=gpd.points_from_xy(schools_df["longitude"], schools_df["latitude"]),
        crs="EPSG:4326"
    )

    # Convert both datasets to EPSG:3857 (meters-based projection)
    schools_gdf = schools_gdf.to_crs(epsg=3857)
    haunted_gdf = haunted_gdf.to_crs(epsg=3857)

    # Create a 10-mile buffer around each haunted place
    haunted_gdf["buffer_10_miles"] = haunted_gdf.geometry.buffer(10 * 1609.34)

    # Count schools within the buffer of each haunted place
    haunted_gdf["schools_within_10_miles"] = haunted_gdf["buffer_10_miles"].apply(
        lambda buffer: schools_gdf[schools_gdf.geometry.within(buffer)].shape[0]
    )

    # Compute nearest school distances using BallTree
    def compute_nearest_distances(haunted_gdf, schools_gdf):
        """
        Computes the nearest school distance for each haunted location using BallTree.
        """
        # Drop rows with NaN values in latitude/longitude
        haunted_gdf = haunted_gdf.dropna(subset=["latitude", "longitude"]).copy()
        schools_gdf = schools_gdf.dropna(subset=["latitude", "longitude"]).copy()

        # Convert degrees to radians for BallTree
        haunted_coords = np.radians(haunted_gdf[["latitude", "longitude"]].to_numpy())
        school_coords = np.radians(schools_gdf[["latitude", "longitude"]].to_numpy())

        if school_coords.shape[0] == 0:
            print("⚠ No valid school coordinates found. Setting distance to NaN.")
            haunted_gdf["distance_to_nearest_school_km"] = np.nan
            return haunted_gdf

        # Build BallTree with school locations
        tree = BallTree(school_coords, metric="haversine")

        # Query the nearest school for each haunted location
        distances, _ = tree.query(haunted_coords, k=1)

        # Convert from radians to kilometers (Earth's radius = 6371 km)
        haunted_gdf.loc[:, "distance_to_nearest_school_km"] = distances[:, 0] * 6371

        return haunted_gdf

    # Compute distances using BallTree
    haunted_gdf = compute_nearest_distances(haunted_gdf, schools_gdf)

    # Add feature 3: Check if haunted place is a school
    haunted_gdf.loc[:, "is_haunted_place_a_school"] = haunted_gdf["location"].str.contains(
        "school", case=False, na=False
    ).map({True: "Yes", False: "No"})

    # Save the updated dataset
    haunted_gdf.to_csv("../data/haunted_places_with_new_features.csv", index=False)
    print("="*30,"otherMIME--Public school dataset has been added successfully","="*30 ) 
    return haunted_gdf

def add_weather_dataset(file):
    """
    This function loads a CSV file containing haunted places, merges it with a weather dataset,
    and adds relevant weather features to each haunted place using the nearest weather station.

    - Extracts weather data from .dly files
    - Filters for US-based stations
    - Keeps only PRCP, SNWD, TMAX, and TMIN values
    - Converts wide format to long format
    - Filters for the last 3 years
    - Merges with station location data
    - Uses KDTree to efficiently find the nearest station for each haunted place
    - Adds derived weather features such as Diurnal Temperature Range (DTR)

    Returns:
        final_df (pd.DataFrame): Processed dataset with added weather features.
    """

    # Path to the folder containing .dly files
    folder_path = "../data/GLOBAL_HISTORICAL_CLIMATOLOGY_NETWORK"  

    # Get a list of all .dly files
    file_list = glob.glob(os.path.join(folder_path, "*.dly"))

    # Define fixed-width columns and corresponding field names
    column_specs = [
        (0, 11),  # ID (Station ID)
        (11, 15),  # YEAR
        (15, 17),  # MONTH
        (17, 21),  # ELEMENT
    ] + [(21 + i * 8, 26 + i * 8) for i in range(31)]  # 31 DAYS (Values)

    # Column names
    column_names = ["ID", "YEAR", "MONTH", "ELEMENT"] + [f"DAY{i}" for i in range(1, 32)]

    # Elements of interest
    desired_elements = {"PRCP", "SNWD", "TMAX", "TMIN"}  # Precip, Snow Depth, Max/Min Temp

    # Get today's date and compute cutoff for the last 2 years
    today = datetime.today()
    last_3_years = today - timedelta(days=2 * 365)  # Approximate 2 years

    def parse_dly_file(path_to_file):
        """
        Parses a single .dly weather data file, filters relevant elements,
        and converts it to a clean long-format DataFrame.
        """
        try:
            df = pd.read_fwf(path_to_file, colspecs=column_specs, header=None, names=column_names)

            # Filter only US stations (ID starts with 'US')
            df = df[df["ID"].str.startswith("US")]

            # Keep only the required weather elements
            df = df[df["ELEMENT"].isin(desired_elements)]

            # Convert wide format to long format
            df_long = df.melt(id_vars=["ID", "YEAR", "MONTH", "ELEMENT"], 
                              var_name="DAY", value_name="VALUE")

            # Extract numerical day values
            df_long["DAY"] = df_long["DAY"].str.extract(r"(\d+)").astype(int)

            # Remove invalid/missing values (-9999 represents missing data)
            df_long = df_long[df_long["VALUE"] != -9999]

            # Keep only valid day values (1-31)
            df_long = df_long[(df_long["DAY"] >= 1) & (df_long["DAY"] <= 31)]

            # Convert to proper date format and remove invalid dates
            df_long["DATE"] = pd.to_datetime(df_long[["YEAR", "MONTH", "DAY"]], errors="coerce")
            df_long.dropna(subset=["DATE"], inplace=True)

            # Filter for the last 3 years only
            df_long = df_long[df_long["DATE"] >= last_3_years]

            # Drop unnecessary columns
            df_long.drop(columns=["YEAR", "MONTH", "DAY"], inplace=True)

            return df_long
        except Exception as e:
            print(f"Error processing {path_to_file}: {e}")
            return pd.DataFrame()  # Return empty DataFrame in case of errors

    # Efficiently process files and store results in a list
    all_data = [parse_dly_file(file) for file in file_list]
    
    # Combine all processed data
    combined_data = pd.concat(all_data, ignore_index=True) 

    # Load station metadata (ID, Latitude, Longitude)
    stations = pd.read_csv("../data/ghcnd-stations.csv", usecols=[0, 1, 2], 
                           header=None, names=["ID", "latitude", "longitude"])

    # Merge weather data with station locations
    merged_df = combined_data.merge(stations, on="ID", how="left")
    
    # Pivot to get a structured format with weather elements as columns
    merged_df_pivot = merged_df.pivot_table(index="ID", columns="ELEMENT", values="VALUE", aggfunc="mean").reset_index()


    # Rename columns for clarity
    merged_df_pivot.columns = ["ID", "Avg_PRCP", "Avg_SNWD", "Avg_TMAX", "Avg_TMIN"]


    # Merge station locations back
    merged_df = merged_df_pivot.merge(stations, on="ID", how="left")

    # Load haunted places dataset
    haunted_places = file


    # Extract coordinates from haunted places
    haunted_coords = np.array(haunted_places[["latitude", "longitude"]])
    

    station_coords = np.array(merged_df[["latitude", "longitude"]])

    # Use KDTree for efficient nearest neighbor search
    tree = cKDTree(station_coords)
    distances, nearest_station_indices = tree.query(haunted_coords)

    # Assign nearest station to each haunted place
    haunted_places["nearest_station_id"] = merged_df.iloc[nearest_station_indices]["ID"].values

    # Merge weather data into haunted places dataset
    final_df = haunted_places.merge(merged_df, left_on="nearest_station_id", right_on="ID", suffixes=("", "_station"))

    # Remove redundant columns
    final_df.drop(columns=["ID", "nearest_station_id", "latitude_station", "longitude_station"], inplace=True, errors="ignore")

    # Compute Diurnal Temperature Range (DTR)
    final_df["Diurnal Temperature Range (DTR)"] = final_df["Avg_TMAX"] - final_df["Avg_TMIN"]

    # Drop TMAX and TMIN as they are no longer needed
    final_df.drop(columns=["Avg_TMAX", "Avg_TMIN"], inplace=True)
    print("="*30,"otherMIME--Weather dataset has been added successfully","="*30 )
    return final_df

    
def add_last_dataset(second_dataset_added):
    # Find Tesseract path automatically
    tesseract_path = shutil.which("tesseract")

    # If not found, set it manually
    if tesseract_path is None:
        import platform
        os_name = platform.system()
        if os_name == "Windows":
            tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Change if installed elsewhere
        elif os_name == "Darwin":  # macOS
            tesseract_path = "/opt/homebrew/bin/tesseract"
        elif os_name == "Linux":
            tesseract_path = "/usr/bin/tesseract"  # Adjust based on your installation
        else:
            raise FileNotFoundError("Tesseract-OCR not found. Please install Tesseract-OCR first: https://github.com/UB-Mannheim/tesseract/wiki")
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

    # Hard-coded dictionary of approximate center coordinates for each state:
    states_coords = {
        "Alabama": (1480, 890),
        "Arizona": (560, 830),
        "Arkansas": (1270, 800),
        "California": (250, 695),
        "Colorado": (780, 605),
        "Connecticut": (2000, 485),
        "Delaware": (1850, 615),
        "Florida": (1660, 1080),
        "Georgia": (1615, 920),
        "Idaho": (450, 360),
        "Illinois": (1380, 550),
        "Indiana": (1490, 590),
        "Iowa": (1230, 460),
        "Kansas": (1040, 640),
        "Kentucky": (1560, 670),
        "Louisiana": (1280, 1000),
        "Maine": (2140, 310),
        "Maryland": (1850, 620),
        "Massachusetts": (1995, 440),
        "Michigan": (1560, 420),
        "Minnesota": (1200, 230),
        "Mississippi": (1380, 880),
        "Missouri": (1270, 630),
        "Montana": (630, 195),
        "Nebraska": (1000, 480),
        "Nevada": (360, 590),
        "New Hampshire": (2060, 390),
        "New Jersey": (1930, 550),
        "New Mexico": (760, 820),
        "New York": (1920, 410),
        "North Carolina": (1760, 760),
        "North Dakota": (990, 170),
        "Ohio": (1630, 545),
        "Oklahoma": (1080, 770),
        "Oregon": (225, 360),
        "Pennsylvania": (1800, 540),
        "Rhode Island": (2060, 485),
        "South Carolina": (1700, 850),
        "South Dakota": (980, 340),
        "Tennessee": (1510, 760),
        "Texas": (1000, 930),
        "Utah": (560, 590),
        "Vermont": (1980, 315),
        "Virginia": (1800, 680),
        "Washington": (235, 178),
        "West Virginia": (1710, 650),
        "Wisconsin": (1360, 330),
        "Wyoming": (715, 410),
    }

    # Path to your image (2256x1270):
    image_path = "../data/img/mental_health.jpg"

    # Read the image
    image = cv2.imread(image_path)

    if image is None:
        raise ValueError("Could not load image. Check the file path.")

    crop_w, crop_h = 140, 70
    results = {}
    state_colors = {}

    for state, (cx, cy) in states_coords.items():
        x1 = max(cx - crop_w // 2, 0)
        y1 = max(cy - crop_h // 2, 0)
        x2 = min(x1 + crop_w, image.shape[1] - 1)
        y2 = min(y1 + crop_h, image.shape[0] - 1)
        
        roi_bgr = image[y1:y2, x1:x2]
        
        # Upscale the small ROI to help Tesseract
        roi_bgr = cv2.resize(roi_bgr, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        
        # Convert to HSV and isolate dark text
        roi_hsv = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2HSV)
        lower_dark = np.array([0, 0, 0])       # guess for dark
        upper_dark = np.array([180, 255, 80])  # guess for lightness upper bound
        mask = cv2.inRange(roi_hsv, lower_dark, upper_dark) 
        mask_inv = 255 - mask

        # Morphological opening to remove specs
        kernel = np.ones((2,2), np.uint8)
        processed = cv2.morphologyEx(mask_inv, cv2.MORPH_OPEN, kernel)
        
        # OCR - digit only
        text = pytesseract.image_to_string(processed, config="--psm 7 -c tessedit_char_whitelist=0123456789")
        text = text.strip()
        
        # Filter out non-digit characters
        digits_only = re.sub(r"[^0-9]", "", text)
        
        results[state] = max(min(int(digits_only),677),135) if digits_only else 179

        ### **Extract Non-White, Non-Black State Color** ###
        roi_pixels = roi_bgr.reshape(-1, 3)  # Flatten the ROI to a list of pixels

        # Define color thresholds (tunable)
        min_black = 55   # Below this is black
        max_white = 225  # Above this is white

        # Filter out black and white pixels
        valid_pixels = [
            (r, g, b) for b, g, r in roi_pixels
            if (r > min_black or g > min_black or b > min_black)  # Not black
            and (r < max_white or g < max_white or b < max_white)  # Not white
        ]

        # Compute the average color if valid pixels exist
        if valid_pixels:
            avg_color = np.mean(valid_pixels, axis=0).astype(int)  # Compute mean and convert to int
            state_colors[state] = tuple(avg_color)  # Store as (R, G, B)
        else:
            state_colors[state] = (0, 0, 0)  # Default if no valid color found

    # Print extracted numbers and colors
    #print("\n--- Extracted Numbers ---")
    #for st, val in results.items():
    #    print(f"{st}: {val}")

    #print("\n--- Extracted State Colors (Filtered) ---")
    #for st, color in state_colors.items():
    #    print(f"{st}: RGB {color}")

    temp_df1 = pd.DataFrame({"state":results.keys(), "mental_health_provider":results.values()})
    temp_df2 = pd.DataFrame({"state":state_colors.keys(), "mental_health_RGB":state_colors.values()})
    mental_health_df = pd.merge(temp_df1, temp_df2, on='state',how='left')

    temp_df1 = pd.DataFrame({"state":results.keys(), "mental_health_provider":results.values()})
    temp_df2 = pd.DataFrame({"state":state_colors.keys(), "mental_health_RGB":state_colors.values()})
    mental_health_df = pd.merge(temp_df1, temp_df2, on='state',how='left')
    add_alaska = pd.DataFrame({'state':'Alaska', 'mental_health_provider':723, 'mental_health_RGB':[(97, 186, 185)]})
    add_hawaii = pd.DataFrame({'state':'Hawaii', 'mental_health_provider':299, 'mental_health_RGB':[(194, 205, 198)]})

    mental_health_df = pd.concat([add_alaska, add_hawaii, mental_health_df], axis=0, ignore_index=True).sort_values('state').reset_index(drop=True)
    mental_health_df




    def get_pipeline_coordinates():
        # Load the image
        image_path = "../data/img/gas_pipe.png"
        image = cv2.imread(image_path)

        # Convert image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Define color ranges for blue and orange in RGB format
        blue_lower = np.array([0, 0, 128])  # Approximate lower bound for blue
        blue_upper = np.array([100, 150, 255])  # Approximate upper bound for blue

        orange_lower = np.array([200, 100, 0])  # Approximate lower bound for orange
        orange_upper = np.array([255, 180, 80])  # Approximate upper bound for orange

        # Create masks for blue and orange pixels
        blue_mask = cv2.inRange(image_rgb, blue_lower, blue_upper)
        orange_mask = cv2.inRange(image_rgb, orange_lower, orange_upper)

        # Get pixel coordinates
        blue_pixels = np.column_stack(np.where(blue_mask > 0))
        orange_pixels = np.column_stack(np.where(orange_mask > 0))

        # Mapping function for latitude and longitude
        def pixel_to_geo(x, y, width=901, height=461):
            lat = 25 + (50 - 25) * (1 - y / 460)  # Linear interpolation for latitude
            lon = -125 + (-70 + 125) * (x / 854)  # Linear interpolation for longitude
            return lat, lon

        # Convert pixel coordinates to geo-coordinates
        blue_coords = [pixel_to_geo(x, y) for y, x in blue_pixels]
        orange_coords = [pixel_to_geo(x, y) for y, x in orange_pixels]

        # Create DataFrames for visualization
        blue_df = pd.DataFrame(blue_coords, columns=["latitude", "longitude"])
        orange_df = pd.DataFrame(orange_coords, columns=["latitude", "longitude"])

        return blue_df, orange_df 
    
    blue_df, orange_df = get_pipeline_coordinates()


    def find_nearby_points_fast(haunted_df, blue_df, orange_df, radius_miles=10):
        """

        Quickly finds if any blue or orange points exist within a rough bounding box of ±5 miles.

        Parameters:
        - haunted_df: DataFrame containing haunted place locations with "Latitude" and "Longitude".
        - blue_df: DataFrame containing blue point coordinates with "Latitude" and "Longitude".
        - orange_df: DataFrame containing orange point coordinates with "Latitude" and "Longitude".
        - radius_miles: Distance threshold in miles (default=10, meaning ±5 miles).

        Returns:
        - A DataFrame indicating if there are nearby blue or orange points for each haunted place.
        """

        # Convert miles to latitude degrees (1 mile ≈ 0.0145 degrees)
        mile_to_degree = 0.0145  # Approximate conversion factor
            # Initialize new columns
        haunted_df["intrastate_gaspipe_within_10miles"] = False
        haunted_df["interstate_gaspipe_within_10miles"] = False


        for idx, hplace in haunted_df.iterrows():
            hplace_state, hplace_lat, hplace_lon = hplace['state'], hplace["latitude"], hplace["longitude"]

            # Compute bounding box (±5 miles)
            lat_range = radius_miles / 2 * mile_to_degree
            lon_range = (radius_miles / 2 * mile_to_degree) / np.cos(np.radians(hplace_lat))

            lat_min, lat_max = hplace_lat - lat_range, hplace_lat + lat_range
            lon_min, lon_max = hplace_lon - lon_range, hplace_lon + lon_range

            # Filter blue and orange points inside the bounding box
            blue_nearby = not blue_df[
                (blue_df["latitude"] >= lat_min) & (blue_df["latitude"] <= lat_max) &
                (blue_df["longitude"] >= lon_min) & (blue_df["longitude"] <= lon_max)
            ].empty

            orange_nearby = not orange_df[
                (orange_df["latitude"] >= lat_min) & (orange_df["latitude"] <= lat_max) &
                (orange_df["longitude"] >= lon_min) & (orange_df["longitude"] <= lon_max)
            ].empty

            haunted_df.at[idx, "intrastate_gaspipe_within_10miles"] = blue_nearby
            haunted_df.at[idx, "interstate_gaspipe_within_10miles"] = orange_nearby

        return haunted_df

    # Example usage:
    result_df = find_nearby_points_fast(second_dataset_added, blue_df, orange_df)
    result_df = result_df.merge(mental_health_df, how='left', on='state')
    print("Feature extraction is done successfully. Save the result in arcgis_img.csv")
    result_df.reset_index(drop=True).to_csv('../data/arcgis_img.csv')

    print("="*30,"otherMIME--arcgis image data has been added successfully","="*30 )
    return result_df

def add_external_datasets(previous_haunted_df):
    """
    previous_haunted_df = pd.DataFrame 
    """
    first_dataset_added = add_public_school_dataset(previous_haunted_df) 
    print("--df.shape(add_public_school_dataset):",first_dataset_added.shape) 
    second_dataset_added = add_weather_dataset(first_dataset_added)
    print("--df.shape(add_weather_dataset):",second_dataset_added.shape)
    third_dataset_added = add_last_dataset(second_dataset_added)
    print("--df.shape(add_last_dataset):",third_dataset_added.shape)
    return third_dataset_added


if __name__ == '__main__':
    # for code QA :
    from data_reader import raw_data
    temp = add_last_dataset(raw_data) 
    print(temp.head(5)) 
    #final_dataset = external_datasets()