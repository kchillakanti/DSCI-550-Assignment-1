import cv2
import pytesseract
import numpy as np
import pandas as pd 
import re

# If Tesseract is not in your PATH, uncomment and specify its location:
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

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
print("\n--- Extracted Numbers ---")
for st, val in results.items():
    print(f"{st}: {val}")

print("\n--- Extracted State Colors (Filtered) ---")
for st, color in state_colors.items():
    print(f"{st}: RGB {color}")

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


import numpy as np
import pandas as pd
import cv2

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

    results = []
    
    for _, hplace in haunted_df.iterrows():
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

        results.append({
            "state": hplace_state,
            "latitude": hplace_lat,
            "longitude": hplace_lon,
            "intrastate_gaspipe_within_10miles": blue_nearby,
            "interstate_gaspipe_within_10miles": orange_nearby
        })
    
    return  pd.DataFrame(results)

# Example usage:
blue_df, orange_df = get_pipeline_coordinates()
haunted_df = pd.read_csv('../data/haunted_places.tsv',sep='\t')
result_df = find_nearby_points_fast(haunted_df, blue_df, orange_df)
# print(result_df)

result_df = result_df.merge(mental_health_df, how='left', on='state')
print("Feature extraction is done successfully. Save the result in arcgis_img.csv")
result_df.to_csv('../data/arcgis_img.csv')
result_df